# Agent Prompt: 18_angular_aria_multiselect

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260108](./README.md)
**Backlog:** [angular_aria_migration.md](../../backlog/angular_aria_migration.md)

---

## Task

Create a shared ARIA-compliant multiselect component using `@angular/aria` primitives to replace custom chip/dropdown implementations.

### Phase 1: Install and Create Wrapper

1. Install `@angular/aria` package
2. Create `AriaMultiselectComponent` in `src/app/shared/components/aria-multiselect/`
3. Use `@angular/aria/combobox` + `@angular/aria/listbox` pattern

### Phase 2: Component Styling & Interactions (CRITICAL)

**Strict Styling Requirements**:

- **Default/Active State**: Primary application color background with transparent text.
- **Selection Screen**: Theme background with primary color text.
- **Button**: Styles must remain consistent (no layout shifts on selection).
- **Icons**: Use logos/icons for options (e.g., PLR resource types) instead of checkboxes whenever possible.

### Phase 3: Replace Existing Components

Replace the following with the new ARIA multiselect:

- Machine Asset Management category/status filters
- Backend filter dropdowns (sort/filter)
- Spatial View category dropdowns

### Example Implementation

```typescript
import {Combobox, ComboboxInput, ComboboxPopup, ComboboxPopupContainer} from '@angular/aria/combobox';
import {Listbox, Option} from '@angular/aria/listbox';
```

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [angular_aria_migration.md](../../backlog/angular_aria_migration.md) | Work item tracking |
| [filter-chip.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/shared/components/filter-chip/) | Current filter chip implementation |

---

## Project Conventions

- **Frontend Build**: `cd praxis/web-client && npx ng build`
- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
- [Angular ARIA](https://material.angular.dev/) - Package documentation
