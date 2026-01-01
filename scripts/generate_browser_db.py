#!/usr/bin/env python3
"""Generate a prebuilt SQLite database for browser mode with PLR definitions.

This script creates a complete SQLite database file that can be loaded directly
by the browser-mode SqliteService, containing:
1. Schema from SQLAlchemy ORM models
2. All PLR machine definitions (from PLR inspection)
3. All PLR resource definitions (from PLR inspection)
4. All PLR deck definitions (from PLR inspection)
5. Capability schemas for each machine type

Usage:
    uv run scripts/generate_browser_db.py

Output:
    praxis/web-client/src/assets/db/praxis.db
"""

from __future__ import annotations

import hashlib
import inspect
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_CLIENT_ROOT = PROJECT_ROOT / "praxis" / "web-client"
ASSETS_DB_DIR = WEB_CLIENT_ROOT / "src" / "assets" / "db"
SCHEMA_SQL_PATH = ASSETS_DB_DIR / "schema.sql"
OUTPUT_DB_PATH = ASSETS_DB_DIR / "praxis.db"


def generate_uuid_from_fqn(fqn: str) -> str:
    """Generate a deterministic UUID from a fully qualified name."""
    # Use MD5 to generate consistent UUIDs from FQN
    hash_bytes = hashlib.md5(fqn.encode()).digest()
    # Format as UUID (8-4-4-4-12)
    hex_str = hash_bytes.hex()
    return f"{hex_str[:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"


def is_json_serializable(val: Any) -> bool:
    """Check if a value is JSON serializable."""
    if val is None or isinstance(val, (str, int, float, bool)):
        return True
    if isinstance(val, (list, tuple)):
        return all(is_json_serializable(v) for v in val)
    if isinstance(val, dict):
        return all(isinstance(k, str) and is_json_serializable(v) for k, v in val.items())
    return False


def safe_json_dumps(obj: Any) -> str:
    """Safely serialize an object to JSON."""
    try:
        return json.dumps(obj)
    except (TypeError, ValueError):
        return "{}"


def extract_category(fqn: str, klass: type) -> str:
    """Determine the PLR category from class hierarchy."""
    from pylabrobot.machines.machine import Machine
    from pylabrobot.resources import Carrier, Deck, Plate, TipRack, Trough

    if issubclass(klass, TipRack):
        return "TipRack"
    if issubclass(klass, Plate):
        return "Plate"
    if issubclass(klass, Trough):
        return "Trough"
    if issubclass(klass, Carrier):
        return "Carrier"
    if issubclass(klass, Deck):
        return "Deck"
    if issubclass(klass, Machine):
        return "Machine"
    return "Resource"


def extract_vendor(fqn: str) -> str | None:
    """Extract vendor name from FQN."""
    match = re.search(r"pylabrobot\.resources\.(\w+)\.", fqn)
    if match:
        vendor = match.group(1)
        if vendor not in {"carrier", "plate", "tip_rack", "trough", "resource", "deck"}:
            return vendor.replace("_", " ").title()
    return None


def extract_properties(klass: type) -> dict[str, Any]:
    """Extract key properties from class definition."""
    from praxis.backend.utils.plr_inspection import get_constructor_params_with_defaults

    props = {}

    for attr in ["num_items", "size_x", "size_y", "size_z", "well_volume"]:
        try:
            class_attr = getattr(type(klass), attr, None)
            if isinstance(class_attr, property):
                continue
            val = getattr(klass, attr, None)
            if val is not None and not callable(val) and is_json_serializable(val):
                props[attr] = val
        except Exception:
            continue

    try:
        ctor_params = get_constructor_params_with_defaults(klass)
        for name, default in ctor_params.items():
            if default is not inspect.Parameter.empty and default is not None:
                if is_json_serializable(default):
                    props[name] = default
    except Exception:
        pass

    return props


def extract_dimensions(klass: type) -> dict[str, float | None]:
    """Extract dimension information from a class."""
    dims = {"size_x_mm": None, "size_y_mm": None, "size_z_mm": None}

    for attr, key in [("size_x", "size_x_mm"), ("size_y", "size_y_mm"), ("size_z", "size_z_mm")]:
        try:
            val = getattr(klass, attr, None)
            if val is not None and isinstance(val, (int, float)):
                dims[key] = float(val)
        except Exception:
            pass

    return dims


