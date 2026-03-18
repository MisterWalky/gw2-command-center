# ============================================================
# Projet      : GW2 Command Center
# Fichier     : scripts/python/run_sync_menu.py
# Rôle        : Menu interactif de synchronisation du projet
# Auteur      : William CROCHOT (MisterWalky)
# Référence   : https://github.com/MisterWalky/gw2-command-center
# Licence     : MIT
# ============================================================
#
# DESCRIPTION
# -----------
# Ce script propose un menu interactif de synchronisation pour
# le projet GW2 Command Center.
#
# Fonctions :
# - choix de l'environnement : TEST / PROD
# - choix du mode de synchronisation
# - sélection d'un ou plusieurs endpoints
# - confirmation finale
# - affichage des durées par endpoint et de la durée totale
#
# RÈGLES
# ------
# - Q permet de quitter à chaque étape
# - les endpoints SNAPSHOT et TIMESERIES sont numérotés
#   séparément
# - la confirmation finale résume l'action avant exécution
# ============================================================

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# ============================================================
# CHEMINS DU PROJET
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]
I18N_DIR = PROJECT_DIR / "dashboard" / "i18n"

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from config.config_base import APP_LANG, ENDPOINTS, SUPPORTED_APP_LANGS  # noqa: E402

# ============================================================
# CONSTANTES
# ============================================================

REFERENCE_LANG = "en"
SYNC_ENDPOINT_SCRIPT = PROJECT_DIR / "scripts" / "python" / "sync_endpoint.py"

UI_NAMESPACE = "RUN_SYNC_MENU_UI"

