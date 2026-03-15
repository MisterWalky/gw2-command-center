# ------------------------------------------------------------
# api_status.py
#
# Affiche des informations simples sur la configuration API :
# - nombre d'endpoints snapshot
# - nombre d'endpoints timeseries
# - nombre total d'endpoints
# ------------------------------------------------------------

import sys
from pathlib import Path

# Ajout de la racine du projet au PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1]))

from config.config_base import ENDPOINTS


def main() -> None:
    """
    Compte les endpoints par mode.
    """
    snapshot_count = 0
    timeseries_count = 0

    for endpoint_cfg in ENDPOINTS.values():
        mode = endpoint_cfg.get("mode")

        if mode == "snapshot":
            snapshot_count += 1
        elif mode == "timeseries":
            timeseries_count += 1

    total_count = snapshot_count + timeseries_count

    print(f"OK|snapshot={snapshot_count}|timeseries={timeseries_count}|total={total_count}")


if __name__ == "__main__":
    main()
