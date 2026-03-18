# ============================================================
# Projet      : GW2 Command Center
# Fichier     : scripts/python/endpoints_status.py
# Rôle        : Affichage des endpoints configurés et de leur état
# Auteur      : William CROCHOT (MisterWalky)
# Référence   : https://github.com/MisterWalky/gw2-command-center
# Licence     : MIT
# ============================================================
#
# DESCRIPTION
# -----------
# Ce script affiche les endpoints configurés dans le projet
# sous forme de tableaux lisibles en console.
#
# L'affichage est localisé via le système i18n du projet.
#
# Affichage :
# - un tableau pour les endpoints SNAPSHOT
# - un tableau pour les endpoints TIMESERIES
#
# Colonnes :
# - endpoint
# - portée
# - dernière mise à jour
#
# La dernière mise à jour provient de la table SYNC_LOG
# de la base SQLite passée en argument.
# ============================================================

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Any

# ============================================================
# CHEMINS DU PROJET
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]
I18N_DIR = PROJECT_DIR / "dashboard" / "i18n"

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from config.config_base import APP_LANG, ENDPOINTS, SUPPORTED_APP_LANGS, TABLES  # noqa: E402

# ============================================================
# CONSTANTES
# ============================================================

REFERENCE_LANG = "en"
SYNC_LOG_TABLE = TABLES["sync_log"]

# ============================================================
# UI - NAMESPACE
# ============================================================

UI_NAMESPACE = "ENDPOINTS_STATUS_UI"

UI_DEFAULTS = {
    "TITLE_SNAPSHOT": "SNAPSHOT",
    "TITLE_TIMESERIES": "TIMESERIES",
    "COLUMN_ENDPOINT": "ENDPOINT",
    "COLUMN_SCOPE": "SCOPE",
    "COLUMN_LAST_UPDATE": "LAST UPDATE",
    "NO_ENDPOINT": "(no endpoint)",
    "SCOPE_LOCALIZED": "localized",
    "SCOPE_GLOBAL": "global",
    "EMPTY": "EMPTY",
}

# ============================================================
# I18N
# ============================================================


def load_json_file(file_path: Path) -> dict[str, Any]:
    if not file_path.exists():
        return {}
    try:
        import json

        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_ui_strings(lang: str) -> dict[str, str]:
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


def ui(ui_strings: dict[str, str], key: str) -> str:
    return ui_strings.get(key, key)


# ============================================================
# DATA
# ============================================================


def fetch_last_updates(db_path: Path) -> dict[str, str]:
    last_updates: dict[str, str] = {}

    if not db_path.exists():
        return last_updates

    try:
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
                return last_updates

            cur.execute(
                f"""
                SELECT endpoint, MAX(start_time)
                FROM {SYNC_LOG_TABLE}
                GROUP BY endpoint
                """
            )

            for endpoint, last_start in cur.fetchall():
                last_updates[str(endpoint)] = str(last_start) if last_start else "-"

    except sqlite3.Error:
        return {}

    return last_updates


def build_rows(last_updates: dict[str, str], ui_strings: dict[str, str]):
    snapshot_rows = []
    timeseries_rows = []

    for endpoint_name, endpoint_cfg in ENDPOINTS.items():
        mode = endpoint_cfg.get("mode", "unknown")
        localized = endpoint_cfg.get("localized", False)

        scope = ui(ui_strings, "SCOPE_LOCALIZED") if localized else ui(ui_strings, "SCOPE_GLOBAL")

        last_update = last_updates.get(endpoint_name, "-")

        row = (endpoint_name, scope, last_update)

        if mode == "snapshot":
            snapshot_rows.append(row)
        elif mode == "timeseries":
            timeseries_rows.append(row)

    snapshot_rows.sort(key=lambda r: r[0])
    timeseries_rows.sort(key=lambda r: r[0])

    return snapshot_rows, timeseries_rows


# ============================================================
# AFFICHAGE
# ============================================================


def print_table(rows, ui_strings):
    if not rows:
        print(ui(ui_strings, "NO_ENDPOINT"))
        return

    col_endpoint = ui(ui_strings, "COLUMN_ENDPOINT")
    col_scope = ui(ui_strings, "COLUMN_SCOPE")
    col_update = ui(ui_strings, "COLUMN_LAST_UPDATE")

    endpoint_width = max(len(col_endpoint), max(len(r[0]) for r in rows))
    scope_width = max(len(col_scope), max(len(r[1]) for r in rows))
    update_width = max(len(col_update), max(len(r[2]) for r in rows))

    print(
        f"{col_endpoint.ljust(endpoint_width)} | "
        f"{col_scope.ljust(scope_width)} | "
        f"{col_update.ljust(update_width)}"
    )
    print(f"{'-'*endpoint_width}-+-" f"{'-'*scope_width}-+-" f"{'-'*update_width}")

    for endpoint, scope, last_update in rows:
        print(
            f"{endpoint.ljust(endpoint_width)} | "
            f"{scope.ljust(scope_width)} | "
            f"{last_update.ljust(update_width)}"
        )


# ============================================================
# MAIN
# ============================================================


def main() -> None:
    ui_lang = APP_LANG if APP_LANG in SUPPORTED_APP_LANGS else REFERENCE_LANG
    ui_strings = load_ui_strings(ui_lang)

    if not ENDPOINTS:
        print(ui(ui_strings, "EMPTY"))
        return

    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("")

    last_updates = fetch_last_updates(db_path)
    snapshot_rows, timeseries_rows = build_rows(last_updates, ui_strings)

    print(ui(ui_strings, "TITLE_SNAPSHOT"))
    print_table(snapshot_rows, ui_strings)
    print()

    print(ui(ui_strings, "TITLE_TIMESERIES"))
    print_table(timeseries_rows, ui_strings)


if __name__ == "__main__":
    main()
