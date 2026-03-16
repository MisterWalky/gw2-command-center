# ============================================================
# Projet      : GW2 Command Center
# Fichier     : config/config_base.py
# Rôle        : Configuration commune du projet
# Auteur      : William CROCHOT (MisterWalky)
# Référence   : https://github.com/MisterWalky/gw2-command-center
# Licence     : MIT
# ============================================================
#
# DESCRIPTION
# -----------
# Ce fichier centralise la configuration commune du projet.
#
# Il contient notamment :
# - l'identité du projet
# - le chargement du fichier .env
# - la lecture de la version depuis le fichier VERSION
# - la configuration API GW2
# - la gestion des langues API
# - la gestion de la langue applicative
# - les chemins du projet
# - les paramètres HTTP communs
# - les constantes partagées entre environnements
# - la création automatique des dossiers runtime
# - la création automatique des fichiers SQLite s'ils n'existent pas
# - la gestion i18n de base de l'application
# - la détection d'une installation incomplète si les fichiers
#   de langue sont absents
#
# CONVENTIONS RETENUES
# --------------------
# - Les commentaires du code restent en français pendant le
#   développement local.
# - Les messages utilisateur normaux doivent être localisés
#   via les fichiers JSON de langue.
# - Les messages critiques de secours peuvent rester codés en
#   dur afin d'expliquer un problème grave, par exemple
#   l'absence du fichier anglais de référence.
# - Les fichiers config_prod.py et config_test.py importent ce
#   fichier puis ne modifient que ce qui varie selon
#   l'environnement.
# - La variable GW2_API_LANGS du fichier .env peut contenir une
#   ou plusieurs langues séparées par des virgules.
# - La variable APP_LANG définit la langue de l'interface
#   applicative et des messages de diagnostic.
# - Dans le code Python, la variable API_LANGS représente la
#   liste normalisée et validée des langues API actives.
#
# STRATÉGIE DE GESTION DES LANGUES API
# ------------------------------------
# 1. Lire GW2_API_LANGS depuis .env
# 2. Nettoyer les espaces et passer en minuscules
# 3. Supprimer les doublons en conservant l'ordre
# 4. Ignorer les langues non supportées
# 5. Si rien n'est exploitable, utiliser "en" par défaut
#
# STRATÉGIE I18N DE L'APPLICATION
# -------------------------------
# 1. Lire APP_LANG depuis .env
# 2. Vérifier que la langue demandée fait partie des langues
#    officiellement supportées par le projet
# 3. Si la langue demandée n'est pas supportée, basculer sur "en"
# 4. Charger en.json comme socle de référence
# 5. Si la langue demandée est "en", utiliser ce socle
# 6. Sinon charger le fichier JSON de la langue demandée
# 7. Fusionner la langue demandée au-dessus du socle anglais
# 8. Si le fichier de la langue demandée est absent, revenir à
#    l'anglais
# 9. Si en.json est absent, considérer que le projet est
#    incomplet et afficher un avertissement critique
#
# EXEMPLES DE CONFIGURATION
# -------------------------
#   APP_LANG=fr
#   GW2_API_LANGS=en
#   GW2_API_LANGS=fr
#   GW2_API_LANGS=fr,en
#   GW2_API_LANGS=fr,en,de
#
# DÉPENDANCES
# -----------
# - python-dotenv
# - json (bibliothèque standard)
#
# REMARQUE
# --------
# La structure des endpoints localisés est pensée pour gérer
# correctement une, deux, trois langues ou plus selon le choix
# de l'utilisateur.
#
# Le principe retenu est :
# - une table principale pour les données non localisées
# - une table i18n dédiée pour les données dépendantes de la
#   langue
#
# Exemple :
# - ITEMS
# - ITEMS_I18N
#
# La liste des langues actives est pilotée par GW2_API_LANGS
# dans la configuration, avec "en" par défaut si rien n'est
# défini.
# ============================================================

# ============================================================
# IMPORTS
# ============================================================

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from config.endpoints import ENDPOINTS

