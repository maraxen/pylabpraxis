# Prompt 8: Capability Dropdown Theme Sync

**Priority**: P2
**Difficulty**: Small
**Type**: Easy Win (CSS Fix)

> **IMPORTANT**: Do NOT use the browser agent. Verify with automated tests only.

---

## Context

The machine capability dropdown menus render with light theme styling even when the app is in dark mode.

---

## Tasks

### 1. Find Capability Dropdown Locations

```bash
grep -r "capabilities" praxis/web-client/src/app --include="*.ts" -l
```

Key files:

- `machine-dialog.component.ts`
- `machine-card.component.ts`

### 2. Ensure Panel Uses Theme Variables

In the component with the dropdown, ensure the mat-select panel class uses theme variables:

```typescript
@Component({
  // ...
  template: `
    <mat-select 
      panelClass="theme-aware-panel"
      ...>
    </mat-select>
  `
})
```

### 3. Add Panel Styles

In `styles.scss` (global) or the component styles:

```scss
.theme-aware-panel {
  background: var(--mat-sys-surface-container) !important;
  
  .mat-mdc-option {
    color: var(--mat-sys-on-surface) !important;
    
    &:hover:not(.mdc-list-item--disabled) {
      background: var(--mat-sys-surface-container-high) !important;
    }
    
    &.mdc-list-item--selected {
      background: var(--mat-sys-primary-container) !important;
      color: var(--mat-sys-on-primary-container) !important;
    }
  }
}
```

### 4. Alternative: Use CDK Overlay Theme

If the issue is with the overlay container, ensure it inherits theme:

```scss
.cdk-overlay-container {
  // Inherit theme from body
  color: var(--mat-sys-on-surface);
  
  .mat-mdc-select-panel {
    background: var(--mat-sys-surface-container);
  }
}
```

---

## Verification

```bash
cd praxis/web-client && npm run build
```

---

## Success Criteria

- [ ] Capability dropdowns use correct theme colors
- [ ] Light mode: light background, dark text
- [ ] Dark mode: dark background, light text
- [ ] Hover states match theme
