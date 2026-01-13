# Agent Prompt: Playground Theming Quick Wins

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P3
**Batch:** [260114_frontend_feedback](./README.md)
**Difficulty:** 🟢 Easy
**Type:** 🟢 Implementation
**Dependencies:** E-01 (WebSerial must work first)
**Backlog Reference:** [GROUP_E_playground_init.md](./GROUP_E_playground_init.md)

---

## 1. The Task

Address styling inconsistencies in playground components (Stepper, Well Selector chips, Loading Skeleton) by replacing hardcoded styles with theme tokens.

**User Feedback:**

> "also make sure we are using themed css and not overrides (the stepper looks off)"
> "well selector is GREAT, feels fluid and natural. let's make the chips in the selected a bit smaller though."
> "playground loading skeleton is working, but can we make sure it's on theme?"

## 2. Technical Implementation Strategy

### Task 1: Stepper Theming

- **File:** `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts`
- **Issue:** Stepper looks off due to hardcoded styles
- **Fix:**
  - Remove or update `.polished-stepper` overrides
  - Use CSS variables (`var(--mat-sys-...)`)
  - Ensure `MatStepper` uses the application theme properly

### Task 2: Well Selector Chips

- **File:** `praxis/web-client/src/app/shared/components/well-selector-dialog/well-selector-dialog.component.ts`
- **Issue:** Chips in selected display too large
- **Fix:**
  - Adjust styles for `.well-chip` or `mat-chip` elements
  - Make selection preview more dense/compact
  - Maintain readability

### Task 3: Loading Skeleton

- **File:** `praxis/web-client/src/app/features/protocols/components/protocol-list-skeleton.component.ts`
- **Also check:** Any other skeleton components in the codebase
- **Issue:** Hardcoded colors don't support dark mode
- **Fix:**
  - Replace hardcoded hex colors (e.g., `#f6f7f8`) with theme tokens
  - Use `var(--mat-sys-surface-container)`, `var(--mat-sys-surface-variant)`, etc.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts` | Stepper styling |
| `praxis/web-client/src/app/shared/components/well-selector-dialog/well-selector-dialog.component.ts` | Well chip sizing |
| `praxis/web-client/src/app/features/protocols/components/protocol-list-skeleton.component.ts` | Skeleton theming |

**Reference Files:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/styles/themes/` | Theme token definitions |

## 4. Constraints & Conventions

- **Styling:** Use design tokens from `styles/themes/`, Angular Material
- **Dark Mode:** All changes must support dark mode automatically via theme tokens
- **No Breaking Changes:** Maintain existing layout/spacing behavior

## 5. Verification Plan

**Definition of Done:**

1. Inventory Stepper looks consistent with app theme
2. Well Selector selection chips are smaller/denser
3. Skeletons use theme variables (support dark mode automatically)
4. No visual regressions

**Test Commands:**

```bash
cd praxis/web-client
npm run start:browser
```

**Manual Verification:**

1. Navigate to `/app/playground`
2. Open inventory dialog - verify stepper styling is on-theme
3. Open well selector - verify chips are appropriately sized
4. Toggle dark/light mode in settings
5. Navigate to protocols tab - verify skeleton (if visible) matches theme

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README
- [ ] Set status in this document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `GROUP_E_playground_init.md` - Parent initiative
