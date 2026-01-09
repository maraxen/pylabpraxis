# Agent Prompt: 23_well_selector_dialog

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260109](./README.md)  
**Backlog:** [dataviz_well_selection.md](../../backlog/dataviz_well_selection.md)  

---

## Task

Implement a polished Well Selector Dialog with proper row/column labeling and bulk selection features. Integrate with protocol run workflow.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [dataviz_well_selection.md](../../backlog/dataviz_well_selection.md) | Backlog |
| [visual_well_selection.md](../../backlog/visual_well_selection.md) | Detailed requirements |
| `praxis/web-client/src/app/shared/components/well-selector/` | Existing component |

---

## UI Requirements

### Grid Layout

```
     1   2   3   4   5   6   7   8   9  10  11  12
   ╔═══╦═══╦═══╦═══╦═══╦═══╦═══╦═══╦═══╦═══╦═══╦═══╗
 A ║A1 ║A2 ║A3 ║   ║   ║   ║   ║   ║   ║   ║   ║A12║  ← Click 'A' to fill/unfill row
   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣
 B ║B1 ║   ║   ║   ║   ║   ║   ║   ║   ║   ║   ║   ║
   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣
 C ║   ║   ║   ║   ║   ║   ║   ║   ║   ║   ║   ║   ║
   ...
 H ║H1 ║   ║   ║   ║   ║   ║   ║   ║   ║   ║   ║H12║
   ╚═══╩═══╩═══╩═══╩═══╩═══╩═══╩═══╩═══╩═══╩═══╩═══╝
     ↑
     Click '1' to fill/unfill column
```

### Features

1. **Row Labels (A-H/A-P)**: Click to toggle entire row
2. **Column Labels (1-12/1-24)**: Click to toggle entire column
3. **Well Labels**: Show "A1", "B2" etc. if space permits (hide if too small)
4. **Well Circles**: Visual indicator for each well (filled/empty state)
5. **Click-and-Drag**: Select rectangle of wells
6. **Quick Actions**: "Select All", "Clear All", "Invert Selection"

### Dialog Integration

```typescript
interface WellSelectorDialogData {
  plateType: '96' | '384';
  initialSelection: string[];  // ["A1", "A2", "B1"]
  mode: 'single' | 'multi';
}

interface WellSelectorDialogResult {
  wells: string[];
  confirmed: boolean;
}
```

### Responsive Sizing

- 96-well: Larger circles, visible labels
- 384-well: Smaller circles, labels on hover only
- Dialog should size appropriately for plate type

---

## Integration Points

1. **Protocol Run Workflow**: Trigger dialog for well-typed parameters
2. **Formly Integration**: Custom field type for well selection
3. **Return Format**: Array of well identifiers (e.g., `["A1", "A2", "B1"]`)

---

## Project Conventions

- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
