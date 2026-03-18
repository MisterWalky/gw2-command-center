# ============================================================
# Projet      : GW2 Command Center
# Fichier     : scripts/python/api_status.py
# Rôle        : Affichage synthétique de l'état des endpoints API
# Auteur      : William CROCHOT (MisterWalky)
# Référence   : https://github.com/MisterWalky/gw2-command-center
# Licence     : MIT
# ============================================================
#
# DESCRIPTION
# -----------
# Ce script affiche un résumé simple de la configuration des
# endpoints API déclarés dans le projet.
#
# Il permet notamment de connaître :
# - le nombre d'endpoints de type snapshot
# - le nombre d'endpoints de type timeseries
# - le nombre total d'endpoints reconnus
#
# FORMAT DE SORTIE
# ----------------
# La sortie est volontairement compacte afin de pouvoir être
# réutilisée facilement dans des scripts batch ou des outils
# de diagnostic.
#
# Exemple :
# OK|snapshot=1|timeseries=1|total=2
# ============================================================

import sys
from pathlib import Path

# ============================================================
# CHEMINS DU PROJET
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from config.config_base import ENDPOINTS  # noqa: E402


def main() -> None:
    """
    Compte les endpoints par mode et affiche un résumé compact.
    """
    snapshot_count = 0
    timeseries_count = 0
    other_count = 0

    for endpoint_cfg in ENDPOINTS.values():
        mode = endpoint_cfg.get("mode")

        if mode == "snapshot":
            snapshot_count += 1
        elif mode == "timeseries":
            timeseries_count += 1
        else:
            other_count += 1

    total_count = snapshot_count + timeseries_count + other_count

    print(
        f"OK|snapshot={snapshot_count}|timeseries={timeseries_count}|"
        f"other={other_count}|total={total_count}"
    )


if __name__ == "__main__":
    main()
