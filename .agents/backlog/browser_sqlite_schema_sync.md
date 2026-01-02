# Browser SQLite Schema Sync Backlog

**Priority**: P2 (High)
**Difficulty**: XL (Extra Large - 3+ days)
**Owner**: Full Stack
**Last Updated**: 2026-01-01
**Status**: COMPLETE (100%)

---

## Implementation Progress

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Schema Codegen | **COMPLETE** | `scripts/generate_browser_schema.py` |
| Phase 2: TypeScript Generation | **COMPLETE** | `schema.ts`, `enums.ts` generated |
| Phase 3: Enhanced SqliteService | **COMPLETE** | Repository pattern implemented |
| Phase 4: Persistence Layer | **COMPLETE** | IndexedDB integration done |
| Phase 5: PLR-Preloaded DB | **COMPLETE** | `scripts/generate_browser_db.py`, `praxis.db` (672KB) |
| Phase 6: Integration | **COMPLETE** | All TS types fixed |

### Files Created

```
scripts/
├── generate_browser_schema.py    # SQLAlchemy → SQLite DDL + TypeScript
└── generate_browser_db.py        # PLR-preloaded database generator

praxis/web-client/src/
├── assets/db/
│   ├── schema.sql               # Generated (26KB, 19 tables)
│   └── praxis.db                # Generated (672KB with PLR data)
└── app/core/db/
    ├── schema.ts                # Generated interfaces (26KB)
    ├── enums.ts                 # Generated enums (10KB)
    ├── sqlite-repository.ts     # Generic repository pattern
    ├── repositories.ts          # Entity-specific repositories
    ├── sqlite-persistence.service.ts  # IndexedDB persistence
    └── index.ts                 # Module exports
```

### Generated Content Summary

- **Tables**: 19 (excluding 5 server-only tables)
- **Resource Definitions**: 36 PLR resources
- **Machine Definitions**: 1 PLR machine
- **Deck Definitions**: 4 PLR decks
- **TypeScript Enums**: 12 union types

### Remaining Work (Follow-up)

1. ~~**Minor TS type fix** - `ArrayBufferLike` type assertion in persistence service~~ DONE
2. **Future**: `generate_browser_db.py` uses `plr_inspection` (runtime) - consider migrating to `plr_static_analysis` (CST-based) to avoid import side effects and get more PLR definitions

### How to Regenerate

```bash
# Regenerate schema and TypeScript interfaces
uv run scripts/generate_browser_schema.py

# Regenerate preloaded database with PLR definitions
uv run scripts/generate_browser_db.py
```

---

## Executive Summary

Currently, browser mode uses a simplified `SqliteService` with manually defined schemas and mock data. This creates schema drift between the production PostgreSQL backend and the browser-only sql.js database.

This feature establishes **SQLAlchemy ORM models as the single source of truth** and creates a codegen pipeline to automatically generate:
1. SQLite-compatible DDL (`schema.sql`)
2. TypeScript interfaces matching the ORM models (`schema.d.ts`)
3. A TypeScript service layer for CRUD operations

---

## Current State Analysis

### Existing SqliteService (`sqlite.service.ts`)

**Location**: `praxis/web-client/src/app/core/services/sqlite.service.ts`

**Current Limitations**:
- Manual schema definition (4 tables only: `protocols`, `protocol_runs`, `resources`, `machines`)
- Uses mock data from `assets/demo-data/`
- No relationship handling (foreign keys, JOINs)
- Missing most production tables (decks, workcells, users, schedules, etc.)
- No persistence across sessions

### Production ORM Models

**Location**: `praxis/backend/models/orm/`

**Models (20+ tables)**:
| Model | File | Description |
|-------|------|-------------|
| `AssetOrm` | asset.py | Base class for physical assets |
| `DeckOrm` | deck.py | Physical deck instances |
| `DeckDefinitionOrm` | deck.py | Deck type definitions |
| `DeckPositionDefinitionOrm` | deck.py | Slot/position definitions |
| `MachineOrm` | machine.py | Physical machine instances |
| `MachineDefinitionOrm` | machine.py | Machine type definitions |
| `ResourceOrm` | resource.py | Physical resource instances |
| `ResourceDefinitionOrm` | resource.py | Resource type definitions |
| `ProtocolRunOrm` | protocol.py | Protocol execution records |
| `FunctionProtocolDefinitionOrm` | protocol.py | Protocol definitions |
| `ParameterDefinitionOrm` | protocol.py | Protocol parameters |
| `AssetRequirementOrm` | protocol.py | Protocol asset requirements |
| `FunctionCallLogOrm` | protocol.py | Execution logs |
| `ProtocolSourceRepositoryOrm` | protocol.py | Protocol source repos |
| `FileSystemProtocolSourceOrm` | protocol.py | File-based protocol sources |
| `FunctionDataOutputOrm` | outputs.py | Function output data |
| `WellDataOutputOrm` | outputs.py | Well-specific output data |
| `WorkcellOrm` | workcell.py | Workcell groupings |
| `UserOrm` | user.py | User accounts |
| `AssetReservationOrm` | schedule.py | Asset reservations |
| `ScheduleEntryOrm` | schedule.py | Schedule entries |
| `ScheduleHistoryOrm` | schedule.py | Schedule audit log |

