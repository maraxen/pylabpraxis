#!/usr/bin/env python3
"""Generate a prebuilt SQLite database for browser mode with PLR definitions.

This script creates a complete SQLite database file that can be loaded directly
by the browser-mode SqliteService, containing:
1. Schema from SQLAlchemy ORM models
2. All PLR machine definitions (from LibCST static analysis)
3. All PLR resource definitions (from LibCST static analysis)
4. All PLR deck definitions (from LibCST static analysis)

Uses PLRSourceParser (LibCST-based) for static analysis without runtime imports,
avoiding deprecation warnings and side effects.

Usage:
    uv run scripts/generate_browser_db.py

Output:
    praxis/web-client/src/assets/db/praxis.db
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_CLIENT_ROOT = PROJECT_ROOT / "praxis" / "web-client"
ASSETS_DB_DIR = WEB_CLIENT_ROOT / "src" / "assets" / "db"
SCHEMA_SQL_PATH = ASSETS_DB_DIR / "schema.sql"
OUTPUT_DB_PATH = ASSETS_DB_DIR / "praxis.db"


def generate_uuid_from_fqn(fqn: str) -> str:
    """Generate a deterministic UUID from a fully qualified name."""
    hash_bytes = hashlib.md5(fqn.encode()).digest()
    hex_str = hash_bytes.hex()
    return f"{hex_str[:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"


def safe_json_dumps(obj: object) -> str:
    """Safely serialize an object to JSON."""
    try:
        return json.dumps(obj)
    except (TypeError, ValueError):
        return "{}"


def discover_resources_static(conn: sqlite3.Connection) -> int:
    """Discover and insert all PLR resource definitions using static analysis."""
    from praxis.backend.utils.plr_static_analysis import (
        PLRSourceParser,
        find_plr_source_root,
    )

    parser = PLRSourceParser(find_plr_source_root())

    # Get class-based resources
    class_resources = parser.discover_resource_classes()

    # Get factory function-based resources
    factory_resources = parser.discover_resource_factories()

    # Combine and deduplicate by FQN
    all_resources = {r.fqn: r for r in class_resources}
    for r in factory_resources:
        if r.fqn not in all_resources:
            all_resources[r.fqn] = r


    now = datetime.now().isoformat()
    count = 0

    for res in all_resources.values():
        try:
            accession_id = generate_uuid_from_fqn(res.fqn)

            # Determine category
            category = res.category or res.class_type.value

            # Extract capabilities as properties
            props = {}
            if res.capabilities:
                if res.capabilities.channels:
                    props["channels"] = res.capabilities.channels
                if res.capabilities.modules:
                    props["modules"] = res.capabilities.modules

            conn.execute(
                """
                INSERT OR REPLACE INTO resource_definition_catalog (
                    accession_id, fqn, name, description, plr_category,
                    is_consumable, vendor, manufacturer,
                    properties_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    accession_id,
                    res.fqn,
                    res.name,
                    res.docstring or "",
                    category,
                    category in ["TipRack", "Plate", "Trough"],
                    res.vendor,
                    res.manufacturer,
                    safe_json_dumps(props),
                    now,
                    now,
                ),
            )
            count += 1
        except Exception:
            pass

    conn.commit()
    return count


