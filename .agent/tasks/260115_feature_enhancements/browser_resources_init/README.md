# Task: Browser Mode Resource Initialization

**ID**: FE-02
**Status**: ⚪ Not Started
**Priority**: P2
**Difficulty**: Easy

---

## 📋 Phase 1: Inspection (I)

**Objective**: Inspect current resource initialization in browser mode to understand seeding logic.

- [ ] Review `praxis/web-client/src/app/core/services/sqlite.service.ts` → `seedDefaultAssets`
- [ ] Check resource models in `praxis/web-client/src/app/core/models/`
- [ ] Identify available labware definitions from PLR catalog
- [ ] Understand consumable vs discrete labware distinction

**Findings**:
> - Current seeding flow
> - Available labware definitions
> - Consumable classification (TipRack = consumable)

---

## 📐 Phase 2: Planning (P)

**Objective**: Plan implementation for seeding browser mode with labware resources.

- [ ] Define labware manifest (which types to include)
- [ ] Design `seedDefaultLabware()` function
- [ ] Plan consumable detection logic
- [ ] Consider idempotency (don't duplicate on reload)

**Implementation Plan**:

1. Create array of labware definition IDs to seed
2. Implement `seedDefaultLabware()` in `SqliteService`
3. For each definition: qty=1 for discrete, qty=9999 for consumables
4. Call during browser mode initialization
5. Add idempotency check (skip if already seeded)

**Definition of Done**:

1. Browser mode shows pre-populated labware in inventory
2. Tip racks show unlimited/high quantity
3. Plates, reservoirs show qty=1
4. Resources usable in protocol setup

---

## 🛠️ Phase 3: Execution (E)

**Objective**: Implement browser mode resource seeding.

- [ ] Define labware list in `SqliteService`:
  ```typescript
  private readonly DEFAULT_LABWARE = [
    { definitionId: 'corning_96_wellplate', isConsumable: false },
    { definitionId: 'opentrons_96_tiprack', isConsumable: true },
    // ...
  ];
  ```
- [ ] Implement `seedDefaultLabware()`:
  ```typescript
  private async seedDefaultLabware(): Promise<void> {
    for (const def of this.DEFAULT_LABWARE) {
      const qty = def.isConsumable ? 9999 : 1;
      await this.createResourceInstance(def.definitionId, qty);
    }
  }
  ```
- [ ] Add idempotency flag or check
- [ ] Call from `initializeDatabase()` or appropriate init

**Work Log**:

- [Pending]

---

## 🧪 Phase 4: Testing & Verification (T)

**Objective**: Verify resource seeding works correctly.

- [ ] Clear browser localStorage/IndexedDB
- [ ] Open app in browser mode
- [ ] Navigate to Assets/Inventory
- [ ] Verify labware resources are pre-populated
- [ ] Verify consumables show high quantity
- [ ] Test using resources in protocol setup

**Results**:
> [To be captured]

---

## 📚 Tracking & Context

- **Matrix Reference**: [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- **Scope**: Browser mode only (not backend mode)
- **Note**: Resources = labware only (not machines, not reagents)
- **Files**:
  - `praxis/web-client/src/app/core/services/sqlite.service.ts`
  - `praxis/web-client/src/app/core/services/asset.service.ts`