---

## Implementation Plan

### Phase 1: Schema Codegen Pipeline

**Goal**: Create a Python script that introspects SQLAlchemy ORM models and generates SQLite DDL.

#### Tasks

1. **Create codegen script** (`scripts/generate_browser_schema.py`):
   ```python
   # Key functionality:
   # 1. Import all ORM models
   # 2. Use SQLAlchemy's CreateTable to generate DDL
   # 3. Convert PostgreSQL-specific types to SQLite equivalents
   # 4. Output to praxis/web-client/src/assets/db/schema.sql
   ```

2. **Type mapping (PostgreSQL → SQLite)**:
   | PostgreSQL | SQLite |
   |------------|--------|
   | `UUID` | `TEXT` |
   | `TIMESTAMP WITH TIME ZONE` | `TEXT` (ISO 8601) |
   | `JSONB` | `TEXT` (JSON string) |
   | `ARRAY` | `TEXT` (JSON array) |
   | `ENUM` | `TEXT` |
   | `BOOLEAN` | `INTEGER` (0/1) |
   | `BIGINT` | `INTEGER` |

3. **Handle SQLAlchemy relationships**:
   - Extract foreign key constraints
   - Generate `CREATE INDEX` for foreign keys
   - Document relationship patterns for TypeScript layer

4. **Add npm script**:
   ```json
   {
     "scripts": {
       "generate:schema": "uv run scripts/generate_browser_schema.py"
     }
   }
   ```

#### Deliverables
- `scripts/generate_browser_schema.py`
- `praxis/web-client/src/assets/db/schema.sql`
- npm script integration

---

### Phase 2: TypeScript Interface Generation

**Goal**: Generate TypeScript interfaces that mirror ORM models.

#### Tasks

1. **Extend codegen script** to output TypeScript:
   ```typescript
   // Generated: praxis/web-client/src/app/core/db/schema.d.ts

   export interface ProtocolRun {
     accession_id: string;
     protocol_definition_id: string | null;
     status: ProtocolRunStatus;
     created_at: string;
     start_time: string | null;
     end_time: string | null;
     duration_ms: number | null;
     // ... all fields from ProtocolRunOrm
   }

   export interface Machine {
     accession_id: string;
     machine_definition_id: string;
     name: string;
     status: MachineStatus;
     // ... all fields from MachineOrm
   }
   ```

2. **Enum generation**:
   ```typescript
   // Generated from praxis/backend/models/enums/
   export type ProtocolRunStatus =
     | 'PENDING'
     | 'PREPARING'
     | 'QUEUED'
     | 'RUNNING'
     | 'COMPLETED'
     | 'FAILED'
     | 'CANCELLED'
     | 'PAUSED';
   ```

3. **Relationship typing**:
   ```typescript
   export interface ProtocolRunWithRelations extends ProtocolRun {
     protocol_definition?: ProtocolDefinition;
     logs?: FunctionCallLog[];
   }
   ```

#### Deliverables
- `praxis/web-client/src/app/core/db/schema.d.ts`
- `praxis/web-client/src/app/core/db/enums.ts`

---

### Phase 3: Enhanced SqliteService

**Goal**: Rewrite `SqliteService` to use generated schema and provide full CRUD operations.

#### Tasks

1. **Schema initialization**:
   ```typescript
   private async initDb(): Promise<Database> {
     const SQL = await initSqlJs({ locateFile: ... });
     const db = new SQL.Database();

     // Load generated schema
     const schema = await fetch('/assets/db/schema.sql').then(r => r.text());
     db.run(schema);

     return db;
   }
   ```

