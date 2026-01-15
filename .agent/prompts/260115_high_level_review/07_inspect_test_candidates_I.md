# Agent Prompt: Interaction Test Planning


**Status:** ✅ Completed
**Priority:** P2
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Medium
**Dependencies:** [06_inspect_resource_errors_I](./06_inspect_resource_management_errors_I.md)
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Plan a suite of **Playwright** and **Vitest** interaction tests to cover critical user flows.
**Constraints**:

- **Chromium Only**: Limit configuration to Chromium/Chrome.
- **Headless**: Tests must run headlessly (no popups).
- **Focus**: Interaction coverage (Clicking, Typing, Flows), not just unit logic.

## 2. Technical Implementation Strategy

**Planning Phase**:

1. Review existing `playwright.config.ts` to ensure Headless Chromium is the default.
2. Identify critical paths needing tests:
    - Protocol Run Flow.
    - Machine/Asset Creation.
    - Workcell Dashboard interaction.

**Output Generation**:

- Create `references/test_plan_v1.md` containing:
  - Updated `playwright.config.ts` snippet.
  - List of 5-10 high-value test scenarios (e.g., "User adds a liquid handler and sees it in inventory").
  - Directory structure for new tests (`e2e/specs/interactions/`).

## 3. Context & References

**Relevant Skills**:

- `playwright-skill` (Configuration & Best Practices)
- `test-driven-development` (Planning tests before code)

**Primary Files to Inspect**:

| Path | Description |
|:-----|:------------|
| `praxis/web-client/playwright.config.ts` | Config |
| `praxis/web-client/e2e/` | Existing Specs |

## 4. Constraints & Conventions

- **Do Not Implement**: PLANNING only (Type P).
- **Output**: `references/test_plan_v1.md`.

## 5. Verification Plan

**Definition of Done**:

1. `references/test_plan_v1.md` created.
2. Prompt `07_generate_interaction_tests_E.md` Queued.

---

## On Completion

- [ ] Create `07_generate_interaction_tests_E.md` (Type E)
- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed
