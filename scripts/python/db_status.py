# ============================================================
# Projet      : GW2 Command Center
# Fichier     : scripts/python/db_status.py
# Rôle        : Affichage synthétique de l'état d'une base SQLite
# Auteur      : William CROCHOT (MisterWalky)
# Référence   : https://github.com/MisterWalky/gw2-command-center
# Licence     : MIT
# ============================================================
#
# DESCRIPTION
# -----------
# Ce script affiche des informations synthétiques sur une base
# SQLite du projet.
#
# Il permet notamment de récupérer :
# - la taille formatée du fichier
# - le nombre de tables
# - le nombre de colonnes
# - le nombre d'index
# - le nombre de lignes dans COMMERCE_PRICES_HISTORY
# - le nombre de lignes dans API_RAW
#
# FORMAT DE SORTIE
# ----------------
# La sortie est volontairement compacte afin de pouvoir être
# réutilisée facilement dans des scripts batch ou des outils
# de diagnostic.
#
# Exemple :
# OK|size=12 345 octets (12,1 Mo)|tables=5|indexes=8|prices=1 250|raw=18 400
# ============================================================

import sqlite3
import sys
from pathlib import Path

# ============================================================
# CHEMINS DU PROJET
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from config.config_base import APP_LANG  # noqa: E402

# ============================================================
# CONSTANTES
# ============================================================

COMMERCE_PRICES_TABLE = "COMMERCE_PRICES_HISTORY"
API_RAW_TABLE = "API_RAW"

LANGUAGE_NUMBER_FORMATS = {
    "en": {
        "thousands_sep": ",",
        "decimal_sep": ".",
        "units": {"bytes": "bytes", "kb": "KB", "mb": "MB", "gb": "GB"},
    },
    "fr": {
        "thousands_sep": " ",
        "decimal_sep": ",",
        "units": {"bytes": "octets", "kb": "Ko", "mb": "Mo", "gb": "Go"},
    },
    "de": {
        "thousands_sep": " ",
        "decimal_sep": ",",
        "units": {"bytes": "Bytes", "kb": "KB", "mb": "MB", "gb": "GB"},
    },
    "es": {
        "thousands_sep": " ",
        "decimal_sep": ",",
        "units": {"bytes": "bytes", "kb": "KB", "mb": "MB", "gb": "GB"},
    },
    "it": {
        "thousands_sep": " ",
        "decimal_sep": ",",
        "units": {"bytes": "byte", "kb": "KB", "mb": "MB", "gb": "GB"},
    },
    "pt": {
        "thousands_sep": " ",
        "decimal_sep": ",",
        "units": {"bytes": "bytes", "kb": "KB", "mb": "MB", "gb": "GB"},
    },
    "pl": {
        "thousands_sep": " ",
        "decimal_sep": ",",
        "units": {"bytes": "bajtów", "kb": "KB", "mb": "MB", "gb": "GB"},
    },
    "ru": {
        "thousands_sep": " ",
        "decimal_sep": ",",
        "units": {"bytes": "байт", "kb": "КБ", "mb": "МБ", "gb": "ГБ"},
    },
    "ja": {
        "thousands_sep": ",",
        "decimal_sep": ".",
        "units": {"bytes": "bytes", "kb": "KB", "mb": "MB", "gb": "GB"},
    },
    "ko": {
        "thousands_sep": ",",
        "decimal_sep": ".",
        "units": {"bytes": "bytes", "kb": "KB", "mb": "MB", "gb": "GB"},
    },
}

DEFAULT_NUMBER_FORMAT = LANGUAGE_NUMBER_FORMATS["en"]


def get_number_format() -> dict[str, object]:
    """
    Retourne la configuration de formatage correspondant
    à la langue applicative.
    """
    return LANGUAGE_NUMBER_FORMATS.get(APP_LANG, DEFAULT_NUMBER_FORMAT)


def format_number(value: int) -> str:
    """
    Formate un entier avec le séparateur de milliers adapté
    à la langue de l'application.
    """
    fmt = get_number_format()
    thousands_sep = str(fmt["thousands_sep"])
    return f"{value:,}".replace(",", thousands_sep)


def format_decimal(value: float) -> str:
    """
    Formate un nombre décimal avec le séparateur décimal adapté
    à la langue de l'application.
    """
    fmt = get_number_format()
    decimal_sep = str(fmt["decimal_sep"])
    return f"{value:.1f}".replace(".", decimal_sep)


def format_size(size: int) -> str:
    """
    Formate la taille d'un fichier avec :
    - séparateur de milliers localisé
    - séparateur décimal localisé
    - unités adaptées à la langue de l'application
    """
    fmt = get_number_format()
    units = fmt["units"]
    assert isinstance(units, dict)

    kb = size / 1024
    mb = kb / 1024
    gb = mb / 1024

    size_str = format_number(size)
    bytes_unit = str(units["bytes"])
    kb_unit = str(units["kb"])
    mb_unit = str(units["mb"])
    gb_unit = str(units["gb"])

    if gb >= 1:
        return f"{size_str} {bytes_unit} ({format_decimal(gb)} {gb_unit})"
    if mb >= 1:
        return f"{size_str} {bytes_unit} ({format_decimal(mb)} {mb_unit})"
    if kb >= 1:
        return f"{size_str} {bytes_unit} ({format_decimal(kb)} {kb_unit})"

    return f"{size_str} {bytes_unit}"


def table_exists(cursor: sqlite3.Cursor, table_name: str) -> bool:
    """
    Vérifie si une table existe dans sqlite_master.
    """
    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = ?
        """,
        (table_name,),
    )
    return cursor.fetchone() is not None


def count_rows_if_exists(cursor: sqlite3.Cursor, table_name: str) -> int:
    """
    Retourne le nombre de lignes d'une table si elle existe,
    sinon 0.
    """
    if not table_exists(cursor, table_name):
        return 0

    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    result = cursor.fetchone()
    return int(result[0]) if result is not None else 0


def main() -> None:
    """
    Point d'entrée principal.
    """
    if len(sys.argv) < 2:
        print("ERROR|missing_path")
        sys.exit(1)

    db_path = Path(sys.argv[1])

    if not db_path.exists():
        print("ERROR|missing_file")
        sys.exit(0)

    try:
        size = db_path.stat().st_size
        size_fmt = format_size(size)

        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()

            cur.execute(
                """
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                """
            )
            table_count = int(cur.fetchone()[0])

            cur.execute(
                """
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE type = 'index'
                  AND name NOT LIKE 'sqlite_%'
                """
            )
            index_count = int(cur.fetchone()[0])

            prices_rows = count_rows_if_exists(cur, COMMERCE_PRICES_TABLE)
            raw_rows = count_rows_if_exists(cur, API_RAW_TABLE)

        print(
            "OK"
            f"|size={size_fmt}"
            f"|tables={table_count}"
            f"|indexes={index_count}"
            f"|prices={format_number(prices_rows)}"
            f"|raw={format_number(raw_rows)}"
        )

    except sqlite3.Error as exc:
        print(f"ERROR|sqlite_error={exc}")
        sys.exit(1)
    except OSError as exc:
        print(f"ERROR|os_error={exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR|unexpected_error={exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
