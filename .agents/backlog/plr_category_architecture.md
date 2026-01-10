# PLR Category Architecture - Separation of Concerns

**Created**: 2026-01-10
**Priority**: P0 (Architectural Foundation)
**Status**: Open

---

## Overview

This backlog tracks the architectural initiative to properly use `plr_category` for resource type classification throughout the application, establishing clear separation of concerns between backend and frontend.

### The Problem

The application currently uses **fragile string matching on FQNs** to determine resource types in many places. This causes bugs like:
- `PlateCarrier` appearing when filtering for `Plate`
- Resources not matching because their FQN doesn't contain expected keywords
- Inconsistent behavior between different parts of the UI

### The Solution

PyLabRobot already provides **inheritance-aware classification** via the `plr_category` field:
- Backend extracts `plr_category` from PLR class hierarchy during sync
- All plates have `plr_category: 'Plate'` regardless of vendor/naming
- All carriers have `plr_category: 'Carrier'`
- This is reliable and doesn't require string parsing

**Architecture principle**: The backend owns classification logic; the frontend consumes and filters by category.

---

## P0: Application-Wide plr_category Audit

**Status**: Open
**Assigned Prompt**: [P0_01_plr_category_audit.md](../prompts/260109/P0_01_plr_category_audit.md)
**Difficulty**: Medium-High (touches many files)

### Scope

Audit and fix ALL places in the codebase that filter or classify resources by type to use `plr_category` instead of FQN string matching.

### Known Problem Areas

1. **Protocol Workflow Asset Selection** (`guided-setup.component.ts`)
   - `matchesByCategory()` - uses FQN string matching
   - `getCompatibleResources()` - cascades the bug

2. **Asset Management** (`assets.component.ts`, `definitions-list.component.ts`)
   - Category filters may use string matching

3. **Playground Inventory** (`inventory-dialog.component.ts`)
   - Resource type filtering

4. **Deck Setup Wizard** (`deck-setup-wizard.component.ts`)
   - Position compatibility checks

5. **Carrier Inference** (`carrier-inference.service.ts`)
   - Determining which carriers fit which resources

6. **Category Inference Utility** (`category-inference.ts`)
   - May duplicate backend logic

### Success Criteria

1. Zero string matching on FQNs for category determination
2. All filtering uses `plr_category` field
3. Backend provides all classification; frontend only consumes
4. Edge cases handled (missing `plr_category` falls back gracefully)

---

## Related Tasks

- **P1_02**: Tactical fix for guided-setup filtering (can be done immediately)
- This P0 ensures the fix is applied consistently app-wide

---

## Technical Notes

### How plr_category is Populated

From `praxis/backend/services/resource_type_definition.py`:
```python
def _get_category_from_plr_class(self, plr_class: type[Any]) -> str | None:
    if hasattr(plr_class, "category"):
        category = plr_class.category
        # Normalization logic...
        return category
    return None
```

The category comes from PLR's own class hierarchy, making it reliable.

### Frontend Access

Resources in both production and browser mode have `plr_category`:
- Production: via API response from `ResourceDefinitionCatalog`
- Browser: via `plr-definitions.ts` data

### Category Values

Standard PLR categories (from `plr-definitions.ts`):
- `'Plate'`
- `'TipRack'`
- `'Reservoir'`
- `'Carrier'`
- `'Deck'`
- `'Tube'`
- `'Resource'` (generic)