def discover_machines_static(conn: sqlite3.Connection) -> int:
    """Discover and insert all PLR machine definitions using static analysis."""
    from praxis.backend.utils.plr_static_analysis import (
        MACHINE_FRONTEND_TYPES,
        PLRClassType,
        PLRSourceParser,
        find_plr_source_root,
    )

    parser = PLRSourceParser(find_plr_source_root())
    machines = parser.discover_machine_classes()

    now = datetime.now().isoformat()
    count = 0

    # Filter to frontend types only (exclude backends for the definition catalog)
    frontend_machines = [m for m in machines if m.class_type in MACHINE_FRONTEND_TYPES]

    for machine in frontend_machines:
        try:
            from praxis.backend.models.pydantic_internals.maintenance import MAINTENANCE_DEFAULTS

            accession_id = generate_uuid_from_fqn(f"machine:{machine.fqn}")

            # Determine machine category from class type
            category_map = {
                PLRClassType.LIQUID_HANDLER: "LiquidHandler",
                PLRClassType.PLATE_READER: "PlateReader",
                PLRClassType.HEATER_SHAKER: "HeaterShaker",
                PLRClassType.SHAKER: "Shaker",
                PLRClassType.TEMPERATURE_CONTROLLER: "TemperatureController",
                PLRClassType.CENTRIFUGE: "Centrifuge",
                PLRClassType.THERMOCYCLER: "Thermocycler",
                PLRClassType.PUMP: "Pump",
                PLRClassType.PUMP_ARRAY: "PumpArray",
                PLRClassType.FAN: "Fan",
                PLRClassType.SEALER: "Sealer",
                PLRClassType.PEELER: "Peeler",
                PLRClassType.POWDER_DISPENSER: "PowderDispenser",
                PLRClassType.INCUBATOR: "Incubator",
                PLRClassType.SCARA: "Arm",
            }
            category = category_map.get(machine.class_type, "Unknown")
            
            # Get default maintenance schedule
            maintenance_schedule = MAINTENANCE_DEFAULTS.get(category, MAINTENANCE_DEFAULTS["DEFAULT"]).model_dump()


            # Check if has deck (liquid handlers typically have decks)
            has_deck = machine.class_type == PLRClassType.LIQUID_HANDLER

            # Get capabilities dict
            caps_dict = machine.to_capabilities_dict() if hasattr(machine, "to_capabilities_dict") else {}

            conn.execute(
                """
                INSERT OR REPLACE INTO machine_definition_catalog (
                    accession_id, fqn, name, description, plr_category,
                    machine_category, has_deck, manufacturer,
                    capabilities, compatible_backends, properties_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    accession_id,
                    machine.fqn,
                    machine.name,
                    machine.docstring or "",
                    "Machine",
                    category,
                    1 if has_deck else 0,
                    machine.manufacturer,
                    safe_json_dumps(caps_dict),
                    safe_json_dumps(machine.compatible_backends),
                    safe_json_dumps({}),
                    now,
                    now,
                ),
            )
            
            # Seed a sample instance for this definition to demo maintenance
            instance_id = generate_uuid_from_fqn(f"instance:{machine.fqn}")
            conn.execute(
                """
                INSERT OR REPLACE INTO machines (
                    accession_id, name, status, machine_definition_accession_id, 
                    created_at, updated_at, maintenance_enabled, maintenance_schedule_json, 
                    location_label
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    instance_id,
                    f"Demo {machine.name}",
                    "available",
                    accession_id,
                    now,
                    now,
                    1,
                    safe_json_dumps(maintenance_schedule),
                    "Main Lab, Bench 1"
                )
            )

            count += 1
        except Exception:
            pass

    conn.commit()
    return count


