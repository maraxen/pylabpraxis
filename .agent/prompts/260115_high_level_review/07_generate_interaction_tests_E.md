# Agent Prompt: Generate Interaction Tests


**Status:** 🟢 Completed
**Priority:** P2
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Medium
**Dependencies:** [07_inspect_test_candidates_I](./07_inspect_test_candidates_I.md)
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Implement the Interaction Test Suite defined in the Test Plan.
**Input**: `references/test_plan_v1.md` (Detailed Scenarios & Structure).
**Goal**: Create high-value Playwright tests for Runtime Controls, Deck View, and Error Handling.

## 2. Technical Implementation Strategy

**Execution Phase**:

1. **Update Configuration**:
    - Modify `praxis/web-client/playwright.config.ts` to enforce `headless: true` and restrict to Chromium, as per the Test Plan.

2. **Scaffold Directory**:
    - Create `praxis/web-client/e2e/specs/interactions/`.

3. **Implement Key Scenarios**:
    - Create `01-execution-controls.spec.ts`: Implement Pause/Resume/Abort flows.
    - Create `02-deck-view.spec.ts`: Implement Labware hover/click verification.
    - Create `03-asset-forms.spec.ts`: Implement validation tests.
    - Create `04-error-handling.spec.ts`: Implement resilience tests (mocking failures if possible, or stubbing).

4. **Verification**:
    - Run `npx playwright test --project=chromium` to ensure all new tests pass.
    - Ensure existing tests still pass.

## 3. Context & References

- **Test Plan**: `references/test_plan_v1.md` (Follow this exactly).
- **Existing Specs**: `praxis/web-client/e2e/specs/` (Use as reference for Page Objects).

## 4. Verification Plan

**Automated Tests**:

- `npm run test:e2e` (or specific playwright command).
- Record a video of the `interactions` suite running successfully (artifact).

---

## On Completion

- [x] Mark this prompt complete in batch README and set status to 🟢 Completed
