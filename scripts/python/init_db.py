# ============================================================
# Projet      : GW2 Command Center
# Fichier     : scripts/python/init_db.py
# Rôle        : Initialisation de la base SQLite du projet
# Auteur      : William CROCHOT (MisterWalky)
# Référence   : https://github.com/MisterWalky/gw2-command-center
# Licence     : MIT
# ============================================================
#
# DESCRIPTION
# -----------
# Ce script initialise une base SQLite du projet.
#
# Il permet de créer :
# - les tables techniques
# - les tables métier des endpoints
# - les tables i18n associées si nécessaire
# - les index techniques et métier
#
# ENVIRONNEMENTS
# --------------
# Le script peut cibler :
# - la base TEST
# - la base PROD
#
# Utilisation :
#   py scripts/python/init_db.py test
#   py scripts/python/init_db.py prod
# ============================================================

from __future__ import annotations

import json
import sqlite3
import sys
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

# ============================================================
# CONSTANTES
# ============================================================

REFERENCE_LANG = "en"
ALLOWED_ENVS = {"test", "prod"}
ALLOWED_MODES = {"snapshot", "timeseries"}

REQUIRED_ENDPOINT_KEYS = {
    "path",
    "localized",
    "mode",
    "table",
    "schema",
}

UI_NAMESPACE = "INIT_DB_UI"