def discover_resources(conn: sqlite3.Connection) -> int:
    """Discover and insert all PLR resource definitions."""
    from praxis.backend.utils.plr_inspection import (
        get_all_carrier_classes,
        get_class_fqn,
        get_deck_classes,
        get_resource_classes,
    )

    resources = get_resource_classes(concrete_only=True)
    carriers = get_all_carrier_classes(concrete_only=True)
    decks = get_deck_classes(concrete_only=True)

    all_classes = {**resources, **carriers, **decks}

    now = datetime.now().isoformat()
    count = 0

    for fqn, klass in all_classes.items():
        try:
            category = extract_category(fqn, klass)
            vendor = extract_vendor(fqn)
            props = extract_properties(klass)
            dims = extract_dimensions(klass)

            accession_id = generate_uuid_from_fqn(fqn)

            # Insert into resource_definition_catalog
            conn.execute(
                """
                INSERT OR REPLACE INTO resource_definition_catalog (
                    accession_id, fqn, name, description, plr_category,
                    is_consumable, vendor,
                    size_x_mm, size_y_mm, size_z_mm,
                    properties_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    accession_id,
                    fqn,
                    klass.__name__,
                    inspect.getdoc(klass) or "",
                    category,
                    category in ["TipRack", "Plate"],
                    vendor,
                    dims["size_x_mm"],
                    dims["size_y_mm"],
                    dims["size_z_mm"],
                    safe_json_dumps(props),
                    now,
                    now,
                ),
            )
            count += 1
        except Exception as e:
            print(f"  Warning: Could not process resource {fqn}: {e}")

    conn.commit()
    return count


def discover_machines(conn: sqlite3.Connection) -> int:
    """Discover and insert all PLR machine definitions."""
    from praxis.backend.utils.plr_inspection import get_class_fqn, get_machine_classes

    machines = get_machine_classes(concrete_only=True)

    now = datetime.now().isoformat()
    count = 0

    for fqn, klass in machines.items():
        try:
            props = extract_properties(klass)
            dims = extract_dimensions(klass)
            has_deck = hasattr(klass, "deck") or "deck" in str(inspect.signature(klass.__init__))

            accession_id = generate_uuid_from_fqn(f"machine:{fqn}")

            # Determine machine category
            category = "Unknown"
            lower_name = klass.__name__.lower()
            if "liquidhandler" in lower_name or "star" in lower_name or "ot2" in lower_name:
                category = "LiquidHandler"
            elif "reader" in lower_name:
                category = "PlateReader"
            elif "shaker" in lower_name:
                category = "Shaker"
            elif "centrifuge" in lower_name:
                category = "Centrifuge"
            elif "incubator" in lower_name:
                category = "Incubator"

            # Insert into machine_definition_catalog
            conn.execute(
                """
                INSERT OR REPLACE INTO machine_definition_catalog (
                    accession_id, fqn, name, description, plr_category,
                    machine_category, has_deck,
                    size_x_mm, size_y_mm, size_z_mm,
                    properties_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    accession_id,
                    fqn,
                    klass.__name__,
                    inspect.getdoc(klass) or "",
                    "Machine",
                    category,
                    1 if has_deck else 0,
                    dims["size_x_mm"],
                    dims["size_y_mm"],
                    dims["size_z_mm"],
                    safe_json_dumps(props),
                    now,
                    now,
                ),
            )
            count += 1
        except Exception as e:
            print(f"  Warning: Could not process machine {fqn}: {e}")

    conn.commit()
    return count


