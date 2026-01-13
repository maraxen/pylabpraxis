# Agent Prompt: Cleanup Unused Imports and Sass Migration

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260113](./README.md)
**Backlog Reference:** [frontend_schema_sync.md](../../backlog/frontend_schema_sync.md)

---

## 1. The Task

The Angular build produces 17 warnings about unused imports and Sass `@import` deprecation. Clean these up to produce a warning-free build.

**User Value:** Clean codebase with no build warnings, improving developer experience and reducing noise.

---

## 2. Technical Implementation Strategy

**Warning Categories:**

1. **Unused Import Warnings** - Angular components importing symbols they don't use
2. **Sass Deprecation Warnings** - Using `@import` instead of `@use` for SCSS files

**Affected Components (Unused Imports):**

| Component | Unused Import |
|:----------|:--------------|
| `AssetDashboardComponent` | `RouterLink` |
| `ForgotPasswordComponent` | `RouterLink` |
| `LoginComponent` | `RouterLink` |
| `RegisterComponent` | `RouterLink` |
| `RunDetailComponent` | `StateDisplayComponent` |
| `HomeComponent` | `MachineCardComponent` |
| `WellSelectorComponent` | `Grid`, `GridRow`, `GridCell`, `NgClass` |
| `GuidedSetupComponent` | Unnecessary optional chain |

**Sass Files with @import:**

The `styles.scss` file uses `@use` for Angular Material but `@import` for other files:

- Line 2: `@import '@angular/cdk/overlay-prebuilt.css';`
- Line 3: `@import 'shepherd.js/dist/css/shepherd.css';`
- Line 4: `@import 'styles/shepherd-theme.scss';`
- Line 5: `@import 'styles/praxis-select.scss';`

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/pages/asset-dashboard/asset-dashboard.component.ts` | Remove unused RouterLink |
| `praxis/web-client/src/app/features/auth/pages/forgot-password/forgot-password.component.ts` | Remove unused RouterLink |
| `praxis/web-client/src/app/features/auth/pages/login/login.component.ts` | Remove unused RouterLink |
| `praxis/web-client/src/app/features/auth/pages/register/register.component.ts` | Remove unused RouterLink |
| `praxis/web-client/src/app/features/execution-monitor/components/run-detail/run-detail.component.ts` | Remove unused StateDisplayComponent |
| `praxis/web-client/src/app/features/home/home.component.ts` | Remove unused MachineCardComponent |
| `praxis/web-client/src/app/shared/components/well-selector/well-selector.component.ts` | Remove unused Grid/GridRow/GridCell/NgClass |
| `praxis/web-client/src/app/features/run-protocol/components/guided-setup/guided-setup.component.ts` | Fix unnecessary optional chain |
| `praxis/web-client/src/styles.scss` | Migrate from `@import` to `@use` |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- Only remove imports that are confirmed unused.
- For Sass migration, use `@use` with appropriate namespace or `as *` for CSS.

---

## 5. Implementation Details

### Step 1: Remove Unused Imports from Components

For each component, find the `imports: [...]` array and remove the unused symbol. Also remove the corresponding import statement at the top of the file.

**Pattern:**

```typescript
// Remove from file-level imports
import { RouterLink } from '@angular/router';

// Remove from component imports array
@Component({
  imports: [RouterLink, /* other imports */],  // Remove RouterLink
})
```

### Step 2: Sass Migration

**Update `src/styles.scss` (Lines 2-5):**

**Before:**

```scss
@use '@angular/material' as mat;
@import '@angular/cdk/overlay-prebuilt.css';
@import 'shepherd.js/dist/css/shepherd.css';
@import 'styles/shepherd-theme.scss';
@import 'styles/praxis-select.scss';
```

**After:**

```scss
@use '@angular/material' as mat;
@use '@angular/cdk/overlay-prebuilt.css' as *;
@use 'shepherd.js/dist/css/shepherd.css' as *;
@use 'styles/shepherd-theme' as *;
@use 'styles/praxis-select' as *;
```

> **Note:** For CSS files, `@use ... as *` includes the styles globally. For SCSS files, remove `.scss` extension.

### Step 3: Fix Unnecessary Optional Chain

In `guided-setup.component.ts`, find the line with unnecessary optional chaining and simplify:

**Example:**

```typescript
// Before - unnecessary optional chain on non-nullable
this.steps?.forEach(...)

// After - if steps is guaranteed to exist
this.steps.forEach(...)
```

---

## 6. Verification Plan

**Definition of Done:**

1. Build produces 0 warnings (or significantly fewer):

   ```bash
   cd praxis/web-client && npm run build 2>&1 | grep -c "warning"
   ```

   Expected: 0 or close to 0.

2. Build succeeds:

   ```bash
   cd praxis/web-client && npm run build
   ```

   Expected: SUCCESS with 0 errors.

3. No runtime errors (spot check):

   ```bash
   cd praxis/web-client && npm start &
   sleep 10  # Wait for dev server
   curl -s http://localhost:4200 | grep -q "app-root" && echo "OK" || echo "FAIL"
   ```

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status (Phase 5 and 6 tasks)
- [ ] Mark this prompt complete in batch README
- [ ] Update DEVELOPMENT_MATRIX.md if all phases complete

---

## References

- `.agents/README.md` - Environment overview
- [styles.scss](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/styles.scss)
- [Sass @use Documentation](https://sass-lang.com/documentation/at-rules/use)
