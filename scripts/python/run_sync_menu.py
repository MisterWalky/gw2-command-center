# ------------------------------------------------------------
# run_sync_menu.py
#
# Menu interactif de synchronisation du projet GW2 API.
#
# Fonctions :
# - choix environnement : TEST / PROD
# - choix d'action :
#     1 = tous les SNAPSHOT
#     2 = tous les TIMESERIES
#     3 = tous les SNAPSHOT + TIMESERIES
#     4 = un seul SNAPSHOT
#     5 = un seul TIMESERIES
#
# Sélection d'un endpoint :
# - par numéro auto
# - ou par nom exact
#
# Numérotation automatique :
# - SNAPSHOT   : 1, 2, 3, ...
# - TIMESERIES : 101, 102, 103, ...
#
# L'ordre suit l'ordre d'apparition dans ENDPOINTS.
#
# Confirmation :
# - une seule validation finale sur le résumé
# - si N, retour au tout début du script
#
# Quitter :
# - Q à chaque étape
#
# Affichage :
# - durée par endpoint
# - durée totale
# ------------------------------------------------------------

import sys
import time
import subprocess
from pathlib import Path


# ------------------------------------------------------------
# AJOUT DE LA RACINE DU PROJET AU PYTHONPATH
# ------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_DIR))


# ------------------------------------------------------------
# IMPORT CONFIG
# ------------------------------------------------------------

from config.config_base import ENDPOINTS


# ------------------------------------------------------------
# OUTILS DE SAISIE
# ------------------------------------------------------------

def ask_choice(prompt: str, valid_choices: set[str]) -> str:
    while True:
        value = input(prompt).strip().upper()

        if value == "Q":
            print()
            print("Arrêt du programme.")
            sys.exit(0)

        if value in valid_choices:
            return value

        print(
            f"Choix invalide. Valeurs attendues : "
            f"{', '.join(sorted(valid_choices))} ou Q pour quitter."
        )


def ask_value(prompt: str) -> str:
    while True:
        value = input(prompt).strip()

        if value.upper() == "Q":
            print()
            print("Arrêt du programme.")
            sys.exit(0)

        if value:
            return value

        print("La saisie ne peut pas être vide. Tapez aussi Q pour quitter.")


def ask_yes_no(prompt: str) -> bool:
    while True:
        value = input(prompt).strip().upper()

        if value == "Q":
            print()
            print("Arrêt du programme.")
            sys.exit(0)

        if value == "Y":
            return True

        if value == "N":
            return False

        print("Réponse invalide. Tapez Y, N ou Q.")


# ------------------------------------------------------------
# OUTILS TEMPS
# ------------------------------------------------------------

def format_duration(seconds: float) -> str:
    total_seconds = int(round(seconds))

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    return f"{minutes:02d}:{secs:02d}"


# ------------------------------------------------------------
# CONSTRUCTION DES LISTES D'ENDPOINTS
# ------------------------------------------------------------

def get_endpoints_by_mode():
    snapshot_names = []
    timeseries_names = []

    for endpoint_name, endpoint_cfg in ENDPOINTS.items():
        mode = endpoint_cfg.get("mode")

        if mode == "snapshot":
            snapshot_names.append(endpoint_name)
        elif mode == "timeseries":
            timeseries_names.append(endpoint_name)

    return snapshot_names, timeseries_names


def build_numbered_endpoints(snapshot_names, timeseries_names):
    snapshot_numbered = [
        (index, endpoint_name)
        for index, endpoint_name in enumerate(snapshot_names, start=1)
    ]

    timeseries_numbered = [
        (100 + index, endpoint_name)
        for index, endpoint_name in enumerate(timeseries_names, start=1)
    ]

    return snapshot_numbered, timeseries_numbered


# ------------------------------------------------------------
# AFFICHAGE
# ------------------------------------------------------------

def display_section(title: str, numbered_endpoints: list[tuple[int, str]]) -> None:
    print()
    print(f"[{title}]")

    if not numbered_endpoints:
        print("Aucun endpoint")
        return

    for menu_id, endpoint_name in numbered_endpoints:
        print(f"{menu_id} - {endpoint_name}")


def display_snapshot_only(snapshot_numbered):
    print()
    print("=====================================")
    print("Endpoints SNAPSHOT disponibles")
    print("=====================================")
    display_section("SNAPSHOT", snapshot_numbered)
    print()
    print("Vous pouvez saisir :")
    print("- le numéro affiché")
    print("- le nom exact de l'endpoint")
    print("- Q pour quitter")


def display_timeseries_only(timeseries_numbered):
    print()
    print("=====================================")
    print("Endpoints TIMESERIES disponibles")
    print("=====================================")
    display_section("TIMESERIES", timeseries_numbered)
    print()
    print("Vous pouvez saisir :")
    print("- le numéro affiché")
    print("- le nom exact de l'endpoint")
    print("- Q pour quitter")


def display_both_sections(snapshot_numbered, timeseries_numbered):
    print()
    print("=====================================")
    print("Endpoints disponibles")
    print("=====================================")
    display_section("SNAPSHOT", snapshot_numbered)
    display_section("TIMESERIES", timeseries_numbered)


# ------------------------------------------------------------
# RÉSOLUTION D'UN ENDPOINT
# ------------------------------------------------------------

def resolve_endpoint(user_value: str, numbered_endpoints: list[tuple[int, str]]) -> str | None:
    by_id = {str(menu_id): endpoint_name for menu_id, endpoint_name in numbered_endpoints}
    by_name = {endpoint_name: endpoint_name for _menu_id, endpoint_name in numbered_endpoints}

    if user_value in by_id:
        return by_id[user_value]

    if user_value in by_name:
        return by_name[user_value]

    return None


