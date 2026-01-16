# Agent Prompt: Browser Mode Resource Initialization - Execution

**Status:** ⚪ Queued
**Priority:** P2
**Batch:** [260115_feature_enhancements](./README.md)
**Difficulty:** Easy
**Dependencies:** `02_browser_resources_init_P.md`
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Implement browser mode seeding so users start with 1 of each labware resource and unlimited consumables.

**Context**: Planning phase completed with labware manifest and seeding strategy.

**Goal**: Execute the implementation:

1. **Add Seeding Function**: Create `seedDefaultLabware()` in `SqliteService`.
2. **Labware Initialization**: Seed 1 instance of each labware type.
3. **Consumable Handling**: Set unlimited quantity for consumable resources (tips).
4. **Integration**: Call seeding during browser mode initialization.

## 2. Technical Implementation Strategy

**Execution Steps**:

1. **Define Labware List**: Array of labware definition IDs to seed.
2. **Create Seeding Method**:
   ```typescript
   private async seedDefaultLabware(): Promise<void> {
     const labwareDefinitions = [...]; // from catalog
     for (const def of labwareDefinitions) {
       const qty = this.isConsumable(def) ? 9999 : 1;
       await this.createResourceInstance(def, qty);
     }
   }
   ```
3. **Consumable Detection**: Implement `isConsumable()` based on resource type (TipRack, etc.).
4. **Call During Init**: Add to `initializeDatabase()` or appropriate init flow.

## 3. Context & References

**Relevant Skills**:

- `frontend-design` (Angular services)

**Primary Files to Modify**:

| Path | Change |
| :--- | :--- |
| `praxis/web-client/src/app/core/services/sqlite.service.ts` | Add seeding method |

## 4. Constraints & Conventions

- **Execute Changes**: This is an EXECUTION task (Type E).
- **Idempotent**: Seeding should not duplicate if already present.
- **Browser Mode Only**: Backend mode should not be affected.

## 5. Verification Plan

**Definition of Done**:

1. Opening browser mode shows pre-populated labware in inventory.
2. Tip racks show unlimited/high quantity.
3. Plates, reservoirs show qty=1.
4. Resources are usable in protocol setup.

**Manual Test**:
1. Clear browser localStorage/IndexedDB.
2. Open app in browser mode.
3. Navigate to Assets/Inventory.
4. Verify labware resources are pre-populated.

---

## On Completion

- [ ] Implementation committed
- [ ] Manual verification passed
- [ ] Mark this prompt complete in batch README
