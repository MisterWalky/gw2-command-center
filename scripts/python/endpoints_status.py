# ------------------------------------------------------------
# endpoints_status.py
#
# Affiche les endpoints configurés dans config_base.py
# sous forme de tableaux lisibles en console.
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
# La dernière mise à jour provient de la table Sync_Log
# de la base SQLite passée en argument.
# ------------------------------------------------------------

import sqlite3
import sys
from pathlib import Path

# Ajout de la racine du projet au PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1]))

from config.config_base import ENDPOINTS


def fetch_last_updates(db_path: Path) -> dict[str, str]:
    """
    Récupère, pour chaque endpoint, la date de dernière synchronisation
    à partir de Sync_Log.

    Retour :
    {
        "items": "2026-03-10 18:42:12",
        "commerce_prices": "2026-03-10 18:45:03",
        ...
    }
    """
    last_updates: dict[str, str] = {}

    if not db_path.exists():
        return last_updates

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'Sync_Log'
            """
        )
        if cur.fetchone() is None:
            conn.close()
            return last_updates

        cur.execute(
            """
            SELECT endpoint, MAX(start_time) AS last_start
            FROM Sync_Log
            GROUP BY endpoint
            ORDER BY endpoint
            """
        )

        for endpoint, last_start in cur.fetchall():
            last_updates[str(endpoint)] = last_start or "-"

        conn.close()

    except Exception:
        return {}

    return last_updates


def build_rows(last_updates: dict[str, str]):
    """
    Construit deux listes :
    - snapshot_rows
    - timeseries_rows

    Chaque ligne contient :
    (endpoint_name, portee, derniere_maj)
    """
    snapshot_rows = []
    timeseries_rows = []

    for endpoint_name, endpoint_cfg in ENDPOINTS.items():
        mode = endpoint_cfg.get("mode", "unknown")
        localized = endpoint_cfg.get("localized", False)
        portee = "localise" if localized else "global"
        derniere_maj = last_updates.get(endpoint_name, "-")

        row = (endpoint_name, portee, derniere_maj)

        if mode == "snapshot":
            snapshot_rows.append(row)
        elif mode == "timeseries":
            timeseries_rows.append(row)

    return snapshot_rows, timeseries_rows


def print_table(rows: list[tuple[str, str, str]]) -> None:
    """
    Affiche un tableau compact et aligné.

    Colonnes :
    - ENDPOINT
    - PORTEE
    - DERNIERE MISE A JOUR
    """
    if not rows:
        print("(aucun endpoint)")
        return

    endpoint_width = max(len("ENDPOINT"), max(len(row[0]) for row in rows))
    portee_width = max(len("PORTEE"), max(len(row[1]) for row in rows))
    maj_width = max(len("DERNIERE MISE A JOUR"), max(len(row[2]) for row in rows))

    print(
        f"{'ENDPOINT'.ljust(endpoint_width)} | "
        f"{'PORTEE'.ljust(portee_width)} | "
        f"{'DERNIERE MISE A JOUR'.ljust(maj_width)}"
    )
    print(
        f"{'-' * endpoint_width}-+-"
        f"{'-' * portee_width}-+-"
        f"{'-' * maj_width}"
    )

    for endpoint_name, portee, derniere_maj in rows:
        print(
            f"{endpoint_name.ljust(endpoint_width)} | "
            f"{portee.ljust(portee_width)} | "
            f"{derniere_maj.ljust(maj_width)}"
        )


def main() -> None:
    """
    Point d'entrée principal.
    """
    if not ENDPOINTS:
        print("EMPTY")
        return

    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("")

    last_updates = fetch_last_updates(db_path)
    snapshot_rows, timeseries_rows = build_rows(last_updates)

    print("SNAPSHOT")
    print_table(snapshot_rows)
    print()

    print("TIMESERIES")
    print_table(timeseries_rows)


if __name__ == "__main__":
    main()