# ============================================================
# DOSSIER RACINE DU PROJET
# ============================================================
# Tous les chemins du projet sont calculés à partir de ce
# dossier racine.
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

# ============================================================
# CHARGEMENT DU FICHIER .ENV
# ============================================================
# Le fichier .env contient les variables locales sensibles ou
# propres à la machine de l'utilisateur.
# ============================================================

ENV_FILE = PROJECT_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)

# ============================================================
# LECTURE DE LA VERSION DU PROJET
# ============================================================
# La version du projet doit avoir une seule source de vérité.
# Cette source est le fichier VERSION placé à la racine.
# ============================================================

VERSION_FILE = PROJECT_DIR / "VERSION"


def read_project_version(version_file: Path, default: str = "0.0.0-dev") -> str:
    """
    Lit la version du projet depuis le fichier VERSION.

    Si le fichier n'existe pas ou ne peut pas être lu,
    retourne une valeur par défaut.
    """
    try:
        content = version_file.read_text(encoding="utf-8").strip()
        return content or default
    except OSError:
        return default


# ============================================================
# IDENTITÉ DU PROJET
# ============================================================

PROJECT_NAME = "GW2 Command Center"
PROJECT_SLUG = "gw2-command-center"
PROJECT_VERSION = read_project_version(VERSION_FILE)

# Dépôt officiel du projet.
# Cette URL est utilisée notamment dans les messages critiques
# quand une installation semble incomplète.
PROJECT_REPOSITORY_URL = "https://github.com/MisterWalky/gw2-command-center"

# ============================================================
# UTILISATEUR / USER-AGENT
# ============================================================
# GW2 recommande un User-Agent identifiable.
# Le nom utilisateur est personnalisable via le fichier .env.
# ============================================================

raw_api_user = os.getenv("GW2_API_USER", "gw2-user").strip()
GW2_API_USER = raw_api_user or "gw2-user"

# ============================================================
# CLÉ API GW2
# ============================================================
# Certains endpoints nécessitent une clé API.
# Si aucune clé n'est définie, la variable vaut None.
# ============================================================

GW2_API_KEY = os.getenv("GW2_API_KEY")
GW2_API_KEY = GW2_API_KEY.strip() if GW2_API_KEY else None

# ============================================================
# LANGUES DE L'APPLICATION
# ============================================================
# Ces langues correspondent aux langues officiellement
# supportées par l'interface de l'outil.
#
# Cette liste est définie manuellement afin de distinguer :
# - les langues prévues par le projet
# - les fichiers réellement présents dans l'installation locale
# ============================================================

SUPPORTED_APP_LANGS = (
    "en",
    "fr",
    "de",
    "es",
    "it",
    "pt",
    "pl",
    "ru",
    "ja",
    "ko",
)

DEFAULT_APP_LANG = "en"

raw_app_lang = os.getenv("APP_LANG", DEFAULT_APP_LANG).strip().lower()
APP_LANG = raw_app_lang or DEFAULT_APP_LANG

APP_LANG_FALLBACK_USED = False
INVALID_APP_LANG_REQUESTED = ""

if APP_LANG not in SUPPORTED_APP_LANGS:
    INVALID_APP_LANG_REQUESTED = APP_LANG
    APP_LANG = DEFAULT_APP_LANG
    APP_LANG_FALLBACK_USED = True

# ============================================================
# LANGUES API
# ============================================================
# Langues supportées à la date de référence actuelle :
# - en : anglais
# - fr : français
# - de : allemand
# - es : espagnol
#
# La variable GW2_API_LANGS peut contenir :
# - une langue : "en"
# - plusieurs langues : "fr,en,de"
# - toutes les langues supportées : "all"
#
# Règles :
# - si absente ou vide -> ["en"]
# - si "all" -> toutes les langues supportées
# - suppression des espaces
# - mise en minuscules
# - suppression des doublons
# - conservation de l'ordre
# - filtrage des langues non supportées
# ============================================================

