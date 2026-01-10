# Agent Prompt: Asset Filtering Bug Fix (Plates & Carriers)

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260109](README.md)
**Backlog Reference:** [protocol_workflow.md](../../backlog/protocol_workflow.md)
**Estimated Complexity:** Medium
**Dependency:** This is a tactical fix. See [P0_01_plr_category_audit.md](P0_01_plr_category_audit.md) for the strategic architectural fix.

---

## 1. The Task

Fix the asset filtering logic in the protocol workflow's asset selection step. Currently:

1. **Not all plates are listed** when selecting resources for a plate-type requirement
2. **Carriers appear in the list** when they shouldn't - carriers are container resources, not consumables

**User Value:** Protocol execution asset selection shows only relevant, compatible resources.

---

## 2. Understanding the Architecture

### How FQN vs plr_category Works

**FQN (Fully Qualified Name)** is always the **SPECIFIC class**, not the base class:
- A Corning plate: `pylabrobot.resources.corning_costar.plates.Cor_96_wellplate_360ul_Fb`
- A Hamilton carrier: `pylabrobot.resources.hamilton.carriers.PLT_CAR_L5AC_A00`
- NOT: `pylabrobot.resources.plate.Plate` (this is only used in type hints)

**plr_category** is the **inheritance-aware classification** extracted from PLR class hierarchy:
- All plates (regardless of vendor) have: `plr_category: 'Plate'`
- All carriers have: `plr_category: 'Carrier'`
- All tip racks have: `plr_category: 'TipRack'`

**The root cause:** The frontend uses string matching on FQNs (fragile) instead of `plr_category` (reliable).

### Current Fragile Pattern (DO NOT EXPAND)
```typescript
// BAD: String matching on FQN - catches "PlateCarrier" when looking for "Plate"
if (resFqnLower.includes('plate')) { ... }
```

### Correct Pattern (USE THIS)
```typescript
// GOOD: Use plr_category for category-based filtering
if (resource.plr_category === 'Plate') { ... }
```

---

## 3. Technical Implementation Strategy

**Quick Fix (This Prompt):**

The frontend already has access to `plr_category` through the Resource interface. Use it instead of string matching.

**Modify `matchesByCategory()` to use `plr_category`:**

```typescript
private matchesByCategory(req: AssetRequirement, res: Resource): boolean {
  // Get the required category from the requirement
  const reqCategory = this.getRequiredCategory(req);
  if (!reqCategory) return false;

  // Use plr_category for reliable matching
  const resCategory = res.plr_category?.toLowerCase() || '';

  return resCategory === reqCategory;
}

private getRequiredCategory(req: AssetRequirement): string | null {
  const reqType = (req.type_hint_str || '').toLowerCase();
  const reqFqn = (req.fqn || '').toLowerCase();

  // Map type hints to categories
  if (reqType.includes('plate') || reqFqn.includes('.plate')) return 'plate';
  if (reqType.includes('tiprack') || reqType.includes('tip_rack')) return 'tiprack';
  if (reqType.includes('trough') || reqType.includes('reservoir')) return 'reservoir';
  if (reqType.includes('tube')) return 'tube';
  if (reqType.includes('carrier')) return 'carrier';

  return null;
}
```

**Key Changes:**
1. Check `res.plr_category` instead of string matching `res.fqn`
2. Map requirement type hints to expected categories
3. Remove all carrier exclusion hacks - they're no longer needed

---

## 4. Files to Modify

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/run-protocol/components/guided-setup/guided-setup.component.ts` | Update `matchesByCategory()` and `getCompatibleResourcesForInventory()` |

**Reference Files:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/models/asset.models.ts` | Resource interface with `plr_category` field |
| `praxis/web-client/src/assets/browser-data/plr-definitions.ts` | Browser mode data shows `plr_category` values |
| `praxis/backend/services/resource_type_definition.py` | Backend extraction of `plr_category` |

---

## 5. Verification Plan

**Definition of Done:**

1. Build succeeds:
   ```bash
   cd praxis/web-client && npm run build
   ```

2. Carriers **never** appear when selecting plates
3. All plate resources appear when selecting for a Plate requirement (regardless of vendor)
4. Tip racks, troughs, and other types filter correctly

**Manual Testing:**

1. Run protocol requiring `Plate` type
2. Verify dropdown shows only `plr_category: 'Plate'` resources
3. Verify NO carriers appear (even PLT_CAR_* named ones)
4. Repeat for TipRack, Trough requirements

---

## 6. On Completion

- [ ] Commit: `fix(protocol): use plr_category for asset filtering instead of FQN string matching`
- [ ] Update backlog item in `backlog/protocol_workflow.md`
- [ ] Mark this prompt complete in batch README

---

## Related Work

- **P0_01_plr_category_audit.md**: Strategic audit to ensure `plr_category` is used consistently throughout the application
- This prompt is a tactical fix; P0_01 is the architectural cleanup