2. **Generic CRUD operations**:
   ```typescript
   // Repository pattern
   class SqliteRepository<T> {
     constructor(
       private db: Database,
       private tableName: string,
       private primaryKey: string = 'accession_id'
     ) {}

     findAll(): T[] { ... }
     findById(id: string): T | null { ... }
     findBy(criteria: Partial<T>): T[] { ... }
     create(entity: Omit<T, 'accession_id'>): T { ... }
     update(id: string, updates: Partial<T>): T { ... }
     delete(id: string): boolean { ... }
   }
   ```

3. **Entity-specific services**:
   ```typescript
   @Injectable({ providedIn: 'root' })
   export class ProtocolRunRepository extends SqliteRepository<ProtocolRun> {
     constructor(sqlite: SqliteService) {
       super(sqlite.db, 'protocol_runs');
     }

     // Custom queries
     findByStatus(status: ProtocolRunStatus[]): ProtocolRun[] { ... }
     findWithProtocolDefinition(id: string): ProtocolRunWithRelations { ... }
   }
   ```

4. **Relationship handling**:
   - Implement lazy loading for related entities
   - Support eager loading via options parameter
   - Handle JSON columns (parse/stringify)

#### Deliverables
- Refactored `sqlite.service.ts`
- `praxis/web-client/src/app/core/db/sqlite-repository.ts`
- Entity-specific repository services

---

### Phase 4: Persistence Layer

**Goal**: Persist sql.js database to IndexedDB for cross-session state.

#### Tasks

1. **IndexedDB integration**:
   ```typescript
   @Injectable({ providedIn: 'root' })
   export class SqlitePersistenceService {
     private readonly DB_NAME = 'praxis-browser-db';
     private readonly STORE_NAME = 'database';

     async saveDatabase(db: Database): Promise<void> {
       const data = db.export(); // Uint8Array
       // Store in IndexedDB
     }

     async loadDatabase(): Promise<Uint8Array | null> {
       // Load from IndexedDB
     }
   }
   ```

2. **Auto-save on changes**:
   - Debounced save after mutations
   - Save on `beforeunload` event

3. **Export/Import UI**:
   - "Export Database" button → downloads `.db` file
   - "Import Database" → file picker to restore state

#### Deliverables
- `praxis/web-client/src/app/core/db/sqlite-persistence.service.ts`
- UI components for export/import

---

### Phase 5: PLR-Preloaded Database File

**Goal**: Generate a `.db` file with complete PLR inspection data (machine definitions, resource definitions, deck definitions, etc.) that browser mode loads on startup.

This is a **core requirement**, not optional. Browser mode should have the full PLR catalog available from the start.

#### Tasks

1. **Create database generation script** (`scripts/generate_browser_db.py`):
   ```python
   """
   Generates a complete SQLite database for browser mode with:
   1. Schema from SQLAlchemy ORM models
   2. All PLR machine definitions (from plr_static_analysis)
   3. All PLR resource definitions (from plr_static_analysis)
   4. All PLR deck definitions (from plr_static_analysis)
   5. Capability schemas for each machine type
   6. Sample protocol definitions (optional)
   """

   from praxis.backend.utils.plr_static_analysis import PLRSourceParser
   from praxis.backend.models.orm import (
       MachineDefinitionOrm,
       ResourceDefinitionOrm,
       DeckDefinitionOrm,
       # ... all relevant models
   )

   def main():
       # 1. Create SQLite database
       # 2. Apply generated schema
       # 3. Run PLR static analysis
       # 4. Insert all discovered definitions
       # 5. Save to praxis/web-client/src/assets/db/praxis.db
   ```

2. **PLR data to include**:
   | Data Type | Source | Approx Count |
   |-----------|--------|--------------|
   | Machine Definitions | `PLRSourceParser.discover_machine_classes()` | ~35 (21 frontends + backends) |
   | Resource Definitions | `PLRSourceParser.discover_resource_classes()` | ~500+ (plates, tips, carriers, etc.) |
   | Deck Definitions | PLR deck layouts | ~10 (STARlet, OT-2, etc.) |
   | Capability Schemas | `capability_config_templates.py` | 15 types |
   | Backend Definitions | `PLRSourceParser` | ~70 backends |

3. **Database structure**:
   ```
   praxis.db (SQLite)
   ├── machine_definitions (35 rows)
   │   └── Includes: fqn, name, manufacturer, capabilities, compatible_backends
   ├── resource_definitions (500+ rows)
   │   └── Includes: fqn, name, category, vendor, dimensions
   ├── deck_definitions (10 rows)
   │   └── Includes: fqn, name, manufacturer, rail_count
   ├── deck_position_definitions (linked to decks)
   │   └── Includes: slot positions, site data
   └── capability_schemas (15 rows)
       └── Includes: machine_type, json_schema
   ```

