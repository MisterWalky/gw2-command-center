# ============================================================
# Projet      : GW2 Command Center
# Fichier     : scripts/python/check_i18n.py
# Rôle        : Vérification et synchronisation des fichiers i18n
# Auteur      : William CROCHOT (MisterWalky)
# Référence   : https://github.com/MisterWalky/gw2-command-center
# Licence     : MIT
# ============================================================
#
# DESCRIPTION
# -----------
# Ce script compare les fichiers de langue du projet à partir
# du fichier anglais en.json, considéré comme référence.
#
# Il permet de :
# - vérifier la cohérence structurelle des fichiers i18n
# - détecter les clés manquantes
# - détecter les clés présentes en trop
# - détecter les différences de type
# - ajouter automatiquement les clés manquantes dans les autres
#   langues à partir de en.json
#
# CONVENTIONS
# -----------
# - en.json est la source de vérité structurelle
# - les autres langues doivent respecter exactement la même
#   arborescence
# - seules les valeurs doivent changer
# - les termes techniques restent en anglais
# - aucune traduction automatique n'est effectuée
#
# MODES
# -----
# check :
#   affiche un rapport sans modifier les fichiers
#
# sync :
#   ajoute dans les langues cibles les clés manquantes avec
#   la valeur anglaise de référence
# ============================================================

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
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

REFERENCE_LANG = "en"
REFERENCE_FILE = I18N_DIR / f"{REFERENCE_LANG}.json"

SUPPORTED_TARGET_LANGS = tuple(lang for lang in SUPPORTED_APP_LANGS if lang != REFERENCE_LANG)

# ============================================================
# LANGUE D'AFFICHAGE DU SCRIPT
# ============================================================
# Priorité :
# 1. argument --ui-lang
# 2. APP_LANG déjà validée par config_base.py
# 3. anglais par défaut
# ============================================================

DEFAULT_UI_LANG = APP_LANG or REFERENCE_LANG

# ============================================================
# CLÉS UI INTERNES DU SCRIPT
# ============================================================
# Ces clés sont lues depuis dashboard/i18n/<lang>.json,
# dans la section CHECK_I18N_UI.
#
# Un fallback interne reste présent pour éviter qu'un oubli
# de clé UI empêche le script de fonctionner.
# ============================================================

UI_NAMESPACE = "CHECK_I18N_UI"

UI_DEFAULTS = {
    "TITLE": "I18N consistency check",
    "REFERENCE_FILE": "Reference file",
    "TARGET_LANGS": "Target languages",
    "MODE": "Mode",
    "PROCESSING": "Processing",
    "LANGUAGE_FILE": "Language file",
    "MISSING_KEYS": "Missing keys",
    "EXTRA_KEYS": "Extra keys",
    "TYPE_MISMATCHES": "Type / structure mismatches",
    "NONE": "None",
    "UPDATED_FILE": "Updated file",
    "NO_CHANGE": "No change",
    "ADDED_KEYS": "Added keys",
    "SUMMARY": "Summary",
    "INVALID_UI_LANG": "Unsupported UI language requested, fallback to English",
    "NO_TARGET_LANGS": "No valid target languages to process",
    "PARSER_DESCRIPTION": "Check and synchronize project i18n files.",
    "HELP_MODE": "check = report only / sync = add missing keys from en.json",
    "HELP_LANGS": "Target languages to process. Default: all supported app languages except en",
    "HELP_UI_LANG": "Language used for this script output. Default: APP_LANG or en",
}

# ============================================================
# CHARGEMENT / SAUVEGARDE JSON
# ============================================================


def load_json_file(file_path: Path) -> dict[str, Any]:
    """
    Charge un fichier JSON et retourne son contenu.

    Si le fichier est absent, illisible ou invalide,
    une exception claire est levée.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Missing file: {file_path}")

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {file_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise TypeError(f"Root JSON object expected in: {file_path}")

    return data


def save_json_file(file_path: Path, data: dict[str, Any]) -> None:
    """
    Sauvegarde un dictionnaire au format JSON lisible.
    """
    file_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


# ============================================================
# OUTILS D'ARBORESCENCE
# ============================================================


def flatten_dict(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """
    Transforme un dictionnaire imbriqué en dictionnaire plat
    avec chemins séparés par des points.
    """
    flat: dict[str, Any] = {}

    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            flat.update(flatten_dict(value, path))
        else:
            flat[path] = value

    return flat


def collect_types(data: dict[str, Any], prefix: str = "") -> dict[str, str]:
    """
    Collecte le type de chaque chemin de l'arborescence.
    """
    collected: dict[str, str] = {}

    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            collected[path] = "dict"
            collected.update(collect_types(value, path))
        elif isinstance(value, list):
            collected[path] = "list"
        elif isinstance(value, str):
            collected[path] = "str"
        elif isinstance(value, bool):
            collected[path] = "bool"
        elif value is None:
            collected[path] = "none"
        else:
            collected[path] = type(value).__name__

    return collected


def get_value_by_path(data: dict[str, Any], path: str) -> Any:
    """
    Lit une valeur dans un dictionnaire imbriqué à partir
    d'un chemin pointé.
    """
    current: Any = data

    for part in path.split("."):
        current = current[part]

    return current


def set_value_by_path(data: dict[str, Any], path: str, value: Any) -> None:
    """
    Écrit une valeur dans un dictionnaire imbriqué à partir
    d'un chemin pointé.
    """
    parts = path.split(".")
    current = data

    for part in parts[:-1]:
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]

    current[parts[-1]] = value


def deep_merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Fusionne deux dictionnaires imbriqués.

    Les valeurs de override remplacent celles de base.
    """
    merged = deepcopy(base)

    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge_dicts(merged[key], value)
        else:
            merged[key] = deepcopy(value)

    return merged


