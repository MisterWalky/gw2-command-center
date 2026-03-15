# ------------------------------------------------------------
# init_db.py
#
# Script unique d'initialisation de la base SQLite.
#
# Il permet de créer les tables et les index :
# - soit dans la base TEST
# - soit dans la base PROD
#
# Utilisation :
#   py scripts/init_db.py test
#   py scripts/init_db.py prod
# ------------------------------------------------------------


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------

import sys
import sqlite3
from pathlib import Path


# ------------------------------------------------------------
# AJOUT DE LA RACINE DU PROJET AU PYTHONPATH
# ------------------------------------------------------------

sys.path.append(str(Path(__file__).resolve().parents[1]))


# ------------------------------------------------------------
# CHARGEMENT DE LA CONFIGURATION
# ------------------------------------------------------------

if len(sys.argv) > 1:
    target_env = sys.argv[1].strip().lower()
else:
    target_env = "test"

if target_env == "prod":
    from config.config_prod import DB_PATH, DEBUG, TABLES, ENDPOINTS
    loaded_env = "PROD"
else:
    from config.config_test import DB_PATH, DEBUG, TABLES, ENDPOINTS
    loaded_env = "TEST"


# ------------------------------------------------------------
# CONSTANTES DE VALIDATION
# ------------------------------------------------------------

ALLOWED_MODES = {"snapshot", "timeseries"}

REQUIRED_ENDPOINT_KEYS = {
    "path",
    "localized",
    "mode",
    "table",
    "schema",
}


# ------------------------------------------------------------
# FONCTION UTILITAIRE : CONSTRUIRE LE SQL DES COLONNES
# ------------------------------------------------------------

def build_columns_sql(schema_dict: dict[str, str]) -> str:
    sql_lines = []

    for column_name, column_type in schema_dict.items():
        sql_lines.append(f"{column_name} {column_type}")

    return ",\n                ".join(sql_lines)


# ------------------------------------------------------------
# FONCTION UTILITAIRE : CONSTRUIRE LE SQL DE LA CLÉ PRIMAIRE
# ------------------------------------------------------------

def build_primary_key_sql(columns: list[str]) -> str:
    if not columns:
        return ""

    joined_columns = ", ".join(columns)
    return f",\n                PRIMARY KEY ({joined_columns})"


# ------------------------------------------------------------
# VALIDATION DE LA CONFIGURATION DES ENDPOINTS
# ------------------------------------------------------------

def validate_endpoints_config() -> None:
    if not isinstance(ENDPOINTS, dict) or not ENDPOINTS:
        raise ValueError("ENDPOINTS doit être un dictionnaire non vide.")

    for endpoint_name, endpoint_config in ENDPOINTS.items():
        if not isinstance(endpoint_config, dict):
            raise ValueError(
                f"L'endpoint '{endpoint_name}' doit être un dictionnaire."
            )

        missing_keys = REQUIRED_ENDPOINT_KEYS - set(endpoint_config.keys())
        if missing_keys:
            raise ValueError(
                f"L'endpoint '{endpoint_name}' est incomplet. "
                f"Clés manquantes : {sorted(missing_keys)}"
            )

        mode = endpoint_config["mode"]
        if mode not in ALLOWED_MODES:
            raise ValueError(
                f"L'endpoint '{endpoint_name}' a un mode invalide : '{mode}'. "
                f"Valeurs autorisées : {sorted(ALLOWED_MODES)}"
            )

        localized = endpoint_config["localized"]
        if not isinstance(localized, bool):
            raise ValueError(
                f"L'endpoint '{endpoint_name}' doit avoir "
                f"'localized' à True ou False."
            )

        table_name = endpoint_config["table"]
        if not isinstance(table_name, str) or not table_name.strip():
            raise ValueError(
                f"L'endpoint '{endpoint_name}' doit avoir un nom de table valide."
            )

        schema = endpoint_config["schema"]
        if not isinstance(schema, dict) or not schema:
            raise ValueError(
                f"L'endpoint '{endpoint_name}' doit avoir un schéma non vide."
            )

        indexes = endpoint_config.get("indexes", [])
        if not isinstance(indexes, list):
            raise ValueError(
                f"L'endpoint '{endpoint_name}' doit avoir 'indexes' sous forme de liste."
            )

        for index_columns in indexes:
            if not isinstance(index_columns, list) or not index_columns:
                raise ValueError(
                    f"L'endpoint '{endpoint_name}' a un index invalide : {index_columns}"
                )

            for column_name in index_columns:
                if column_name not in schema:
                    raise ValueError(
                        f"L'endpoint '{endpoint_name}' référence la colonne "
                        f"'{column_name}' dans un index, mais cette colonne "
                        f"n'existe pas dans le schéma."
                    )

        if mode == "timeseries":
            primary_key = endpoint_config.get("primary_key", [])

            if not primary_key:
                raise ValueError(
                    f"L'endpoint timeseries '{endpoint_name}' doit définir 'primary_key'."
                )

            if not isinstance(primary_key, list):
                raise ValueError(
                    f"L'endpoint '{endpoint_name}' doit avoir 'primary_key' sous forme de liste."
                )

            for column_name in primary_key:
                if column_name not in schema:
                    raise ValueError(
                        f"L'endpoint '{endpoint_name}' référence la colonne "
                        f"'{column_name}' dans primary_key, mais cette colonne "
                        f"n'existe pas dans le schéma."
                    )


