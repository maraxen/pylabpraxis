# Machine Frontend/Backend Separation Migration Plan

**Status**: INSPECTION COMPLETE - Ready for execution
**Created**: 2026-01-17
**Updated**: 2026-01-17 (Inspection phase completed)
**Scope**: Backend models, services, API, frontend types, browser DB generation

---

## Executive Summary

Refactor the data model to properly separate PyLabRobot's frontend/backend architecture:
- **Frontend**: Abstract machine interface (`LiquidHandler`, `PlateReader`) - the high-level API
- **Backend**: Hardware driver (`STARBackend`, `SimulatorBackend`) - the low-level communication

**Current**: Single `MachineDefinition` conflates both concepts with workarounds (`frontend_fqn`, `compatible_backends`)
**Target**: Separate `MachineFrontendDefinition` and `MachineBackendDefinition` tables with proper relationships

---

## Phase 0: Inspection Scope

### 0.1 Files to Inspect (Backend - Python)

#### Core Models (MUST inspect thoroughly)
```
praxis/backend/models/domain/machine.py          # Current unified model - WILL BE SPLIT
praxis/backend/models/domain/asset.py            # Asset base class - check inheritance
praxis/backend/models/domain/sqlmodel_base.py   # Base class - understand PraxisBase
praxis/backend/models/enums.py                   # MachineCategoryEnum, MachineStatusEnum
praxis/backend/models/__init__.py                # Re-exports - will need updates
```

#### Services (MUST inspect - business logic)
```
praxis/backend/services/machine.py                        # Machine CRUD - WILL CHANGE
praxis/backend/services/machine_type_definition.py        # Discovery/sync - MAJOR CHANGES
praxis/backend/services/hardware_discovery.py             # Returns plr_backend - integration point
praxis/backend/services/plr_type_base.py                  # Base service class
praxis/backend/services/utils/crud_base.py                # CRUD base patterns
```

#### Static Analysis (MUST inspect - discovers PLR types)
```
praxis/backend/utils/plr_static_analysis/__init__.py      # Exports, BACKEND_TYPE_TO_FRONTEND_FQN
praxis/backend/utils/plr_static_analysis/parser.py        # PLRSourceParser - discovers machines
praxis/backend/utils/plr_static_analysis/models.py        # DiscoveredClass model
praxis/backend/utils/plr_static_analysis/visitors/        # AST visitors
```

#### Runtime (MUST inspect - instantiation)
```
praxis/backend/core/workcell_runtime/machine_manager.py  # initialize_machine() - uses fqn
praxis/backend/core/workcell_runtime/core.py             # WorkcellRuntime class
praxis/backend/core/workcell.py                          # Workcell container
```

#### API Layer (MUST inspect - endpoints)
```
praxis/backend/api/machines.py                   # Machine REST endpoints
praxis/backend/api/hardware.py                   # Hardware discovery endpoints
praxis/backend/api/assets.py                     # Asset endpoints (if machines included)
```

### 0.2 Files to Inspect (Frontend - TypeScript)

#### Schema/Types (MUST inspect)
```
praxis/web-client/src/app/core/db/schema.ts              # Browser DB schema - auto-generated
praxis/web-client/src/app/core/api-generated/models/     # OpenAPI generated types
praxis/web-client/src/app/features/assets/models/        # Feature-specific models
```

#### Repositories (MUST inspect - DB access)
```
praxis/web-client/src/app/core/db/repositories.ts        # Repository interfaces
praxis/web-client/src/app/core/db/sqlite-repository.ts   # SQLite implementation
```

#### Services (SHOULD inspect - may reference machine types)
```
praxis/web-client/src/app/features/assets/services/asset.service.ts
praxis/web-client/src/app/features/run-protocol/services/deck-catalog.service.ts
praxis/web-client/src/app/features/run-protocol/services/execution.service.ts
```

#### Components (SHOULD inspect - UI that displays machines)
```
praxis/web-client/src/app/features/assets/components/machine-list/
praxis/web-client/src/app/shared/dialogs/add-asset-dialog/
praxis/web-client/src/app/shared/components/hardware-discovery-dialog/
```

### 0.3 Files to Inspect (PyLabRobot - Reference Only)

```
external/pylabrobot/pylabrobot/machines/machine.py       # Machine base class
external/pylabrobot/pylabrobot/machines/backend.py       # MachineBackend base class
external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py  # Frontend example
external/pylabrobot/pylabrobot/liquid_handling/backends/backend.py  # Backend base example
external/pylabrobot/pylabrobot/liquid_handling/backends/hamilton/STAR_backend.py  # Concrete backend
```

### 0.4 Scripts (MUST inspect)
```
scripts/generate_browser_db.py                   # Generates praxis.db for browser
scripts/generate_browser_schema.py               # Generates TypeScript schema
scripts/openapi_generate.sh (or similar)         # OpenAPI codegen script
```

### 0.5 Inspection Checklist

For each file, document:
- [ ] Current references to `MachineDefinition` / `Machine`
- [ ] How `fqn`, `frontend_fqn`, `compatible_backends` are used
- [ ] Foreign key relationships involving machines
- [ ] Any hardcoded assumptions about machine structure
- [ ] Test files that will need updates

---

## Phase 0.5: Inspection Findings Summary

### Critical Discovery: Where FQN is Used

**Single Point of Instantiation:**
- `praxis/backend/core/workcell_runtime/machine_manager.py:95` - ONLY place that instantiates machines
- Flow: `target_class = get_class_from_fqn(machine_model.fqn)` → instantiate → setup()
- **No backend selection logic exists** - whatever FQN is stored gets instantiated

**Current FQN Sources:**
1. `Machine.fqn` (inherited from Asset) - currently points to backend/simulator class
2. `MachineDefinition.fqn` - points to backend/simulator class
3. `MachineDefinition.frontend_fqn` - points to frontend class (workaround field)
4. `Machine.simulation_backend_name` - string name of selected simulator (not FQN, needs resolution)

**Key Assumption to Break:**
- Currently: One machine instance = one FQN = one class instantiation
- Target: One machine instance = frontend FQN + backend definition selection

### Architecture Pattern Insights

**Discovery Pipeline:**
```
PLR Source Code
    ↓ (LibCST static analysis)
DiscoveredClass (frontend or backend, is_simulated flag)
    ↓ (MachineTypeDefinitionService)
MachineDefinition (catalog)
    ├─ fqn: backend/simulator FQN
    ├─ frontend_fqn: frontend FQN (workaround)
    ├─ compatible_backends: list of backend FQNs
    └─ is_simulated_frontend: boolean flag
```

**Simulator Abstraction (Current):**
- Multiple simulators grouped into ONE synthetic frontend per category
- `MachineDefinition.is_simulated_frontend = True` marks synthetic definition
- `available_simulation_backends` lists all available simulators for that category
- User selects `simulation_backend_name` when creating machine instance
- **Problem**: Simulator backend name is string, not FQN - needs runtime resolution

### Frontend/Backend Distinction Currently Visible

| Component | Frontend Awareness | Backend Awareness |
|-----------|-------------------|-------------------|
| MachineDefinition | `frontend_fqn` field | `fqn` field (backend) |
| MachineTypeDefinitionService | `BACKEND_TYPE_TO_FRONTEND_FQN` map | `compatible_backends` field |
| PLRSourceParser | Discovers both, stored separately | Both in `DiscoveredClass` |
| Hardware discovery | Hardcoded backend FQNs in 3 places | No frontend awareness |
| Machine instantiation | NOT USED | Direct FQN instantiation |
| API layer | Returned in responses | Direct use in machine creation |

**Critical Gap:** Hardware discovery returns `plr_backend` FQN suggestion, but `POST /api/v1/hardware/register` is not yet implemented - TODO comment at line 443.

