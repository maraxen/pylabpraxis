# Agent Prompt: Protocol Assets & Compilation Execution


**Status:** ✅ Completed
**Priority:** P2
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Intricate
**Dependencies:** `implementation_plan.md`
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Implement the approved plan to enable Asset & Machine Selection in Browser Mode and correctly resolve protocol parameters (including Labware and Machines) in the Python (Pyodide) environment.

**Problem Summary**:

1. `RunProtocolComponent` bypasses asset selection in browser mode.
2. `ExecutionService` passes raw JSON parameters to Python, but protocols expect `Plate`/`TipRack` objects.

## 2. Technical Implementation Strategy

**Execution Phase**:

1. **Review Plan**: Read the approved `implementation_plan.md` in the artifacts directory (or if moved, check `.agent/prompts/260115_high_level_review/implementation_plan.md`).
2. **Frontend Changes**:
    - Edit `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts`:
        - Remove `applyBrowserModeDefaults()` asset clearing logic.
        - Ensure "Select Assets" and **"Well Selection"** steps are accessible and functional.
    - Edit `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts`:
        - Update `buildProtocolExecutionCode` to inject parameter resolution logic.
        - Ensure `protocol` definition (with parameter types) is available during build.
3. **Runtime Changes**:
    - Edit `praxis/web-client/src/assets/python/web_bridge.py`:
        - Add `resolve_param(value, type_hint)` or similar helper to instantiate PLR objects (`Plate`, `TipRack`) from JSON dictionaries.

**Verification**:

- **Automated**: Run `run-protocol.component.spec.ts`.
- **Manual/Browser**:
  - PROMPT THE USER TO COMPLETE THESE STEPS.
  - Launch Browser Mode.
  - Select Protocol with Plate & Wells.
  - **Verify Well Selection Step appears and works.**
  - Run Protocol.
  - Verify successful execution without "AttributeError".

## 3. Context & References

**Relevant Skills**:

- `senior-fullstack`
- `backend-dev-guidelines`

**Primary Files**:

- `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts`
- `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts`
- `praxis/web-client/src/assets/python/web_bridge.py`

## 4. Constraints & Conventions

- **Execute**: This is an EXECUTION task (Type E).
- **Output**: Modified code files, functional browser mode asset selection.
- **Review**: Use `notify_user` to request review of changes if significant.

## 5. Verification Plan

**Definition of Done**:

1. Asset Selection and Well Selection steps work in Browser Mode.
2. Python execution receives resolved PLR objects, not just dicts.
3. `walkthrough.md` created to document the fix and testing.

---

## On Completion

- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed
