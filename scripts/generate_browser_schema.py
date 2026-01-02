#!/usr/bin/env python3
"""Generate SQLite schema and TypeScript interfaces from SQLAlchemy ORM models.

This script introspects SQLAlchemy ORM models and generates:
1. SQLite-compatible DDL (schema.sql)
2. TypeScript interfaces matching ORM models (schema.ts)
3. TypeScript enums from Python enums (enums.ts)

Usage:
    uv run scripts/generate_browser_schema.py

Outputs:
    - praxis/web-client/src/assets/db/schema.sql
    - praxis/web-client/src/app/core/db/schema.ts
    - praxis/web-client/src/app/core/db/enums.ts
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.engine import create_engine
from sqlalchemy.schema import CreateIndex, CreateTable

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_CLIENT_ROOT = PROJECT_ROOT / "praxis" / "web-client"
ASSETS_DB_DIR = WEB_CLIENT_ROOT / "src" / "assets" / "db"
CORE_DB_DIR = WEB_CLIENT_ROOT / "src" / "app" / "core" / "db"

# Output files
SCHEMA_SQL_PATH = ASSETS_DB_DIR / "schema.sql"
SCHEMA_TS_PATH = CORE_DB_DIR / "schema.ts"
ENUMS_TS_PATH = CORE_DB_DIR / "enums.ts"

# Tables to EXCLUDE from browser mode (server-only tables)
EXCLUDED_TABLES = {
    "schedule_entries",
    "schedule_history",
    "asset_reservations",
    "scheduler_metrics_view",
    "users",
}


def snake_to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(word.capitalize() for word in name.split("_"))


def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    pascal = snake_to_pascal(name)
    return pascal[0].lower() + pascal[1:] if pascal else ""


def get_sqlalchemy_type_name(column_type: Any) -> str:
    """Get the SQLAlchemy type name as a string."""
    type_class = type(column_type)
    return type_class.__name__


def sqlalchemy_to_sqlite_type(column_type: Any) -> str:
    """Map SQLAlchemy/PostgreSQL types to SQLite equivalents."""
    type_name = get_sqlalchemy_type_name(column_type)

    # Direct mappings
    type_map = {
        "UUID": "TEXT",
        "JSONB": "TEXT",
        "JSON": "TEXT",
        "DateTime": "TEXT",
        "Boolean": "INTEGER",
        "Float": "REAL",
        "Integer": "INTEGER",
        "BigInteger": "INTEGER",
        "String": "TEXT",
        "Text": "TEXT",
        "LargeBinary": "BLOB",
        "Enum": "TEXT",
        "ARRAY": "TEXT",
    }

    if type_name in type_map:
        return type_map[type_name]

    # Handle TypeDecorator subclasses
    if hasattr(column_type, "impl"):
        return sqlalchemy_to_sqlite_type(column_type.impl)

    # Handle variants (like JsonVariant)
    if hasattr(column_type, "_variant_mapping"):
        # Get the base type (JSON)
        return "TEXT"

    return "TEXT"


def sqlalchemy_to_typescript_type(column_type: Any, nullable: bool = False) -> str:
    """Map SQLAlchemy types to TypeScript types."""
    type_name = get_sqlalchemy_type_name(column_type)

    # Handle Enum types
    if type_name == "Enum" and hasattr(column_type, "enums"):
        # Get the enum class name
        if hasattr(column_type, "enum_class") and column_type.enum_class:
            enum_name = column_type.enum_class.__name__
            # Remove 'Enum' suffix if present
            ts_enum_name = enum_name.replace("Enum", "")
            base_type = ts_enum_name
        else:
            # Fall back to union of enum values
            values = " | ".join(f"'{v}'" for v in column_type.enums)
            base_type = values
    else:
        type_map = {
            "UUID": "string",
            "JSONB": "Record<string, unknown>",
            "JSON": "Record<string, unknown>",
            "DateTime": "string",
            "Boolean": "boolean",
            "Float": "number",
            "Integer": "number",
            "BigInteger": "number",
            "String": "string",
            "Text": "string",
            "LargeBinary": "Uint8Array",
            "ARRAY": "unknown[]",
        }

        base_type = type_map.get(type_name, "unknown")

        # Handle TypeDecorator subclasses
        if base_type == "unknown" and hasattr(column_type, "impl"):
            return sqlalchemy_to_typescript_type(column_type.impl, nullable)

        # Handle variants (like JsonVariant)
        if base_type == "unknown" and hasattr(column_type, "_variant_mapping"):
            base_type = "Record<string, unknown>"

    if nullable:
        return f"{base_type} | null"
    return base_type


def generate_sqlite_ddl(metadata: Any) -> str:
    """Generate SQLite DDL from SQLAlchemy metadata."""
    # Create a SQLite engine for DDL compilation
    engine = create_engine("sqlite:///:memory:")

    lines = [
        "-- Auto-generated SQLite schema from SQLAlchemy ORM models",
        f"-- Generated at: {datetime.now().isoformat()}",
        "-- DO NOT EDIT MANUALLY - regenerate using: uv run scripts/generate_browser_schema.py",
        "",
        "-- Enable foreign key support",
        "PRAGMA foreign_keys = ON;",
        "",
        "-- Metadata table for schema versioning",
        "CREATE TABLE IF NOT EXISTS _schema_metadata (",
        "    key TEXT PRIMARY KEY,",
        "    value TEXT NOT NULL",
        ");",
        "",
        f"INSERT OR REPLACE INTO _schema_metadata (key, value) VALUES ('generated_at', '{datetime.now().isoformat()}');",
        "INSERT OR REPLACE INTO _schema_metadata (key, value) VALUES ('schema_version', '1.0.0');",
        "",
    ]

    # Sort tables by dependency order (tables with no foreign keys first)
    sorted_tables = sorted(
        metadata.tables.values(),
        key=lambda t: (len(list(t.foreign_keys)), t.name),
    )

    for table in sorted_tables:
        if table.name in EXCLUDED_TABLES:
            lines.append(f"-- EXCLUDED: {table.name} (server-only)")
            lines.append("")
            continue

        # Generate CREATE TABLE statement
        create_stmt = CreateTable(table)

        try:
            # Compile to SQLite dialect
            compiled = create_stmt.compile(dialect=engine.dialect)
            ddl_str = str(compiled).strip()

            # Post-process to convert PostgreSQL-specific syntax
            ddl_str = convert_ddl_to_sqlite(ddl_str, table)

            lines.append(f"-- Table: {table.name}")
            lines.append(ddl_str + ";")
            lines.append("")

            # Generate indexes
            for index in table.indexes:
                try:
                    idx_stmt = CreateIndex(index)
                    idx_compiled = idx_stmt.compile(dialect=engine.dialect)
                    lines.append(str(idx_compiled).strip() + ";")
                except Exception:
                    # Skip indexes that can't be compiled
                    pass

            lines.append("")

        except Exception as e:
            lines.append(f"-- ERROR generating DDL for {table.name}: {e}")
            lines.append("")

    return "\n".join(lines)


def convert_ddl_to_sqlite(ddl: str, table: Any) -> str:
    """Convert PostgreSQL-specific DDL to SQLite-compatible DDL."""
    # Replace PostgreSQL types with SQLite equivalents
    replacements = [
        (r"\bUUID\b", "TEXT"),
        (r"\bJSONB\b", "TEXT"),
        (r"\bJSON\b", "TEXT"),
        (r"\bTIMESTAMP WITH TIME ZONE\b", "TEXT"),
        (r"\bTIMESTAMP WITHOUT TIME ZONE\b", "TEXT"),
        (r"\bTIMESTAMP\b", "TEXT"),
        (r"\bBOOLEAN\b", "INTEGER"),
        (r"\bBIGINT\b", "INTEGER"),
        (r"\bSMALLINT\b", "INTEGER"),
        (r"\bDOUBLE PRECISION\b", "REAL"),
        (r"\bBYTEA\b", "BLOB"),
        (r"\bLARGEBINARY\b", "BLOB"),
        # Remove server_default with now() - SQLite doesn't support this the same way
        (r"DEFAULT \(now\(\)\)", "DEFAULT (datetime('now'))"),
        (r"server_default=.*?\)", ""),
    ]

    for pattern, replacement in replacements:
        ddl = re.sub(pattern, replacement, ddl, flags=re.IGNORECASE)

    # Handle ENUM types - convert to TEXT with CHECK constraint
    # SQLAlchemy compiles enums as VARCHAR for SQLite, which is fine

    # Remove PostgreSQL-specific extensions
    return re.sub(r"SERIAL\b", "INTEGER", ddl, flags=re.IGNORECASE)



def generate_typescript_interfaces(metadata: Any) -> str:
    """Generate TypeScript interfaces from SQLAlchemy metadata."""
    lines = [
        "/**",
        " * Auto-generated TypeScript interfaces from SQLAlchemy ORM models",
        f" * Generated at: {datetime.now().isoformat()}",
        " * DO NOT EDIT MANUALLY - regenerate using: uv run scripts/generate_browser_schema.py",
        " */",
        "",
        "/* eslint-disable @typescript-eslint/no-explicit-any */",
        "",
        "import type {",
    ]

    # Collect all enum types used
    enum_types = set()
    for table in metadata.tables.values():
        if table.name in EXCLUDED_TABLES:
            continue
        for column in table.columns:
            col_type = column.type
            if hasattr(col_type, "enum_class") and col_type.enum_class:
                enum_name = col_type.enum_class.__name__.replace("Enum", "")
                enum_types.add(enum_name)

    # Import enum types
    for enum_type in sorted(enum_types):
        lines.append(f"  {enum_type},")
    lines.append("} from './enums';")
    lines.append("")

    # Generate interfaces for each table
    for table in sorted(metadata.tables.values(), key=lambda t: t.name):
        if table.name in EXCLUDED_TABLES:
            continue

        interface_name = snake_to_pascal(table.name)
        # Remove trailing 's' for singular form, handle special cases
        if interface_name.endswith("ies"):
            interface_name = interface_name[:-3] + "y"
        elif interface_name.endswith("ses"):
            interface_name = interface_name[:-2]
        elif interface_name.endswith("s") and not interface_name.endswith("ss"):
            interface_name = interface_name[:-1]

        lines.append("/**")
        lines.append(f" * Interface for the '{table.name}' table")
        lines.append(" */")
        lines.append(f"export interface {interface_name} {{")

        for column in table.columns:
            nullable = column.nullable or column.default is not None
            ts_type = sqlalchemy_to_typescript_type(column.type, nullable)
            comment = column.comment or ""
            if comment:
                lines.append(f"  /** {comment} */")
            lines.append(f"  {column.name}: {ts_type};")

        lines.append("}")
        lines.append("")

    return "\n".join(lines)


def generate_typescript_enums() -> str:
    """Generate TypeScript enums from Python enums."""
    # Import all enums
    from praxis.backend.models.enums import (
        AssetReservationStatusEnum,
        AssetType,
        DataOutputTypeEnum,
        FunctionCallStatusEnum,
        MachineCategoryEnum,
        MachineStatusEnum,
        ProtocolRunStatusEnum,
        ProtocolSourceStatusEnum,
        ResourceCategoryEnum,
        ResourceStatusEnum,
        SpatialContextEnum,
        WorkcellStatusEnum,
    )

    all_enums = [
        AssetReservationStatusEnum,
        AssetType,
        DataOutputTypeEnum,
        FunctionCallStatusEnum,
        MachineCategoryEnum,
        MachineStatusEnum,
        ProtocolRunStatusEnum,
        ProtocolSourceStatusEnum,
        ResourceCategoryEnum,
        ResourceStatusEnum,
        SpatialContextEnum,
        WorkcellStatusEnum,
        # Exclude schedule enums as schedule tables are excluded
        # ScheduleHistoryEventEnum,
        # ScheduleHistoryEventTriggerEnum,
        # ScheduleStatusEnum,
    ]

    lines = [
        "/**",
        " * Auto-generated TypeScript enums from Python enums",
        f" * Generated at: {datetime.now().isoformat()}",
        " * DO NOT EDIT MANUALLY - regenerate using: uv run scripts/generate_browser_schema.py",
        " */",
        "",
    ]

    for enum_class in all_enums:
        enum_name = enum_class.__name__.replace("Enum", "")
        lines.append("/**")
        lines.append(f" * {enum_class.__doc__ or f'Enum: {enum_name}'}")
        lines.append(" */")

        # Generate as union type for better TypeScript ergonomics
        values = [f"'{member.value}'" for member in enum_class]
        lines.append(f"export type {enum_name} =")
        for i, value in enumerate(values):
            if i == len(values) - 1:
                lines.append(f"  | {value};")
            else:
                lines.append(f"  | {value}")
        lines.append("")

        # Also generate a const object for runtime access
        lines.append(f"export const {enum_name}Values = {{")
        for member in enum_class:
            member_name = member.name
            lines.append(f"  {member_name}: '{member.value}' as const,")
        lines.append("} as const;")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Main entry point for schema generation."""
    # Import all ORM models to populate metadata
    # This import triggers registration of all tables with Base.metadata
    from praxis.backend.utils.db import Base

    # Ensure output directories exist
    ASSETS_DB_DIR.mkdir(parents=True, exist_ok=True)
    CORE_DB_DIR.mkdir(parents=True, exist_ok=True)

    # Generate SQLite DDL
    sqlite_ddl = generate_sqlite_ddl(Base.metadata)
    SCHEMA_SQL_PATH.write_text(sqlite_ddl)

    # Generate TypeScript interfaces
    ts_interfaces = generate_typescript_interfaces(Base.metadata)
    SCHEMA_TS_PATH.write_text(ts_interfaces)

    # Generate TypeScript enums
    ts_enums = generate_typescript_enums()
    ENUMS_TS_PATH.write_text(ts_enums)

    # Print summary
    included_tables = [
        t.name for t in Base.metadata.tables.values() if t.name not in EXCLUDED_TABLES
    ]
    for _table_name in sorted(included_tables):
        pass

    for _table_name in sorted(EXCLUDED_TABLES):
        pass



if __name__ == "__main__":
    main()
