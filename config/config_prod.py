# ============================================================
# Projet      : GW2 Command Center
# Fichier     : config/config_prod.py
# Rôle        : Configuration de production du projet
# Auteur      : William CROCHOT (MisterWalky)
# Référence   : https://github.com/MisterWalky/gw2-command-center
# Licence     : MIT
# ============================================================
#
# DESCRIPTION
# -----------
# Ce fichier définit la configuration de production du projet.
#
# Il importe la configuration commune depuis config_base.py
# puis redéfinit uniquement les paramètres qui doivent varier
# pour l'environnement de production.
#
# Cette configuration est destinée :
# - à la base de données principale
# - aux synchronisations réelles
# - aux traitements de production
# - à l'alimentation des outils d'analyse
#
# CONVENTION
# ----------
# Toute la logique commune reste dans config_base.py.
# Ce fichier ne doit contenir que les surcharges propres à la
# production.
#
# I18N
# ----
# Les messages utilisateur normaux passent par tr().
# Les messages critiques éventuels liés à l'absence des fichiers
# de langue sont gérés par config_base.py.
# ============================================================

# ============================================================
# IMPORTS
# ============================================================

from config.config_base import (
    API_LANGS,
    APP_LANG,
    DEFAULT_DB_FILE,
    ENDPOINTS,
    GW2_API_KEY,
    GW2_API_USER,
    PROJECT_DIR,
    PROJECT_SLUG,
    PROJECT_VERSION,
    TABLES,
    print_i18n_warnings,
    tr,
)

# ============================================================
# ENVIRONNEMENT
# ============================================================

ENV = "PROD"

# ============================================================
# BASE DE DONNÉES DE PRODUCTION
# ============================================================
# La base de production correspond à la base principale du
# projet.
# ============================================================

DB_PATH = DEFAULT_DB_FILE
DB_NAME = DB_PATH.name

# ============================================================
# PARAMÈTRES RÉSEAU DE PRODUCTION
# ============================================================
# Ces paramètres sont utilisés lors des synchronisations
# réelles sur l'API officielle.
# ============================================================

HTTP_TIMEOUT = 30
BATCH_SIZE = 200
SLEEP_SEC = 0.12

# ============================================================
# USER-AGENT DE PRODUCTION
# ============================================================
# Un User-Agent explicite permet d'identifier clairement le
# contexte d'exécution côté projet.
# ============================================================

USER_AGENT = f"{PROJECT_SLUG}-prod/{PROJECT_VERSION} ({GW2_API_USER})"

REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
}

# ============================================================
# PARAMÈTRES DE PRODUCTION
# ============================================================

USE_TEST_IDS = False
TEST_IDS: list[int] = []

# ============================================================
# DEBUG
# ============================================================

DEBUG = False

# ============================================================
# AFFICHAGE SI LANCÉ DIRECTEMENT
# ============================================================
# Cet affichage sert surtout au diagnostic rapide de la
# configuration de production.
# ============================================================

if __name__ == "__main__":
    print(tr("CONFIG_PROD.DIRECT_RUN_TITLE", "Production configuration loaded"))
    print(f"{tr('CONFIG_PROD.ENVIRONMENT', 'Environment')} : {ENV}")
    print(f"{tr('CONFIG_PROD.PROJECT_DIR', 'Project directory')} : {PROJECT_DIR}")
    print(f"{tr('CONFIG_PROD.DB_PATH', 'Database path')} : {DB_PATH}")
    print(f"{tr('CONFIG_PROD.API_USER', 'API user')} : {GW2_API_USER}")
    print(f"{tr('CONFIG_PROD.USER_AGENT', 'User-Agent')} : {USER_AGENT}")
    print(
        f"{tr('CONFIG_PROD.API_KEY_DETECTED', 'API key detected')} : "
        f"{tr('COMMON.YES', 'yes') if GW2_API_KEY else tr('COMMON.NO', 'no')}"
    )
    print(f"{tr('CONFIG_PROD.APP_LANG', 'Application language')} : " f"{APP_LANG}")
    print(f"{tr('CONFIG_PROD.API_LANGS', 'API languages')} : " f"{API_LANGS}")
    print(f"{tr('CONFIG_PROD.ENDPOINTS', 'Configured endpoints')} : " f"{list(ENDPOINTS.keys())}")
    print(f"{tr('CONFIG_PROD.SQLITE_TECHNICAL_TABLES', 'Technical SQLite tables')} : " f"{TABLES}")
    print(
        f"{tr('CONFIG_PROD.SQLITE_BUSINESS_TABLES', 'Business SQLite tables')} : "
        f"{[cfg['table'] for cfg in ENDPOINTS.values() if 'table' in cfg]}"
    )

    # Avertissement critique si les fichiers de langue sont
    # totalement absents.
    print_i18n_warnings()