### Multiple Inheritance Pattern in Machine

**Current:**
- `Machine(MachineBase, Asset, table=True)`
- MachineBase provides schema fields (machine_category, status, connection_info)
- Asset provides additional JSON fields (properties_json, plr_state, plr_definition)
- Both ultimately inherit from PraxisBase
- SQLModel merges into single `machines` table (Table-Per-Class)

**Impact:** Separation must maintain this inheritance pattern while adding new FKs.

### Browser vs API Mode Duality in Frontend

**AssetService branches on `isBrowserMode()`:**
- Browser mode: Uses SqliteService.machines repository (direct SQLite)
- API mode: Uses generated ApiMachinesService (HTTP calls)
- Both paths use same `MachineCreate` schema but behave differently
- **Update operation:** Browser mode throws error "not implemented"; API mode works
- **Type casting:** Heavy use of `as unknown as Machine` to bypass TypeScript

**Frontend implications:**
- UI must handle dual data paths
- No type safety between API models and feature models
- Maintenance fields (MaintenanceSchedule) need JSON round-trip serialization

### Scripts and Database Generation

**Dependencies (must run in order):**
1. `generate_browser_schema.py` - Reflects SQLAlchemy metadata → schema.sql + schema.ts
2. `generate_browser_db.py` - Creates praxis.db using schema.sql + static analysis
3. `generate_openapi.py` - Extracts OpenAPI spec from FastAPI app

**Key data sources for generation:**
- Machine definitions: Discovered via `PLRSourceParser.discover_machine_classes()` filtered to MACHINE_FRONTEND_TYPES only
- Backend mapping: Uses `BACKEND_TYPE_TO_FRONTEND_FQN` static mapping for discovery

**Excluded from browser DB** (server-only tables):
- users, schedule_entries, schedule_history, asset_reservations, scheduler_metrics_view

---

## Phase 1: Planning Guidelines

### 1.1 New Data Model Design

#### MachineFrontendDefinition (rename from MachineDefinition)
Represents the abstract machine interface (e.g., `LiquidHandler`, `PlateReader`).

```python
class MachineFrontendDefinition(PraxisBase, table=True):
    __tablename__ = "machine_frontend_definitions"

    # Identity
    fqn: str  # e.g., "pylabrobot.liquid_handling.LiquidHandler"
    name: str  # e.g., "Liquid Handler"

    # Classification
    machine_category: MachineCategoryEnum
    plr_category: str | None  # Original PLR category string

    # Capabilities (what operations this frontend supports)
    capabilities: dict[str, Any] | None  # e.g., {"aspirate": true, "dispense": true}
    capabilities_config: dict[str, Any] | None  # User-configurable capability schema

    # Deck association
    has_deck: bool = False
    deck_definition_accession_id: uuid.UUID | None  # FK to deck_definition_catalog

    # Metadata
    description: str | None
    manufacturer: str | None  # For branded frontends
    model: str | None

    # Relationships
    compatible_backends: list["MachineBackendDefinition"] = Relationship(back_populates="frontend")
```

#### MachineBackendDefinition (NEW)
Represents the hardware driver (e.g., `STARBackend`, `SimulatorBackend`).

```python
class MachineBackendDefinition(PraxisBase, table=True):
    __tablename__ = "machine_backend_definitions"

    # Identity
    fqn: str  # e.g., "pylabrobot.liquid_handling.backends.hamilton.STAR.STARBackend"
    name: str  # e.g., "Hamilton STAR Backend"

    # Classification
    backend_type: BackendTypeEnum  # REAL_HARDWARE, SIMULATOR, CHATTERBOX

    # Connection requirements
    connection_config: dict[str, Any] | None  # JSON schema for connection params
    # e.g., {"type": "object", "properties": {"port": {"type": "string"}}}

    # Hardware info
    manufacturer: str | None  # e.g., "Hamilton"
    model: str | None  # e.g., "STAR"

    # Frontend compatibility
    frontend_definition_accession_id: uuid.UUID  # FK to machine_frontend_definitions (required)
    frontend: "MachineFrontendDefinition" = Relationship(back_populates="compatible_backends")

    # Metadata
    description: str | None
    is_deprecated: bool = False
```

#### Machine (physical instance) - MODIFIED
```python
class Machine(Asset, table=True):
    __tablename__ = "machines"

    # ... existing Asset fields ...

    # NEW: Explicit frontend/backend references
    frontend_definition_accession_id: uuid.UUID | None  # FK
    backend_definition_accession_id: uuid.UUID | None   # FK

    # Backend instance configuration (specific to this machine)
    backend_config: dict[str, Any] | None  # e.g., {"port": "/dev/ttyUSB0", "baud": 9600}

    # DEPRECATED (remove after migration):
    # fqn - now derived from frontend_definition.fqn
    # connection_info - replaced by backend_config
    # simulation_backend_name - now just select a simulator backend_definition
    # is_simulation_override - derived from backend_definition.backend_type

    # Relationships
    frontend_definition: "MachineFrontendDefinition" = Relationship()
    backend_definition: "MachineBackendDefinition" = Relationship()
```

### 1.2 New Enums

```python
class BackendTypeEnum(str, Enum):
    REAL_HARDWARE = "real_hardware"  # Connects to physical device
    SIMULATOR = "simulator"          # PLR visualizer/simulator
    CHATTERBOX = "chatterbox"        # Print-only, no hardware
    MOCK = "mock"                    # For testing
```

### 1.3 Service Layer Changes

#### MachineTypeDefinitionService → Split into two services

1. **MachineFrontendDefinitionService**
   - Discovers frontend classes from PLR source
   - Sync frontends to DB

2. **MachineBackendDefinitionService**
   - Discovers backend classes from PLR source
   - Links backends to their compatible frontends
   - Handles simulator/chatterbox detection

#### MachineService changes
- `create_machine()` now requires `frontend_definition_id` + `backend_definition_id`
- `connection_info` → `backend_config`
- Remove simulation-specific fields

### 1.4 Static Analysis Changes

Update `PLRSourceParser` to:
1. Discover frontends separately (classes inheriting from `Machine` directly)
2. Discover backends separately (classes inheriting from `MachineBackend` or specialized backends)
3. Map backends to frontends via class hierarchy analysis

Update `DiscoveredClass` model:
- Add `is_frontend: bool`
- Add `is_backend: bool`
- Add `frontend_fqn: str | None` for backends

### 1.5 API Changes

#### New Endpoints
```
GET  /api/v1/machine-frontends/           # List all frontend definitions
GET  /api/v1/machine-frontends/{id}       # Get frontend definition
GET  /api/v1/machine-frontends/{id}/backends  # Get compatible backends

GET  /api/v1/machine-backends/            # List all backend definitions
GET  /api/v1/machine-backends/{id}        # Get backend definition
```

#### Modified Endpoints
```
POST /api/v1/machines/                    # Now requires frontend_id + backend_id
GET  /api/v1/machines/{id}                # Returns frontend + backend info
```

#### Deprecated Endpoints
```
GET  /api/v1/machine-definitions/         # Replace with /machine-frontends/ + /machine-backends/
```

---

## Phase 2: Execution Steps (Detailed)

> **For executing agent**: Each step includes exact commands, file paths, code examples, and validation checkpoints. Execute steps in order. Do not proceed to next step until validation passes.

### Environment Setup

```bash
# Working directory for all commands
cd /Users/mar/Projects/pylabpraxis

# Ensure dependencies are available
uv sync

# Create rollback point
git tag pre-machine-separation
git stash  # if uncommitted changes exist
```

---

### Step 2.1: Create New Enum (BackendTypeEnum)

**File**: `/Users/mar/Projects/pylabpraxis/praxis/backend/models/enums/machine.py`

**Action**: Add new enum after `MachineStatusEnum`:

```python
class BackendTypeEnum(str, enum.Enum):
    """Type of machine backend implementation."""
    REAL_HARDWARE = "real_hardware"  # Connects to physical device
    SIMULATOR = "simulator"          # PLR visualizer/simulator
    CHATTERBOX = "chatterbox"        # Print-only, no hardware
    MOCK = "mock"                    # For testing
```

**Validation**:
```bash
uv run python -c "from praxis.backend.models.enums import BackendTypeEnum; print(BackendTypeEnum.SIMULATOR.value)"
# Expected: "simulator"
```

---

### Step 2.2: Create MachineFrontendDefinition Model

**File**: Create `/Users/mar/Projects/pylabpraxis/praxis/backend/models/domain/machine_frontend.py`

**Content** (complete file):

```python
"""Machine Frontend Definition model - represents abstract machine interfaces."""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

from praxis.backend.models.domain.sqlmodel_base import PraxisBase
from praxis.backend.models.enums import MachineCategoryEnum
from praxis.backend.utils.db import JsonVariant

if TYPE_CHECKING:
    from praxis.backend.models.domain.deck import DeckDefinition
    from praxis.backend.models.domain.machine_backend import MachineBackendDefinition


class MachineFrontendDefinitionBase(PraxisBase):
    """Base schema for MachineFrontendDefinition."""

    fqn: str = Field(index=True, unique=True, description="Frontend class FQN (e.g., pylabrobot.liquid_handling.LiquidHandler)")
    description: str | None = Field(default=None)
    plr_category: str | None = Field(default=None, description="Original PyLabRobot category string")
    machine_category: MachineCategoryEnum | None = Field(default=None)

    # Capabilities
    capabilities: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)
    capabilities_config: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)

    # Deck association
    has_deck: bool = Field(default=False)

    # Metadata
    manufacturer: str | None = Field(default=None)
    model: str | None = Field(default=None)


class MachineFrontendDefinition(MachineFrontendDefinitionBase, table=True):
    """Machine frontend definition ORM model."""

    __tablename__ = "machine_frontend_definitions"
    __table_args__ = (UniqueConstraint("name"),)

    machine_category: MachineCategoryEnum = Field(
        default=MachineCategoryEnum.UNKNOWN,
        sa_column=SAEnum(MachineCategoryEnum),
    )

    # Foreign keys
    deck_definition_accession_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="deck_definition_catalog.accession_id",
    )

    # Relationships
    deck_definition: "DeckDefinition | None" = Relationship()
    compatible_backends: list["MachineBackendDefinition"] = Relationship(back_populates="frontend")


class MachineFrontendDefinitionCreate(MachineFrontendDefinitionBase):
    """Schema for creating a MachineFrontendDefinition."""
    pass


class MachineFrontendDefinitionRead(MachineFrontendDefinitionBase):
    """Schema for reading a MachineFrontendDefinition."""
    accession_id: uuid.UUID


class MachineFrontendDefinitionUpdate(SQLModel):
    """Schema for updating a MachineFrontendDefinition."""
    name: str | None = None
    fqn: str | None = None
    description: str | None = None
    plr_category: str | None = None
    machine_category: MachineCategoryEnum | None = None
    capabilities: dict[str, Any] | None = None
    capabilities_config: dict[str, Any] | None = None
    has_deck: bool | None = None
    manufacturer: str | None = None
    model: str | None = None
```

**Validation**:
```bash
uv run python -c "from praxis.backend.models.domain.machine_frontend import MachineFrontendDefinition; print(MachineFrontendDefinition.__tablename__)"
# Expected: "machine_frontend_definitions"
```

---

### Step 2.3: Create MachineBackendDefinition Model

**File**: Create `/Users/mar/Projects/pylabpraxis/praxis/backend/models/domain/machine_backend.py`

**Content** (complete file):

```python
"""Machine Backend Definition model - represents hardware drivers."""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from praxis.backend.models.domain.sqlmodel_base import PraxisBase
from praxis.backend.models.enums import BackendTypeEnum
from praxis.backend.utils.db import JsonVariant

if TYPE_CHECKING:
    from praxis.backend.models.domain.machine_frontend import MachineFrontendDefinition


class MachineBackendDefinitionBase(PraxisBase):
    """Base schema for MachineBackendDefinition."""

    fqn: str = Field(index=True, unique=True, description="Backend class FQN")
    description: str | None = Field(default=None)

    # Classification
    backend_type: BackendTypeEnum = Field(default=BackendTypeEnum.REAL_HARDWARE)

    # Connection requirements (JSON schema)
    connection_config: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)

    # Hardware info
    manufacturer: str | None = Field(default=None)
    model: str | None = Field(default=None)

    # Deprecation flag
    is_deprecated: bool = Field(default=False)


class MachineBackendDefinition(MachineBackendDefinitionBase, table=True):
    """Machine backend definition ORM model."""

    __tablename__ = "machine_backend_definitions"
    __table_args__ = (UniqueConstraint("name"),)

    backend_type: BackendTypeEnum = Field(
        default=BackendTypeEnum.REAL_HARDWARE,
        sa_column=SAEnum(BackendTypeEnum),
    )

    # Foreign key to frontend (required - every backend has exactly one frontend type)
    frontend_definition_accession_id: uuid.UUID = Field(
        foreign_key="machine_frontend_definitions.accession_id",
    )

    # Relationships
    frontend: "MachineFrontendDefinition" = Relationship(back_populates="compatible_backends")


class MachineBackendDefinitionCreate(MachineBackendDefinitionBase):
    """Schema for creating a MachineBackendDefinition."""
    frontend_definition_accession_id: uuid.UUID


class MachineBackendDefinitionRead(MachineBackendDefinitionBase):
    """Schema for reading a MachineBackendDefinition."""
    accession_id: uuid.UUID
    frontend_definition_accession_id: uuid.UUID


class MachineBackendDefinitionUpdate(SQLModel):
    """Schema for updating a MachineBackendDefinition."""
    name: str | None = None
    fqn: str | None = None
    description: str | None = None
    backend_type: BackendTypeEnum | None = None
    connection_config: dict[str, Any] | None = None
    manufacturer: str | None = None
    model: str | None = None
    is_deprecated: bool | None = None
```

**Validation**:
```bash
uv run python -c "from praxis.backend.models.domain.machine_backend import MachineBackendDefinition; print(MachineBackendDefinition.__tablename__)"
# Expected: "machine_backend_definitions"
```

---

### Step 2.4: Update Machine Model with New FKs

**File**: `/Users/mar/Projects/pylabpraxis/praxis/backend/models/domain/machine.py`

**Changes**: Add new foreign keys and relationships to `Machine` class (around line 230-260).

**Add these fields** to the `Machine` class after existing FK fields:

```python
    # NEW: Explicit frontend/backend definition references
    frontend_definition_accession_id: uuid.UUID | None = Field(
        default=None,
        description="Reference to frontend definition",
        foreign_key="machine_frontend_definitions.accession_id",
    )
    backend_definition_accession_id: uuid.UUID | None = Field(
        default=None,
        description="Reference to backend definition",
        foreign_key="machine_backend_definitions.accession_id",
    )

    # Backend instance configuration
    backend_config: dict[str, Any] | None = Field(
        default=None,
        sa_type=JsonVariant,
        description="Backend-specific configuration (port, IP, baud rate, etc.)",
    )
```

**Add these relationships** after existing relationships (around line 305):

```python
    frontend_definition: Optional["MachineFrontendDefinition"] = Relationship()
    backend_definition: Optional["MachineBackendDefinition"] = Relationship()
```

**Add TYPE_CHECKING imports** at top of file:

```python
if TYPE_CHECKING:
    # ... existing imports ...
    from praxis.backend.models.domain.machine_frontend import MachineFrontendDefinition
    from praxis.backend.models.domain.machine_backend import MachineBackendDefinition
```

