# Agent Prompt: Browser Mode Resource Initialization - Planning

**Status:** ⚪ Queued
**Priority:** P2
**Batch:** [260115_feature_enhancements](./README.md)
**Difficulty:** Easy
**Dependencies:** `02_browser_resources_init_I.md`, `references/browser_resources_audit.md`
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Plan the implementation for seeding browser mode with 1 of each labware resource and unlimited consumables.

**Context**: Inspection phase documented the current seeding flow and available labware definitions.

**Goal**: Create a plan covering:

1. **Labware Selection**: Which labware types to include (plates, tip racks, reservoirs, etc.).
2. **Quantity Logic**: qty=1 for discrete labware, qty=unlimited (or high number like 9999) for consumables.
3. **Seeding Integration**: Where to add the new seeding calls in `SqliteService`.
4. **UX Considerations**: How these appear in inventory (editable quantities? deletable?).

## 2. Technical Implementation Strategy

**Planning Deliverables**:

1. **Labware Manifest**: Explicit list of labware definitions to seed.
2. **Seeding Function**: Pseudo-code for `seedDefaultLabware()`.
3. **Consumable Detection**: Logic to identify consumable resources (tips, reagent containers).
4. **Inventory Display**: Any UI considerations for pre-seeded resources.

**Output Generation**:

- Update `implementation_plan.md` or create task-specific plan document.

## 3. Context & References

**Relevant Skills**:

- `frontend-design` (Angular patterns)

**Primary Files to Plan Changes**:

| Path | Planned Change |
| :--- | :--- |
| `praxis/web-client/src/app/core/services/sqlite.service.ts` | Add `seedDefaultLabware()` |
| `praxis/web-client/src/app/core/services/asset.service.ts` | Potentially call new seeding |

## 4. Constraints & Conventions

- **Do Not Execute**: This is a PLANNING task (Type P).
- **Scope**: Browser mode only.
- **Note**: Keep labware list maintainable (consider using definition catalog).

## 5. Verification Plan

**Definition of Done**:

1. Labware manifest is documented.
2. Seeding logic is planned with consumable handling.
3. Prompt `02_browser_resources_init_E.md` is ready for execution.

---

## On Completion

- [ ] Document labware manifest and seeding plan
- [ ] Mark this prompt complete in batch README
- [ ] Proceed to `02_browser_resources_init_E.md`
