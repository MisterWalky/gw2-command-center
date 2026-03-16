# ============================================================
# Projet      : GW2 Command Center
# Fichier     : config/endpoints.py
# Rôle        : Définition centralisée des endpoints API
# Auteur      : William CROCHOT (MisterWalky)
# Référence   : https://github.com/MisterWalky/gw2-command-center
# Licence     : MIT
# ============================================================
#
# DESCRIPTION
# -----------
# Ce fichier centralise la définition des endpoints API
# utilisés par le projet.
#
# Chaque endpoint décrit :
# - son chemin API
# - son mode de collecte
# - son caractère localisé ou non
# - sa ou ses tables SQLite
# - son schéma principal
# - son schéma i18n éventuel
# - ses clés primaires
# - ses index
#
# OBJECTIF
# --------
# Séparer la configuration métier des endpoints de la
# configuration générale du projet.
#
# Ce choix permet :
# - de garder config_base.py plus lisible
# - d'ajouter facilement de nouveaux endpoints
# - de préparer la future montée en charge du projet
# - d'anticiper un volume important d'endpoints
#
# CONVENTION
# ----------
# Les endpoints localisés utilisent :
# - une table principale pour les données non localisées
# - une table i18n pour les champs dépendants de la langue
# ============================================================

# ============================================================
# ENDPOINTS API UTILISÉS
# ============================================================

ENDPOINTS = {
    "items": {
        "path": "/items",
        "localized": True,
        "mode": "snapshot",
        "table": "ITEMS",
        "i18n_table": "ITEMS_I18N",
        "schema": {
            "id": "INTEGER PRIMARY KEY",
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
        "i18n_schema": {
            "item_id": "INTEGER NOT NULL",
            "lang": "TEXT NOT NULL",
            "name": "TEXT",
            "description": "TEXT",
            "updated_at": "TEXT",
        },
        "i18n_primary_key": ["item_id", "lang"],
        "indexes": [
            ["rarity"],
            ["type"],
            ["level"],
        ],
        "i18n_indexes": [
            ["lang"],
            ["name"],
        ],
    },
    "commerce_prices": {
        "path": "/commerce/prices",
        "localized": False,
        "mode": "timeseries",
        "table": "COMMERCE_PRICES_HISTORY",
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