SUPPORTED_API_LANGS = ("en", "fr", "de", "es")
DEFAULT_API_LANG = "en"
ALL_API_LANGS_KEYWORD = "all"

raw_api_langs = os.getenv("GW2_API_LANGS", "").strip().lower()

INVALID_API_LANGS: list[str] = []
API_LANGS: list[str] = []

if raw_api_langs == ALL_API_LANGS_KEYWORD:
    API_LANGS = list(SUPPORTED_API_LANGS)
else:
    parsed_langs = [lang.strip() for lang in raw_api_langs.split(",")] if raw_api_langs else []
    seen_langs = set()

    for lang in parsed_langs:
        if not lang:
            continue

        if lang not in SUPPORTED_API_LANGS:
            if lang not in INVALID_API_LANGS:
                INVALID_API_LANGS.append(lang)
            continue

        if lang in seen_langs:
            continue

        seen_langs.add(lang)
        API_LANGS.append(lang)

FALLBACK_API_LANG_USED = False

if not API_LANGS:
    API_LANGS = [DEFAULT_API_LANG]
    FALLBACK_API_LANG_USED = True

API_PRIMARY_LANG = API_LANGS[0]

# ============================================================
# USER-AGENT COMMUN PAR DÉFAUT
# ============================================================

BASE_USER_AGENT = f"{PROJECT_SLUG}/{PROJECT_VERSION} ({GW2_API_USER})"

# ============================================================
# ENVIRONNEMENT
# ============================================================

ENV = "BASE"

# ============================================================
# DOSSIERS DU PROJET
# ============================================================
# Ces constantes centralisent tous les chemins importants du
# projet afin d'éviter les chemins écrits en dur ailleurs.
# ============================================================

CONFIG_DIR = PROJECT_DIR / "config"
DB_DIR = PROJECT_DIR / "databases"
LOG_DIR = PROJECT_DIR / "logs"
MODULES_DIR = PROJECT_DIR / "modules"
SCRIPTS_DIR = PROJECT_DIR / "scripts"
SQL_DIR = PROJECT_DIR / "sql"
DASHBOARD_DIR = PROJECT_DIR / "dashboard"
I18N_DIR = DASHBOARD_DIR / "i18n"
EXPORTS_DIR = PROJECT_DIR / "exports"
SNAPSHOTS_DIR = PROJECT_DIR / "snapshots"
TEMP_DIR = PROJECT_DIR / "temp"

# ============================================================
# FICHIERS SQLITE PAR DÉFAUT
# ============================================================
# Ces fichiers peuvent être créés automatiquement s'ils
# n'existent pas encore.
#
# Important :
# - créer le fichier .db ne crée pas les tables
# - l'initialisation du schéma reste du ressort de init_db
# ============================================================

DEFAULT_DB_FILE = DB_DIR / "GW2_API.db"
TEST_DB_FILE = DB_DIR / "GW2_TEST.db"

# ============================================================
# CRÉATION AUTOMATIQUE DES DOSSIERS RUNTIME
# ============================================================
# Les dossiers runtime sont des dossiers utiles à l'exécution
# locale mais qui ne nécessitent pas forcément de contenu
# versionné à l'avance.
# ============================================================

RUNTIME_DIRS = (
    DB_DIR,
    LOG_DIR,
    EXPORTS_DIR,
    SNAPSHOTS_DIR,
    TEMP_DIR,
)


def ensure_runtime_directories() -> None:
    """
    Crée automatiquement les dossiers runtime du projet
    s'ils n'existent pas encore.
    """
    for directory in RUNTIME_DIRS:
        directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# CRÉATION AUTOMATIQUE DES FICHIERS SQLITE
# ============================================================
# La création automatique d'un fichier SQLite vide permet
# d'éviter certaines erreurs de démarrage sur un projet neuf.
# ============================================================

AUTO_CREATE_SQLITE_FILES = True


def ensure_sqlite_file(db_file: Path) -> None:
    """
    Crée un fichier SQLite vide s'il n'existe pas encore.

    Remarque :
    le simple fait de créer le fichier ne crée pas les tables.
    """
    db_file.parent.mkdir(parents=True, exist_ok=True)

    if not db_file.exists():
        db_file.touch()