**Update MachineCreate** to include:
```python
    frontend_definition_accession_id: uuid.UUID | None = None
    backend_definition_accession_id: uuid.UUID | None = None
    backend_config: dict[str, Any] | None = None
```

**Update MachineUpdate** to include:
```python
    frontend_definition_accession_id: uuid.UUID | None = None
    backend_definition_accession_id: uuid.UUID | None = None
    backend_config: dict[str, Any] | None = None
```

**Validation**:
```bash
uv run python -c "from praxis.backend.models.domain.machine import Machine; print('frontend_definition_accession_id' in Machine.model_fields)"
# Expected: True
```

---

### Step 2.5: Update Model Exports

**File**: `/Users/mar/Projects/pylabpraxis/praxis/backend/models/__init__.py`

**Add exports** for new models:

```python
from praxis.backend.models.domain.machine_frontend import (
    MachineFrontendDefinition,
    MachineFrontendDefinitionBase,
    MachineFrontendDefinitionCreate,
    MachineFrontendDefinitionRead,
    MachineFrontendDefinitionUpdate,
)
from praxis.backend.models.domain.machine_backend import (
    MachineBackendDefinition,
    MachineBackendDefinitionBase,
    MachineBackendDefinitionCreate,
    MachineBackendDefinitionRead,
    MachineBackendDefinitionUpdate,
)
from praxis.backend.models.enums import BackendTypeEnum
```

**Validation**:
```bash
uv run python -c "from praxis.backend.models import MachineFrontendDefinition, MachineBackendDefinition, BackendTypeEnum; print('OK')"
# Expected: OK
```

---

### Step 2.6: Update Static Analysis Parser

**File**: `/Users/mar/Projects/pylabpraxis/praxis/backend/utils/plr_static_analysis/parser.py`

**Add two new methods** to `PLRSourceParser` class:

```python
    def discover_frontend_classes(self) -> list[DiscoveredClass]:
        """Discover frontend machine classes only (LiquidHandler, PlateReader, etc.)."""
        all_classes = self.discover_machine_classes()
        return [cls for cls in all_classes if cls.class_type in MACHINE_FRONTEND_TYPES]

    def discover_backend_classes(self) -> list[DiscoveredClass]:
        """Discover backend machine classes only (STARBackend, SimulatorBackend, etc.)."""
        all_classes = self.discover_machine_classes()
        return [cls for cls in all_classes if cls.class_type in MACHINE_BACKEND_TYPES]
```

**Validation**:
```bash
uv run python -c "
from praxis.backend.utils.plr_static_analysis import PLRSourceParser
parser = PLRSourceParser()
frontends = parser.discover_frontend_classes()
backends = parser.discover_backend_classes()
print(f'Frontends: {len(frontends)}, Backends: {len(backends)}')
"
# Expected: Frontends: N, Backends: M (both > 0)
```

---

### Step 2.7: Create Frontend Definition Service

**File**: Create `/Users/mar/Projects/pylabpraxis/praxis/backend/services/machine_frontend_definition.py`

**Content** (complete file):

```python
"""Service for Machine Frontend Definition discovery and management."""

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.domain.machine_frontend import (
    MachineFrontendDefinition,
    MachineFrontendDefinitionCreate,
    MachineFrontendDefinitionUpdate,
)
from praxis.backend.models.enums import MachineCategoryEnum
from praxis.backend.services.plr_type_base import DiscoverableTypeServiceBase
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.plr_static_analysis import (
    PLRSourceParser,
    find_plr_source_root,
    MACHINE_FRONTEND_TYPES,
)

logger = get_logger(__name__)


class MachineFrontendDefinitionService(
    DiscoverableTypeServiceBase[
        MachineFrontendDefinition,
        MachineFrontendDefinitionCreate,
        MachineFrontendDefinitionUpdate,
    ]
):
    """Service for discovering and syncing machine frontend definitions."""

    def __init__(self, db: AsyncSession, plr_source_path: Path | None = None) -> None:
        self.db = db
        self._plr_source_path = plr_source_path
        self._parser: PLRSourceParser | None = None

    @property
    def parser(self) -> PLRSourceParser:
        if self._parser is None:
            plr_path = self._plr_source_path or find_plr_source_root()
            self._parser = PLRSourceParser(plr_path)
        return self._parser

    @property
    def _orm_model(self) -> type[MachineFrontendDefinition]:
        return MachineFrontendDefinition

    async def discover_and_synchronize_type_definitions(self) -> list[MachineFrontendDefinition]:
        """Discover frontend definitions from PyLabRobot source and sync to DB."""
        logger.info("Discovering machine frontend types...")

        discovered = self.parser.discover_frontend_classes()
        logger.info("Discovered %d frontend types.", len(discovered))

        synced = []
        for cls in discovered:
            if cls.is_abstract:
                continue

            definition = await self._upsert_frontend(cls)
            synced.append(definition)

        await self.db.commit()
        logger.info("Synchronized %d frontend definitions.", len(synced))
        return synced

    async def _upsert_frontend(self, cls) -> MachineFrontendDefinition:
        """Create or update a frontend definition."""
        existing = await self.db.execute(
            select(MachineFrontendDefinition).filter(MachineFrontendDefinition.fqn == cls.fqn)
        )
        existing_def = existing.scalar_one_or_none()

        # Map PLRClassType to MachineCategoryEnum
        category_name = cls.class_type.name if cls.class_type else "UNKNOWN"
        try:
            machine_category = MachineCategoryEnum[category_name]
        except KeyError:
            machine_category = MachineCategoryEnum.UNKNOWN

        if existing_def:
            existing_def.name = cls.name
            existing_def.description = cls.docstring
            existing_def.machine_category = machine_category
            existing_def.manufacturer = cls.manufacturer
            existing_def.capabilities = cls.to_capabilities_dict()
            self.db.add(existing_def)
            return existing_def

        new_def = MachineFrontendDefinition(
            name=cls.name,
            fqn=cls.fqn,
            description=cls.docstring,
            plr_category=cls.class_type.value if cls.class_type else None,
            machine_category=machine_category,
            manufacturer=cls.manufacturer,
            capabilities=cls.to_capabilities_dict(),
            capabilities_config=cls.capabilities_config.model_dump() if cls.capabilities_config else None,
        )
        self.db.add(new_def)
        return new_def


class MachineFrontendDefinitionCRUDService(
    CRUDBase[
        MachineFrontendDefinition,
        MachineFrontendDefinitionCreate,
        MachineFrontendDefinitionUpdate,
    ]
):
    """CRUD service for frontend definitions."""
    pass
```

**Validation**:
```bash
uv run python -c "from praxis.backend.services.machine_frontend_definition import MachineFrontendDefinitionService; print('OK')"
# Expected: OK
```

---

### Step 2.8: Create Backend Definition Service

**File**: Create `/Users/mar/Projects/pylabpraxis/praxis/backend/services/machine_backend_definition.py`

**Content** (complete file):

```python
"""Service for Machine Backend Definition discovery and management."""

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.domain.machine_backend import (
    MachineBackendDefinition,
    MachineBackendDefinitionCreate,
    MachineBackendDefinitionUpdate,
)
from praxis.backend.models.domain.machine_frontend import MachineFrontendDefinition
from praxis.backend.models.enums import BackendTypeEnum
from praxis.backend.services.plr_type_base import DiscoverableTypeServiceBase
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.plr_static_analysis import (
    BACKEND_TYPE_TO_FRONTEND_FQN,
    PLRSourceParser,
    find_plr_source_root,
)

logger = get_logger(__name__)


class MachineBackendDefinitionService(
    DiscoverableTypeServiceBase[
        MachineBackendDefinition,
        MachineBackendDefinitionCreate,
        MachineBackendDefinitionUpdate,
    ]
):
    """Service for discovering and syncing machine backend definitions."""

    def __init__(self, db: AsyncSession, plr_source_path: Path | None = None) -> None:
        self.db = db
        self._plr_source_path = plr_source_path
        self._parser: PLRSourceParser | None = None

    @property
    def parser(self) -> PLRSourceParser:
        if self._parser is None:
            plr_path = self._plr_source_path or find_plr_source_root()
            self._parser = PLRSourceParser(plr_path)
        return self._parser

    @property
    def _orm_model(self) -> type[MachineBackendDefinition]:
        return MachineBackendDefinition

    async def discover_and_synchronize_type_definitions(self) -> list[MachineBackendDefinition]:
        """Discover backend definitions from PyLabRobot source and sync to DB."""
        logger.info("Discovering machine backend types...")

        discovered = self.parser.discover_backend_classes()
        logger.info("Discovered %d backend types.", len(discovered))

        synced = []
        for cls in discovered:
            if cls.is_abstract:
                continue

            definition = await self._upsert_backend(cls)
            if definition:
                synced.append(definition)

        await self.db.commit()
        logger.info("Synchronized %d backend definitions.", len(synced))
        return synced

    async def _upsert_backend(self, cls) -> MachineBackendDefinition | None:
        """Create or update a backend definition."""
        # Find the frontend this backend is compatible with
        frontend_fqn = BACKEND_TYPE_TO_FRONTEND_FQN.get(cls.class_type)
        if not frontend_fqn:
            logger.warning("No frontend mapping for backend type %s", cls.class_type)
            return None

        # Look up frontend definition
        frontend_result = await self.db.execute(
            select(MachineFrontendDefinition).filter(MachineFrontendDefinition.fqn == frontend_fqn)
        )
        frontend_def = frontend_result.scalar_one_or_none()

        if not frontend_def:
            logger.warning("Frontend %s not found for backend %s", frontend_fqn, cls.fqn)
            return None

        # Determine backend type
        backend_type = BackendTypeEnum.REAL_HARDWARE
        if cls.is_simulated():
            name_lower = cls.name.lower()
            if "chatterbox" in name_lower:
                backend_type = BackendTypeEnum.CHATTERBOX
            elif "mock" in name_lower:
                backend_type = BackendTypeEnum.MOCK
            else:
                backend_type = BackendTypeEnum.SIMULATOR

        # Check for existing
        existing = await self.db.execute(
            select(MachineBackendDefinition).filter(MachineBackendDefinition.fqn == cls.fqn)
        )
        existing_def = existing.scalar_one_or_none()

        if existing_def:
            existing_def.name = cls.name
            existing_def.description = cls.docstring
            existing_def.backend_type = backend_type
            existing_def.manufacturer = cls.manufacturer
            existing_def.frontend_definition_accession_id = frontend_def.accession_id
            existing_def.connection_config = cls.connection_config.model_dump() if cls.connection_config else None
            self.db.add(existing_def)
            return existing_def

        new_def = MachineBackendDefinition(
            name=cls.name,
            fqn=cls.fqn,
            description=cls.docstring,
            backend_type=backend_type,
            manufacturer=cls.manufacturer,
            frontend_definition_accession_id=frontend_def.accession_id,
            connection_config=cls.connection_config.model_dump() if cls.connection_config else None,
        )
        self.db.add(new_def)
        return new_def


class MachineBackendDefinitionCRUDService(
    CRUDBase[
        MachineBackendDefinition,
        MachineBackendDefinitionCreate,
        MachineBackendDefinitionUpdate,
    ]
):
    """CRUD service for backend definitions."""
    pass
```

**Validation**:
```bash
uv run python -c "from praxis.backend.services.machine_backend_definition import MachineBackendDefinitionService; print('OK')"
# Expected: OK
```

---

### Step 2.9: Create API Endpoints for Frontend Definitions

**File**: Create `/Users/mar/Projects/pylabpraxis/praxis/backend/api/machine_frontends.py`

**Content** (complete file):

```python
"""API endpoints for Machine Frontend Definitions."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.api.deps import get_db
from praxis.backend.models import (
    MachineFrontendDefinition,
    MachineFrontendDefinitionCreate,
    MachineFrontendDefinitionRead,
    MachineFrontendDefinitionUpdate,
)
from praxis.backend.services.machine_frontend_definition import (
    MachineFrontendDefinitionCRUDService,
)

router = APIRouter()


@router.get("/", response_model=list[MachineFrontendDefinitionRead])
async def list_frontend_definitions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all machine frontend definitions."""
    service = MachineFrontendDefinitionCRUDService(MachineFrontendDefinition, db)
    return await service.get_multi(skip=skip, limit=limit)


@router.get("/{accession_id}", response_model=MachineFrontendDefinitionRead)
async def get_frontend_definition(
    accession_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific frontend definition."""
    service = MachineFrontendDefinitionCRUDService(MachineFrontendDefinition, db)
    result = await service.get(accession_id)
    if not result:
        raise HTTPException(status_code=404, detail="Frontend definition not found")
    return result


@router.get("/{accession_id}/backends", response_model=list)
async def get_compatible_backends(
    accession_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get backends compatible with this frontend."""
    from praxis.backend.models import MachineBackendDefinition, MachineBackendDefinitionRead
    from sqlalchemy import select

    result = await db.execute(
        select(MachineBackendDefinition).filter(
            MachineBackendDefinition.frontend_definition_accession_id == accession_id
        )
    )
    backends = result.scalars().all()
    return backends


@router.post("/", response_model=MachineFrontendDefinitionRead, status_code=status.HTTP_201_CREATED)
async def create_frontend_definition(
    data: MachineFrontendDefinitionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new frontend definition."""
    service = MachineFrontendDefinitionCRUDService(MachineFrontendDefinition, db)
    return await service.create(obj_in=data)


@router.put("/{accession_id}", response_model=MachineFrontendDefinitionRead)
async def update_frontend_definition(
    accession_id: UUID,
    data: MachineFrontendDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a frontend definition."""
    service = MachineFrontendDefinitionCRUDService(MachineFrontendDefinition, db)
    existing = await service.get(accession_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Frontend definition not found")
    return await service.update(db_obj=existing, obj_in=data)


@router.delete("/{accession_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_frontend_definition(
    accession_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a frontend definition."""
    service = MachineFrontendDefinitionCRUDService(MachineFrontendDefinition, db)
    existing = await service.get(accession_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Frontend definition not found")
    await service.remove(id=accession_id)
```

---

### Step 2.10: Create API Endpoints for Backend Definitions

**File**: Create `/Users/mar/Projects/pylabpraxis/praxis/backend/api/machine_backends.py`

**Content** (complete file):

```python
"""API endpoints for Machine Backend Definitions."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.api.deps import get_db
from praxis.backend.models import (
    MachineBackendDefinition,
    MachineBackendDefinitionCreate,
    MachineBackendDefinitionRead,
    MachineBackendDefinitionUpdate,
)
from praxis.backend.services.machine_backend_definition import (
    MachineBackendDefinitionCRUDService,
)

router = APIRouter()


@router.get("/", response_model=list[MachineBackendDefinitionRead])
async def list_backend_definitions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all machine backend definitions."""
    service = MachineBackendDefinitionCRUDService(MachineBackendDefinition, db)
    return await service.get_multi(skip=skip, limit=limit)


@router.get("/{accession_id}", response_model=MachineBackendDefinitionRead)
async def get_backend_definition(
    accession_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific backend definition."""
    service = MachineBackendDefinitionCRUDService(MachineBackendDefinition, db)
    result = await service.get(accession_id)
    if not result:
        raise HTTPException(status_code=404, detail="Backend definition not found")
    return result


@router.post("/", response_model=MachineBackendDefinitionRead, status_code=status.HTTP_201_CREATED)
async def create_backend_definition(
    data: MachineBackendDefinitionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new backend definition."""
    service = MachineBackendDefinitionCRUDService(MachineBackendDefinition, db)
    return await service.create(obj_in=data)


@router.put("/{accession_id}", response_model=MachineBackendDefinitionRead)
async def update_backend_definition(
    accession_id: UUID,
    data: MachineBackendDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a backend definition."""
    service = MachineBackendDefinitionCRUDService(MachineBackendDefinition, db)
    existing = await service.get(accession_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Backend definition not found")
    return await service.update(db_obj=existing, obj_in=data)


@router.delete("/{accession_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_backend_definition(
    accession_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a backend definition."""
    service = MachineBackendDefinitionCRUDService(MachineBackendDefinition, db)
    existing = await service.get(accession_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Backend definition not found")
    await service.remove(id=accession_id)
```

