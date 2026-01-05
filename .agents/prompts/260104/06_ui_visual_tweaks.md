# Task: UI Visual Tweaks (P3)

## Context

Minor visual/UI tweaks needed for polish - spacing and layout issues in Asset Management.

## Backlog Reference

See: `.agents/backlog/ui_visual_tweaks.md`

## Scope

### 1. Registry Tab Spacing

**Location:** Asset Management → Registry tab

- Audit current spacing in registry accordions (Machine Definitions, Resource Definitions)
- Ensure consistent padding/margin between items
- Match spacing with Inventory tabs

### 2. Machine Tab Spacing

**Location:** Asset Management → Machines tab

- Audit spacing in machine accordions/cards
- Ensure consistent padding/margin between items
- Proper spacing for machine cards/rows

### 3. General Audit

- Consistent button sizes
- Consistent card padding
- Loading states for async operations
- Empty states with helpful messages

## Files to Modify

- `praxis/web-client/src/app/features/assets/assets.component.scss`
- `praxis/web-client/src/app/features/assets/components/resource-accordion/resource-accordion.component.scss`
- Other component styles as needed

## Expected Outcome

- Consistent, readable spacing throughout Asset Management
- No visual layout issues
- Professional, polished appearance
