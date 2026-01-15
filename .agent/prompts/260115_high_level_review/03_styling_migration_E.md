# Agent Prompt: Styling Migration Execution


**Status:** ✅ Completed
**Priority:** P3
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Medium
**Dependencies:** `references/styling_audit_report.md`, `brain/7967f498-1db7-43ee-9148-957a052f7def/implementation_plan.md`

---

## 1. The Task

**Objective**: Execute the migration of the frontend codebase from hardcoded styling values to Theme CSS Variables and Tailwind utility classes as defined in the approved `implementation_plan.md`.
**Input**:

- `references/styling_audit_report.md`
- `brain/7967f498-1db7-43ee-9148-957a052f7def/implementation_plan.md`

## 2. Technical Implementation Strategy

Follow the steps outlined in the implementation plan:

1. **Update Global Styles**: Add missing semantic tokens to `praxis/web-client/src/styles.scss`.
2. **Global Search & Replace**: Batch replace hardcoded hex codes with CSS variables across the codebase.
3. **Component Refactoring**:
    - Refactor `unified-shell.component.ts` (Layout).
    - Refactor `view-controls.component.ts` (UI Controls).
4. **Verification**:
    - Ensure build success (`npm run build`).
    - Verify visual consistency in both Light and Dark modes.

## 3. Context & References

**Relevant Skills**:

- `frontend-design`
- `code-maintenance`

**Primary Files**:

- `praxis/web-client/src/styles.scss`
- `praxis/web-client/src/app/layout/unified-shell.component.ts`
- `praxis/web-client/src/app/shared/components/view-controls/view-controls.component.ts`

## 4. Constraints & Conventions

- Use Tailwind utilities where possible for spacing and common colors.
- Use `var(--...)` for theme variables that must react to light/dark mode changes.
- Ensure 1:1 visual parity with the existing UI.

## 5. Verification Plan

**Definition of Done**:

1. All targeted hardcoded hex codes are replaced with variables.
2. Layout components use standard spacing.
3. Build passes and UI looks correct in both themes.
4. `walkthrough.md` created with proof of work.

---

## On Completion

- [ ] Mark this prompt complete in batch README.