---

### Step 2.11: Register New API Routers

**File**: `/Users/mar/Projects/pylabpraxis/praxis/backend/main.py`

**Add imports** near other router imports:

```python
from praxis.backend.api import machine_frontends, machine_backends
```

**Add router registrations** after existing machine router:

```python
app.include_router(
    machine_frontends.router,
    prefix="/api/v1/machine-frontends",
    tags=["Machine Frontends"],
)
app.include_router(
    machine_backends.router,
    prefix="/api/v1/machine-backends",
    tags=["Machine Backends"],
)
```

**Validation**:
```bash
uv run python -c "from praxis.backend.main import app; routes = [r.path for r in app.routes]; print('/api/v1/machine-frontends/' in str(routes))"
# Expected: True
```

---

### Step 2.12: Update Machine Instantiation (Critical)

**File**: `/Users/mar/Projects/pylabpraxis/praxis/backend/core/workcell_runtime/machine_manager.py`

**Replace the instantiation logic** around line 95. Find this code:

```python
target_class = get_class_from_fqn(machine_model.fqn)
```

**Replace with**:

```python
# Determine FQN based on new frontend/backend separation
if machine_model.backend_definition_accession_id and machine_model.frontend_definition_accession_id:
    # New pattern: instantiate backend, pass to frontend
    if machine_model.backend_definition is None or machine_model.frontend_definition is None:
        # Eager load the relationships if not already loaded
        from sqlalchemy.orm import selectinload
        from praxis.backend.models import Machine as MachineModel
        async with runtime.db_session_factory() as db_session:
            from sqlalchemy import select
            result = await db_session.execute(
                select(MachineModel)
                .options(selectinload(MachineModel.frontend_definition))
                .options(selectinload(MachineModel.backend_definition))
                .filter(MachineModel.accession_id == machine_model.accession_id)
            )
            machine_model = result.scalar_one()

    backend_fqn = machine_model.backend_definition.fqn
    frontend_fqn = machine_model.frontend_definition.fqn
    backend_config = machine_model.backend_config or {}

    # Instantiate backend
    backend_class = get_class_from_fqn(backend_fqn)
    backend_instance = backend_class(**backend_config)

    # Instantiate frontend with backend
    target_class = get_class_from_fqn(frontend_fqn)
    machine_config["backend"] = backend_instance
else:
    # Legacy pattern: use fqn directly (backwards compatibility)
    target_class = get_class_from_fqn(machine_model.fqn)
```

**Validation**: Run existing machine tests to ensure backwards compatibility.

---

### Step 2.13: Regenerate Databases and Schema

**Commands** (run in order):

```bash
cd /Users/mar/Projects/pylabpraxis

# Step 1: Generate new SQLite schema and TypeScript interfaces
uv run python scripts/generate_browser_schema.py

# Step 2: Regenerate browser database with new tables
uv run python scripts/generate_browser_db.py

# Step 3: Generate OpenAPI spec
uv run python scripts/generate_openapi.py

# Step 4: Regenerate TypeScript API client (if using openapi-generator)
# Check praxis/web-client/package.json for the actual command
cd praxis/web-client
npm run generate:api  # or similar - check package.json
```

**Validation**:
```bash
# Check schema has new tables
grep -c "machine_frontend_definitions\|machine_backend_definitions" praxis/web-client/src/assets/db/schema.sql
# Expected: 2 (both tables present)

# Check TypeScript interfaces generated
grep -c "MachineFrontendDefinition\|MachineBackendDefinition" praxis/web-client/src/app/core/db/schema.ts
# Expected: 2 (both interfaces present)
```

---

### Step 2.14: Update Frontend Repositories

**File**: `/Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/db/repositories.ts`

**Add new repository classes** after `MachineDefinitionRepository`:

```typescript
export class MachineFrontendDefinitionRepository extends SqliteRepository<WithIndex<MachineFrontendDefinition>> {
    constructor(db: Database) {
        super(db, 'machine_frontend_definitions', 'accession_id');
    }

    findByFqn(fqn: string): MachineFrontendDefinition | null {
        const results = this.findBy({ fqn } as Partial<WithIndex<MachineFrontendDefinition>>);
        return results.length > 0 ? results[0] : null;
    }

    findByCategory(category: string): MachineFrontendDefinition[] {
        return this.findBy({ machine_category: category } as Partial<WithIndex<MachineFrontendDefinition>>);
    }
}

export class MachineBackendDefinitionRepository extends SqliteRepository<WithIndex<MachineBackendDefinition>> {
    constructor(db: Database) {
        super(db, 'machine_backend_definitions', 'accession_id');
    }

    findByFqn(fqn: string): MachineBackendDefinition | null {
        const results = this.findBy({ fqn } as Partial<WithIndex<MachineBackendDefinition>>);
        return results.length > 0 ? results[0] : null;
    }

    findByFrontend(frontendId: string): MachineBackendDefinition[] {
        return this.findBy({ frontend_definition_accession_id: frontendId } as Partial<WithIndex<MachineBackendDefinition>>);
    }
}
```

**Add imports** for the new schema types at top of file.

---

### Step 2.15: Run All Tests

**Commands**:

```bash
cd /Users/mar/Projects/pylabpraxis

# Backend unit tests
uv run pytest tests/models/ -v --tb=short

# Backend service tests
uv run pytest tests/services/ -v --tb=short

# Backend API tests
uv run pytest tests/api/ -v --tb=short

# Full backend test suite
uv run pytest tests/ -v --tb=short -x

# Frontend tests
cd praxis/web-client
npm test -- --run
```

**Expected**: All tests pass. If any fail, fix before proceeding.

---

### Step 2.16: Manual Validation

**Start the backend**:
```bash
cd /Users/mar/Projects/pylabpraxis
uv run uvicorn praxis.backend.main:app --reload --port 8000
```

**Test endpoints**:
```bash
# List frontend definitions
curl http://localhost:8000/api/v1/machine-frontends/

# List backend definitions
curl http://localhost:8000/api/v1/machine-backends/

# List machines (should still work - backwards compat)
curl http://localhost:8000/api/v1/machines/
```

**Expected**: All return valid JSON (possibly empty arrays if no data seeded yet).

---

## Phase 3: Testing Strategy

> **For executing agent**: Run these tests in order. All tests must pass before proceeding to next section.

### 3.1 Backend Unit Tests

**Create test file**: `/Users/mar/Projects/pylabpraxis/tests/models/test_machine_frontend_definition.py`

