#!/usr/bin/env python3
"""Check browser database table counts."""

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "praxis" / "web-client" / "src" / "assets" / "db" / "praxis.db"

if not DB_PATH.exists():
    print(f"❌ Database not found: {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)

# Get all tables
cursor = conn.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '_%'
    ORDER BY name
""")

tables = [row[0] for row in cursor.fetchall()]

print("=" * 80)
print("BROWSER DATABASE TABLE COUNTS")
print("=" * 80)
print()

# Special queries for key tables
key_tables = {
    "resource_definitions": "Resources",
    "machine_definitions": "Machines + Backends",
    "deck_definition_catalog": "Decks",
    "function_protocol_definitions": "Protocols",
    "parameter_definitions": "Parameters",
    "protocol_asset_requirements": "Asset Requirements",
    "machines": "Machine Instances",
    "workcells": "Workcells",
}

print("KEY TABLES:")
print("-" * 80)
for table, label in key_tables.items():
    if table in tables:
        count_cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
        count = count_cursor.fetchone()[0]
        print(f"  {label:30} {count:>6} rows")

# Breakdown machine_definitions by category
print()
print("MACHINE DEFINITION BREAKDOWN:")
print("-" * 80)
cursor = conn.execute("""
    SELECT plr_category, COUNT(*) 
    FROM machine_definitions 
    GROUP BY plr_category 
    ORDER BY plr_category
""")
for cat, count in cursor.fetchall():
    print(f"  {cat:30} {count:>6} rows")

print()
print("ALL TABLES:")
print("-" * 80)
for table in tables:
    count_cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
    count = count_cursor.fetchone()[0]
    print(f"  {table:40} {count:>6} rows")

conn.close()

print()
print("=" * 80)
print("✅ Database audit complete")
print("=" * 80)
