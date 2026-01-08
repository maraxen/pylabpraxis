# Agent Prompt: 04_ui_visual_tweaks

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260108](./README.md)  
**Backlog:** [chip_filter_standardization.md](../../backlog/chip_filter_standardization.md)  
**Priority:** P3

---

## Task

Fix UI spacing, alignment, and theme consistency in the Asset Registry and Machine components. Ensure all cards have clear boundaries via theme-synced outlines or gradients.

---

## Implementation Steps

### 1. Registry Spacing Fix

**Issue:** Padding issues in the Asset Registry list view.

Update styles in `praxis/web-client/src/app/features/assets/components/resource-list/resource-list.component.ts` (inline styles):

```scss
.resource-list-container {
  // Ensure consistent padding
  padding: 16px;
  
  .mat-table {
    border: 1px solid var(--mat-sys-outline-variant);
    border-radius: 8px;
    overflow: hidden;
  }

  .resource-row {
    transition: background-color 0.2s ease;
    
    &:hover {
      background-color: var(--mat-sys-surface-container-highest);
    }
  }
}
```

### 2. Machine Tab Alignment

**Issue:** Vertical alignment of status indicators in the Machines tab.

Update styles in `praxis/web-client/src/app/shared/components/machine-card/machine-card.component.ts` (inline styles or template classes):

```scss
.machine-card-header {
  display: flex;
  align-items: center;  // Vertical center alignment
  
  .status-indicator {
    // Ensure consistent size and alignment
    flex-shrink: 0;
    width: 12px;
    height: 12px;
    margin-right: 8px;
  }
}
```

### 3. Grid Layout Consistency

**Issue:** Resource cards have inconsistent height with varying metadata.

Update card styles to ensure consistent height:

```scss
.resource-card {
  // Fixed minimum height for consistency
  min-height: 120px;
  
  // Flex layout for content distribution
  display: flex;
  flex-direction: column;
  
  .card-content {
    flex: 1;
  }
  
  .card-actions {
    margin-top: auto;
  }
}
```

### 4. Theme-Synced Card Boundaries

**Issue:** Boundaries between items can be unclear in certain themes.
**Goal:** Use theme-synced outlines or gradients to make item boundaries distinct.

Update `praxis/web-client/src/app/shared/components/machine-card/machine-card.component.ts`:

- Ensure the card has a visible border using `var(--mat-sys-outline-variant)`.
- Consider using a subtle gradient: `linear-gradient(to bottom right, var(--mat-sys-surface-container-low), var(--mat-sys-surface-container))`.

```html
<!-- Example implementation in MachineCard template -->
<div class="border-[1.5px] border-[var(--mat-sys-outline-variant)] bg-gradient-to-br from-[var(--mat-sys-surface-container-low)] to-[var(--mat-sys-surface-container)] rounded-2xl ...">
  ...
</div>
```

### 5. Visual Verification

Use the browser subagent to verify changes in both light and dark modes (if available):

1. Navigate to Assets → Resources tab
2. Capture screenshot of resource list
3. Navigate to Assets → Machines tab
4. Capture screenshot of machine list
5. Verify boundaries are clear and colors are theme-consistent.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [chip_filter_standardization.md](../../backlog/chip_filter_standardization.md) | Backlog tracking |
| [resource-list.component.ts](../../../features/assets/components/resource-list/resource-list.component.ts) | Resource list styles/logic |
| [machine-card.component.ts](../../../shared/components/machine-card/machine-card.component.ts) | Machine card styles/logic |

---

## Project Conventions

- **CSS**: Use CSS variables from design system where applicable
- **Spacing**: Use multiples of 4px (4, 8, 12, 16, 24, etc.)

See [codestyles/html-css.md](../../codestyles/html-css.md) for conventions.

---

## On Completion

- [ ] Capture before/after screenshots
- [ ] Update [chip_filter_standardization.md](../../backlog/chip_filter_standardization.md) - mark UI Visual Tweaks complete
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
