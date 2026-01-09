# Agent Prompt: 22_aria_component_polish

Examine `.agents/README.md` for development context.

**Status:** 🟡 In Progress (Official pattern refactor complete; focusing/states unblocked)  
**Batch:** [260109](./README.md)  
**Backlog:** [angular_aria_migration.md](../../backlog/angular_aria_migration.md)  

---

## Task

Polish ARIA components (Select, Multiselect, Autocomplete) with proper focus behavior, theme-consistent states, and sleeker visual design.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [angular_aria_migration.md](../../backlog/angular_aria_migration.md) | Migration backlog |
| `praxis/web-client/src/app/shared/components/aria-select/` | Select component |
| `praxis/web-client/src/app/shared/components/aria-multiselect/` | Multiselect component |
| `praxis/web-client/src/app/shared/components/aria-autocomplete/` | Autocomplete component |

---

## Issues to Fix

### 1. Focus/Blur Behavior

- **Autoclose on Unfocus**: Dropdown should close when focus moves outside, while retaining selection state
- **State Persistence**: Selected values must persist after blur
- **Re-open Behavior**: Re-focusing should show current selection highlighted

### 2. Theme Synchronization (All States)

Current issue: "Selected" state is hardcoded to light mode styling.

| State | Light Mode | Dark Mode |
|-------|------------|-----------|
| Default | Theme bg, primary text | Theme bg, primary text |
| Hover | Subtle highlight | Subtle highlight |
| **Selected** | Primary gradient text ✨ | Primary gradient text ✨ |
| Focused | Outline indicator | Outline indicator |
| Disabled | Muted text | Muted text |

### 3. Multiselect Visual Redesign

- **Remove big checkbox look** - replace with sleeker indicator
- **Match single-select pattern**: Use checkmark icon on right or subtle background change
- **Selected items**: Apply gradient text effect

### 4. Gradient Text Effect

Apply to selected items in both modes:

```scss
.selected-option {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

### 5. Autocomplete CSS Optimization

- Audit and simplify CSS rules
- Remove redundant overrides
- Ensure consistent sizing with other components

---

## Testing Checklist

- [ ] Toggle theme while dropdown open - states update correctly
- [ ] Click outside dropdown - closes but retains selection
- [ ] Re-open - shows previous selection
- [ ] Multiselect visual matches single-select pattern
- [ ] Gradient text visible in light AND dark mode
- [ ] Keyboard navigation works (Tab, Arrow, Enter, Esc)

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
