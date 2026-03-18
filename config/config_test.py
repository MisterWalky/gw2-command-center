# ============================================================
# Projet      : GW2 Command Center
# Fichier     : config/config_test.py
# Rôle        : Configuration de test du projet
# Auteur      : William CROCHOT (MisterWalky)
# Référence   : https://github.com/MisterWalky/gw2-command-center
# Licence     : MIT
# ============================================================
#
# DESCRIPTION
# -----------
# Ce fichier définit la configuration de test du projet.
#
# Il importe la configuration commune depuis config_base.py
# puis ne redéfinit que les paramètres utiles aux essais
# locaux et aux validations techniques.
#
# Cette configuration est destinée :
# - à la base de données de test ;
# - aux essais sur un petit volume de données ;
# - aux vérifications de comportement ;
# - aux diagnostics sans risque pour la base principale.
#
# CONVENTION
# ----------
# Toute la logique commune reste dans config_base.py.
# Ce fichier ne doit contenir que les surcharges propres à
# l'environnement de test.
#
# I18N
# ----
# Les messages utilisateur normaux passent par tr().
# Les messages critiques éventuels liés à l'absence des fichiers
# de langue sont gérés par config_base.py.
# ============================================================

from config.config_base import (
    API_LANGS,
    APP_LANG,
    ENDPOINTS,
    GW2_API_KEY,
    GW2_API_USER,
    PROJECT_DIR,
    PROJECT_SLUG,
    PROJECT_VERSION,
    TABLES,
    TEST_DB_FILE,
    print_i18n_warnings,
    tr,
)

# ============================================================
# ENVIRONNEMENT
# ============================================================
# Cette valeur permet d'identifier clairement que cette
# configuration cible un usage de test et non la production.
# ============================================================

ENV = "TEST"

# ============================================================
# BASE DE DONNÉES DE TEST
# ============================================================
# La base de test doit rester séparée de la base principale
# afin de permettre des essais sans impact sur les données
# de production.
# ============================================================

DB_PATH = TEST_DB_FILE
DB_NAME = DB_PATH.name

# ============================================================
# PARAMÈTRES RÉSEAU DE TEST
# ============================================================
# En environnement de test, on réduit volontairement la taille
# des lots pour faciliter les vérifications, et on supprime la
# pause entre les appels pour accélérer les essais.
# ============================================================

HTTP_TIMEOUT = 30
BATCH_SIZE = 5
SLEEP_SEC = 0.0

# ============================================================
# USER-AGENT DE TEST
# ============================================================
# Le User-Agent reste identifiable, mais mentionne ici le mode
# TEST afin de distinguer plus facilement les essais de
# l'usage standard du projet.
# ============================================================

USER_AGENT = f"{PROJECT_SLUG}-test/{PROJECT_VERSION} ({GW2_API_USER})"

REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
}

# ============================================================
# PARAMÈTRES DE TEST
# ============================================================
# Ces options permettent de piloter des essais reproductibles.
#
# USE_TEST_IDS :
# - True  -> utiliser la liste TEST_IDS définie ci-dessous
# - False -> laisser le script récupérer les IDs selon sa
#            logique normale
# ============================================================

USE_TEST_IDS = True

TEST_IDS = [
    19721,
    23009,
    125,
    126,
    108801,
]

# ============================================================
# DEBUG
# ============================================================
# Le mode debug est activé en test pour faciliter l'analyse
# des comportements et l'affichage des informations utiles.
# ============================================================

DEBUG = True

# ============================================================
# AFFICHAGE SI LANCÉ DIRECTEMENT
# ============================================================
# Cet affichage sert au diagnostic rapide de la configuration
# de test et permet de vérifier visuellement les principaux
# paramètres actifs.
# ============================================================

if __name__ == "__main__":
    print(tr("CONFIG_TEST.DIRECT_RUN_TITLE", "Test configuration loaded"))
    print(f"{tr('CONFIG_TEST.ENVIRONMENT', 'Environment')} : {ENV}")
    print(f"{tr('CONFIG_TEST.PROJECT_DIR', 'Project directory')} : {PROJECT_DIR}")
    print(f"{tr('CONFIG_TEST.DB_PATH', 'Database used')} : {DB_PATH}")
    print(f"{tr('CONFIG_TEST.API_USER', 'API user')} : {GW2_API_USER}")
    print(f"{tr('CONFIG_TEST.USER_AGENT', 'User-Agent')} : {USER_AGENT}")
    print(
        f"{tr('CONFIG_TEST.API_KEY_DETECTED', 'API key detected')} : "
        f"{tr('COMMON.YES', 'yes') if GW2_API_KEY else tr('COMMON.NO', 'no')}"
    )
    print(f"{tr('CONFIG_TEST.APP_LANG', 'Application language')} : {APP_LANG}")
    print(f"{tr('CONFIG_TEST.API_LANGS', 'API languages')} : {API_LANGS}")
    print(f"{tr('CONFIG_TEST.ENDPOINTS', 'Configured endpoints')} : {list(ENDPOINTS.keys())}")
    print(f"{tr('CONFIG_TEST.TEST_IDS', 'Test IDs')} : {TEST_IDS}")
    print(f"{tr('CONFIG_TEST.SQLITE_TECHNICAL_TABLES', 'Technical SQLite tables')} : {TABLES}")
    print(
        f"{tr('CONFIG_TEST.SQLITE_BUSINESS_TABLES', 'Business SQLite tables')} : "
        f"{[cfg['table'] for cfg in ENDPOINTS.values() if 'table' in cfg]}"
    )

    print_i18n_warnings()
