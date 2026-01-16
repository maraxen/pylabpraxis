# Task: Browser Mode Resource Initialization

**ID**: FE-02
**Status**: ✅ Completed
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
>
> - Current seeding: `seedDefaultAssets()` creates 1 instance per definition (lines 600-616)
> - Resources are individual instances (no quantity field)
> - Available labware: 17 plates, 9 tip racks, reservoirs from `plr-definitions.ts`
> - **Existing feature**: `infiniteConsumables` flag (default: true in browser mode) shows consumables with ∞ symbol
> - UI already handles unlimited consumables via app.store.ts
> - Approach: Create 1 instance per definition, let infinite flag handle consumables

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

- 2026-01-15: Modified `seedDefaultAssets()` in `sqlite.service.ts` (lines 581-623)
  - Simplified approach: Create 1 instance per definition
  - Leverage existing `infiniteConsumables` flag (app.store.ts) for unlimited consumables
  - Updated comments to reference infinite flag
  - Users can manually add more resources as needed

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
>
> - Implementation complete (simplified from initial approach)
> - Expected: ~26 resource instances (1 per definition)
> - Consumables display ∞ symbol via existing infiniteConsumables flag
> - Manual testing: Clear browser DB (?resetdb=1), reload, check inventory
> - Verify consumables show ∞ in resource accordion

---

## 📚 Tracking & Context

- **Matrix Reference**: [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- **Scope**: Browser mode only (not backend mode)
- **Note**: Resources = labware only (not machines, not reagents)
- **Files**:
  - `praxis/web-client/src/app/core/services/sqlite.service.ts`
  - `praxis/web-client/src/app/core/services/asset.service.ts`
