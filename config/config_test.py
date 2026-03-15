# ------------------------------------------------------------
# config_test.py
# ------------------------------------------------------------
# Configuration TEST du projet GW2_API_PROJECT.
#
# Ce fichier importe toute la configuration commune depuis
# config_base.py puis remplace uniquement ce qui est utile
# pour les tests.
#
# Avantages :
# - fichier court
# - facile à modifier
# - très lisible
# - aucun risque pour la base de production
# ------------------------------------------------------------

from config.config_base import *  # noqa: F403,F401

# ------------------------------------------------------------
# 1) ENVIRONNEMENT
# ------------------------------------------------------------

ENV = "TEST"


# ------------------------------------------------------------
# 2) BASE DE DONNÉES DE TEST
# ------------------------------------------------------------

DB_NAME = "GW2_TEST.db"
DB_PATH = DB_DIR / DB_NAME  # noqa: F405


# ------------------------------------------------------------
# 3) PARAMÈTRES RÉSEAU DE TEST
# ------------------------------------------------------------
# En test, on travaille sur peu d'IDs et sans pause.

HTTP_TIMEOUT = 30
BATCH_SIZE = 5
SLEEP_SEC = 0


# ------------------------------------------------------------
# 4) USER-AGENT DE TEST
# ------------------------------------------------------------

USER_AGENT = f"{PROJECT_NAME}_TEST/{PROJECT_VERSION} ({GW2_API_USER})"  # noqa: F405

REQUEST_HEADERS = {"User-Agent": USER_AGENT}


# ------------------------------------------------------------
# 5) PARAMÈTRES DE TEST
# ------------------------------------------------------------
# Permet de choisir si le script doit utiliser une liste fixe
# d'IDs ou aller chercher les IDs via l'API.

USE_TEST_IDS = True

TEST_IDS = [
    19721,
    23009,
    125,
    126,
    108801,
]


# ------------------------------------------------------------
# 6) DEBUG
# ------------------------------------------------------------

DEBUG = True


# ------------------------------------------------------------
# 7) AFFICHAGE SI LANCÉ DIRECTEMENT
# ------------------------------------------------------------

if __name__ == "__main__":
    print("Configuration TEST chargée")
    print("Environnement :", ENV)
    print("Projet :", PROJECT_DIR)  # noqa: F405
    print("Base utilisée :", DB_PATH)
    print("Utilisateur API :", GW2_API_USER)  # noqa: F405
    print("User-Agent :", USER_AGENT)
    print("Clé API détectée :", "oui" if GW2_API_KEY else "non")  # noqa: F405
    print("Langues API :", API_LANGS)  # noqa: F405
    print("Endpoints :", ENDPOINTS)  # noqa: F405
    print("IDs de test :", TEST_IDS)
    print("Tables techniques SQLite :", TABLES)  # noqa: F405
    print("Tables métier SQLite :", [cfg["table"] for cfg in ENDPOINTS.values()])  # noqa: F405
