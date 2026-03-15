# ------------------------------------------------------------
# config_prod.py
# ------------------------------------------------------------
# Configuration PRODUCTION du projet GW2_API_PROJECT.
#
# Ce fichier importe la configuration commune depuis
# config_base.py puis remplace uniquement ce qui doit être
# différent en production.
#
# Cette configuration est destinée à la vraie base de données,
# aux synchronisations réelles et à l'alimentation d'Excel.
# ------------------------------------------------------------

from config.config_base import *  # noqa: F403,F401

# ------------------------------------------------------------
# 1) ENVIRONNEMENT
# ------------------------------------------------------------

ENV = "PROD"


# ------------------------------------------------------------
# 2) BASE DE DONNÉES DE PRODUCTION
# ------------------------------------------------------------

DB_NAME = "GW2_API.db"
DB_PATH = DB_DIR / DB_NAME  # noqa: F405


# ------------------------------------------------------------
# 3) PARAMÈTRES RÉSEAU DE PRODUCTION
# ------------------------------------------------------------

HTTP_TIMEOUT = 30
BATCH_SIZE = 200
SLEEP_SEC = 0.12


# ------------------------------------------------------------
# 4) USER-AGENT DE PRODUCTION
# ------------------------------------------------------------

USER_AGENT = f"{PROJECT_NAME}_PROD/{PROJECT_VERSION} ({GW2_API_USER})"  # noqa: F405

REQUEST_HEADERS = {"User-Agent": USER_AGENT}


# ------------------------------------------------------------
# 5) PARAMÈTRES DE PRODUCTION
# ------------------------------------------------------------

USE_TEST_IDS = False
TEST_IDS: list[int] = []


# ------------------------------------------------------------
# 6) DEBUG
# ------------------------------------------------------------

DEBUG = False


# ------------------------------------------------------------
# 7) AFFICHAGE SI LANCÉ DIRECTEMENT
# ------------------------------------------------------------

if __name__ == "__main__":
    print("Configuration PRODUCTION chargée")
    print("Environnement :", ENV)
    print("Projet :", PROJECT_DIR)  # noqa: F405
    print("Base utilisée :", DB_PATH)
    print("Utilisateur API :", GW2_API_USER)  # noqa: F405
    print("User-Agent :", USER_AGENT)
    print("Clé API détectée :", "oui" if GW2_API_KEY else "non")  # noqa: F405
    print("Langues API :", API_LANGS)  # noqa: F405
    print("Endpoints :", ENDPOINTS)  # noqa: F405
    print("Tables techniques SQLite :", TABLES)  # noqa: F405
    print("Tables métier SQLite :", [cfg["table"] for cfg in ENDPOINTS.values()])  # noqa: F405
