# ============================================================
# Projet      : GW2 Command Center
# Fichier     : scripts/python/sync_status.py
# Rôle        : Affichage synthétique des dernières synchronisations
# Auteur      : William CROCHOT (MisterWalky)
# Référence   : https://github.com/MisterWalky/gw2-command-center
# Licence     : MIT
# ============================================================
#
# DESCRIPTION
# -----------
# Ce script affiche les dernières synchronisations enregistrées
# dans la table SYNC_LOG.
#
# Pour chaque couple endpoint + locale, il affiche :
# - l'endpoint
# - le statut
# - l'heure de début
# - la durée
# - le nombre d'enregistrements traités
# - le débit moyen
#
# L'affichage est localisé via le système i18n du projet.
# ============================================================

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# ============================================================
# CHEMINS DU PROJET
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]
I18N_DIR = PROJECT_DIR / "dashboard" / "i18n"

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from config.config_base import APP_LANG, SUPPORTED_APP_LANGS, TABLES  # noqa: E402

# ============================================================
# CONSTANTES
# ============================================================

REFERENCE_LANG = "en"
SYNC_LOG_TABLE = TABLES["sync_log"]

UI_NAMESPACE = "SYNC_STATUS_UI"

UI_DEFAULTS = {
    "NO_SYNC": "No synchronization recorded.",
    "MISSING_PATH": "ERROR",
    "MISSING_DB": "Missing database.",
    "COLUMN_ENDPOINT": "ENDPOINT",
    "COLUMN_STATUS": "STATUS",
    "COLUMN_START": "START",
    "COLUMN_DURATION": "DURATION",
    "COLUMN_RECORDS": "RECORDS",
    "COLUMN_RATE": "RATE",
    "LOCALE_ALL": "all",
    "RATE_SUFFIX": "/s",
    "STATUS_SUCCESS": "SUCCESS",
    "STATUS_ERROR": "ERROR",
    "STATUS_FAILED": "FAILED",
    "STATUS_RUNNING": "RUNNING",
    "STATUS_UNKNOWN": "UNKNOWN",
}

LANGUAGE_NUMBER_FORMATS = {
    "en": {"thousands_sep": ",", "decimal_sep": "."},
    "fr": {"thousands_sep": " ", "decimal_sep": ","},
    "de": {"thousands_sep": " ", "decimal_sep": ","},
    "es": {"thousands_sep": " ", "decimal_sep": ","},
    "it": {"thousands_sep": " ", "decimal_sep": ","},
    "pt": {"thousands_sep": " ", "decimal_sep": ","},
    "pl": {"thousands_sep": " ", "decimal_sep": ","},
    "ru": {"thousands_sep": " ", "decimal_sep": ","},
    "ja": {"thousands_sep": ",", "decimal_sep": "."},
    "ko": {"thousands_sep": ",", "decimal_sep": "."},
}

DEFAULT_NUMBER_FORMAT = LANGUAGE_NUMBER_FORMATS["en"]

# ============================================================
# I18N
# ============================================================


def load_json_file(file_path: Path) -> dict[str, Any]:
    """
    Charge un fichier JSON et retourne un dictionnaire.
    """
    if not file_path.exists():
        return {}

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return data if isinstance(data, dict) else {}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Fusionne récursivement deux dictionnaires.
    """
    result = dict(base)

    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def load_ui_strings(lang: str) -> dict[str, str]:
    """
    Charge les chaînes UI du script avec fallback anglais.
    """
    reference_file = I18N_DIR / f"{REFERENCE_LANG}.json"
    reference_data = load_json_file(reference_file)

    if lang == REFERENCE_LANG:
        merged = reference_data
    else:
        target_file = I18N_DIR / f"{lang}.json"
        target_data = load_json_file(target_file)
        merged = deep_merge(reference_data, target_data)

    namespace = merged.get(UI_NAMESPACE, {})
    if not isinstance(namespace, dict):
        namespace = {}

    resolved = dict(UI_DEFAULTS)

    for key, value in namespace.items():
        if isinstance(value, str):
            resolved[key] = value

    return resolved


def ui(ui_strings: dict[str, str], key: str, default: str) -> str:
    """
    Retourne une chaîne localisée avec fallback.
    """
    return ui_strings.get(key, default)


# ============================================================
# FORMATAGE
# ============================================================


def get_number_format() -> dict[str, str]:
    """
    Retourne la configuration de formatage numérique selon APP_LANG.
    """
    return LANGUAGE_NUMBER_FORMATS.get(APP_LANG, DEFAULT_NUMBER_FORMAT)


def format_number(value: int) -> str:
    """
    Formate un entier avec séparateur de milliers localisé.
    """
    fmt = get_number_format()
    thousands_sep = fmt["thousands_sep"]
    return f"{value:,}".replace(",", thousands_sep)


def format_decimal(value: float) -> str:
    """
    Formate un décimal avec séparateur décimal localisé.
    """
    fmt = get_number_format()
    decimal_sep = fmt["decimal_sep"]
    return f"{value:.1f}".replace(".", decimal_sep)


def translate_status(status: str, ui_strings: dict[str, str]) -> str:
    """
    Traduit les statuts techniques.
    """
    mapping = {
        "SUCCESS": ui(ui_strings, "STATUS_SUCCESS", "SUCCESS"),
        "ERROR": ui(ui_strings, "STATUS_ERROR", "ERROR"),
        "FAILED": ui(ui_strings, "STATUS_FAILED", "FAILED"),
        "RUNNING": ui(ui_strings, "STATUS_RUNNING", "RUNNING"),
    }
    return mapping.get(status.upper(), ui(ui_strings, "STATUS_UNKNOWN", "UNKNOWN"))


def compute_duration_seconds(start: str, end: str) -> int | None:
    """
    Calcule une durée en secondes à partir de deux timestamps ISO.
    """
    if not start or not end:
        return None

    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        return int((end_dt - start_dt).total_seconds())
    except Exception:
        return None


def format_duration(seconds: int | None) -> str:
    """
    Formate une durée au format HH:MM:SS.
    """
    if seconds is None or seconds < 0:
        return "-"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_rate(records: int, seconds: int | None, ui_strings: dict[str, str]) -> str:
    """
    Calcule et formate le débit moyen.
    """
    if seconds is None or seconds <= 0:
        return "-"

    rate = records / seconds
    return f"{format_decimal(rate)} {ui(ui_strings, 'RATE_SUFFIX', '/s')}"


# ============================================================
# ACCÈS SQLITE
# ============================================================


def fetch_rows(
    db_path: Path, ui_strings: dict[str, str]
) -> list[tuple[str, str, str, str | None, str, int]]:
    """
    Récupère la dernière synchronisation pour chaque couple
    endpoint + locale.
    """
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = ?
            """,
            (SYNC_LOG_TABLE,),
        )

        if cur.fetchone() is None:
            return []

        cur.execute(
            f"""
            WITH latest AS (
                SELECT
                    endpoint,
                    COALESCE(locale, ?) AS locale_norm,
                    MAX(start_time) AS max_start_time
                FROM {SYNC_LOG_TABLE}
                GROUP BY endpoint, COALESCE(locale, ?)
            )
            SELECT
                s.endpoint,
                COALESCE(s.locale, ?),
                s.start_time,
                s.end_time,
                COALESCE(s.status, ''),
                COALESCE(s.records_processed, 0)
            FROM {SYNC_LOG_TABLE} s
            INNER JOIN latest l
                ON s.endpoint = l.endpoint
               AND COALESCE(s.locale, ?) = l.locale_norm
               AND s.start_time = l.max_start_time
            ORDER BY s.start_time DESC
            """,
            (
                ui(ui_strings, "LOCALE_ALL", "all"),
                ui(ui_strings, "LOCALE_ALL", "all"),
                ui(ui_strings, "LOCALE_ALL", "all"),
                ui(ui_strings, "LOCALE_ALL", "all"),
            ),
        )

        rows = cur.fetchall()

    return rows


