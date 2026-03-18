# ============================================================
# Projet      : GW2 Command Center
# Fichier     : scripts/python/run_snapshot_sync.py
# Rôle        : Lancement de la synchronisation des endpoints snapshot
# Auteur      : William CROCHOT (MisterWalky)
# Référence   : https://github.com/MisterWalky/gw2-command-center
# Licence     : MIT
# ============================================================
#
# DESCRIPTION
# -----------
# Ce script lance la synchronisation de tous les endpoints
# snapshot définis dans ENDPOINTS.
#
# Les endpoints de type timeseries sont ignorés.
#
# ENVIRONNEMENTS
# --------------
# Le script peut cibler :
# - la base TEST
# - la base PROD
#
# Utilisation :
#   py scripts/python/run_snapshot_sync.py test
#   py scripts/python/run_snapshot_sync.py prod
# ============================================================

from __future__ import annotations

import json
import subprocess
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

from config.config_base import APP_LANG, SUPPORTED_APP_LANGS  # noqa: E402

# ============================================================
# CONSTANTES
# ============================================================

REFERENCE_LANG = "en"
ALLOWED_ENVS = {"test", "prod"}

UI_NAMESPACE = "RUN_SNAPSHOT_SYNC_UI"

UI_DEFAULTS = {
    "INVALID_ENV": "Invalid environment requested, fallback to TEST",
    "NO_SNAPSHOT_ENDPOINT": "No snapshot endpoint found in ENDPOINTS",
    "TITLE": "GW2 API synchronization - SNAPSHOT",
    "ENVIRONMENT": "Environment",
    "ENDPOINTS": "Endpoints",
    "SYNC_START": "Synchronization",
    "SYNC_FAILED": "Synchronization failed",
    "LAUNCHER_STOPPED": "Launcher stopped",
    "SYNC_COMPLETED": "Snapshot synchronization completed",
}

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
# CHARGEMENT DE LA CONFIGURATION
# ============================================================


def resolve_target_env(argv: list[str]) -> str:
    """
    Détermine l'environnement cible à partir des arguments.
    """
    if argv:
        requested = argv[0].strip().lower()
    else:
        requested = "test"

    if requested in ALLOWED_ENVS:
        return requested

    return "test"


def load_runtime_config(target_env: str) -> dict[str, Any]:
    """
    Charge la configuration adaptée à l'environnement demandé.
    """
    if target_env == "prod":
        from config.config_prod import ENDPOINTS

        return {
            "ENDPOINTS": ENDPOINTS,
            "LOADED_ENV": "PROD",
        }

    from config.config_test import ENDPOINTS

    return {
        "ENDPOINTS": ENDPOINTS,
        "LOADED_ENV": "TEST",
    }


# ============================================================
# OUTILS
# ============================================================


def get_snapshot_endpoints(endpoints: dict[str, Any]) -> list[str]:
    """
    Retourne la liste triée des endpoints de type snapshot.
    """
    snapshot_endpoints = [
        endpoint_name
        for endpoint_name, endpoint_config in endpoints.items()
        if endpoint_config.get("mode") == "snapshot"
    ]

    snapshot_endpoints.sort()
    return snapshot_endpoints


# ============================================================
# FONCTION PRINCIPALE
# ============================================================


def main() -> None:
    ui_lang = APP_LANG if APP_LANG in SUPPORTED_APP_LANGS else REFERENCE_LANG
    ui_strings = load_ui_strings(ui_lang)

    requested_env = sys.argv[1].strip().lower() if len(sys.argv) > 1 else "test"
    target_env = resolve_target_env(sys.argv[1:])

    if requested_env != target_env:
        print(
            f"{ui(ui_strings, 'INVALID_ENV', 'Invalid environment requested, fallback to TEST')} : "
            f"{requested_env}"
        )

    runtime_config = load_runtime_config(target_env)
    endpoints: dict[str, Any] = runtime_config["ENDPOINTS"]
    loaded_env: str = runtime_config["LOADED_ENV"]

    snapshot_endpoints = get_snapshot_endpoints(endpoints)

    if not snapshot_endpoints:
        print(
            ui(
                ui_strings,
                "NO_SNAPSHOT_ENDPOINT",
                "No snapshot endpoint found in ENDPOINTS",
            )
        )
        return

    print("=====================================")
    print(ui(ui_strings, "TITLE", "GW2 API synchronization - SNAPSHOT"))
    print(f"{ui(ui_strings, 'ENVIRONMENT', 'Environment')} : {loaded_env}")
    print(f"{ui(ui_strings, 'ENDPOINTS', 'Endpoints')} : {', '.join(snapshot_endpoints)}")
    print("=====================================")

    sync_script = PROJECT_DIR / "scripts" / "python" / "sync_endpoint.py"

    for endpoint_name in snapshot_endpoints:
        print()
        print(f"--- {ui(ui_strings, 'SYNC_START', 'Synchronization')} : " f"{endpoint_name} ---")

        result = subprocess.run(
            [
                sys.executable,
                str(sync_script),
                target_env,
                endpoint_name,
            ],
            cwd=PROJECT_DIR,
            check=False,
        )

        if result.returncode != 0:
            print()
            print(
                f"{ui(ui_strings, 'SYNC_FAILED', 'Synchronization failed')} : " f"{endpoint_name}"
            )
            print(ui(ui_strings, "LAUNCHER_STOPPED", "Launcher stopped"))
            sys.exit(result.returncode)

    print()
    print("=====================================")
    print(ui(ui_strings, "SYNC_COMPLETED", "Snapshot synchronization completed"))
    print("=====================================")


if __name__ == "__main__":
    main()
