# ------------------------------------------------------------
# config_base.py
# ------------------------------------------------------------
# Configuration COMMUNE du projet GW2_API_PROJECT.
#
# Ce fichier contient tout ce qui est partagé entre :
# - les scripts de TEST
# - les scripts de PRODUCTION
#
# Les fichiers config_test.py et config_prod.py importent ce
# fichier puis ne modifient que ce qui change selon
# l'environnement.
# ------------------------------------------------------------


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------

import os
from pathlib import Path

from dotenv import load_dotenv

# ------------------------------------------------------------
# CHARGEMENT DU FICHIER .ENV
# ------------------------------------------------------------
# Le fichier .env permet de stocker hors du code :
# - la clé API GW2
# - le nom utilisateur utilisé dans le User-Agent
# ------------------------------------------------------------

load_dotenv()


# ------------------------------------------------------------
# IDENTITÉ DU PROJET
# ------------------------------------------------------------

PROJECT_NAME = "GW2_API_PROJECT"
PROJECT_VERSION = "1.0"


# ------------------------------------------------------------
# UTILISATEUR / USER-AGENT
# ------------------------------------------------------------
# GW2 recommande un User-Agent identifiable.
# Le nom utilisateur est personnalisable via le fichier .env.

GW2_API_USER = os.getenv("GW2_API_USER", "YourName")


# ------------------------------------------------------------
# CLÉ API GW2
# ------------------------------------------------------------
# Certains endpoints nécessitent une clé API.
# Si aucune clé n'est définie, la variable vaut None.

GW2_API_KEY = os.getenv("GW2_API_KEY")


# ------------------------------------------------------------
# USER-AGENT COMMUN PAR DÉFAUT
# ------------------------------------------------------------

BASE_USER_AGENT = f"{PROJECT_NAME}/{PROJECT_VERSION} ({GW2_API_USER})"


# ------------------------------------------------------------
# 1) ENVIRONNEMENT
# ------------------------------------------------------------

ENV = "BASE"


# ------------------------------------------------------------
# 2) DOSSIER RACINE DU PROJET
# ------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]


# ------------------------------------------------------------
# 3) DOSSIERS DU PROJET
# ------------------------------------------------------------

CONFIG_DIR = PROJECT_DIR / "config"
DB_DIR = PROJECT_DIR / "databases"
LOG_DIR = PROJECT_DIR / "logs"
MODULES_DIR = PROJECT_DIR / "modules"
SCRIPTS_DIR = PROJECT_DIR / "scripts"
SQL_DIR = PROJECT_DIR / "sql"


# ------------------------------------------------------------
# 4) CRÉATION AUTOMATIQUE DES DOSSIERS
# ------------------------------------------------------------

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
MODULES_DIR.mkdir(parents=True, exist_ok=True)
SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
SQL_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 5) CONFIGURATION API GW2
# ------------------------------------------------------------

API_BASE = "https://api.guildwars2.com/v2"

# Langues utilisées pour les endpoints compatibles avec ?lang=
API_LANGS = ["fr", "en"]


# ------------------------------------------------------------
# 6) PARAMÈTRES HTTP COMMUNS
# ------------------------------------------------------------

USER_AGENT = BASE_USER_AGENT

REQUEST_HEADERS = {"User-Agent": USER_AGENT}

HTTP_TIMEOUT = 30


# ------------------------------------------------------------
# 7) FORMAT DATE / TIMESTAMP
# ------------------------------------------------------------

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ------------------------------------------------------------
# 8) PARAMÈTRES PAR DÉFAUT
# ------------------------------------------------------------

BATCH_SIZE = 200
SLEEP_SEC = 0.0
DEBUG = False
USE_TEST_IDS = False
TEST_IDS: list[int] = []


# ------------------------------------------------------------
# 9) TABLES SQLITE TECHNIQUES UNIVERSELLES
# ------------------------------------------------------------
# api_ids     -> suivi des identifiants connus
# api_raw     -> données brutes provenant directement de l'API
# api_index   -> table technique pour détecter rapidement
#                les changements
# api_history -> historique détaillé des changements détectés
# sync_log    -> journal des synchronisations et des erreurs

TABLES = {
    "api_ids": "API_IDS",
    "api_raw": "API_RAW",
    "api_index": "API_INDEX",
    "api_history": "API_HISTORY",
    "sync_log": "Sync_Log",
}


# ------------------------------------------------------------
# 10) ENDPOINTS API UTILISÉS
# ------------------------------------------------------------

ENDPOINTS = {
    # --------------------------------------------------------
    # ENDPOINT : items
    # --------------------------------------------------------
    "items": {
        "path": "/items",
        "localized": True,
        "mode": "snapshot",
        "table": "Items",
        "schema": {
            "id": "INTEGER PRIMARY KEY",
            "name_fr": "TEXT",
            "name_en": "TEXT",
            "description_fr": "TEXT",
            "description_en": "TEXT",
            "type": "TEXT",
            "level": "INTEGER",
            "rarity": "TEXT",
            "vendor_value": "INTEGER",
            "chat_link": "TEXT",
            "icon": "TEXT",
            "details_type": "TEXT",
            "created_at": "TEXT",
            "updated_at": "TEXT",
        },
        "indexes": [
            ["rarity"],
            ["type"],
            ["level"],
        ],
    },
    # --------------------------------------------------------
    # ENDPOINT : commerce_prices
    # --------------------------------------------------------
    "commerce_prices": {
        "path": "/commerce/prices",
        "localized": False,
        "mode": "timeseries",
        "table": "Commerce_Prices_History",
        "schema": {
            "observed_at": "TEXT NOT NULL",
            "item_id": "INTEGER NOT NULL",
            "buy_quantity": "INTEGER",
            "buy_unit_price": "INTEGER",
            "sell_quantity": "INTEGER",
            "sell_unit_price": "INTEGER",
        },
        "primary_key": ["observed_at", "item_id"],
        "indexes": [
            ["item_id"],
            ["observed_at"],
        ],
    },
}


# ------------------------------------------------------------
# 11) FONCTION UTILITAIRE POUR CONSTRUIRE LES URLS
# ------------------------------------------------------------


def build_endpoint(name: str) -> str:
    """
    Construit l'URL complète d'un endpoint à partir de son nom.
    """
    return f"{API_BASE}{ENDPOINTS[name]['path']}"


# ------------------------------------------------------------
# 12) AFFICHAGE SI LANCÉ DIRECTEMENT
# ------------------------------------------------------------

if __name__ == "__main__":
    print("Configuration BASE chargée")
    print("Projet :", PROJECT_NAME)
    print("Version :", PROJECT_VERSION)
    print("Utilisateur API :", GW2_API_USER)
    print("User-Agent :", USER_AGENT)
    print("Clé API détectée :", "oui" if GW2_API_KEY else "non")
    print("Projet :", PROJECT_DIR)
    print("API Base :", API_BASE)
    print("Langues API :", API_LANGS)
    print("Endpoints :", list(ENDPOINTS.keys()))
    print("Tables techniques SQLite :", TABLES)
