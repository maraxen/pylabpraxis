# Agent Prompt: 04_ui_visual_tweaks

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260108](./README.md)  
**Backlog:** [chip_filter_standardization.md](../../backlog/chip_filter_standardization.md)  
**Priority:** P3

---

## Task

Fix UI spacing and alignment issues in the Asset Registry and Machine tabs.

---

## Implementation Steps

### 1. Registry Spacing Fix

**Issue:** Padding issues in the Asset Registry list view.

Update `praxis/web-client/src/app/features/assets/components/resource-list/resource-list.component.scss`:

```scss
.resource-list {
  // Ensure consistent padding between cards
  .resource-card {
    margin-bottom: 12px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  // Fix filter bar spacing
  .filter-section {
    padding: 16px;
    margin-bottom: 16px;
  }
}
```

### 2. Machine Tab Alignment

**Issue:** Vertical alignment of status indicators in the Machines tab.

Update `praxis/web-client/src/app/features/assets/components/machine-card/machine-card.component.scss`:

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

### 4. Visual Verification

Use the browser subagent to verify changes:

1. Navigate to Assets → Resources tab
2. Capture screenshot of resource list
3. Navigate to Assets → Machines tab
4. Capture screenshot of machine list
5. Verify alignment and spacing in both views

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [chip_filter_standardization.md](../../backlog/chip_filter_standardization.md) | Backlog tracking |
| [resource-list.component.scss](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/components/resource-list/resource-list.component.scss) | Resource list styles |
| [machine-card.component.scss](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/components/machine-card/machine-card.component.scss) | Machine card styles |

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