# ============================================================
# CHARGEMENT DES CHAINES UI VIA LE SYSTEME I18N DU PROJET
# ============================================================


def load_project_i18n(lang: str) -> dict[str, Any]:
    """
    Charge les chaînes i18n du projet en appliquant la stratégie :
    1. charger en.json
    2. charger la langue demandée si différente
    3. fusionner
    """
    reference_data = load_json_file(REFERENCE_FILE)

    if lang == REFERENCE_LANG:
        return reference_data

    target_file = I18N_DIR / f"{lang}.json"
    if not target_file.exists():
        return reference_data

    target_data = load_json_file(target_file)
    return deep_merge_dicts(reference_data, target_data)


def load_ui_strings(ui_lang: str) -> dict[str, str]:
    """
    Charge les chaînes UI du script depuis le namespace
    CHECK_I18N_UI du système i18n du projet.

    Fallback :
    - en.json fusionné
    - UI_DEFAULTS pour toute clé absente
    """
    project_i18n = load_project_i18n(ui_lang)
    namespace_data = project_i18n.get(UI_NAMESPACE, {})

    if not isinstance(namespace_data, dict):
        namespace_data = {}

    resolved = dict(UI_DEFAULTS)

    for key, value in namespace_data.items():
        if isinstance(value, str):
            resolved[key] = value

    return resolved


# ============================================================
# OUTILS D'AFFICHAGE
# ============================================================


def ui(ui_strings: dict[str, str], key: str, default: str) -> str:
    """
    Retourne une chaîne localisée pour l'interface interne
    du script.
    """
    return ui_strings.get(key, default)


def print_section(title: str) -> None:
    """
    Affiche un titre de section lisible en console.
    """
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


def print_items(title: str, items: list[str], none_label: str) -> None:
    """
    Affiche une liste d'éléments ou un message indiquant
    qu'aucun problème n'a été détecté.
    """
    print(f"\n- {title}")

    if not items:
        print(f"  {none_label}")
        return

    for item in items:
        print(f"  • {item}")


# ============================================================
# COMPARAISON
# ============================================================


def compare_language(
    reference_data: dict[str, Any],
    target_data: dict[str, Any],
) -> dict[str, list[str]]:
    """
    Compare une langue cible à la langue de référence.

    Retourne :
    - missing_keys
    - extra_keys
    - type_mismatches
    """
    ref_flat = flatten_dict(reference_data)
    tgt_flat = flatten_dict(target_data)

    ref_types = collect_types(reference_data)
    tgt_types = collect_types(target_data)

    missing_keys = sorted(set(ref_flat) - set(tgt_flat))
    extra_keys = sorted(set(tgt_flat) - set(ref_flat))

    type_mismatches: list[str] = []

    common_paths = sorted(set(ref_types) & set(tgt_types))
    for path in common_paths:
        if ref_types[path] != tgt_types[path]:
            type_mismatches.append(
                f"{path} -> expected: {ref_types[path]}, found: {tgt_types[path]}"
            )

    return {
        "missing_keys": missing_keys,
        "extra_keys": extra_keys,
        "type_mismatches": type_mismatches,
    }


# ============================================================
# SYNCHRONISATION DES CLÉS MANQUANTES
# ============================================================


def sync_missing_keys(
    reference_data: dict[str, Any],
    target_data: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    """
    Ajoute les clés manquantes à la langue cible à partir
    du fichier de référence anglais.

    Retourne :
    - le dictionnaire mis à jour
    - la liste des clés ajoutées
    """
    updated = deepcopy(target_data)
    report = compare_language(reference_data, target_data)

    added_keys: list[str] = []

    for path in report["missing_keys"]:
        ref_value = deepcopy(get_value_by_path(reference_data, path))
        set_value_by_path(updated, path, ref_value)
        added_keys.append(path)

    return updated, added_keys


# ============================================================
# TRAITEMENT D'UNE LANGUE
# ============================================================


def process_language(
    ui_strings: dict[str, str],
    target_lang: str,
    reference_data: dict[str, Any],
    mode: str,
) -> None:
    """
    Vérifie et, si demandé, synchronise une langue cible.
    """
    target_file = I18N_DIR / f"{target_lang}.json"
    target_data = load_json_file(target_file)

    report_before = compare_language(reference_data, target_data)

    print_section(f"{ui(ui_strings, 'LANGUAGE_FILE', 'Language file')} : {target_file.name}")
    print_items(
        ui(ui_strings, "MISSING_KEYS", "Missing keys"),
        report_before["missing_keys"],
        ui(ui_strings, "NONE", "None"),
    )
    print_items(
        ui(ui_strings, "EXTRA_KEYS", "Extra keys"),
        report_before["extra_keys"],
        ui(ui_strings, "NONE", "None"),
    )
    print_items(
        ui(ui_strings, "TYPE_MISMATCHES", "Type / structure mismatches"),
        report_before["type_mismatches"],
        ui(ui_strings, "NONE", "None"),
    )

    if mode == "check":
        return

    updated_data, added_keys = sync_missing_keys(reference_data, target_data)

    if added_keys:
        save_json_file(target_file, updated_data)
        print(f"\n{ui(ui_strings, 'UPDATED_FILE', 'Updated file')} : {target_file.name}")
        print_items(
            ui(ui_strings, "ADDED_KEYS", "Added keys"),
            added_keys,
            ui(ui_strings, "NONE", "None"),
        )
    else:
        print(f"\n{ui(ui_strings, 'NO_CHANGE', 'No change')} : {target_file.name}")


# ============================================================
# PRE-PARSING UI LANG
# ============================================================


def resolve_requested_ui_lang(argv: list[str]) -> str:
    """
    Effectue un pré-parsing minimal pour récupérer --ui-lang
    avant de construire le parser principal.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--ui-lang", default=DEFAULT_UI_LANG)
    args, _ = parser.parse_known_args(argv)

    requested = (args.ui_lang or DEFAULT_UI_LANG).strip().lower()

    if requested in SUPPORTED_APP_LANGS:
        return requested

    return REFERENCE_LANG


# ============================================================
# ARGUMENTS CLI
# ============================================================


def build_parser(ui_strings: dict[str, str]) -> argparse.ArgumentParser:
    """
    Construit le parser argparse avec des chaînes localisées.
    """
    parser = argparse.ArgumentParser(
        description=ui(
            ui_strings,
            "PARSER_DESCRIPTION",
            "Check and synchronize project i18n files.",
        )
    )

    parser.add_argument(
        "--mode",
        choices=("check", "sync"),
        default="check",
        help=ui(
            ui_strings,
            "HELP_MODE",
            "check = report only / sync = add missing keys from en.json",
        ),
    )

    parser.add_argument(
        "--langs",
        nargs="*",
        default=list(SUPPORTED_TARGET_LANGS),
        help=ui(
            ui_strings,
            "HELP_LANGS",
            "Target languages to process. Default: all supported app languages except en",
        ),
    )

    parser.add_argument(
        "--ui-lang",
        default=DEFAULT_UI_LANG,
        help=ui(
            ui_strings,
            "HELP_UI_LANG",
            "Language used for this script output. Default: APP_LANG or en",
        ),
    )

    return parser


def parse_args(ui_strings: dict[str, str]) -> argparse.Namespace:
    """
    Analyse les arguments du script avec un parser localisé.
    """
    parser = build_parser(ui_strings)
    return parser.parse_args()


# ============================================================
# POINT D'ENTRÉE
# ============================================================


def main() -> None:
    """
    Point d'entrée principal.
    """
    preselected_ui_lang = resolve_requested_ui_lang(sys.argv[1:])
    ui_strings = load_ui_strings(preselected_ui_lang)

    args = parse_args(ui_strings)

    requested_ui_lang = (args.ui_lang or "").strip().lower()
    ui_lang = requested_ui_lang if requested_ui_lang in SUPPORTED_APP_LANGS else REFERENCE_LANG
    ui_strings = load_ui_strings(ui_lang)

    if requested_ui_lang != ui_lang:
        print(
            ui(
                ui_strings,
                "INVALID_UI_LANG",
                "Unsupported UI language requested, fallback to English",
            )
            + f" : {requested_ui_lang}"
        )

    target_langs = [lang for lang in args.langs if lang in SUPPORTED_TARGET_LANGS]

    if not target_langs:
        print(ui(ui_strings, "NO_TARGET_LANGS", "No valid target languages to process"))
        return

    reference_data = load_json_file(REFERENCE_FILE)

    print_section(ui(ui_strings, "TITLE", "I18N consistency check"))
    print(f"{ui(ui_strings, 'REFERENCE_FILE', 'Reference file')} : {REFERENCE_FILE.name}")
    print(f"{ui(ui_strings, 'TARGET_LANGS', 'Target languages')} : {', '.join(target_langs)}")
    print(f"{ui(ui_strings, 'MODE', 'Mode')} : {args.mode}")

    for target_lang in target_langs:
        print(f"\n{ui(ui_strings, 'PROCESSING', 'Processing')} : {target_lang}")
        process_language(
            ui_strings=ui_strings,
            target_lang=target_lang,
            reference_data=reference_data,
            mode=args.mode,
        )

    print_section(ui(ui_strings, "SUMMARY", "Summary"))


if __name__ == "__main__":
    main()