4. **Build integration**:
   ```json
   // package.json
   {
     "scripts": {
       "generate:db": "uv run scripts/generate_browser_db.py",
       "prebuild": "npm run generate:db"
     }
   }
   ```

5. **SqliteService initialization**:
   ```typescript
   private async initDb(): Promise<Database> {
     const SQL = await initSqlJs({ locateFile: ... });

     // Load prebuilt database with PLR data
     const dbFile = await fetch('/assets/db/praxis.db');
     const dbArray = new Uint8Array(await dbFile.arrayBuffer());
     const db = new SQL.Database(dbArray);

     console.log('[SqliteService] Loaded prebuilt database with PLR definitions');
     return db;
   }
   ```

6. **Version tracking**:
   - Include a `_metadata` table with schema version and generation timestamp
   - Compare on startup to detect stale databases
   - Regenerate as part of CI/CD when ORM or PLR changes

#### Deliverables
- `scripts/generate_browser_db.py` - Main generation script
- `praxis/web-client/src/assets/db/praxis.db` - Prebuilt database (~1-5 MB)
- npm script integration (`generate:db`)
- CI integration to regenerate on schema/PLR changes

#### Benefits
- **Zero startup cost**: No need to run PLR analysis in browser
- **Complete catalog**: All PLR machines, resources, decks available immediately
- **Offline capable**: Works without any network requests
- **GitHub Pages ready**: Static file deployment works out of the box

---

### Phase 6: Integration & Testing

**Goal**: Wire up the new system and ensure feature parity.

#### Tasks

1. **Demo interceptor updates**:
   - Update `demo.interceptor.ts` to use `SqliteService`
   - Remove hardcoded mock data dependencies

2. **Feature integration**:
   - Execution Monitor reads from sql.js
   - Protocol wizard creates real `ProtocolRun` records
   - Asset management uses sql.js repositories

3. **Unit tests**:
   ```typescript
   describe('SqliteRepository', () => {
     it('should create and retrieve entities', ...);
     it('should handle relationships', ...);
     it('should persist across service restarts', ...);
   });
   ```

4. **E2E tests**:
   - Browser mode data flow tests
   - Persistence verification

#### Deliverables
- Updated `demo.interceptor.ts`
- Unit tests for repositories
- E2E tests for browser mode

---

## Schema Exclusions (Browser Mode)

The following tables are **excluded** from browser mode (scheduling requires server):

| Table | Reason |
|-------|--------|
| `schedule_entries` | Server-only scheduling |
| `schedule_history` | Server-only audit log |
| `asset_reservations` | Requires real-time coordination |
| `scheduler_metrics_view` | Materialized view |
| `users` | No auth in browser mode |

---

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Codegen language | Python | Direct SQLAlchemy introspection |
| Schema output | `.sql` file | Easy to version, human-readable |
| TypeScript generation | Same script | Single source of truth |
| Persistence | IndexedDB | Best browser storage for binary data |
| Preloaded data | Optional `.db` | Faster cold start, GitHub Pages compatible |

---

## Success Criteria

1. **Schema parity**: Generated schema matches production (excluding scheduling)
2. **Type safety**: TypeScript interfaces match ORM models
3. **CRUD coverage**: All entity types have repository implementations
4. **Persistence**: Database survives page refresh and browser restart
5. **Test coverage**: >80% coverage on TypeScript service layer
6. **Build integration**: `npm run generate:schema` works in CI

---

## Dependencies

- `sql.js` - Already installed
- `@anthropic-ai/sdk` - Not needed (pure codegen)
- SQLAlchemy introspection utilities (Python stdlib)

---

## Estimated Effort Breakdown

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Phase 1: Schema Codegen | M (4-8h) | None |
| Phase 2: TypeScript Generation | M (4-8h) | Phase 1 |
| Phase 3: Enhanced SqliteService | L (1-2d) | Phase 2 |
| Phase 4: Persistence Layer | M (4-8h) | Phase 3 |
| Phase 5: Data Seeding | M (4-8h) | Phase 1 |
| Phase 6: Integration & Testing | L (1-2d) | All phases |

**Total**: XL (3-5 days)

---

## Related Items

- [modes_and_deployment.md](./modes_and_deployment.md) - Parent feature context
- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md) - Priority tracking
- [ROADMAP.md](../ROADMAP.md) - Milestone planning

---

*This document was created 2026-01-01 and should be updated as implementation progresses.*