```python
"""Tests for MachineFrontendDefinition model."""

import pytest
from praxis.backend.models import (
    MachineFrontendDefinition,
    MachineFrontendDefinitionCreate,
    MachineCategoryEnum,
)


def test_frontend_definition_create():
    """Test creating a frontend definition."""
    create_data = MachineFrontendDefinitionCreate(
        name="Test Liquid Handler",
        fqn="pylabrobot.liquid_handling.LiquidHandler",
        machine_category=MachineCategoryEnum.LIQUID_HANDLER,
    )
    assert create_data.fqn == "pylabrobot.liquid_handling.LiquidHandler"


def test_frontend_definition_model():
    """Test frontend definition model instantiation."""
    model = MachineFrontendDefinition(
        name="Test Frontend",
        fqn="test.frontend.TestFrontend",
        machine_category=MachineCategoryEnum.UNKNOWN,
    )
    assert model.fqn == "test.frontend.TestFrontend"
    assert model.has_deck is False
```

**Create test file**: `/Users/mar/Projects/pylabpraxis/tests/models/test_machine_backend_definition.py`

```python
"""Tests for MachineBackendDefinition model."""

import pytest
import uuid
from praxis.backend.models import (
    MachineBackendDefinition,
    MachineBackendDefinitionCreate,
    BackendTypeEnum,
)


def test_backend_definition_create():
    """Test creating a backend definition."""
    frontend_id = uuid.uuid4()
    create_data = MachineBackendDefinitionCreate(
        name="Test STAR Backend",
        fqn="pylabrobot.liquid_handling.backends.hamilton.STAR",
        backend_type=BackendTypeEnum.REAL_HARDWARE,
        frontend_definition_accession_id=frontend_id,
    )
    assert create_data.backend_type == BackendTypeEnum.REAL_HARDWARE


def test_backend_type_enum():
    """Test BackendTypeEnum values."""
    assert BackendTypeEnum.REAL_HARDWARE.value == "real_hardware"
    assert BackendTypeEnum.SIMULATOR.value == "simulator"
    assert BackendTypeEnum.CHATTERBOX.value == "chatterbox"
    assert BackendTypeEnum.MOCK.value == "mock"
```

**Run unit tests**:
```bash
cd /Users/mar/Projects/pylabpraxis
uv run pytest tests/models/test_machine_frontend_definition.py tests/models/test_machine_backend_definition.py -v
# Expected: All tests pass
```

### 3.2 Service Tests

**Create test file**: `/Users/mar/Projects/pylabpraxis/tests/services/test_machine_frontend_definition_service.py`

```python
"""Tests for MachineFrontendDefinitionService."""

import pytest
from praxis.backend.utils.plr_static_analysis import PLRSourceParser, MACHINE_FRONTEND_TYPES


def test_discover_frontend_classes():
    """Test that frontend discovery finds frontends only."""
    parser = PLRSourceParser()
    frontends = parser.discover_frontend_classes()

    assert len(frontends) > 0, "Should discover at least one frontend"

    for frontend in frontends:
        assert frontend.class_type in MACHINE_FRONTEND_TYPES, \
            f"Class {frontend.name} should be a frontend type, got {frontend.class_type}"
```

**Create test file**: `/Users/mar/Projects/pylabpraxis/tests/services/test_machine_backend_definition_service.py`

```python
"""Tests for MachineBackendDefinitionService."""

import pytest
from praxis.backend.utils.plr_static_analysis import PLRSourceParser, MACHINE_BACKEND_TYPES


def test_discover_backend_classes():
    """Test that backend discovery finds backends only."""
    parser = PLRSourceParser()
    backends = parser.discover_backend_classes()

    assert len(backends) > 0, "Should discover at least one backend"

    for backend in backends:
        assert backend.class_type in MACHINE_BACKEND_TYPES, \
            f"Class {backend.name} should be a backend type, got {backend.class_type}"


def test_simulator_detection():
    """Test that simulators are correctly identified."""
    parser = PLRSourceParser()
    backends = parser.discover_backend_classes()

    simulators = [b for b in backends if b.is_simulated()]
    assert len(simulators) > 0, "Should find at least one simulator backend"
```

**Run service tests**:
```bash
uv run pytest tests/services/test_machine_frontend_definition_service.py tests/services/test_machine_backend_definition_service.py -v
# Expected: All tests pass
```

### 3.3 API Tests

**Create test file**: `/Users/mar/Projects/pylabpraxis/tests/api/test_machine_frontends_api.py`

```python
"""Tests for machine frontend API endpoints."""

import pytest
from httpx import AsyncClient
from praxis.backend.main import app


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_list_frontend_definitions(client):
    """Test listing frontend definitions."""
    response = await client.get("/api/v1/machine-frontends/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_nonexistent_frontend(client):
    """Test getting a nonexistent frontend definition."""
    import uuid
    response = await client.get(f"/api/v1/machine-frontends/{uuid.uuid4()}")
    assert response.status_code == 404
```

**Run API tests**:
```bash
uv run pytest tests/api/test_machine_frontends_api.py -v
# Expected: All tests pass
```

### 3.4 Full Test Suite

```bash
cd /Users/mar/Projects/pylabpraxis

# Run all backend tests
uv run pytest tests/ -v --tb=short -x

# If tests fail, fix issues and re-run
# Do NOT proceed until all tests pass
```

**Expected**: 100% pass rate on all tests.

### 3.5 Frontend Tests

```bash
cd /Users/mar/Projects/pylabpraxis/praxis/web-client

# Run frontend tests
npm test -- --run

# Build to check for TypeScript errors
npm run build
```

**Expected**: Build succeeds with no TypeScript errors.

### 3.6 Integration Validation

**Start backend and verify new endpoints work**:

```bash
# Terminal 1: Start backend
cd /Users/mar/Projects/pylabpraxis
uv run uvicorn praxis.backend.main:app --reload --port 8000

# Terminal 2: Test endpoints
curl -s http://localhost:8000/api/v1/machine-frontends/ | python -m json.tool
curl -s http://localhost:8000/api/v1/machine-backends/ | python -m json.tool
curl -s http://localhost:8000/api/v1/machines/ | python -m json.tool

# All should return valid JSON (arrays, possibly empty)
```

### 3.7 Regression Checklist

Before considering migration complete, verify:

```bash
# Check 1: Import all new models without error
uv run python -c "
from praxis.backend.models import (
    MachineFrontendDefinition,
    MachineBackendDefinition,
    BackendTypeEnum,
    Machine,
)
print('✓ All models import successfully')
"

# Check 2: Static analysis works
uv run python -c "
from praxis.backend.utils.plr_static_analysis import PLRSourceParser
parser = PLRSourceParser()
frontends = parser.discover_frontend_classes()
backends = parser.discover_backend_classes()
print(f'✓ Discovered {len(frontends)} frontends and {len(backends)} backends')
"

# Check 3: Database generation scripts work
uv run python scripts/generate_browser_schema.py
uv run python scripts/generate_browser_db.py
echo "✓ Database generation completed"

# Check 4: TypeScript types generated
grep -q "MachineFrontendDefinition" praxis/web-client/src/app/core/db/schema.ts && \
grep -q "MachineBackendDefinition" praxis/web-client/src/app/core/db/schema.ts && \
echo "✓ TypeScript interfaces generated"

# Check 5: Backwards compatibility
uv run python -c "
from praxis.backend.models import Machine
m = Machine(name='test', fqn='test.backend.TestBackend')
print(f'✓ Machine with legacy fqn still works: {m.fqn}')
"
```

**All 5 checks must pass before migration is considered complete.**

---

## Phase 4: Rollback Plan

Since this is a clean break:

1. **Before starting**: Tag current commit
   ```bash
   git tag pre-machine-separation
   ```

2. **If issues arise**:
   ```bash
   git checkout pre-machine-separation
   # Regenerate databases
   ```

3. **No data migration needed** - databases are regenerated

---

## Appendix A: Files Changed Summary

### New Files (12 files)
| File | Purpose |
|------|---------|
| `praxis/backend/models/domain/machine_frontend.py` | MachineFrontendDefinition ORM model |
| `praxis/backend/models/domain/machine_backend.py` | MachineBackendDefinition ORM model |
| `praxis/backend/services/machine_frontend_definition.py` | Frontend discovery and CRUD service |
| `praxis/backend/services/machine_backend_definition.py` | Backend discovery and CRUD service |
| `praxis/backend/api/machine_frontends.py` | REST endpoints for frontends |
| `praxis/backend/api/machine_backends.py` | REST endpoints for backends |
| `tests/models/test_machine_frontend_definition.py` | Unit tests for frontend model |
| `tests/models/test_machine_backend_definition.py` | Unit tests for backend model |
| `tests/services/test_machine_frontend_definition_service.py` | Service tests |
| `tests/services/test_machine_backend_definition_service.py` | Service tests |
| `tests/api/test_machine_frontends_api.py` | API endpoint tests |
| `tests/api/test_machine_backends_api.py` | API endpoint tests |

### Modified Files (17 files)
| File | Changes |
|------|---------|
| `praxis/backend/models/enums/machine.py` | Add BackendTypeEnum |
| `praxis/backend/models/domain/machine.py` | Add FKs: frontend_definition_accession_id, backend_definition_accession_id, backend_config |
| `praxis/backend/models/__init__.py` | Export new models and enum |
| `praxis/backend/utils/plr_static_analysis/parser.py` | Add discover_frontend_classes(), discover_backend_classes() |
| `praxis/backend/core/workcell_runtime/machine_manager.py` | Add backend selection logic at instantiation |
| `praxis/backend/main.py` | Register new routers |
| `scripts/generate_browser_db.py` | Add discovery for new tables (optional) |
| `praxis/web-client/src/app/core/db/schema.ts` | Auto-generated - new interfaces |
| `praxis/web-client/src/app/core/db/repositories.ts` | Add MachineFrontendDefinitionRepository, MachineBackendDefinitionRepository |

### Generated Files (auto-updated by scripts)
| File | Generator |
|------|-----------|
| `praxis/web-client/src/assets/db/schema.sql` | `generate_browser_schema.py` |
| `praxis/web-client/src/app/core/db/schema.ts` | `generate_browser_schema.py` |
| `praxis/web-client/src/app/core/db/enums.ts` | `generate_browser_schema.py` |
| `praxis/web-client/src/assets/db/praxis.db` | `generate_browser_db.py` |
| `praxis/web-client/src/assets/api/openapi.json` | `generate_openapi.py` |

---

## Appendix B: Troubleshooting

### Import Errors

**Problem**: `ImportError: cannot import name 'BackendTypeEnum'`
**Solution**: Ensure enum is exported in `praxis/backend/models/enums/__init__.py`:
```python
from praxis.backend.models.enums.machine import BackendTypeEnum
```

**Problem**: `ImportError: cannot import name 'MachineFrontendDefinition'`
**Solution**: Ensure export in `praxis/backend/models/__init__.py`.

### Circular Import Errors

**Problem**: `ImportError: cannot import name 'MachineBackendDefinition' (partially initialized)`
**Solution**: Use `TYPE_CHECKING` guard:
```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from praxis.backend.models.domain.machine_backend import MachineBackendDefinition
```

### Database Errors

**Problem**: `sqlite3.OperationalError: no such table: machine_frontend_definitions`
**Solution**: Regenerate database:
```bash
uv run python scripts/generate_browser_schema.py
uv run python scripts/generate_browser_db.py
```

**Problem**: `sqlalchemy.exc.OperationalError: foreign key mismatch`
**Solution**: Drop database and regenerate (clean break):
```bash
rm praxis/web-client/src/assets/db/praxis.db
uv run python scripts/generate_browser_db.py
```

### API Errors

**Problem**: `404 Not Found` on `/api/v1/machine-frontends/`
**Solution**: Ensure router is registered in `main.py`:
```python
from praxis.backend.api import machine_frontends
app.include_router(machine_frontends.router, prefix="/api/v1/machine-frontends", tags=["Machine Frontends"])
```

### TypeScript Errors

**Problem**: `Cannot find name 'MachineFrontendDefinition'`
**Solution**: Regenerate TypeScript interfaces:
```bash
uv run python scripts/generate_browser_schema.py
```

### Test Failures

**Problem**: Tests fail with `fixture 'client' not found`
**Solution**: Ensure pytest-asyncio is installed:
```bash
uv add pytest-asyncio --dev
```

---

## Appendix C: Decision Log

| Decision | Rationale |
|----------|-----------|
| Clean break (no migration) | User confirmed no active state, DBs can be regenerated |
| Separate tables (not embedded) | Proper normalization, enables querying backends independently |
| Backend requires frontend FK | Every backend must be compatible with exactly one frontend type |
| Keep Machine.fqn temporarily | Backwards compat during transition - machines without new FKs still work |
| BackendTypeEnum | Clear distinction between real hardware, simulators, test backends |
| Backend instantiated first | Matches PLR pattern: `LiquidHandler(backend=STARBackend(...))` |
| Frontends discovered before backends | Backends require frontend FK, so frontends must exist first |

---

## Appendix D: Key Code Patterns

### How Machine Instantiation Works (After Migration)

```python
# In machine_manager.py - the core instantiation pattern
if machine_model.backend_definition_accession_id:
    # New pattern: instantiate backend first, inject into frontend
    backend = get_class_from_fqn(machine_model.backend_definition.fqn)(**backend_config)
    frontend = get_class_from_fqn(machine_model.frontend_definition.fqn)(backend=backend, ...)
else:
    # Legacy pattern: direct FQN instantiation (backwards compat)
    target_class = get_class_from_fqn(machine_model.fqn)
```

### Discovery Order Matters

```python
# In discovery API endpoint - frontends MUST be synced before backends
async def sync_all_definitions(db: AsyncSession):
    # Step 1: Sync frontends first (backends have FK to frontends)
    frontend_service = MachineFrontendDefinitionService(db)
    await frontend_service.discover_and_synchronize_type_definitions()

    # Step 2: Sync backends (can now reference frontends)
    backend_service = MachineBackendDefinitionService(db)
    await backend_service.discover_and_synchronize_type_definitions()
```

### Frontend/Backend Relationship Query

```python
# Get all backends compatible with a frontend
from sqlalchemy import select
result = await db.execute(
    select(MachineBackendDefinition)
    .filter(MachineBackendDefinition.frontend_definition_accession_id == frontend.accession_id)
)
backends = result.scalars().all()
```

---

## Appendix E: Post-Migration Cleanup (Future)

After migration is stable and all machines use new pattern:

1. **Remove deprecated fields from Machine**:
   - `connection_info` → replaced by `backend_config`
   - `simulation_backend_name` → replaced by backend_definition FK
   - `is_simulation_override` → derived from backend_definition.backend_type

2. **Remove deprecated MachineDefinition table**:
   - Replace with MachineFrontendDefinition + MachineBackendDefinition
   - Update all references

3. **Remove backwards compatibility code**:
   - `machine_manager.py` legacy instantiation path
   - Direct fqn usage in Machine model

4. **Update frontend to only use new pattern**:
   - Machine creation flow: select frontend → select backend → configure
   - Remove legacy machine definition handling

---

## Completion Checklist

Before marking migration as complete:

- [ ] All Phase 2 steps executed
- [ ] All Phase 3 tests pass
- [ ] All Phase 3.7 regression checks pass
- [ ] New API endpoints respond correctly
- [ ] Browser mode works with new schema
- [ ] Existing machines still work (backwards compat)
- [ ] Documentation updated (if any exists)
- [ ] Git commit created with summary of changes

**Final command to verify success**:
```bash
cd /Users/mar/Projects/pylabpraxis
uv run pytest tests/ -v --tb=short && echo "✓ ALL TESTS PASS - Migration complete"
```
