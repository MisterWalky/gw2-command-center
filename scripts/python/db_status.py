# ------------------------------------------------------------
# db_status.py
#
# Affiche des informations synthétiques sur une base SQLite :
# - taille formatée
# - nombre de tables
# - nombre d'index
# - nombre de lignes dans Commerce_Prices_History
# - nombre de lignes dans API_RAW
# ------------------------------------------------------------

import sqlite3
import sys
from pathlib import Path


def format_number(n: int) -> str:
    """
    Formate un entier avec séparateur de milliers = espace.
    """
    return f"{n:,}".replace(",", " ")


def format_decimal_fr(value: float) -> str:
    """
    Formate un nombre décimal avec virgule française.
    Exemple :
    17.6 -> '17,6'
    """
    return f"{value:.1f}".replace(".", ",")


def format_size(size: int) -> str:
    """
    Formate la taille avec :
    - séparateur de milliers = espace
    - unité lisible avec 1 décimale
    """
    kb = size / 1024
    mb = kb / 1024
    gb = mb / 1024

    size_str = format_number(size)

    if gb >= 1:
        return f"{size_str} octets ({format_decimal_fr(gb)} Go)"
    if mb >= 1:
        return f"{size_str} octets ({format_decimal_fr(mb)} Mo)"
    if kb >= 1:
        return f"{size_str} octets ({format_decimal_fr(kb)} Ko)"

    return f"{size_str} octets"


def table_exists(cursor, table_name: str) -> bool:
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


def main():
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

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            """
        )
        table_count = cur.fetchone()[0]

        cur.execute(
            """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'index'
              AND name NOT LIKE 'sqlite_%'
            """
        )
        index_count = cur.fetchone()[0]

        prices_rows = 0
        raw_rows = 0

        if table_exists(cur, "Commerce_Prices_History"):
            cur.execute("SELECT COUNT(*) FROM Commerce_Prices_History")
            prices_rows = cur.fetchone()[0]

        if table_exists(cur, "API_RAW"):
            cur.execute("SELECT COUNT(*) FROM API_RAW")
            raw_rows = cur.fetchone()[0]

        conn.close()

        print(
            "OK"
            f"|size={size_fmt}"
            f"|tables={table_count}"
            f"|indexes={index_count}"
            f"|prices={format_number(prices_rows)}"
            f"|raw={format_number(raw_rows)}"
        )

    except Exception as exc:
        print(f"ERROR|{exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()