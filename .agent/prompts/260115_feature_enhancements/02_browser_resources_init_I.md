# Agent Prompt: Browser Mode Resource Initialization - Inspection

**Status:** 🔵 Ready
**Priority:** P2
**Batch:** [260115_feature_enhancements](./README.md)
**Difficulty:** Easy
**Dependencies:** None
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Inspect the current resource initialization in browser mode to understand how labware assets are seeded and where to inject "1 of each resource" logic.

**Problem**: In browser mode, users currently don't have any labware resources pre-populated. They should start with 1 of every labware type (plates, tip racks, etc.) and unlimited quantities for consumables (tips).

**Goal**: Document:

1. **Current Seeding Logic**: Where and how `SqliteService` seeds assets in browser mode.
2. **Resource Definitions**: What labware definitions exist in the catalog/PLR.
3. **Consumable vs Non-Consumable**: How to distinguish consumables (unlimited) from discrete labware (qty=1).
4. **Inventory Integration**: How seeded resources appear in the asset inventory UI.

## 2. Technical Implementation Strategy

**Inspection Phase**:

1. **SqliteService Review**: Read `praxis/web-client/src/app/core/services/sqlite.service.ts` → `seedDefaultAssets` and related methods.
2. **Resource Models**: Read `praxis/web-client/src/app/core/models/` for resource/labware type definitions.
3. **PLR Catalog**: Identify where labware definitions come from (likely PLR resource catalog or local definitions).
4. **Asset Service**: Read `praxis/web-client/src/app/core/services/asset.service.ts` for how resources are managed.

**Output Generation**:

- Create `references/browser_resources_audit.md` with:
  - Current seeding flow analysis
  - List of available labware definitions
  - Consumable classification strategy
  - Integration points for new seeding logic

## 3. Context & References

**Relevant Skills**:

- `frontend-design` (Angular service patterns)

**Primary Files to Inspect**:

| Path | Description |
| :--- | :--- |
| `praxis/web-client/src/app/core/services/sqlite.service.ts` | Asset seeding logic |
| `praxis/web-client/src/app/core/services/asset.service.ts` | Asset management |
| `praxis/web-client/src/app/core/models/resource.model.ts` | Resource type definitions |
| `external/pylabrobot/pylabrobot/resources/` | PLR resource catalog |

## 4. Constraints & Conventions

- **Do Not Implement**: This is an INSPECTION task (Type I).
- **Scope**: Browser mode only (not backend mode).
- **Note**: Resources are labware only (not machines, not reagents).

## 5. Verification Plan

**Definition of Done**:

1. `references/browser_resources_audit.md` exists with seeding flow analysis.
2. List of labware types to seed is documented.
3. Consumable vs discrete classification is clear.
4. Prompt `02_browser_resources_init_P.md` is ready to proceed.

---

## On Completion

- [ ] Create `references/browser_resources_audit.md`
- [ ] Mark this prompt complete in batch README
- [ ] Proceed to `02_browser_resources_init_P.md`
