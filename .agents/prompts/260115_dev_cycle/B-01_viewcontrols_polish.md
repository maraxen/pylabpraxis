# Agent Prompt: ViewControls Visual Polish

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Medium  
**Dependencies:** I-01  
**Input Artifact:** `viewcontrols_inspection_findings.md`

---

## 1. The Task

Refine the `ViewControlsComponent` styling to fix spacing, responsive issues, and dark mode visibility.

**Issues (from Audit Notes B.1 & B.5):**

- Weird spacing on desktop/mobile (too long).
- "Add Filters" menu text invisible in dark mode.
- Hardcoded color usage issues.

## 2. Implementation Steps

### Step 1: Spacing & Layout

- Use `viewcontrols_inspection_findings.md` to identify specific CSS classes.
- Reduce padding/margins to make the bar more compact.
- Ensure efficient wrapping on mobile (< 768px).

### Step 2: Dark Mode Fixes

- Fix "Add Filters" menu text color (ensure it uses theme tokens like `var(--sys-on-surface)`).
- Audit other dropdowns for similar issues.

### Step 3: Theme Tokens

- Replace any hardcoded hex/rgb values with generic tokens.

## 3. Constraints

- **Styling**: `scss` files only.
- **Reference**: Screenshots in `.agents/tmp/` (if captured during inspection).

## 4. Verification Plan

- [ ] "Add Filters" text is visible in Dark Mode.
- [ ] Bar looks compact on Desktop.
- [ ] Bar wraps correctly on Mobile.

---

## On Completion

- [ ] Update this prompt status to 🟢 Completed.
