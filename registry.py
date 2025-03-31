# unibase/registry.py

import json
import os

REGISTRY_FILE = "registry.json"

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def save_registry(registry):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2)

def add_connection(db_type, connection):
    registry = load_registry()
    if db_type not in registry:
        registry[db_type] = []
    registry[db_type].append({
        "host": connection.host,
        "port": connection.port,
        "user": connection.user,
        "active": connection.active,
        "data": connection.data,
        "repr": str(connection)
    })
    save_registry(registry)

def get_connections(db_types=None):
    registry = load_registry()
    if db_types is None:
        return registry
    filtered = {}
    for db_type in db_types:
        if db_type in registry:
            filtered[db_type] = registry[db_type]
    return filtered

def remove_connection(db_type, connection):
    registry = load_registry()
    if db_type in registry:
        registry[db_type] = [conn for conn in registry[db_type] if conn["repr"] != str(connection)]
        save_registry(registry)

def update_connection(db_type, connection):
    """
    Update all entries for the given db_type that match the connection's host and user.
    This ensures that any changes (like new records or metadata) are persisted.
    """
    registry = load_registry()
    if db_type in registry:
        for idx, conn in enumerate(registry[db_type]):
            if conn["host"] == connection.host and conn["user"] == connection.user:
                registry[db_type][idx] = {
                    "host": connection.host,
                    "port": connection.port,
                    "user": connection.user,
                    "active": connection.active,
                    "data": connection.data,
                    "repr": str(connection)
                }
        save_registry(registry)

def clear_registry():
    """
    Clear the registry by writing an empty dictionary to the file.
    """
    save_registry({})
