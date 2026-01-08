# Agent Prompt: 19_aria_well_selector_grid

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260108](./README.md)
**Backlog:** [dataviz_well_selection.md](../../backlog/dataviz_well_selection.md)

---

## Task

Refactor the `WellSelectorComponent` to use `@angular/aria/grid` for an ARIA-compliant, accessible microplate well selector.

### Requirements

1. **ARIA Grid Pattern**: Implement using `Grid`, `GridRow`, `GridCell`, `GridCellWidget`
2. **Individual Click Selection**: Click any cell to toggle selection
3. **Click-and-Drag Selection**: Click and drag to select multiple cells
4. **Selection Controls**:
   - "Clear Selection" button
   - "Invert Selection" button
5. **Animation Rendering**: Visual feedback for selection state changes

### Example Implementation

```typescript
import {Grid, GridRow, GridCell, GridCellWidget} from '@angular/aria/grid';

@Component({
  selector: 'app-well-selector',
  imports: [Grid, GridRow, GridCell, GridCellWidget],
  // ...
})
```

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [dataviz_well_selection.md](../../backlog/dataviz_well_selection.md) | Work item tracking |
| [well-selector/](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/shared/components/well-selector/) | Current implementation |
| [visual_well_selection.md](../../backlog/visual_well_selection.md) | Related backlog |

---

## Project Conventions

- **Frontend Build**: `cd praxis/web-client && npx ng build`
- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status in `dataviz_well_selection.md`
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
- [angular_aria_migration.md](../../backlog/angular_aria_migration.md) - Related migration
