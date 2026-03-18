# ============================================================
# Projet      : GW2 Command Center
# Fichier     : scripts/python/sync_endpoint.py
# Rôle        : Synchronisation d'un endpoint GW2 API
# Auteur      : William CROCHOT (MisterWalky)
# Référence   : https://github.com/MisterWalky/gw2-command-center
# Licence     : MIT
# ============================================================
#
# DESCRIPTION
# -----------
# Ce script synchronise un endpoint unique défini dans ENDPOINTS.
#
# Il prend en charge :
# - les endpoints snapshot
# - les endpoints timeseries
# - les endpoints localisés
# - la journalisation dans les tables techniques
# - l'écriture dans les tables métier
#
# Utilisation :
#   py scripts/python/sync_endpoint.py test items
#   py scripts/python/sync_endpoint.py prod commerce_prices
# ============================================================

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
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

UI_NAMESPACE = "SYNC_ENDPOINT_UI"

UI_DEFAULTS = {
    "INVALID_ENV": "Invalid environment requested, fallback to TEST",
    "MISSING_ENDPOINT_ARG": "Missing endpoint argument",
    "UNKNOWN_ENDPOINT": "Unknown endpoint",
    "SYNC_TITLE": "GW2 endpoint synchronization",
    "ENVIRONMENT": "Environment",
    "ENDPOINT": "Endpoint",
    "MODE": "Mode",
    "LOCALIZED": "Localized",
    "API_LANGS": "API languages",
    "FETCHING_IDS": "Fetching IDs",
    "FETCHING_BATCH": "Fetching batch",
    "PROCESSING_LANG": "Processing language",
    "RECORDS_FETCHED": "Records fetched",
    "SYNC_SUCCESS": "Synchronization completed successfully",
    "SYNC_FAILED": "Synchronization failed",
    "SYNC_LOG_ID": "Sync log ID",
    "RECORDS_PROCESSED": "Records processed",
    "NO_IDS_FOUND": "No IDs found for this endpoint",
    "START_TIME": "Start time",
    "END_TIME": "End time",
    "STATUS_RUNNING": "running",
    "STATUS_SUCCESS": "success",
    "STATUS_FAILED": "failed",
    "YES": "yes",
    "NO": "no",
}

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

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
# CONFIGURATION RUNTIME
# ============================================================


def resolve_target_env(argv: list[str]) -> str:
    """
    Détermine l'environnement cible.
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
        from config.config_prod import (
            API_BASE,
            API_LANGS,
            BATCH_SIZE,
            DB_PATH,
            DEBUG,
            ENDPOINTS,
            GW2_API_KEY,
            HTTP_TIMEOUT,
            REQUEST_HEADERS,
            SLEEP_SEC,
            TABLES,
        )

        return {
            "API_LANGS": API_LANGS,
            "API_BASE": API_BASE,
            "BATCH_SIZE": BATCH_SIZE,
            "DB_PATH": DB_PATH,
            "DEBUG": DEBUG,
            "ENDPOINTS": ENDPOINTS,
            "GW2_API_KEY": GW2_API_KEY,
            "HTTP_TIMEOUT": HTTP_TIMEOUT,
            "REQUEST_HEADERS": REQUEST_HEADERS,
            "SLEEP_SEC": SLEEP_SEC,
            "TABLES": TABLES,
            "LOADED_ENV": "PROD",
        }

    from config.config_test import (
        API_BASE,
        API_LANGS,
        BATCH_SIZE,
        DB_PATH,
        DEBUG,
        ENDPOINTS,
        GW2_API_KEY,
        HTTP_TIMEOUT,
        REQUEST_HEADERS,
        SLEEP_SEC,
        TABLES,
    )

    return {
        "API_LANGS": API_LANGS,
        "API_BASE": API_BASE,
        "BATCH_SIZE": BATCH_SIZE,
        "DB_PATH": DB_PATH,
        "DEBUG": DEBUG,
        "ENDPOINTS": ENDPOINTS,
        "GW2_API_KEY": GW2_API_KEY,
        "HTTP_TIMEOUT": HTTP_TIMEOUT,
        "REQUEST_HEADERS": REQUEST_HEADERS,
        "SLEEP_SEC": SLEEP_SEC,
        "TABLES": TABLES,
        "LOADED_ENV": "TEST",
    }


# ============================================================
# OUTILS GÉNÉRAUX
# ============================================================


def now_str() -> str:
    """
    Retourne le timestamp courant formaté.
    """
    return datetime.now().strftime(TIMESTAMP_FORMAT)


def chunked(values: list[int], size: int) -> list[list[int]]:
    """
    Découpe une liste en sous-listes de taille donnée.
    """
    return [values[index : index + size] for index in range(0, len(values), size)]


def json_dumps_sorted(value: Any) -> str:
    """
    Sérialise un objet JSON de manière stable.
    """
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compute_hash(value: Any) -> str:
    """
    Calcule un hash SHA-256 stable pour un objet sérialisable.
    """
    payload = json_dumps_sorted(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ============================================================
# HTTP / API
# ============================================================


def build_request_headers(base_headers: dict[str, str], api_key: str | None) -> dict[str, str]:
    """
    Construit les en-têtes HTTP.
    """
    headers = dict(base_headers)

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    return headers


def api_get_json(
    api_base: str,
    endpoint_path: str,
    headers: dict[str, str],
    timeout: int,
    params: dict[str, str] | None = None,
) -> Any:
    """
    Exécute une requête GET JSON sur l'API GW2.
    """
    query = urllib.parse.urlencode(params or {})
    url = f"{api_base}{endpoint_path}"

    if query:
        url = f"{url}?{query}"

    request = urllib.request.Request(url=url, headers=headers, method="GET")

    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw)


def fetch_all_ids(
    api_base: str,
    endpoint_path: str,
    headers: dict[str, str],
    timeout: int,
) -> list[int]:
    """
    Récupère la liste complète des IDs d'un endpoint.
    """
    data = api_get_json(
        api_base=api_base,
        endpoint_path=endpoint_path,
        headers=headers,
        timeout=timeout,
        params=None,
    )

    if not isinstance(data, list):
        raise ValueError("Expected a list of IDs from endpoint root call.")

    ids: list[int] = []
    for value in data:
        if isinstance(value, int):
            ids.append(value)

    return ids


def fetch_records_batch(
    api_base: str,
    endpoint_path: str,
    headers: dict[str, str],
    timeout: int,
    ids_batch: list[int],
    lang: str | None = None,
) -> list[dict[str, Any]]:
    """
    Récupère un lot détaillé de records.
    """
    params: dict[str, str] = {
        "ids": ",".join(str(value) for value in ids_batch),
    }

    if lang:
        params["lang"] = lang

    data = api_get_json(
        api_base=api_base,
        endpoint_path=endpoint_path,
        headers=headers,
        timeout=timeout,
        params=params,
    )

    if not isinstance(data, list):
        raise ValueError("Expected a list of records from detailed endpoint call.")

    records: list[dict[str, Any]] = []
    for value in data:
        if isinstance(value, dict):
            records.append(value)

    return records


# ============================================================
# SYNC_LOG
# ============================================================


def insert_sync_log(
    conn: sqlite3.Connection,
    sync_log_table: str,
    endpoint_name: str,
    locale: str | None,
    start_time: str,
    status: str,
    message: str | None = None,
) -> int:
    """
    Insère une ligne de début de synchronisation.
    """
    cur = conn.execute(
        f"""
        INSERT INTO {sync_log_table} (
            endpoint,
            locale,
            start_time,
            status,
            message
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (endpoint_name, locale, start_time, status, message),
    )
    return int(cur.lastrowid)


def update_sync_log(
    conn: sqlite3.Connection,
    sync_log_table: str,
    sync_id: int,
    end_time: str,
    records_processed: int,
    status: str,
    message: str | None = None,
) -> None:
    """
    Met à jour la ligne de synchronisation.
    """
    conn.execute(
        f"""
        UPDATE {sync_log_table}
        SET end_time = ?,
            records_processed = ?,
            status = ?,
            message = ?
        WHERE sync_id = ?
        """,
        (end_time, records_processed, status, message, sync_id),
    )


# ============================================================
# TABLES TECHNIQUES
# ============================================================


def mark_api_ids(
    conn: sqlite3.Connection,
    api_ids_table: str,
    endpoint_name: str,
    current_ids: list[int],
    sync_time: str,
) -> None:
    """
    Met à jour API_IDS pour l'état courant des identifiants.
    """
    current_ids_str = [str(value) for value in current_ids]

    conn.execute(
        f"""
        UPDATE {api_ids_table}
        SET is_active = 0,
            last_seen_at = ?
        WHERE endpoint = ?
        """,
        (sync_time, endpoint_name),
    )

    for entity_id in current_ids_str:
        conn.execute(
            f"""
            INSERT INTO {api_ids_table} (
                endpoint,
                entity_id,
                first_seen_at,
                last_seen_at,
                is_active
            )
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(endpoint, entity_id)
            DO UPDATE SET
                last_seen_at = excluded.last_seen_at,
                is_active = 1
            """,
            (endpoint_name, entity_id, sync_time, sync_time),
        )


def upsert_api_raw(
    conn: sqlite3.Connection,
    api_raw_table: str,
    endpoint_name: str,
    entity_id: str,
    locale: str | None,
    record: dict[str, Any],
    content_hash: str,
    fetched_at: str,
) -> None:
    """
    Met à jour API_RAW.
    """
    conn.execute(
        f"""
        INSERT INTO {api_raw_table} (
            endpoint,
            entity_id,
            locale,
            json_data,
            content_hash,
            fetched_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(endpoint, entity_id, locale)
        DO UPDATE SET
            json_data = excluded.json_data,
            content_hash = excluded.content_hash,
            fetched_at = excluded.fetched_at
        """,
        (
            endpoint_name,
            entity_id,
            locale,
            json.dumps(record, ensure_ascii=False, indent=2),
            content_hash,
            fetched_at,
        ),
    )


def sync_api_index_and_history(
    conn: sqlite3.Connection,
    tables: dict[str, str],
    endpoint_name: str,
    entity_id: str,
    locale: str | None,
    record: dict[str, Any],
    content_hash: str,
    sync_time: str,
) -> None:
    """
    Met à jour API_INDEX et API_HISTORY.
    """
    api_index_table = tables["api_index"]
    api_history_table = tables["api_history"]

    row = conn.execute(
        f"""
        SELECT content_hash
        FROM {api_index_table}
        WHERE endpoint = ?
          AND entity_id = ?
          AND locale IS ?
        """,
        (endpoint_name, entity_id, locale),
    ).fetchone()

    old_hash = str(row[0]) if row is not None else None

    conn.execute(
        f"""
        INSERT INTO {api_index_table} (
            endpoint,
            entity_id,
            locale,
            content_hash,
            first_seen_at,
            last_seen_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(endpoint, entity_id, locale)
        DO UPDATE SET
            content_hash = excluded.content_hash,
            last_seen_at = excluded.last_seen_at
        """,
        (endpoint_name, entity_id, locale, content_hash, sync_time, sync_time),
    )

    if old_hash is None:
        conn.execute(
            f"""
            INSERT INTO {api_history_table} (
                endpoint,
                entity_id,
                locale,
                change_type,
                old_hash,
                new_hash,
                old_json_data,
                new_json_data,
                change_summary,
                changed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                endpoint_name,
                entity_id,
                locale,
                "created",
                None,
                content_hash,
                None,
                json.dumps(record, ensure_ascii=False, indent=2),
                "Initial record inserted",
                sync_time,
            ),
        )
    elif old_hash != content_hash:
        conn.execute(
            f"""
            INSERT INTO {api_history_table} (
                endpoint,
                entity_id,
                locale,
                change_type,
                old_hash,
                new_hash,
                old_json_data,
                new_json_data,
                change_summary,
                changed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                endpoint_name,
                entity_id,
                locale,
                "updated",
                old_hash,
                content_hash,
                None,
                json.dumps(record, ensure_ascii=False, indent=2),
                "Content hash changed",
                sync_time,
            ),
        )


# ============================================================
# TRANSFORMATIONS MÉTIER
# ============================================================


def normalize_items_main_row(record: dict[str, Any], sync_time: str) -> dict[str, Any]:
    """
    Transforme un item API en ligne métier principale.
    """
    details = record.get("details", {})
    details_type = details.get("type") if isinstance(details, dict) else None

    return {
        "id": record.get("id"),
        "type": record.get("type"),
        "level": record.get("level"),
        "rarity": record.get("rarity"),
        "vendor_value": record.get("vendor_value"),
        "chat_link": record.get("chat_link"),
        "icon": record.get("icon"),
        "details_type": details_type,
        "created_at": sync_time,
        "updated_at": sync_time,
    }


def normalize_items_i18n_row(record: dict[str, Any], lang: str, sync_time: str) -> dict[str, Any]:
    """
    Transforme un item API en ligne i18n.
    """
    return {
        "item_id": record.get("id"),
        "lang": lang,
        "name": record.get("name"),
        "description": record.get("description"),
        "updated_at": sync_time,
    }


def normalize_commerce_prices_row(record: dict[str, Any], observed_at: str) -> dict[str, Any]:
    """
    Transforme un record commerce_prices en ligne métier.
    """
    buy = record.get("buys", {})
    sell = record.get("sells", {})

    if not isinstance(buy, dict):
        buy = {}
    if not isinstance(sell, dict):
        sell = {}

    return {
        "observed_at": observed_at,
        "item_id": record.get("id"),
        "buy_quantity": buy.get("quantity"),
        "buy_unit_price": buy.get("unit_price"),
        "sell_quantity": sell.get("quantity"),
        "sell_unit_price": sell.get("unit_price"),
    }


# ============================================================
# ÉCRITURE MÉTIER
# ============================================================


def upsert_items_main(
    conn: sqlite3.Connection,
    table_name: str,
    row: dict[str, Any],
) -> None:
    """
    Upsert de la table métier ITEMS.
    """
    conn.execute(
        f"""
        INSERT INTO {table_name} (
            id,
            type,
            level,
            rarity,
            vendor_value,
            chat_link,
            icon,
            details_type,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id)
        DO UPDATE SET
            type = excluded.type,
            level = excluded.level,
            rarity = excluded.rarity,
            vendor_value = excluded.vendor_value,
            chat_link = excluded.chat_link,
            icon = excluded.icon,
            details_type = excluded.details_type,
            updated_at = excluded.updated_at
        """,
        (
            row["id"],
            row["type"],
            row["level"],
            row["rarity"],
            row["vendor_value"],
            row["chat_link"],
            row["icon"],
            row["details_type"],
            row["created_at"],
            row["updated_at"],
        ),
    )


def upsert_items_i18n(
    conn: sqlite3.Connection,
    table_name: str,
    row: dict[str, Any],
) -> None:
    """
    Upsert de la table métier ITEMS_I18N.
    """
    conn.execute(
        f"""
        INSERT INTO {table_name} (
            item_id,
            lang,
            name,
            description,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(item_id, lang)
        DO UPDATE SET
            name = excluded.name,
            description = excluded.description,
            updated_at = excluded.updated_at
        """,
        (
            row["item_id"],
            row["lang"],
            row["name"],
            row["description"],
            row["updated_at"],
        ),
    )


def insert_commerce_prices(
    conn: sqlite3.Connection,
    table_name: str,
    row: dict[str, Any],
) -> None:
    """
    Insert dans la table COMMERCE_PRICES_HISTORY.
    """
    conn.execute(
        f"""
        INSERT INTO {table_name} (
            observed_at,
            item_id,
            buy_quantity,
            buy_unit_price,
            sell_quantity,
            sell_unit_price
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            row["observed_at"],
            row["item_id"],
            row["buy_quantity"],
            row["buy_unit_price"],
            row["sell_quantity"],
            row["sell_unit_price"],
        ),
    )


# ============================================================
# PIPELINE PAR ENDPOINT
# ============================================================


def process_items_records(
    conn: sqlite3.Connection,
    endpoint_cfg: dict[str, Any],
    tables: dict[str, str],
    records: list[dict[str, Any]],
    lang: str,
    sync_time: str,
    write_main_table: bool,
) -> int:
    """
    Traite un lot de records items.
    """
    processed = 0
    main_table = endpoint_cfg["table"]
    i18n_table = endpoint_cfg["i18n_table"]

    for record in records:
        entity_id = str(record.get("id"))
        content_hash = compute_hash(record)

        upsert_api_raw(
            conn=conn,
            api_raw_table=tables["api_raw"],
            endpoint_name="items",
            entity_id=entity_id,
            locale=lang,
            record=record,
            content_hash=content_hash,
            fetched_at=sync_time,
        )

        sync_api_index_and_history(
            conn=conn,
            tables=tables,
            endpoint_name="items",
            entity_id=entity_id,
            locale=lang,
            record=record,
            content_hash=content_hash,
            sync_time=sync_time,
        )

        if write_main_table:
            upsert_items_main(
                conn=conn,
                table_name=main_table,
                row=normalize_items_main_row(record, sync_time),
            )

        upsert_items_i18n(
            conn=conn,
            table_name=i18n_table,
            row=normalize_items_i18n_row(record, lang, sync_time),
        )

        processed += 1

    return processed


def process_commerce_prices_records(
    conn: sqlite3.Connection,
    endpoint_cfg: dict[str, Any],
    tables: dict[str, str],
    records: list[dict[str, Any]],
    sync_time: str,
) -> int:
    """
    Traite un lot de records commerce_prices.
    """
    processed = 0
    table_name = endpoint_cfg["table"]

    for record in records:
        entity_id = str(record.get("id"))
        content_hash = compute_hash(record)

        upsert_api_raw(
            conn=conn,
            api_raw_table=tables["api_raw"],
            endpoint_name="commerce_prices",
            entity_id=entity_id,
            locale=None,
            record=record,
            content_hash=content_hash,
            fetched_at=sync_time,
        )

        sync_api_index_and_history(
            conn=conn,
            tables=tables,
            endpoint_name="commerce_prices",
            entity_id=entity_id,
            locale=None,
            record=record,
            content_hash=content_hash,
            sync_time=sync_time,
        )

        insert_commerce_prices(
            conn=conn,
            table_name=table_name,
            row=normalize_commerce_prices_row(record, sync_time),
        )

        processed += 1

    return processed


# ============================================================
# SYNCHRONISATION PRINCIPALE
# ============================================================


def sync_endpoint(
    conn: sqlite3.Connection,
    runtime_config: dict[str, Any],
    endpoint_name: str,
    endpoint_cfg: dict[str, Any],
    ui_strings: dict[str, str],
) -> int:
    """
    Exécute la synchronisation métier d'un endpoint.
    """
    api_base: str = runtime_config["API_BASE"]
    api_langs: list[str] = runtime_config["API_LANGS"]
    batch_size: int = runtime_config["BATCH_SIZE"]
    api_key: str | None = runtime_config["GW2_API_KEY"]
    timeout: int = runtime_config["HTTP_TIMEOUT"]
    base_headers: dict[str, str] = runtime_config["REQUEST_HEADERS"]
    sleep_sec: float = runtime_config["SLEEP_SEC"]
    tables: dict[str, str] = runtime_config["TABLES"]

    endpoint_path = endpoint_cfg["path"]
    mode = endpoint_cfg["mode"]
    localized = endpoint_cfg["localized"]

    headers = build_request_headers(base_headers, api_key)
    sync_time = now_str()

    print("============================================================")
    print(ui(ui_strings, "SYNC_TITLE", "GW2 endpoint synchronization"))
    print("============================================================")
    print(f"{ui(ui_strings, 'ENDPOINT', 'Endpoint')} : {endpoint_name}")
    print(f"{ui(ui_strings, 'MODE', 'Mode')} : {mode}")
    print(
        f"{ui(ui_strings, 'LOCALIZED', 'Localized')} : "
        f"{ui(ui_strings, 'YES', 'yes') if localized else ui(ui_strings, 'NO', 'no')}"
    )
    print(f"{ui(ui_strings, 'START_TIME', 'Start time')} : {sync_time}")

    if localized:
        print(f"{ui(ui_strings, 'API_LANGS', 'API languages')} : {', '.join(api_langs)}")

    print(f"{ui(ui_strings, 'FETCHING_IDS', 'Fetching IDs')}...")

    ids = fetch_all_ids(
        api_base=api_base,
        endpoint_path=endpoint_path,
        headers=headers,
        timeout=timeout,
    )

    if not ids:
        print(ui(ui_strings, "NO_IDS_FOUND", "No IDs found for this endpoint"))
        return 0

    mark_api_ids(
        conn=conn,
        api_ids_table=tables["api_ids"],
        endpoint_name=endpoint_name,
        current_ids=ids,
        sync_time=sync_time,
    )

    ids_batches = chunked(ids, batch_size)
    processed_total = 0

    if localized:
        primary_lang = api_langs[0]

        for lang in api_langs:
            print(f"{ui(ui_strings, 'PROCESSING_LANG', 'Processing language')} : {lang}")

            for batch_index, ids_batch in enumerate(ids_batches, start=1):
                print(
                    f"{ui(ui_strings, 'FETCHING_BATCH', 'Fetching batch')} "
                    f"{batch_index}/{len(ids_batches)}"
                )

                records = fetch_records_batch(
                    api_base=api_base,
                    endpoint_path=endpoint_path,
                    headers=headers,
                    timeout=timeout,
                    ids_batch=ids_batch,
                    lang=lang,
                )

                processed_total += process_items_records(
                    conn=conn,
                    endpoint_cfg=endpoint_cfg,
                    tables=tables,
                    records=records,
                    lang=lang,
                    sync_time=sync_time,
                    write_main_table=(lang == primary_lang),
                )

                if sleep_sec > 0:
                    time.sleep(sleep_sec)

    else:
        for batch_index, ids_batch in enumerate(ids_batches, start=1):
            print(
                f"{ui(ui_strings, 'FETCHING_BATCH', 'Fetching batch')} "
                f"{batch_index}/{len(ids_batches)}"
            )

            records = fetch_records_batch(
                api_base=api_base,
                endpoint_path=endpoint_path,
                headers=headers,
                timeout=timeout,
                ids_batch=ids_batch,
                lang=None,
            )

            if endpoint_name == "commerce_prices":
                processed_total += process_commerce_prices_records(
                    conn=conn,
                    endpoint_cfg=endpoint_cfg,
                    tables=tables,
                    records=records,
                    sync_time=sync_time,
                )
            else:
                raise ValueError(f"Unsupported non-localized endpoint: {endpoint_name}")

            if sleep_sec > 0:
                time.sleep(sleep_sec)

    print(f"{ui(ui_strings, 'RECORDS_PROCESSED', 'Records processed')} : {processed_total}")
    return processed_total


# ============================================================
# MAIN
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

    if len(sys.argv) < 3 or not sys.argv[2].strip():
        raise ValueError(ui(ui_strings, "MISSING_ENDPOINT_ARG", "Missing endpoint argument"))

    endpoint_name = sys.argv[2].strip()

    runtime_config = load_runtime_config(target_env)
    endpoints: dict[str, Any] = runtime_config["ENDPOINTS"]
    db_path: Path = runtime_config["DB_PATH"]
    tables: dict[str, str] = runtime_config["TABLES"]

    if endpoint_name not in endpoints:
        raise ValueError(
            f"{ui(ui_strings, 'UNKNOWN_ENDPOINT', 'Unknown endpoint')} : {endpoint_name}"
        )

    endpoint_cfg = endpoints[endpoint_name]

    db_path.parent.mkdir(parents=True, exist_ok=True)

    sync_time = now_str()
    sync_log_id = -1

    with sqlite3.connect(db_path) as conn:
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA foreign_keys=ON;")

            sync_log_id = insert_sync_log(
                conn=conn,
                sync_log_table=tables["sync_log"],
                endpoint_name=endpoint_name,
                locale=None,
                start_time=sync_time,
                status=ui(ui_strings, "STATUS_RUNNING", "running"),
                message=None,
            )

            print(f"{ui(ui_strings, 'SYNC_LOG_ID', 'Sync log ID')} : {sync_log_id}")

            processed_total = sync_endpoint(
                conn=conn,
                runtime_config=runtime_config,
                endpoint_name=endpoint_name,
                endpoint_cfg=endpoint_cfg,
                ui_strings=ui_strings,
            )

            update_sync_log(
                conn=conn,
                sync_log_table=tables["sync_log"],
                sync_id=sync_log_id,
                end_time=now_str(),
                records_processed=processed_total,
                status=ui(ui_strings, "STATUS_SUCCESS", "success"),
                message=None,
            )

            conn.commit()

            print(f"{ui(ui_strings, 'SYNC_SUCCESS', 'Synchronization completed successfully')}")
            print(f"{ui(ui_strings, 'END_TIME', 'End time')} : {now_str()}")

        except Exception as exc:
            conn.rollback()

            if sync_log_id != -1:
                try:
                    update_sync_log(
                        conn=conn,
                        sync_log_table=tables["sync_log"],
                        sync_id=sync_log_id,
                        end_time=now_str(),
                        records_processed=0,
                        status=ui(ui_strings, "STATUS_FAILED", "failed"),
                        message=str(exc),
                    )
                    conn.commit()
                except Exception:
                    pass

            print(f"{ui(ui_strings, 'SYNC_FAILED', 'Synchronization failed')} : {exc}")
            raise


if __name__ == "__main__":
    main()
