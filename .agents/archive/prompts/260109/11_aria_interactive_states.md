# Agent Prompt: 11_aria_interactive_states

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260109](./README.md)  
**Backlog:** [ui_consistency.md](../../backlog/ui_consistency.md)  

---

## Task

Fix interactive states for ARIA components (Multiselect/Select/Autocomplete) where clicking permanently changes rendering style instead of reverting on deselect.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [ui_consistency.md](../../backlog/ui_consistency.md) | Work item tracking (Phase 4) |
| `praxis/web-client/src/app/shared/components/aria-select/` | Select component |
| `praxis/web-client/src/app/shared/components/aria-multiselect/` | Multiselect component |
| `praxis/web-client/src/app/shared/components/aria-autocomplete/` | Autocomplete component |

---

## Requirements

### State Styling

| State | Background | Text Color |
|-------|------------|------------|
| Default/Active | Primary app color | Transparent/theme text |
| Selection Screen | Theme background | Primary color text |
| Button | Consistent (no change) |

### Rich Multiselect Options

- Use logos/icons (e.g., PLR resource type icons) instead of checkboxes whenever possible
- Example: Machine category icons, resource type indicators

---

## Implementation

1. **Audit Current Styling**:
   - Identify CSS classes applied on interaction
   - Trace styling persistence bug

2. **Fix State Transitions**:
   - Ensure selected → unselected reverts styling
   - Use Angular state bindings correctly

3. **Add Icon Support**:
   - Create `optionIcon` input for options
   - Render SVG/icon instead of checkbox when provided

---

## Expected Outcome

- ARIA components reset styling on deselection
- Consistent appearance across all three component types
- Optional icon support for rich selection displays

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