def discover_decks(conn: sqlite3.Connection) -> int:
    """Discover and insert all PLR deck definitions."""
    from praxis.backend.utils.plr_inspection import get_class_fqn, get_deck_classes

    decks = get_deck_classes(concrete_only=True)

    now = datetime.now().isoformat()
    count = 0

    for fqn, klass in decks.items():
        try:
            props = extract_properties(klass)
            dims = extract_dimensions(klass)

            accession_id = generate_uuid_from_fqn(f"deck:{fqn}")

            # Insert into deck_definition_catalog
            conn.execute(
                """
                INSERT OR REPLACE INTO deck_definition_catalog (
                    accession_id, fqn, name, description, plr_category,
                    default_size_x_mm, default_size_y_mm, default_size_z_mm,
                    additional_properties_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    accession_id,
                    fqn,
                    klass.__name__,
                    inspect.getdoc(klass) or "",
                    "Deck",
                    dims["size_x_mm"],
                    dims["size_y_mm"],
                    dims["size_z_mm"],
                    safe_json_dumps(props),
                    now,
                    now,
                ),
            )
            count += 1
        except Exception as e:
            print(f"  Warning: Could not process deck {fqn}: {e}")

    conn.commit()
    return count


def insert_metadata(conn: sqlite3.Connection) -> None:
    """Insert metadata about the database generation."""
    now = datetime.now().isoformat()

    conn.execute(
        "INSERT OR REPLACE INTO _schema_metadata (key, value) VALUES (?, ?)",
        ("generated_at", now),
    )
    conn.execute(
        "INSERT OR REPLACE INTO _schema_metadata (key, value) VALUES (?, ?)",
        ("schema_version", "1.0.0"),
    )
    conn.execute(
        "INSERT OR REPLACE INTO _schema_metadata (key, value) VALUES (?, ?)",
        ("generator", "generate_browser_db.py"),
    )
    conn.commit()


def add_sample_workcell(conn: sqlite3.Connection) -> None:
    """Add a sample workcell for demo purposes."""
    now = datetime.now().isoformat()
    workcell_id = str(uuid4())

    conn.execute(
        """
        INSERT OR REPLACE INTO workcells (
            accession_id, name, description, physical_location, status,
            created_at, updated_at, properties_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            workcell_id,
            "Demo Workcell",
            "A sample workcell for browser-mode demonstration",
            "Virtual Lab 1",
            "available",
            now,
            now,
            "{}",
        ),
    )
    conn.commit()
    print(f"  Added sample workcell: Demo Workcell")


def main() -> None:
    """Main entry point for database generation."""
    print("Generating browser database with PLR definitions...")

    # Ensure output directory exists
    ASSETS_DB_DIR.mkdir(parents=True, exist_ok=True)

    # Check for schema file
    if not SCHEMA_SQL_PATH.exists():
        print(f"Schema file not found at {SCHEMA_SQL_PATH}")
        print("Run 'uv run scripts/generate_browser_schema.py' first")
        return

    # Remove existing database
    if OUTPUT_DB_PATH.exists():
        OUTPUT_DB_PATH.unlink()
        print(f"Removed existing database at {OUTPUT_DB_PATH}")

    # Create new database
    print(f"Creating database at {OUTPUT_DB_PATH}")
    conn = sqlite3.connect(OUTPUT_DB_PATH)

    try:
        # Load and execute schema
        print("Loading schema from schema.sql...")
        schema = SCHEMA_SQL_PATH.read_text()
        conn.executescript(schema)
        print("  Schema applied successfully")

        # Discover and insert PLR definitions
        print("\nDiscovering PLR resource definitions...")
        resource_count = discover_resources(conn)
        print(f"  Inserted {resource_count} resource definitions")

        print("\nDiscovering PLR machine definitions...")
        machine_count = discover_machines(conn)
        print(f"  Inserted {machine_count} machine definitions")

        print("\nDiscovering PLR deck definitions...")
        deck_count = discover_decks(conn)
        print(f"  Inserted {deck_count} deck definitions")

        # Add sample workcell
        print("\nAdding sample data...")
        add_sample_workcell(conn)

        # Update metadata
        insert_metadata(conn)

        # Get database size
        conn.commit()
        db_size = OUTPUT_DB_PATH.stat().st_size

        print(f"\n{'=' * 50}")
        print("Database generation complete!")
        print(f"{'=' * 50}")
        print(f"Output: {OUTPUT_DB_PATH}")
        print(f"Size: {db_size / 1024:.1f} KB")
        print(f"\nContents:")
        print(f"  - Resource definitions: {resource_count}")
        print(f"  - Machine definitions: {machine_count}")
        print(f"  - Deck definitions: {deck_count}")

        # Show table statistics
        print("\nTable row counts:")
        cursor = conn.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '_%'
            ORDER BY name
            """
        )
        for (table_name,) in cursor.fetchall():
            count_cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = count_cursor.fetchone()[0]
            if count > 0:
                print(f"  {table_name}: {count} rows")

    except Exception as e:
        print(f"Error generating database: {e}")
        raise
    finally:
        conn.close()

    print("\nDone!")


if __name__ == "__main__":
    main()
