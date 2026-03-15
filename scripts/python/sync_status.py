# ------------------------------------------------------------
# sync_status.py
#
# Affiche les dernières synchronisations enregistrées
# dans la table Sync_Log avec :
#
# - endpoint
# - statut
# - début
# - durée
# - enregistrements
# - débit
#
# Les intitulés de colonnes sont en français.
# ------------------------------------------------------------

import sqlite3
import sys
from pathlib import Path
from datetime import datetime


def format_number(n: int) -> str:
    """Séparateur de milliers avec espace."""
    return f"{n:,}".replace(",", " ")


def format_decimal_fr(value: float) -> str:
    """Décimal français avec virgule."""
    return f"{value:.1f}".replace(".", ",")


def translate_status(status: str) -> str:
    """Traduction des statuts techniques."""
    mapping = {
        "SUCCESS": "SUCCES",
        "ERROR": "ERREUR",
        "FAILED": "ECHEC",
        "RUNNING": "EN COURS",
    }
    return mapping.get(status.upper(), status)


def compute_duration_seconds(start: str, end: str):
    """Calcule la durée en secondes."""
    if not start or not end:
        return None

    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        return int((end_dt - start_dt).total_seconds())
    except Exception:
        return None


def format_duration(seconds):
    """Formate HH:MM:SS."""
    if seconds is None or seconds < 0:
        return "-"

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    return f"{h:02}:{m:02}:{s:02}"


def format_rate(records, seconds):
    """Calcule le débit."""
    if seconds is None or seconds <= 0:
        return "-"

    rate = records / seconds
    return f"{format_decimal_fr(rate)} /s"


def fetch_rows(db_path: Path):
    """
    Récupère la dernière synchronisation pour chaque couple
    endpoint + locale.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name='Sync_Log'
        """
    )

    if cur.fetchone() is None:
        conn.close()
        return []

    cur.execute(
        """
        WITH latest AS (
            SELECT
                endpoint,
                COALESCE(locale,'all') AS locale_norm,
                MAX(start_time) AS max_start_time
            FROM Sync_Log
            GROUP BY endpoint, COALESCE(locale,'all')
        )
        SELECT
            s.endpoint,
            COALESCE(s.locale,'all'),
            s.start_time,
            s.end_time,
            COALESCE(s.status,''),
            COALESCE(s.records_processed,0)
        FROM Sync_Log s
        INNER JOIN latest l
            ON s.endpoint=l.endpoint
           AND COALESCE(s.locale,'all')=l.locale_norm
           AND s.start_time=l.max_start_time
        ORDER BY s.start_time DESC
        """
    )

    rows = cur.fetchall()
    conn.close()

    return rows


def print_table(rows):
    """
    Affiche un tableau aligné avec en-têtes en français.
    """
    if not rows:
        print("Aucune synchronisation enregistree.")
        return

    display_rows = []

    for endpoint, locale, start, end, status, records in rows:
        endpoint_locale = f"{endpoint} [{locale}]"
        seconds = compute_duration_seconds(start, end)

        display_rows.append(
            (
                endpoint_locale,
                translate_status(status),
                start,
                format_duration(seconds),
                format_number(records),
                format_rate(records, seconds),
            )
        )

    endpoint_w = max(len("ENDPOINT"), max(len(r[0]) for r in display_rows))
    statut_w = max(len("STATUT"), max(len(r[1]) for r in display_rows))
    debut_w = max(len("DEBUT"), max(len(r[2]) for r in display_rows))
    duree_w = max(len("DUREE"), max(len(r[3]) for r in display_rows))
    enreg_w = max(len("ENREGISTREMENTS"), max(len(r[4]) for r in display_rows))
    debit_w = max(len("DEBIT"), max(len(r[5]) for r in display_rows))

    print(
        f"{'ENDPOINT'.ljust(endpoint_w)} | "
        f"{'STATUT'.ljust(statut_w)} | "
        f"{'DEBUT'.ljust(debut_w)} | "
        f"{'DUREE'.ljust(duree_w)} | "
        f"{'ENREGISTREMENTS'.rjust(enreg_w)} | "
        f"{'DEBIT'.rjust(debit_w)}"
    )

    print(
        f"{'-'*endpoint_w}-+-"
        f"{'-'*statut_w}-+-"
        f"{'-'*debut_w}-+-"
        f"{'-'*duree_w}-+-"
        f"{'-'*enreg_w}-+-"
        f"{'-'*debit_w}"
    )

    for r in display_rows:
        print(
            f"{r[0].ljust(endpoint_w)} | "
            f"{r[1].ljust(statut_w)} | "
            f"{r[2].ljust(debut_w)} | "
            f"{r[3].ljust(duree_w)} | "
            f"{r[4].rjust(enreg_w)} | "
            f"{r[5].rjust(debit_w)}"
        )


def main():
    """
    Point d'entrée principal.
    """
    if len(sys.argv) < 2:
        print("ERREUR")
        return

    db_path = Path(sys.argv[1])

    if not db_path.exists():
        print("Base absente.")
        return

    rows = fetch_rows(db_path)
    print_table(rows)


if __name__ == "__main__":
    main()