# ------------------------------------------------------------
# SQL DE CRÉATION DES TABLES TECHNIQUES
# ------------------------------------------------------------

def get_technical_table_sql() -> dict[str, str]:
    return {
        # ----------------------------------------------------
        # TABLE API_IDS
        # ----------------------------------------------------
        # Suit les identifiants connus d'un endpoint dans le temps.

        "api_ids": f"""
        CREATE TABLE IF NOT EXISTS {TABLES["api_ids"]} (
            endpoint TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (endpoint, entity_id)
        );
        """,

        # ----------------------------------------------------
        # TABLE API_RAW
        # ----------------------------------------------------

        "api_raw": f"""
        CREATE TABLE IF NOT EXISTS {TABLES["api_raw"]} (
            endpoint TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            locale TEXT,
            json_data TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            PRIMARY KEY (endpoint, entity_id, locale)
        );
        """,

        # ----------------------------------------------------
        # TABLE API_INDEX
        # ----------------------------------------------------

        "api_index": f"""
        CREATE TABLE IF NOT EXISTS {TABLES["api_index"]} (
            endpoint TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            locale TEXT,
            content_hash TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            PRIMARY KEY (endpoint, entity_id, locale)
        );
        """,

        # ----------------------------------------------------
        # TABLE API_HISTORY
        # ----------------------------------------------------

        "api_history": f"""
        CREATE TABLE IF NOT EXISTS {TABLES["api_history"]} (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            locale TEXT,
            change_type TEXT NOT NULL,
            old_hash TEXT,
            new_hash TEXT,
            old_json_data TEXT,
            new_json_data TEXT,
            change_summary TEXT,
            changed_at TEXT NOT NULL
        );
        """,

        # ----------------------------------------------------
        # TABLE Sync_Log
        # ----------------------------------------------------

        "sync_log": f"""
        CREATE TABLE IF NOT EXISTS {TABLES["sync_log"]} (
            sync_id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT NOT NULL,
            locale TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT,
            records_processed INTEGER,
            status TEXT NOT NULL,
            message TEXT
        );
        """,
    }


# ------------------------------------------------------------
# SQL DE CRÉATION DES TABLES FINALES
# ------------------------------------------------------------

def get_endpoint_table_sql() -> dict[str, str]:
    sql_map: dict[str, str] = {}

    for endpoint_name, endpoint_config in ENDPOINTS.items():
        table_name = endpoint_config["table"]
        schema = endpoint_config["schema"]
        mode = endpoint_config["mode"]

        columns_sql = build_columns_sql(schema)

        if mode == "snapshot":
            sql_map[endpoint_name] = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {columns_sql}
            );
            """

        elif mode == "timeseries":
            primary_key = endpoint_config.get("primary_key", [])
            primary_key_sql = build_primary_key_sql(primary_key)

            sql_map[endpoint_name] = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {columns_sql}
                {primary_key_sql}
            );
            """

    return sql_map


# ------------------------------------------------------------
# SQL DE CRÉATION DES INDEX
# ------------------------------------------------------------

def get_index_sql() -> list[str]:
    sql_list = [
        # ----------------------------------------------------
        # INDEX TABLES TECHNIQUES
        # ----------------------------------------------------

        f"""
        CREATE INDEX IF NOT EXISTS idx_api_ids_endpoint
        ON {TABLES["api_ids"]}(endpoint);
        """,

        f"""
        CREATE INDEX IF NOT EXISTS idx_api_ids_active
        ON {TABLES["api_ids"]}(is_active);
        """,

        f"""
        CREATE INDEX IF NOT EXISTS idx_api_ids_endpoint_active
        ON {TABLES["api_ids"]}(endpoint, is_active);
        """,

        f"""
        CREATE INDEX IF NOT EXISTS idx_api_raw_endpoint
        ON {TABLES["api_raw"]}(endpoint);
        """,

        f"""
        CREATE INDEX IF NOT EXISTS idx_api_raw_locale
        ON {TABLES["api_raw"]}(locale);
        """,

        f"""
        CREATE INDEX IF NOT EXISTS idx_api_raw_hash
        ON {TABLES["api_raw"]}(content_hash);
        """,

        f"""
        CREATE INDEX IF NOT EXISTS idx_api_raw_endpoint_locale
        ON {TABLES["api_raw"]}(endpoint, locale);
        """,

        f"""
        CREATE INDEX IF NOT EXISTS idx_api_index_hash
        ON {TABLES["api_index"]}(content_hash);
        """,

        f"""
        CREATE INDEX IF NOT EXISTS idx_api_index_endpoint
        ON {TABLES["api_index"]}(endpoint);
        """,

        f"""
        CREATE INDEX IF NOT EXISTS idx_api_index_endpoint_locale
        ON {TABLES["api_index"]}(endpoint, locale);
        """,

        f"""
        CREATE INDEX IF NOT EXISTS idx_api_history_endpoint
        ON {TABLES["api_history"]}(endpoint);
        """,

        f"""
        CREATE INDEX IF NOT EXISTS idx_api_history_entity_id
        ON {TABLES["api_history"]}(entity_id);
        """,

        f"""
        CREATE INDEX IF NOT EXISTS idx_api_history_changed_at
        ON {TABLES["api_history"]}(changed_at);
        """,

        f"""
        CREATE INDEX IF NOT EXISTS idx_sync_log_endpoint
        ON {TABLES["sync_log"]}(endpoint);
        """,

        f"""
        CREATE INDEX IF NOT EXISTS idx_sync_log_status
        ON {TABLES["sync_log"]}(status);
        """,
    ]

    for endpoint_name, endpoint_config in ENDPOINTS.items():
        table_name = endpoint_config["table"]
        indexes = endpoint_config.get("indexes", [])

        for columns in indexes:
            index_name = f"idx_{endpoint_name}_" + "_".join(columns)
            joined_columns = ", ".join(columns)

            sql_list.append(f"""
            CREATE INDEX IF NOT EXISTS {index_name}
            ON {table_name}({joined_columns});
            """)

    return sql_list


# ------------------------------------------------------------
# CRÉATION DES TABLES
# ------------------------------------------------------------

def create_tables(conn: sqlite3.Connection) -> None:
    for table_key, sql in get_technical_table_sql().items():
        conn.execute(sql)

        if DEBUG:
            print(f"Table technique créée ou déjà existante : {table_key}")

    for table_key, sql in get_endpoint_table_sql().items():
        conn.execute(sql)

        if DEBUG:
            print(f"Table endpoint créée ou déjà existante : {table_key}")


# ------------------------------------------------------------
# CRÉATION DES INDEX
# ------------------------------------------------------------

def create_indexes(conn: sqlite3.Connection) -> None:
    for sql in get_index_sql():
        conn.execute(sql)

    if DEBUG:
        print("Index créés ou déjà existants.")


# ------------------------------------------------------------
# FONCTION PRINCIPALE
# ------------------------------------------------------------

def main() -> None:
    validate_endpoints_config()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")

        create_tables(conn)
        create_indexes(conn)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    print(f"Base initialisée avec succès [{loaded_env}] : {DB_PATH}")


# ------------------------------------------------------------
# LANCEMENT DU SCRIPT
# ------------------------------------------------------------

if __name__ == "__main__":
    main()