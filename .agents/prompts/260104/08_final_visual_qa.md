# Task: Final Visual QA & Test Suite (P2)

## Context

Comprehensive visual and interaction testing combining automated Playwright tests with a manual QA checklist.

## Backlog Reference

See: `.agents/backlog/final_visual_qa.md`

## Scope

### Part 1: Automated E2E Tests (Playwright)

**Critical User Flows to Test:**

1. **Protocol Execution Flow**
   - Select protocol → Configure parameters → Select machine → Setup deck → Start execution

2. **Asset Management Flow**
   - View machines → Add machine → View resources → Add resource → Delete

3. **REPL Session Flow** (after JupyterLite migration)
   - Open REPL → Execute code → View output

4. **Execution Monitor Flow**
   - View run history → Apply filters → View run details

**Visual Regression:**
- Screenshot key views in light and dark mode
- Set up baseline comparison
- Run on CI

### Part 2: Manual QA Checklist

**Visual Inspection:**
- Spacing & alignment consistency
- Typography readability
- Color contrast and theme consistency
- Icon consistency

**Interaction Testing:**
- Scrolling behavior
- Flex container behavior
- Hover/focus states
- Loading/error states

**Feature-Specific:**
- Home page
- Asset Management (each tab)
- Run Protocol (each step)
- Execution Monitor
- REPL
- Settings

### Part 3: Browser Agent Review

- Automated navigation to every route
- Click all buttons/links
- Fill all forms
- Check for console errors
- Performance audit

## Files to Create

- `praxis/web-client/e2e/visual-regression.spec.ts`
- `praxis/web-client/e2e/critical-flows.spec.ts`
- `.agents/QA_CHECKLIST.md` (manual checklist)

## Expected Outcome

- Comprehensive E2E test coverage
- Visual regression baseline established
- Manual QA checklist completed
- No critical bugs or visual issues