UI_DEFAULTS = {
    "PROGRAM_STOPPED": "Program stopped.",
    "INVALID_CHOICE": "Invalid choice.",
    "EXPECTED_VALUES": "Expected values",
    "OR_Q_TO_QUIT": "or Q to quit",
    "EMPTY_INPUT": "Input cannot be empty. You can also type Q to quit.",
    "INVALID_YN": "Invalid answer. Type Y, N or Q.",
    "NO_ENDPOINT": "No endpoint",
    "AVAILABLE_SNAPSHOT": "Available SNAPSHOT endpoints",
    "AVAILABLE_TIMESERIES": "Available TIMESERIES endpoints",
    "AVAILABLE_ENDPOINTS": "Available endpoints",
    "YOU_CAN_ENTER": "You can enter:",
    "DISPLAYED_NUMBER": "the displayed number",
    "EXACT_NAME": "the exact endpoint name",
    "QUIT_HINT": "Q to quit",
    "CHOOSE_ENVIRONMENT": "Choose environment",
    "TEST": "TEST",
    "PROD": "PROD",
    "YOUR_CHOICE": "Your choice: ",
    "CHOOSE_ACTION": "Choose action",
    "ACTION_ALL_SNAPSHOT": "Synchronize all SNAPSHOT endpoints",
    "ACTION_ALL_TIMESERIES": "Synchronize all TIMESERIES endpoints",
    "ACTION_ALL_BOTH": "Synchronize all SNAPSHOT + TIMESERIES endpoints",
    "ACTION_ONE_SNAPSHOT": "Synchronize one SNAPSHOT endpoint",
    "ACTION_ONE_TIMESERIES": "Synchronize one TIMESERIES endpoint",
    "ENDPOINT_TO_RUN": "Endpoint to run: ",
    "INVALID_ENDPOINT": "Invalid endpoint. Enter a valid number, a valid name, or Q.",
    "NO_ENDPOINT_IN_SECTION": "No endpoint available in this section",
    "SYNC_START": "Synchronization",
    "SUMMARY_BEFORE_RUN": "Summary before launch",
    "ENVIRONMENT": "Environment",
    "ENDPOINTS": "Endpoints",
    "CONFIRM_SUMMARY": "Confirm this summary? (Y/N): ",
    "NO_ENDPOINT_DEFINED": "No endpoint defined in ENDPOINTS.",
    "NO_ENDPOINT_TO_SYNC": "No endpoint to synchronize.",
    "SUMMARY_REJECTED": "Summary rejected. Back to the start of the script.",
    "SYNC_LAUNCH": "Starting synchronization",
    "DURATION": "Duration",
    "SYNC_FAILED": "Synchronization failed",
    "DURATION_SUMMARY": "Duration summary",
    "TOTAL_TIME": "Total time",
    "SYNC_COMPLETED": "Synchronization completed",
    "SECTION_SNAPSHOT": "SNAPSHOT",
    "SECTION_TIMESERIES": "TIMESERIES",
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
# OUTILS DE SAISIE
# ============================================================


def ask_choice(prompt: str, valid_choices: set[str], ui_strings: dict[str, str]) -> str:
    """
    Demande un choix parmi une liste de valeurs valides.
    """
    while True:
        value = input(prompt).strip().upper()

        if value == "Q":
            print()
            print(ui(ui_strings, "PROGRAM_STOPPED", "Program stopped."))
            sys.exit(0)

        if value in valid_choices:
            return value

        print(
            f"{ui(ui_strings, 'INVALID_CHOICE', 'Invalid choice.')} "
            f"{ui(ui_strings, 'EXPECTED_VALUES', 'Expected values')} : "
            f"{', '.join(sorted(valid_choices))} "
            f"{ui(ui_strings, 'OR_Q_TO_QUIT', 'or Q to quit')}."
        )


def ask_value(prompt: str, ui_strings: dict[str, str]) -> str:
    """
    Demande une saisie texte non vide.
    """
    while True:
        value = input(prompt).strip()

        if value.upper() == "Q":
            print()
            print(ui(ui_strings, "PROGRAM_STOPPED", "Program stopped."))
            sys.exit(0)

        if value:
            return value

        print(
            ui(
                ui_strings,
                "EMPTY_INPUT",
                "Input cannot be empty. You can also type Q to quit.",
            )
        )


def ask_yes_no(prompt: str, ui_strings: dict[str, str]) -> bool:
    """
    Demande une confirmation Y/N.
    """
    while True:
        value = input(prompt).strip().upper()

        if value == "Q":
            print()
            print(ui(ui_strings, "PROGRAM_STOPPED", "Program stopped."))
            sys.exit(0)

        if value == "Y":
            return True

        if value == "N":
            return False

        print(ui(ui_strings, "INVALID_YN", "Invalid answer. Type Y, N or Q."))


# ============================================================
# OUTILS TEMPS
# ============================================================


def format_duration(seconds: float) -> str:
    """
    Formate une durée en mm:ss ou hh:mm:ss.
    """
    total_seconds = int(round(seconds))

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    return f"{minutes:02d}:{secs:02d}"


# ============================================================
# CONSTRUCTION DES LISTES D'ENDPOINTS
# ============================================================


def get_endpoints_by_mode() -> tuple[list[str], list[str]]:
    """
    Retourne les endpoints snapshot et timeseries.
    """
    snapshot_names: list[str] = []
    timeseries_names: list[str] = []

    for endpoint_name, endpoint_cfg in ENDPOINTS.items():
        mode = endpoint_cfg.get("mode")

        if mode == "snapshot":
            snapshot_names.append(endpoint_name)
        elif mode == "timeseries":
            timeseries_names.append(endpoint_name)

    return snapshot_names, timeseries_names


def build_numbered_endpoints(
    snapshot_names: list[str],
    timeseries_names: list[str],
) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    """
    Construit les listes numérotées pour les deux sections.
    """
    snapshot_numbered = [
        (index, endpoint_name) for index, endpoint_name in enumerate(snapshot_names, start=1)
    ]

    timeseries_numbered = [
        (100 + index, endpoint_name)
        for index, endpoint_name in enumerate(timeseries_names, start=1)
    ]

    return snapshot_numbered, timeseries_numbered


# ============================================================
# AFFICHAGE
# ============================================================


def display_section(
    title: str,
    numbered_endpoints: list[tuple[int, str]],
    ui_strings: dict[str, str],
) -> None:
    """
    Affiche une section d'endpoints numérotés.
    """
    print()
    print(f"[{title}]")

    if not numbered_endpoints:
        print(ui(ui_strings, "NO_ENDPOINT", "No endpoint"))
        return

    for menu_id, endpoint_name in numbered_endpoints:
        print(f"{menu_id} - {endpoint_name}")


def display_snapshot_only(
    snapshot_numbered: list[tuple[int, str]],
    ui_strings: dict[str, str],
) -> None:
    """
    Affiche uniquement la section SNAPSHOT.
    """
    print()
    print("=====================================")
    print(ui(ui_strings, "AVAILABLE_SNAPSHOT", "Available SNAPSHOT endpoints"))
    print("=====================================")
    display_section(
        ui(ui_strings, "SECTION_SNAPSHOT", "SNAPSHOT"),
        snapshot_numbered,
        ui_strings,
    )
    print()
    print(ui(ui_strings, "YOU_CAN_ENTER", "You can enter:"))
    print(f"- {ui(ui_strings, 'DISPLAYED_NUMBER', 'the displayed number')}")
    print(f"- {ui(ui_strings, 'EXACT_NAME', 'the exact endpoint name')}")
    print(f"- {ui(ui_strings, 'QUIT_HINT', 'Q to quit')}")


def display_timeseries_only(
    timeseries_numbered: list[tuple[int, str]],
    ui_strings: dict[str, str],
) -> None:
    """
    Affiche uniquement la section TIMESERIES.
    """
    print()
    print("=====================================")
    print(ui(ui_strings, "AVAILABLE_TIMESERIES", "Available TIMESERIES endpoints"))
    print("=====================================")
    display_section(
        ui(ui_strings, "SECTION_TIMESERIES", "TIMESERIES"),
        timeseries_numbered,
        ui_strings,
    )
    print()
    print(ui(ui_strings, "YOU_CAN_ENTER", "You can enter:"))
    print(f"- {ui(ui_strings, 'DISPLAYED_NUMBER', 'the displayed number')}")
    print(f"- {ui(ui_strings, 'EXACT_NAME', 'the exact endpoint name')}")
    print(f"- {ui(ui_strings, 'QUIT_HINT', 'Q to quit')}")


def display_both_sections(
    snapshot_numbered: list[tuple[int, str]],
    timeseries_numbered: list[tuple[int, str]],
    ui_strings: dict[str, str],
) -> None:
    """
    Affiche les sections SNAPSHOT et TIMESERIES.
    """
    print()
    print("=====================================")
    print(ui(ui_strings, "AVAILABLE_ENDPOINTS", "Available endpoints"))
    print("=====================================")
    display_section(
        ui(ui_strings, "SECTION_SNAPSHOT", "SNAPSHOT"),
        snapshot_numbered,
        ui_strings,
    )
    display_section(
        ui(ui_strings, "SECTION_TIMESERIES", "TIMESERIES"),
        timeseries_numbered,
        ui_strings,
    )


# ============================================================
# RÉSOLUTION D'UN ENDPOINT
# ============================================================


def resolve_endpoint(user_value: str, numbered_endpoints: list[tuple[int, str]]) -> str | None:
    """
    Résout un endpoint à partir de son numéro ou de son nom exact.
    """
    by_id = {str(menu_id): endpoint_name for menu_id, endpoint_name in numbered_endpoints}
    by_name = {endpoint_name: endpoint_name for _menu_id, endpoint_name in numbered_endpoints}

    if user_value in by_id:
        return by_id[user_value]

    if user_value in by_name:
        return by_name[user_value]

    return None


# ============================================================
# CHOIX MENUS
# ============================================================


def choose_environment(ui_strings: dict[str, str]) -> str:
    """
    Demande le choix de l'environnement.
    """
    print("=====================================")
    print(ui(ui_strings, "CHOOSE_ENVIRONMENT", "Choose environment"))
    print(f"1 - {ui(ui_strings, 'TEST', 'TEST')}")
    print(f"2 - {ui(ui_strings, 'PROD', 'PROD')}")
    print("Q - Quitter")
    print("=====================================")

    choice = ask_choice(
        ui(ui_strings, "YOUR_CHOICE", "Your choice: "),
        {"1", "2"},
        ui_strings,
    )
    return "test" if choice == "1" else "prod"


def choose_action(ui_strings: dict[str, str]) -> str:
    """
    Demande le choix de l'action à exécuter.
    """
    print()
    print("=====================================")
    print(ui(ui_strings, "CHOOSE_ACTION", "Choose action"))
    print(f"1 - {ui(ui_strings, 'ACTION_ALL_SNAPSHOT', 'Synchronize all SNAPSHOT endpoints')}")
    print(f"2 - {ui(ui_strings, 'ACTION_ALL_TIMESERIES', 'Synchronize all TIMESERIES endpoints')}")
    print(
        f"3 - {ui(ui_strings, 'ACTION_ALL_BOTH', 'Synchronize all SNAPSHOT + TIMESERIES endpoints')}"
    )
    print(f"4 - {ui(ui_strings, 'ACTION_ONE_SNAPSHOT', 'Synchronize one SNAPSHOT endpoint')}")
    print(f"5 - {ui(ui_strings, 'ACTION_ONE_TIMESERIES', 'Synchronize one TIMESERIES endpoint')}")
    print("Q - Quitter")
    print("=====================================")

    return ask_choice(
        ui(ui_strings, "YOUR_CHOICE", "Your choice: "),
        {"1", "2", "3", "4", "5"},
        ui_strings,
    )


def choose_single_endpoint(
    section_name: str,
    numbered_endpoints: list[tuple[int, str]],
    ui_strings: dict[str, str],
) -> str:
    """
    Demande la sélection d'un seul endpoint.
    """
    if not numbered_endpoints:
        raise ValueError(
            f"{ui(ui_strings, 'NO_ENDPOINT_IN_SECTION', 'No endpoint available in this section')} : "
            f"{section_name}"
        )

    while True:
        user_value = ask_value(
            ui(ui_strings, "ENDPOINT_TO_RUN", "Endpoint to run: "),
            ui_strings,
        )
        resolved = resolve_endpoint(user_value, numbered_endpoints)

        if resolved is not None:
            return resolved

        print(
            ui(
                ui_strings,
                "INVALID_ENDPOINT",
                "Invalid endpoint. Enter a valid number, a valid name, or Q.",
            )
        )


# ============================================================
# LANCEMENT DES SYNCHRONISATIONS
# ============================================================


def run_sync_for_endpoint(
    env: str, endpoint_name: str, ui_strings: dict[str, str]
) -> tuple[int, float]:
    """
    Lance la synchronisation d'un endpoint et retourne
    le code retour + la durée.
    """
    print()
    print(
        f"{ui(ui_strings, 'SYNC_START', 'Synchronization')} : " f"{endpoint_name} [{env.upper()}]"
    )

    start_time = time.perf_counter()

    result = subprocess.run(
        [
            sys.executable,
            str(SYNC_ENDPOINT_SCRIPT),
            env,
            endpoint_name,
        ],
        cwd=PROJECT_DIR,
        check=False,
    )

    duration = time.perf_counter() - start_time
    return result.returncode, duration


# ============================================================
# CONSTRUCTION DE LA LISTE À LANCER
# ============================================================


def build_endpoints_to_run(
    action: str,
    snapshot_names: list[str],
    timeseries_names: list[str],
    snapshot_numbered: list[tuple[int, str]],
    timeseries_numbered: list[tuple[int, str]],
    ui_strings: dict[str, str],
) -> list[str]:
    """
    Construit la liste des endpoints à exécuter selon l'action.
    """
    if action == "1":
        return snapshot_names

    if action == "2":
        return timeseries_names

    if action == "3":
        display_both_sections(snapshot_numbered, timeseries_numbered, ui_strings)
        return snapshot_names + timeseries_names

    if action == "4":
        display_snapshot_only(snapshot_numbered, ui_strings)
        selected = choose_single_endpoint(
            ui(ui_strings, "SECTION_SNAPSHOT", "SNAPSHOT"),
            snapshot_numbered,
            ui_strings,
        )
        return [selected]

    if action == "5":
        display_timeseries_only(timeseries_numbered, ui_strings)
        selected = choose_single_endpoint(
            ui(ui_strings, "SECTION_TIMESERIES", "TIMESERIES"),
            timeseries_numbered,
            ui_strings,
        )
        return [selected]

    raise ValueError(f"Unknown action: {action}")


def confirm_summary(env: str, endpoints_to_run: list[str], ui_strings: dict[str, str]) -> bool:
    """
    Affiche le résumé avant lancement et demande confirmation.
    """
    print()
    print("=====================================")
    print(ui(ui_strings, "SUMMARY_BEFORE_RUN", "Summary before launch"))
    print("=====================================")
    print(f"{ui(ui_strings, 'ENVIRONMENT', 'Environment')} : {env.upper()}")
    print(f"{ui(ui_strings, 'ENDPOINTS', 'Endpoints')} : {', '.join(endpoints_to_run)}")
    print()

    return ask_yes_no(
        ui(ui_strings, "CONFIRM_SUMMARY", "Confirm this summary? (Y/N): "),
        ui_strings,
    )


# ============================================================
# MAIN
# ============================================================


def main() -> None:
    """
    Point d'entrée principal.
    """
    ui_lang = APP_LANG if APP_LANG in SUPPORTED_APP_LANGS else REFERENCE_LANG
    ui_strings = load_ui_strings(ui_lang)

    snapshot_names, timeseries_names = get_endpoints_by_mode()

    if not snapshot_names and not timeseries_names:
        print(ui(ui_strings, "NO_ENDPOINT_DEFINED", "No endpoint defined in ENDPOINTS."))
        sys.exit(1)

    snapshot_numbered, timeseries_numbered = build_numbered_endpoints(
        snapshot_names,
        timeseries_names,
    )

    while True:
        env = choose_environment(ui_strings)
        action = choose_action(ui_strings)

        endpoints_to_run = build_endpoints_to_run(
            action=action,
            snapshot_names=snapshot_names,
            timeseries_names=timeseries_names,
            snapshot_numbered=snapshot_numbered,
            timeseries_numbered=timeseries_numbered,
            ui_strings=ui_strings,
        )

        if not endpoints_to_run:
            print(ui(ui_strings, "NO_ENDPOINT_TO_SYNC", "No endpoint to synchronize."))
            continue

        if not confirm_summary(env, endpoints_to_run, ui_strings):
            print()
            print(
                ui(
                    ui_strings,
                    "SUMMARY_REJECTED",
                    "Summary rejected. Back to the start of the script.",
                )
            )
            print()
            continue

        print()
        print("=====================================")
        print(ui(ui_strings, "SYNC_LAUNCH", "Starting synchronization"))
        print(f"{ui(ui_strings, 'ENVIRONMENT', 'Environment')} : {env.upper()}")
        print(f"{ui(ui_strings, 'ENDPOINTS', 'Endpoints')} : {', '.join(endpoints_to_run)}")
        print("=====================================")

        global_start = time.perf_counter()
        endpoint_results: list[tuple[str, float]] = []

        for endpoint_name in endpoints_to_run:
            return_code, duration = run_sync_for_endpoint(env, endpoint_name, ui_strings)
            endpoint_results.append((endpoint_name, duration))

            print(
                f"{ui(ui_strings, 'DURATION', 'Duration')} [{endpoint_name}] : "
                f"{format_duration(duration)}"
            )

            if return_code != 0:
                print()
                print(
                    f"{ui(ui_strings, 'SYNC_FAILED', 'Synchronization failed')} : "
                    f"{endpoint_name}"
                )
                sys.exit(return_code)

        global_duration = time.perf_counter() - global_start

        print()
        print("=====================================")
        print(ui(ui_strings, "DURATION_SUMMARY", "Duration summary"))
        print("=====================================")

        for endpoint_name, duration in endpoint_results:
            print(f"- {endpoint_name} : {format_duration(duration)}")

        print(f"{ui(ui_strings, 'TOTAL_TIME', 'Total time')} : {format_duration(global_duration)}")

        print()
        print("=====================================")
        print(ui(ui_strings, "SYNC_COMPLETED", "Synchronization completed"))
        print("=====================================")
        return


if __name__ == "__main__":
    main()