def ensure_runtime_sqlite_files() -> None:
    """
    Crée les fichiers SQLite de base du projet s'ils n'existent
    pas encore.
    """
    if not AUTO_CREATE_SQLITE_FILES:
        return

    ensure_sqlite_file(DEFAULT_DB_FILE)
    ensure_sqlite_file(TEST_DB_FILE)


# Exécution immédiate de la préparation runtime.
ensure_runtime_directories()
ensure_runtime_sqlite_files()

# ============================================================
# CONFIGURATION API GW2
# ============================================================

API_BASE = "https://api.guildwars2.com/v2"

# ============================================================
# PARAMÈTRES HTTP COMMUNS
# ============================================================

USER_AGENT = BASE_USER_AGENT

REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
}

HTTP_TIMEOUT = 30

# ============================================================
# FORMAT DATE / TIMESTAMP
# ============================================================

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================
# PARAMÈTRES PAR DÉFAUT
# ============================================================
# Ces valeurs servent de socle commun. Les environnements
# spécifiques peuvent les surcharger.
# ============================================================

BATCH_SIZE = 200
SLEEP_SEC = 0.0
DEBUG = False
USE_TEST_IDS = False
TEST_IDS: list[int] = []

# ============================================================
# TABLES SQLITE TECHNIQUES UNIVERSELLES
# ============================================================
# Ces tables servent au fonctionnement interne du pipeline,
# indépendamment des tables métier propres à chaque endpoint.
# ============================================================

TABLES = {
    "api_ids": "API_IDS",
    "api_raw": "API_RAW",
    "api_index": "API_INDEX",
    "api_history": "API_HISTORY",
    "sync_log": "SYNC_LOG",
}

# ============================================================
# ÉTAT I18N
# ============================================================
# Ces indicateurs permettent de savoir si l'application utilise :
# - la langue demandée ;
# - un repli vers l'anglais ;
# - ou aucun fichier de langue exploitable.
# ============================================================

I18N_REQUESTED_LANG_USED = False
I18N_FALLBACK_EN_USED = False
I18N_FILES_MISSING = False
I18N_REQUESTED_LANG_FILE_MISSING = False
I18N_MISSING_LANG_CODE = ""

# ============================================================
# FONCTIONS UTILITAIRES I18N
# ============================================================


def load_lang_file(lang_code: str) -> dict[str, Any]:
    """
    Charge un fichier de langue JSON.

    Si le fichier n'existe pas, ne peut pas être lu ou ne
    contient pas un dictionnaire valide, retourne un
    dictionnaire vide.
    """
    lang_file = I18N_DIR / f"{lang_code}.json"

    if not lang_file.exists():
        return {}

    try:
        with lang_file.open("r", encoding="utf-8") as fh:
            data = json.load(fh)

            if isinstance(data, dict):
                return data

    except json.JSONDecodeError:
        return {}

    except OSError:
        return {}

    return {}


def merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Fusionne deux dictionnaires récursivement.

    Règles :
    - les valeurs du dictionnaire 'override' remplacent celles
      du dictionnaire 'base'
    - si une clé contient elle-même deux dictionnaires, la
      fusion est faite récursivement

    Cette logique permet d'utiliser en.json comme socle commun,
    puis de le compléter ou de le surcharger avec la langue
    demandée.
    """
    result = dict(base)

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def get_i18n_value(
    data: dict[str, Any],
    key_path: str,
    default: str | None = None,
) -> str:
    """
    Lit une valeur dans un dictionnaire i18n via un chemin à points.

    Exemple :
        CONFIG_BASE.PROJECT
    """
    current: Any = data

    for part in key_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return default if default is not None else key_path
        current = current[part]

    if isinstance(current, str):
        return current

    return default if default is not None else key_path


def load_app_i18n(lang_code: str) -> dict[str, Any]:
    """
    Charge les traductions de l'application.

    Stratégie retenue :
    1. charger en.json comme socle de référence
    2. si la langue demandée est 'en', retourner ce socle
    3. sinon charger la langue demandée
    4. fusionner la langue demandée au-dessus de l'anglais
    5. si le fichier de la langue demandée est absent, revenir
       à l'anglais
    6. si aucun fichier anglais n'est disponible, considérer
       que le projet est incomplet

    Cette approche permet :
    - d'avoir un fallback anglais global
    - d'accepter des fichiers de langue partiels
    - de distinguer une langue supportée mais absente localement
    - de limiter les erreurs visibles par l'utilisateur
    """
    global I18N_REQUESTED_LANG_USED
    global I18N_FALLBACK_EN_USED
    global I18N_FILES_MISSING
    global I18N_REQUESTED_LANG_FILE_MISSING
    global I18N_MISSING_LANG_CODE

    I18N_REQUESTED_LANG_USED = False
    I18N_FALLBACK_EN_USED = False
    I18N_FILES_MISSING = False
    I18N_REQUESTED_LANG_FILE_MISSING = False
    I18N_MISSING_LANG_CODE = ""

    en_data = load_lang_file("en")

    if not en_data:
        I18N_FILES_MISSING = True
        return {}

    if lang_code == "en":
        I18N_REQUESTED_LANG_USED = True
        return en_data

    requested_data = load_lang_file(lang_code)

    if not requested_data:
        I18N_FALLBACK_EN_USED = True
        I18N_REQUESTED_LANG_FILE_MISSING = True
        I18N_MISSING_LANG_CODE = lang_code
        return en_data

    I18N_REQUESTED_LANG_USED = True
    return merge_dicts(en_data, requested_data)


# Chargement global du dictionnaire applicatif.
APP_I18N = load_app_i18n(APP_LANG)


def tr(key_path: str, default: str | None = None) -> str:
    """
    Retourne une chaîne traduite à partir du dictionnaire chargé.

    Si la clé n'existe pas, retourne la valeur par défaut fournie.
    """
    return get_i18n_value(APP_I18N, key_path, default=default)


def get_i18n_warning_lines() -> list[str]:
    """
    Retourne une liste de messages d'avertissement si les fichiers
    de langue sont absents ou si le projet semble incomplet.

    Ces messages critiques restent volontairement codés en dur
    afin de pouvoir s'afficher même si l'i18n est complètement
    indisponible.

    Ils doivent être :
    - courts
    - explicites
    - compréhensibles immédiatement
    """
    warning_lines: list[str] = []

    if I18N_FILES_MISSING:
        warning_lines.append("--------------------------------------------------")
        warning_lines.append("CRITICAL: English language file is missing.")
        warning_lines.append("This project appears incomplete.")
        warning_lines.append("Please download the missing files from:")
        warning_lines.append(PROJECT_REPOSITORY_URL)
        warning_lines.append("--------------------------------------------------")

    return warning_lines


def print_i18n_warnings() -> None:
    """
    Affiche les avertissements i18n s'il y a lieu.

    Cet affichage doit intervenir dès qu'un lancement direct
    permet de constater une installation incomplète.
    """
    for line in get_i18n_warning_lines():
        print(line)


# ============================================================
# DIAGNOSTIC DE CONFIGURATION
# ============================================================


def print_config_diagnostics() -> None:
    """
    Affiche un diagnostic lisible de la configuration commune.
    """
    print("=" * 60)
    print(tr("CONFIG_BASE.DIRECT_RUN_TITLE", "Base configuration loaded"))
    print("=" * 60)

    print(f"{tr('CONFIG_BASE.PROJECT', 'Project')} : {PROJECT_NAME}")
    print(f"{tr('CONFIG_BASE.VERSION', 'Version')} : {PROJECT_VERSION}")
    print(f"{tr('CONFIG_BASE.ENVIRONMENT', 'Environment')} : {ENV}")
    print(f"{tr('CONFIG_BASE.PROJECT_DIR', 'Project directory')} : {PROJECT_DIR}")
    print(f"{tr('CONFIG_BASE.VERSION_FILE', 'Version file')} : {VERSION_FILE}")
    print(f"{tr('CONFIG_BASE.ENV_FILE', 'Environment file')} : {ENV_FILE}")

    print()

    print(f"{tr('CONFIG_BASE.API_USER', 'API user')} : {GW2_API_USER}")
    print(f"{tr('CONFIG_BASE.USER_AGENT', 'User-Agent')} : {USER_AGENT}")
    print(
        f"{tr('CONFIG_BASE.API_KEY_DETECTED', 'API key detected')} : "
        f"{tr('COMMON.YES', 'yes') if GW2_API_KEY else tr('COMMON.NO', 'no')}"
    )

    print()

    print(
        f"{tr('CONFIG_BASE.SUPPORTED_LANGS', 'Supported API languages')} : "
        f"{', '.join(SUPPORTED_API_LANGS)}"
    )
    print(
        f"{tr('CONFIG_BASE.SUPPORTED_APP_LANGS', 'Supported application languages')} : "
        f"{', '.join(SUPPORTED_APP_LANGS)}"
    )
    print(f"{tr('CONFIG_BASE.API_LANGS', 'Active API languages')} : {', '.join(API_LANGS)}")
    print(f"{tr('CONFIG_BASE.PRIMARY_LANG', 'Primary API language')} : {API_PRIMARY_LANG}")
    print(f"{tr('CONFIG_BASE.APP_LANG', 'Application language')} : {APP_LANG}")

    if INVALID_APP_LANG_REQUESTED:
        print(
            f"{tr('CONFIG_BASE.INVALID_APP_LANG', 'Unsupported application language requested')} : "
            f"{INVALID_APP_LANG_REQUESTED}"
        )

    if APP_LANG_FALLBACK_USED:
        print(
            f"{tr('CONFIG_BASE.APP_LANG_FALLBACK_USED', 'Fallback application language used')} : "
            f"{APP_LANG}"
        )

    if INVALID_API_LANGS:
        print(
            f"{tr('CONFIG_BASE.INVALID_LANGS', 'Unsupported API languages ignored')} : "
            f"{', '.join(INVALID_API_LANGS)}"
        )

    if FALLBACK_API_LANG_USED:
        print(
            f"{tr('CONFIG_BASE.FALLBACK_LANG_USED', 'Fallback API language used')} : "
            f"{DEFAULT_API_LANG}"
        )

    if I18N_REQUESTED_LANG_FILE_MISSING:
        print(
            f"{tr('CONFIG_BASE.MISSING_APP_LANG_FILE', 'Missing application language file')} : "
            f"{I18N_MISSING_LANG_CODE}.json"
        )

    if I18N_FALLBACK_EN_USED:
        print(
            f"{tr('CONFIG_BASE.I18N_FALLBACK_EN_USED', 'English fallback language file used')} : "
            f"{tr('COMMON.YES', 'yes')}"
        )

    print()

    print(f"{tr('CONFIG_BASE.API_BASE', 'API base')} : {API_BASE}")
    print(f"{tr('CONFIG_BASE.DEFAULT_DB_FILE', 'Default database file')} : {DEFAULT_DB_FILE}")
    print(f"{tr('CONFIG_BASE.TEST_DB_FILE', 'Test database file')} : {TEST_DB_FILE}")
    print(
        f"{tr('CONFIG_BASE.ENDPOINTS', 'Configured endpoints')} : " f"{', '.join(ENDPOINTS.keys())}"
    )
    print(
        f"{tr('CONFIG_BASE.SQLITE_TECHNICAL_TABLES', 'Technical SQLite tables')} : "
        f"{', '.join(TABLES.values())}"
    )

    print("=" * 60)

    print_i18n_warnings()


# ============================================================
# AFFICHAGE SI LANCÉ DIRECTEMENT
# ============================================================
# Cet affichage sert surtout au diagnostic rapide de la
# configuration commune.
# ============================================================

if __name__ == "__main__":
    print_config_diagnostics()