# ------------------------------------------------------------
# CHOIX MENUS
# ------------------------------------------------------------

def choose_environment() -> str:
    print("=====================================")
    print("Choix de l'environnement")
    print("1 - TEST")
    print("2 - PROD")
    print("Q - Quitter")
    print("=====================================")

    choice = ask_choice("Votre choix : ", {"1", "2"})
    return "test" if choice == "1" else "prod"


def choose_action() -> str:
    print()
    print("=====================================")
    print("Choix de l'action")
    print("1 - Synchroniser tous les endpoints SNAPSHOT")
    print("2 - Synchroniser tous les endpoints TIMESERIES")
    print("3 - Synchroniser tous les endpoints SNAPSHOT + TIMESERIES")
    print("4 - Synchroniser un seul endpoint SNAPSHOT")
    print("5 - Synchroniser un seul endpoint TIMESERIES")
    print("Q - Quitter")
    print("=====================================")

    return ask_choice("Votre choix : ", {"1", "2", "3", "4", "5"})


def choose_single_endpoint(section_name: str, numbered_endpoints: list[tuple[int, str]]) -> str:
    if not numbered_endpoints:
        raise ValueError(f"Aucun endpoint disponible dans la section {section_name}.")

    while True:
        user_value = ask_value("Endpoint à lancer : ")
        resolved = resolve_endpoint(user_value, numbered_endpoints)

        if resolved is not None:
            return resolved

        print("Endpoint invalide. Saisissez un numéro, un nom valide, ou Q.")


# ------------------------------------------------------------
# LANCEMENT DES SYNCHRONISATIONS
# ------------------------------------------------------------

def run_sync_for_endpoint(env: str, endpoint_name: str) -> tuple[int, float]:
    print()
    print(f"Synchronisation : {endpoint_name} [{env.upper()}]")

    start_time = time.perf_counter()

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_DIR / "scripts" / "sync_endpoint.py"),
            env,
            endpoint_name,
        ],
        cwd=PROJECT_DIR,
        check=False,
    )

    duration = time.perf_counter() - start_time
    return result.returncode, duration


# ------------------------------------------------------------
# CONSTRUCTION DE LA LISTE À LANCER
# ------------------------------------------------------------

def build_endpoints_to_run(
    action,
    snapshot_names,
    timeseries_names,
    snapshot_numbered,
    timeseries_numbered,
):
    if action == "1":
        return snapshot_names

    if action == "2":
        return timeseries_names

    if action == "3":
        display_both_sections(snapshot_numbered, timeseries_numbered)
        return snapshot_names + timeseries_names

    if action == "4":
        display_snapshot_only(snapshot_numbered)
        selected = choose_single_endpoint("SNAPSHOT", snapshot_numbered)
        return [selected]

    if action == "5":
        display_timeseries_only(timeseries_numbered)
        selected = choose_single_endpoint("TIMESERIES", timeseries_numbered)
        return [selected]

    raise ValueError(f"Action inconnue : {action}")


def confirm_summary(env: str, endpoints_to_run: list[str]) -> bool:
    print()
    print("=====================================")
    print("Résumé avant lancement")
    print("=====================================")
    print("Environnement :", env.upper())
    print("Endpoints :", ", ".join(endpoints_to_run))
    print()
    return ask_yes_no("Valider ce résumé ? (Y/N) : ")


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():
    snapshot_names, timeseries_names = get_endpoints_by_mode()

    if not snapshot_names and not timeseries_names:
        print("Aucun endpoint défini dans ENDPOINTS.")
        sys.exit(1)

    snapshot_numbered, timeseries_numbered = build_numbered_endpoints(
        snapshot_names,
        timeseries_names,
    )

    while True:
        env = choose_environment()
        action = choose_action()

        endpoints_to_run = build_endpoints_to_run(
            action=action,
            snapshot_names=snapshot_names,
            timeseries_names=timeseries_names,
            snapshot_numbered=snapshot_numbered,
            timeseries_numbered=timeseries_numbered,
        )

        if not endpoints_to_run:
            print("Aucun endpoint à synchroniser.")
            continue

        if not confirm_summary(env, endpoints_to_run):
            print()
            print("Résumé refusé. Retour au début du script.")
            print()
            continue

        print()
        print("=====================================")
        print("Lancement de la synchronisation")
        print("Environnement :", env.upper())
        print("Endpoints :", ", ".join(endpoints_to_run))
        print("=====================================")

        global_start = time.perf_counter()
        endpoint_results = []

        for endpoint_name in endpoints_to_run:
            return_code, duration = run_sync_for_endpoint(env, endpoint_name)
            endpoint_results.append((endpoint_name, duration))

            print(f"Durée [{endpoint_name}] : {format_duration(duration)}")

            if return_code != 0:
                print()
                print(f"Erreur : échec de synchronisation pour '{endpoint_name}'.")
                sys.exit(return_code)

        global_duration = time.perf_counter() - global_start

        print()
        print("=====================================")
        print("Résumé des durées")
        print("=====================================")

        for endpoint_name, duration in endpoint_results:
            print(f"- {endpoint_name} : {format_duration(duration)}")

        print(f"Temps total : {format_duration(global_duration)}")

        print()
        print("=====================================")
        print("Synchronisation terminée")
        print("=====================================")
        return


if __name__ == "__main__":
    main()