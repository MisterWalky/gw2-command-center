# ------------------------------------------------------------
# run_snapshot_sync.py
#
# Lance la synchronisation de tous les endpoints snapshot
# définis dans ENDPOINTS.
#
# Ignore automatiquement les endpoints "timeseries".
#
# Utilisation :
#   py scripts/run_snapshot_sync.py test
#   py scripts/run_snapshot_sync.py prod
# ------------------------------------------------------------

import sys
import subprocess
from pathlib import Path


# ------------------------------------------------------------
# AJOUT DE LA RACINE DU PROJET AU PYTHONPATH
# ------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_DIR))


# ------------------------------------------------------------
# CHARGEMENT DE L'ENVIRONNEMENT
# ------------------------------------------------------------

if len(sys.argv) > 1:
    target_env = sys.argv[1].strip().lower()
else:
    target_env = "test"

if target_env == "prod":
    from config.config_prod import ENDPOINTS
    loaded_env = "PROD"
else:
    from config.config_test import ENDPOINTS
    loaded_env = "TEST"


# ------------------------------------------------------------
# RÉCUPÉRATION DES ENDPOINTS SNAPSHOT
# ------------------------------------------------------------

snapshot_endpoints = [
    endpoint_name
    for endpoint_name, endpoint_config in ENDPOINTS.items()
    if endpoint_config.get("mode") == "snapshot"
]


# ------------------------------------------------------------
# FONCTION PRINCIPALE
# ------------------------------------------------------------

def main() -> None:
    if not snapshot_endpoints:
        print("Aucun endpoint snapshot trouvé dans ENDPOINTS.")
        return

    print("=====================================")
    print("Synchronisation GW2 API - SNAPSHOT")
    print("Environnement :", loaded_env)
    print("Endpoints :", ", ".join(snapshot_endpoints))
    print("=====================================")

    for endpoint_name in snapshot_endpoints:
        print()
        print(f"--- Synchronisation : {endpoint_name} ---")

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_DIR / "scripts" / "sync_endpoint.py"),
                target_env,
                endpoint_name,
            ],
            cwd=PROJECT_DIR,
            check=False,
        )

        if result.returncode != 0:
            print()
            print(f"Erreur : échec de synchronisation pour '{endpoint_name}'.")
            print("Arrêt du lanceur.")
            sys.exit(result.returncode)

    print()
    print("=====================================")
    print("Synchronisation snapshot terminée")
    print("=====================================")


# ------------------------------------------------------------
# LANCEMENT DU SCRIPT
# ------------------------------------------------------------

if __name__ == "__main__":
    main()