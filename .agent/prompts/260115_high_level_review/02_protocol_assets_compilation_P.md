# Agent Prompt: Protocol Assets & Compilation Planning


**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** High
**Dependencies:** `references/protocol_asset_audit.md`
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Create a technical plan to enable Asset Selection in Browser Mode and implement proper Protocol Parameter Compilation for Pyodide execution.

**Problem Summary**:

- **Asset Selection**: Currently hard-skipped in `RunProtocolComponent` when in browser mode.
- **Compilation**: Parameters are passed as raw JSON (UUIDs) to Python, but protocols expect python primitives or `Plate`/`Container` objects (or lists/python primitives containing these). The Python environment doesn't automatically resolve these.

## 2. Technical Implementation Strategy

**Planning Phase**:

1. **Review the Audit**: Read `references/protocol_asset_audit.md` to understand the exact code locations and gaps.
2. **Design the Solution**:
    - **Frontend**: How to allow `RunProtocolComponent` to show asset selection even in standard browser mode? Use "Mock Assets" or standard `AssetService`?
    - **Compiler**: How to change `ExecutionService.buildProtocolExecutionCode` to include parameter *types/metadata*?
    - **Runtime**: How to modify the generated Python script to:
        - Import `pylabrobot.resources` classes (`Plate`, `TipRack`, etc.).
        - Instantiate or look up the objects based on the passed UUIDs.
        - Pass the *resolved* objects to the protocol function.

**Output Generation**:

- Create `implementation_plan.md` detailing:
  - **File Changes**:
    - `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts` (Remove bypass).
    - `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts` (Improve compiler).
    - Any necessary changes to `web_bridge.py` or helper scripts.
  - **Verification Plan**:
    - How to verify asset selection works in browser.
    - How to verify the Python script receives actual objects (e.g. by printing `type(plate)` in a test protocol).

## 3. Context & References

**Relevant Skills**:

- `senior-fullstack` (Angular + Python context)
- `backend-dev-guidelines` (Correct parameter handling)

**Primary Files**:

| Path | Description |
|:-----|:------------|
| `references/protocol_asset_audit.md` | Findings from Inspection Phase (Must Read) |
| `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts` | Target for modification |
| `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts` | Target for modification |

## 4. Constraints & Conventions

- **Do Not Execute**: This is a PLANNING task (Type P).
- **Output**: `implementation_plan.md` artifact.
- **Review**: Plan must be reviewed by User before moving to Execution.

## 5. Verification Plan

**Definition of Done**:

1. `implementation_plan.md` created and approved.
2. Prompt `02_protocol_assets_compilation_E.md` Queued.

---

## On Completion

- [ ] Create `02_protocol_assets_compilation_E.md` (Type E)
- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed
