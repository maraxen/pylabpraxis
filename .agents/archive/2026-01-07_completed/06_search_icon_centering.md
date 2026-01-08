# Prompt 6: Search Icon Centering

**Priority**: P2
**Difficulty**: Small
**Type**: Easy Win (CSS Fix)

> **IMPORTANT**: Do NOT use the browser agent. Verify with automated tests only.

---

## Context

Search icons in various components are not vertically centered within search input fields.

---

## Tasks

### 1. Find All Search Fields

Search for search input patterns:

```bash
grep -r "matPrefix.*search" praxis/web-client/src/app --include="*.ts" --include="*.html"
```

### 2. Apply Consistent Styling

The issue is typically in the icon prefix alignment. Add this CSS fix to each component with search:

```scss
:host ::ng-deep .search-field {
  .mat-mdc-form-field-icon-prefix {
    padding: 0 8px;
    display: flex;
    align-items: center;
  }
  
  .mat-icon {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
```

### 3. Known Locations to Check

1. `machine-filters.component.ts` - Lines 55-73
2. `run-protocol.component.ts` - Protocol search
3. `jupyterlite-repl.component.ts` - Asset menu search (if applicable)
4. `resource-filters.component.ts` (if exists)

### 4. Create Shared Search Field Style

Optionally, create a shared class in `styles.scss`:

```scss
.praxis-search-field {
  .mat-mdc-form-field-icon-prefix {
    padding: 0 8px !important;
    display: flex !important;
    align-items: center !important;
  }
  
  .mat-mdc-form-field-icon-suffix {
    padding: 0 8px !important;
    display: flex !important;
    align-items: center !important;
  }
}
```

Then apply `class="praxis-search-field"` to all mat-form-fields with search.

---

## Verification

Build and check for CSS compilation errors:

```bash
cd praxis/web-client && npm run build
```

---

## Success Criteria

- [x] Search icon aligned vertically in machine filters
- [x] Search icon aligned vertically in protocol search
- [x] Consistent styling across all search fields
- [x] No CSS compilation errors