def discover_decks_static(conn: sqlite3.Connection) -> int:
    """Discover and insert all PLR deck definitions using static analysis."""
    from praxis.backend.utils.plr_static_analysis import (
        PLRClassType,
        PLRSourceParser,
        find_plr_source_root,
    )

    parser = PLRSourceParser(find_plr_source_root())
    all_resources = parser.discover_resource_classes()

    # Filter to deck classes only
    decks = [r for r in all_resources if r.class_type == PLRClassType.DECK]

    now = datetime.now().isoformat()
    count = 0

    for deck in decks:
        try:
            accession_id = generate_uuid_from_fqn(f"deck:{deck.fqn}")

            conn.execute(
                """
                INSERT OR REPLACE INTO deck_definition_catalog (
                    accession_id, fqn, name, description, plr_category,
                    additional_properties_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    accession_id,
                    deck.fqn,
                    deck.name,
                    deck.docstring or "",
                    "Deck",
                    safe_json_dumps({"manufacturer": deck.manufacturer, "vendor": deck.vendor}),
                    now,
                    now,
                ),
            )
            count += 1
        except Exception:
            pass

    conn.commit()
    return count


def discover_backends_static(conn: sqlite3.Connection) -> int:
    """Discover and insert all PLR backend definitions using static analysis."""
    from praxis.backend.utils.plr_static_analysis import (
        MACHINE_BACKEND_TYPES,
        PLRClassType,
        PLRSourceParser,
        find_plr_source_root,
    )

    parser = PLRSourceParser(find_plr_source_root())
    machines = parser.discover_machine_classes()

    # Filter to backend types only
    backends = [m for m in machines if m.class_type in MACHINE_BACKEND_TYPES]

    now = datetime.now().isoformat()
    count = 0

    # Map backend types to frontend category names
    backend_category_map = {
        PLRClassType.LH_BACKEND: "LiquidHandlerBackend",
        PLRClassType.PR_BACKEND: "PlateReaderBackend",
        PLRClassType.HS_BACKEND: "HeaterShakerBackend",
        PLRClassType.SHAKER_BACKEND: "ShakerBackend",
        PLRClassType.TEMP_BACKEND: "TemperatureControllerBackend",
        PLRClassType.CENTRIFUGE_BACKEND: "CentrifugeBackend",
        PLRClassType.THERMOCYCLER_BACKEND: "ThermocyclerBackend",
        PLRClassType.PUMP_BACKEND: "PumpBackend",
        PLRClassType.PUMP_ARRAY_BACKEND: "PumpArrayBackend",
        PLRClassType.FAN_BACKEND: "FanBackend",
        PLRClassType.SEALER_BACKEND: "SealerBackend",
        PLRClassType.PEELER_BACKEND: "PeelerBackend",
        PLRClassType.POWDER_DISPENSER_BACKEND: "PowderDispenserBackend",
        PLRClassType.INCUBATOR_BACKEND: "IncubatorBackend",
        PLRClassType.SCARA_BACKEND: "ScaraBackend",
    }

    for backend in backends:
        try:
            accession_id = generate_uuid_from_fqn(f"backend:{backend.fqn}")
            category = backend_category_map.get(backend.class_type, "UnknownBackend")

            # Get capabilities dict
            caps_dict = backend.to_capabilities_dict() if hasattr(backend, "to_capabilities_dict") else {}

            conn.execute(
                """
                INSERT OR REPLACE INTO machine_definition_catalog (
                    accession_id, fqn, name, description, plr_category,
                    machine_category, has_deck, manufacturer,
                    capabilities, compatible_backends, properties_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    accession_id,
                    backend.fqn,
                    backend.name,
                    backend.docstring or "",
                    "Backend",
                    category,
                    0,  # backends don't have decks
                    backend.manufacturer,
                    safe_json_dumps(caps_dict),
                    safe_json_dumps([]),  # backends don't have compatible_backends
                    safe_json_dumps({}),
                    now,
                    now,
                ),
            )
            count += 1
        except Exception:
            pass

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
        ("generator", "generate_browser_db.py (LibCST static analysis)"),
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


def main() -> None:
    """Main entry point for database generation."""
    # Ensure output directory exists
    ASSETS_DB_DIR.mkdir(parents=True, exist_ok=True)

    # Check for schema file
    if not SCHEMA_SQL_PATH.exists():
        return

    # Remove existing database
    if OUTPUT_DB_PATH.exists():
        OUTPUT_DB_PATH.unlink()

    # Create new database
    conn = sqlite3.connect(OUTPUT_DB_PATH)

    try:
        # Load and execute schema
        schema = SCHEMA_SQL_PATH.read_text()
        conn.executescript(schema)

        # Discover and insert PLR definitions using static analysis
        discover_resources_static(conn)

        discover_machines_static(conn)

        discover_decks_static(conn)

        discover_backends_static(conn)

        # Add sample workcell
        add_sample_workcell(conn)

        # Update metadata
        insert_metadata(conn)

        # Get database size
        conn.commit()
        OUTPUT_DB_PATH.stat().st_size


        # Show table statistics
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
                pass

    except Exception:
        raise
    finally:
        conn.close()



if __name__ == "__main__":
    main()