UI_DEFAULTS = {
    "SUCCESS": "Database initialized successfully",
    "INVALID_ENV": "Invalid environment requested, fallback to TEST",
    "TECH_TABLE_CREATED": "Technical table created or already exists",
    "ENDPOINT_TABLE_CREATED": "Endpoint table created or already exists",
    "I18N_TABLE_CREATED": "I18N table created or already exists",
    "INDEXES_CREATED": "Indexes created or already exist",
    "ERROR_ENDPOINTS_EMPTY": "ENDPOINTS must be a non-empty dictionary",
    "ERROR_ENDPOINT_NOT_DICT": "Endpoint configuration must be a dictionary",
    "ERROR_ENDPOINT_INCOMPLETE": "Endpoint configuration is incomplete",
    "ERROR_MISSING_KEYS": "Missing keys",
    "ERROR_INVALID_MODE": "Endpoint has an invalid mode",
    "ERROR_ALLOWED_VALUES": "Allowed values",
    "ERROR_LOCALIZED_BOOL": "Endpoint must define localized as True or False",
    "ERROR_INVALID_TABLE": "Endpoint must define a valid table name",
    "ERROR_INVALID_SCHEMA": "Endpoint must define a non-empty schema",
    "ERROR_INVALID_INDEXES": "Endpoint must define indexes as a list",
    "ERROR_INVALID_INDEX": "Endpoint has an invalid index",
    "ERROR_UNKNOWN_SCHEMA_COLUMN_INDEX": "Index references an unknown schema column",
    "ERROR_MISSING_PRIMARY_KEY": "Timeseries endpoint must define primary_key",
    "ERROR_INVALID_PRIMARY_KEY": "Endpoint must define primary_key as a list",
    "ERROR_UNKNOWN_SCHEMA_COLUMN_PRIMARY_KEY": "Primary key references an unknown schema column",
    "ERROR_MISSING_I18N_TABLE": "Localized endpoint must define i18n_table",
    "ERROR_INVALID_I18N_SCHEMA": "Localized endpoint must define a non-empty i18n_schema",
    "ERROR_MISSING_I18N_PRIMARY_KEY": "Localized endpoint must define i18n_primary_key",
    "ERROR_UNKNOWN_I18N_SCHEMA_COLUMN_PRIMARY_KEY": "I18N primary key references an unknown i18n_schema column",
    "ERROR_INVALID_I18N_INDEXES": "Endpoint must define i18n_indexes as a list",
    "ERROR_INVALID_I18N_INDEX": "Endpoint has an invalid i18n index",
    "ERROR_UNKNOWN_I18N_SCHEMA_COLUMN_INDEX": "I18N index references an unknown i18n_schema column",
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
# CHARGEMENT DE LA CONFIGURATION
# ============================================================


def resolve_target_env(argv: list[str]) -> str:
    """
    Détermine l'environnement cible à partir des arguments.
    """
    if argv:
        requested = argv[0].strip().lower()
    else:
        requested = "test"

    if requested in ALLOWED_ENVS:
        return requested

    return "test"


def load_runtime_config(target_env: str) -> dict[str, Any]:
    """
    Charge la configuration adaptée à l'environnement demandé.
    """
    if target_env == "prod":
        from config.config_prod import DB_PATH, DEBUG, ENDPOINTS, TABLES

        return {
            "DB_PATH": DB_PATH,
            "DEBUG": DEBUG,
            "ENDPOINTS": ENDPOINTS,
            "TABLES": TABLES,
            "LOADED_ENV": "PROD",
        }

    from config.config_test import DB_PATH, DEBUG, ENDPOINTS, TABLES

    return {
        "DB_PATH": DB_PATH,
        "DEBUG": DEBUG,
        "ENDPOINTS": ENDPOINTS,
        "TABLES": TABLES,
        "LOADED_ENV": "TEST",
    }


# ============================================================
# OUTILS SQL
# ============================================================


def build_columns_sql(schema_dict: dict[str, str]) -> str:
    """
    Construit la déclaration SQL des colonnes.
    """
    sql_lines: list[str] = []

    for column_name, column_type in schema_dict.items():
        sql_lines.append(f"{column_name} {column_type}")

    return ",\n                ".join(sql_lines)


def build_primary_key_sql(columns: list[str]) -> str:
    """
    Construit la déclaration SQL d'une clé primaire composite.
    """
    if not columns:
        return ""

    joined_columns = ", ".join(columns)
    return f",\n                PRIMARY KEY ({joined_columns})"


# ============================================================
# VALIDATION DE LA CONFIGURATION DES ENDPOINTS
# ============================================================


def validate_endpoints_config(endpoints: dict[str, Any], ui_strings: dict[str, str]) -> None:
    """
    Valide la structure de configuration des endpoints.

    Les erreurs de validation remontent avec des messages
    localisables et un fallback anglais.
    """
    if not isinstance(endpoints, dict) or not endpoints:
        raise ValueError(
            ui(
                ui_strings,
                "ERROR_ENDPOINTS_EMPTY",
                "ENDPOINTS must be a non-empty dictionary",
            )
        )

    for endpoint_name, endpoint_config in endpoints.items():
        if not isinstance(endpoint_config, dict):
            raise ValueError(
                f"{ui(ui_strings, 'ERROR_ENDPOINT_NOT_DICT', 'Endpoint configuration must be a dictionary')} : "
                f"{endpoint_name}"
            )

        missing_keys = REQUIRED_ENDPOINT_KEYS - set(endpoint_config.keys())
        if missing_keys:
            raise ValueError(
                f"{ui(ui_strings, 'ERROR_ENDPOINT_INCOMPLETE', 'Endpoint configuration is incomplete')} : "
                f"{endpoint_name} | "
                f"{ui(ui_strings, 'ERROR_MISSING_KEYS', 'Missing keys')} : {sorted(missing_keys)}"
            )

        mode = endpoint_config["mode"]
        if mode not in ALLOWED_MODES:
            raise ValueError(
                f"{ui(ui_strings, 'ERROR_INVALID_MODE', 'Endpoint has an invalid mode')} : "
                f"{endpoint_name} -> {mode} | "
                f"{ui(ui_strings, 'ERROR_ALLOWED_VALUES', 'Allowed values')} : {sorted(ALLOWED_MODES)}"
            )

        localized = endpoint_config["localized"]
        if not isinstance(localized, bool):
            raise ValueError(
                f"{ui(ui_strings, 'ERROR_LOCALIZED_BOOL', 'Endpoint must define localized as True or False')} : "
                f"{endpoint_name}"
            )

        table_name = endpoint_config["table"]
        if not isinstance(table_name, str) or not table_name.strip():
            raise ValueError(
                f"{ui(ui_strings, 'ERROR_INVALID_TABLE', 'Endpoint must define a valid table name')} : "
                f"{endpoint_name}"
            )

        schema = endpoint_config["schema"]
        if not isinstance(schema, dict) or not schema:
            raise ValueError(
                f"{ui(ui_strings, 'ERROR_INVALID_SCHEMA', 'Endpoint must define a non-empty schema')} : "
                f"{endpoint_name}"
            )

        indexes = endpoint_config.get("indexes", [])
        if not isinstance(indexes, list):
            raise ValueError(
                f"{ui(ui_strings, 'ERROR_INVALID_INDEXES', 'Endpoint must define indexes as a list')} : "
                f"{endpoint_name}"
            )

        for index_columns in indexes:
            if not isinstance(index_columns, list) or not index_columns:
                raise ValueError(
                    f"{ui(ui_strings, 'ERROR_INVALID_INDEX', 'Endpoint has an invalid index')} : "
                    f"{endpoint_name} -> {index_columns}"
                )

            for column_name in index_columns:
                if column_name not in schema:
                    raise ValueError(
                        f"{ui(ui_strings, 'ERROR_UNKNOWN_SCHEMA_COLUMN_INDEX', 'Index references an unknown schema column')} : "
                        f"{endpoint_name} -> {column_name}"
                    )

        if mode == "timeseries":
            primary_key = endpoint_config.get("primary_key", [])

            if not primary_key:
                raise ValueError(
                    f"{ui(ui_strings, 'ERROR_MISSING_PRIMARY_KEY', 'Timeseries endpoint must define primary_key')} : "
                    f"{endpoint_name}"
                )

            if not isinstance(primary_key, list):
                raise ValueError(
                    f"{ui(ui_strings, 'ERROR_INVALID_PRIMARY_KEY', 'Endpoint must define primary_key as a list')} : "
                    f"{endpoint_name}"
                )

            for column_name in primary_key:
                if column_name not in schema:
                    raise ValueError(
                        f"{ui(ui_strings, 'ERROR_UNKNOWN_SCHEMA_COLUMN_PRIMARY_KEY', 'Primary key references an unknown schema column')} : "
                        f"{endpoint_name} -> {column_name}"
                    )

        if localized:
            i18n_table = endpoint_config.get("i18n_table")
            i18n_schema = endpoint_config.get("i18n_schema")
            i18n_primary_key = endpoint_config.get("i18n_primary_key", [])
            i18n_indexes = endpoint_config.get("i18n_indexes", [])

            if not isinstance(i18n_table, str) or not i18n_table.strip():
                raise ValueError(
                    f"{ui(ui_strings, 'ERROR_MISSING_I18N_TABLE', 'Localized endpoint must define i18n_table')} : "
                    f"{endpoint_name}"
                )

            if not isinstance(i18n_schema, dict) or not i18n_schema:
                raise ValueError(
                    f"{ui(ui_strings, 'ERROR_INVALID_I18N_SCHEMA', 'Localized endpoint must define a non-empty i18n_schema')} : "
                    f"{endpoint_name}"
                )

            if not isinstance(i18n_primary_key, list) or not i18n_primary_key:
                raise ValueError(
                    f"{ui(ui_strings, 'ERROR_MISSING_I18N_PRIMARY_KEY', 'Localized endpoint must define i18n_primary_key')} : "
                    f"{endpoint_name}"
                )

            for column_name in i18n_primary_key:
                if column_name not in i18n_schema:
                    raise ValueError(
                        f"{ui(ui_strings, 'ERROR_UNKNOWN_I18N_SCHEMA_COLUMN_PRIMARY_KEY', 'I18N primary key references an unknown i18n_schema column')} : "
                        f"{endpoint_name} -> {column_name}"
                    )

            if not isinstance(i18n_indexes, list):
                raise ValueError(
                    f"{ui(ui_strings, 'ERROR_INVALID_I18N_INDEXES', 'Endpoint must define i18n_indexes as a list')} : "
                    f"{endpoint_name}"
                )

            for index_columns in i18n_indexes:
                if not isinstance(index_columns, list) or not index_columns:
                    raise ValueError(
                        f"{ui(ui_strings, 'ERROR_INVALID_I18N_INDEX', 'Endpoint has an invalid i18n index')} : "
                        f"{endpoint_name} -> {index_columns}"
                    )

                for column_name in index_columns:
                    if column_name not in i18n_schema:
                        raise ValueError(
                            f"{ui(ui_strings, 'ERROR_UNKNOWN_I18N_SCHEMA_COLUMN_INDEX', 'I18N index references an unknown i18n_schema column')} : "
                            f"{endpoint_name} -> {column_name}"
                        )


# ============================================================
# SQL DE CRÉATION DES TABLES TECHNIQUES
# ============================================================


def get_technical_table_sql(tables: dict[str, str]) -> dict[str, str]:
    return {
        "api_ids": f"""
        CREATE TABLE IF NOT EXISTS {tables["api_ids"]} (
            endpoint TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (endpoint, entity_id)
        );
        """,
        "api_raw": f"""
        CREATE TABLE IF NOT EXISTS {tables["api_raw"]} (
            endpoint TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            locale TEXT,
            json_data TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            PRIMARY KEY (endpoint, entity_id, locale)
        );
        """,
        "api_index": f"""
        CREATE TABLE IF NOT EXISTS {tables["api_index"]} (
            endpoint TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            locale TEXT,
            content_hash TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            PRIMARY KEY (endpoint, entity_id, locale)
        );
        """,
        "api_history": f"""
        CREATE TABLE IF NOT EXISTS {tables["api_history"]} (
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
        "sync_log": f"""
        CREATE TABLE IF NOT EXISTS {tables["sync_log"]} (
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


# ============================================================
# SQL DE CRÉATION DES TABLES MÉTIER
# ============================================================


def get_endpoint_table_sql(endpoints: dict[str, Any]) -> dict[str, str]:
    sql_map: dict[str, str] = {}

    for endpoint_name, endpoint_config in endpoints.items():
        table_name = endpoint_config["table"]
        schema = endpoint_config["schema"]
        mode = endpoint_config["mode"]

        columns_sql = build_columns_sql(schema)

        if mode == "snapshot":
            sql_map[
                endpoint_name
            ] = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {columns_sql}
            );
            """
        elif mode == "timeseries":
            primary_key = endpoint_config.get("primary_key", [])
            primary_key_sql = build_primary_key_sql(primary_key)

            sql_map[
                endpoint_name
            ] = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {columns_sql}
                {primary_key_sql}
            );
            """

    return sql_map


def get_i18n_table_sql(endpoints: dict[str, Any]) -> dict[str, str]:
    """
    Construit le SQL des tables i18n pour les endpoints localisés.
    """
    sql_map: dict[str, str] = {}

    for endpoint_name, endpoint_config in endpoints.items():
        if not endpoint_config.get("localized", False):
            continue

        i18n_table = endpoint_config["i18n_table"]
        i18n_schema = endpoint_config["i18n_schema"]
        i18n_primary_key = endpoint_config["i18n_primary_key"]

        columns_sql = build_columns_sql(i18n_schema)
        primary_key_sql = build_primary_key_sql(i18n_primary_key)

        sql_map[
            f"{endpoint_name}_i18n"
        ] = f"""
        CREATE TABLE IF NOT EXISTS {i18n_table} (
            {columns_sql}
            {primary_key_sql}
        );
        """

    return sql_map


# ============================================================
# SQL DE CRÉATION DES INDEX
# ============================================================


def get_index_sql(tables: dict[str, str], endpoints: dict[str, Any]) -> list[str]:
    sql_list = [
        f"""
        CREATE INDEX IF NOT EXISTS idx_api_ids_endpoint
        ON {tables["api_ids"]}(endpoint);
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_api_ids_active
        ON {tables["api_ids"]}(is_active);
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_api_ids_endpoint_active
        ON {tables["api_ids"]}(endpoint, is_active);
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_api_raw_endpoint
        ON {tables["api_raw"]}(endpoint);
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_api_raw_locale
        ON {tables["api_raw"]}(locale);
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_api_raw_hash
        ON {tables["api_raw"]}(content_hash);
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_api_raw_endpoint_locale
        ON {tables["api_raw"]}(endpoint, locale);
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_api_index_hash
        ON {tables["api_index"]}(content_hash);
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_api_index_endpoint
        ON {tables["api_index"]}(endpoint);
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_api_index_endpoint_locale
        ON {tables["api_index"]}(endpoint, locale);
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_api_history_endpoint
        ON {tables["api_history"]}(endpoint);
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_api_history_entity_id
        ON {tables["api_history"]}(entity_id);
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_api_history_changed_at
        ON {tables["api_history"]}(changed_at);
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_sync_log_endpoint
        ON {tables["sync_log"]}(endpoint);
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_sync_log_status
        ON {tables["sync_log"]}(status);
        """,
    ]

    for endpoint_name, endpoint_config in endpoints.items():
        table_name = endpoint_config["table"]
        indexes = endpoint_config.get("indexes", [])

        for columns in indexes:
            index_name = f"idx_{endpoint_name}_" + "_".join(columns)
            joined_columns = ", ".join(columns)

            sql_list.append(
                f"""
            CREATE INDEX IF NOT EXISTS {index_name}
            ON {table_name}({joined_columns});
            """
            )

        if endpoint_config.get("localized", False):
            i18n_table = endpoint_config["i18n_table"]
            i18n_indexes = endpoint_config.get("i18n_indexes", [])

            for columns in i18n_indexes:
                index_name = f"idx_{endpoint_name}_i18n_" + "_".join(columns)
                joined_columns = ", ".join(columns)

                sql_list.append(
                    f"""
                CREATE INDEX IF NOT EXISTS {index_name}
                ON {i18n_table}({joined_columns});
                """
                )

    return sql_list


# ============================================================
# CRÉATION DES TABLES
# ============================================================


def create_tables(
    conn: sqlite3.Connection,
    tables: dict[str, str],
    endpoints: dict[str, Any],
    debug: bool,
    ui_strings: dict[str, str],
) -> None:
    for table_key, sql in get_technical_table_sql(tables).items():
        conn.execute(sql)

        if debug:
            print(
                f"{ui(ui_strings, 'TECH_TABLE_CREATED', 'Technical table created or already exists')} : "
                f"{table_key}"
            )

    for table_key, sql in get_endpoint_table_sql(endpoints).items():
        conn.execute(sql)

        if debug:
            print(
                f"{ui(ui_strings, 'ENDPOINT_TABLE_CREATED', 'Endpoint table created or already exists')} : "
                f"{table_key}"
            )

    for table_key, sql in get_i18n_table_sql(endpoints).items():
        conn.execute(sql)

        if debug:
            print(
                f"{ui(ui_strings, 'I18N_TABLE_CREATED', 'I18N table created or already exists')} : "
                f"{table_key}"
            )


def create_indexes(
    conn: sqlite3.Connection,
    tables: dict[str, str],
    endpoints: dict[str, Any],
    debug: bool,
    ui_strings: dict[str, str],
) -> None:
    for sql in get_index_sql(tables, endpoints):
        conn.execute(sql)

    if debug:
        print(ui(ui_strings, "INDEXES_CREATED", "Indexes created or already exist"))


# ============================================================
# FONCTION PRINCIPALE
# ============================================================


def main() -> None:
    ui_lang = APP_LANG if APP_LANG in SUPPORTED_APP_LANGS else REFERENCE_LANG
    ui_strings = load_ui_strings(ui_lang)

    requested_env = sys.argv[1].strip().lower() if len(sys.argv) > 1 else "test"
    target_env = resolve_target_env(sys.argv[1:])

    if requested_env != target_env:
        print(
            f"{ui(ui_strings, 'INVALID_ENV', 'Invalid environment requested, fallback to TEST')} : "
            f"{requested_env}"
        )

    runtime_config = load_runtime_config(target_env)

    db_path: Path = runtime_config["DB_PATH"]
    debug: bool = runtime_config["DEBUG"]
    tables: dict[str, str] = runtime_config["TABLES"]
    endpoints: dict[str, Any] = runtime_config["ENDPOINTS"]
    loaded_env: str = runtime_config["LOADED_ENV"]

    validate_endpoints_config(endpoints, ui_strings)

    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA foreign_keys=ON;")

            create_tables(conn, tables, endpoints, debug, ui_strings)
            create_indexes(conn, tables, endpoints, debug, ui_strings)

            conn.commit()

        except Exception:
            conn.rollback()
            raise

    print(
        f"{ui(ui_strings, 'SUCCESS', 'Database initialized successfully')} "
        f"[{loaded_env}] : {db_path}"
    )


if __name__ == "__main__":
    main()