# ============================================================
# AFFICHAGE
# ============================================================


def print_table(
    rows: list[tuple[str, str, str, str | None, str, int]],
    ui_strings: dict[str, str],
) -> None:
    """
    Affiche un tableau aligné avec en-têtes localisés.
    """
    if not rows:
        print(ui(ui_strings, "NO_SYNC", "No synchronization recorded."))
        return

    display_rows: list[tuple[str, str, str, str, str, str]] = []

    for endpoint, locale, start, end, status, records in rows:
        endpoint_locale = f"{endpoint} [{locale}]"
        seconds = compute_duration_seconds(start, end)

        display_rows.append(
            (
                endpoint_locale,
                translate_status(status, ui_strings),
                start,
                format_duration(seconds),
                format_number(int(records)),
                format_rate(int(records), seconds, ui_strings),
            )
        )

    col_endpoint = ui(ui_strings, "COLUMN_ENDPOINT", "ENDPOINT")
    col_status = ui(ui_strings, "COLUMN_STATUS", "STATUS")
    col_start = ui(ui_strings, "COLUMN_START", "START")
    col_duration = ui(ui_strings, "COLUMN_DURATION", "DURATION")
    col_records = ui(ui_strings, "COLUMN_RECORDS", "RECORDS")
    col_rate = ui(ui_strings, "COLUMN_RATE", "RATE")

    endpoint_w = max(len(col_endpoint), max(len(r[0]) for r in display_rows))
    status_w = max(len(col_status), max(len(r[1]) for r in display_rows))
    start_w = max(len(col_start), max(len(r[2]) for r in display_rows))
    duration_w = max(len(col_duration), max(len(r[3]) for r in display_rows))
    records_w = max(len(col_records), max(len(r[4]) for r in display_rows))
    rate_w = max(len(col_rate), max(len(r[5]) for r in display_rows))

    print(
        f"{col_endpoint.ljust(endpoint_w)} | "
        f"{col_status.ljust(status_w)} | "
        f"{col_start.ljust(start_w)} | "
        f"{col_duration.ljust(duration_w)} | "
        f"{col_records.rjust(records_w)} | "
        f"{col_rate.rjust(rate_w)}"
    )

    print(
        f"{'-' * endpoint_w}-+-"
        f"{'-' * status_w}-+-"
        f"{'-' * start_w}-+-"
        f"{'-' * duration_w}-+-"
        f"{'-' * records_w}-+-"
        f"{'-' * rate_w}"
    )

    for row in display_rows:
        print(
            f"{row[0].ljust(endpoint_w)} | "
            f"{row[1].ljust(status_w)} | "
            f"{row[2].ljust(start_w)} | "
            f"{row[3].ljust(duration_w)} | "
            f"{row[4].rjust(records_w)} | "
            f"{row[5].rjust(rate_w)}"
        )


# ============================================================
# MAIN
# ============================================================


def main() -> None:
    """
    Point d'entrée principal.
    """
    ui_lang = APP_LANG if APP_LANG in SUPPORTED_APP_LANGS else REFERENCE_LANG
    ui_strings = load_ui_strings(ui_lang)

    if len(sys.argv) < 2:
        print(ui(ui_strings, "MISSING_PATH", "ERROR"))
        return

    db_path = Path(sys.argv[1])

    if not db_path.exists():
        print(ui(ui_strings, "MISSING_DB", "Missing database."))
        return

    rows = fetch_rows(db_path, ui_strings)
    print_table(rows, ui_strings)


if __name__ == "__main__":
    main()
