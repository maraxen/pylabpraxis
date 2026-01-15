# Agent Prompt: Protocol Assets & Compilation Inspection


**Status:** ✅ Completed
**Priority:** P2
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Medium
**Dependencies:** None
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Inspect and plan fixes for (1) Asset Selection skipping in Browser Mode and (2) Protocol Parameter Compilation for Pyodide.
**Problem 1**: `RunProtocolComponent` explicitly skips asset selection in browser mode. This prevents testing the "Asset Selection" UX.
**Problem 2**: `ExecutionService` passes raw JSON parameters (UUID strings) to the Python function. Real protocols expect `pylabrobot.resources.Plate` objects, not strings. The UUIDs need to be *resolved* to objects before the function is called.

## 2. Technical Implementation Strategy

**Inspection Phase**:

1. Review `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts` (specifically `applyBrowserModeDefaults`).
2. Review `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts` (`buildProtocolExecutionCode`).

**Output Generation**:

- Create `references/protocol_asset_audit.md` detailing:
  - Exact location of the "Browser Mode Bypass" code.
  - The JSON structure of parameters currently sent to Pyodide.
  - Findings on `praxis/web-client/src/assets/python/web_bridge.py` capabilities.

## 3. Context & References

**Relevant Skills**:

- `senior-fullstack` (Angular + Python context)
- `backend-dev-guidelines` (Correct parameter handling)

**Primary Files to Inspect**:

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts` | Selection Logic |
| `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts` | Compiler Logic |
| `praxis/web-client/src/assets/python/web_bridge.py` | Python <-> JS Bridge |

## 4. Constraints & Conventions

- **Do Not Implement**: This is an INSPECTION task (Type I).
- **No Code Changes**: Do not modify code. Only read and log.
- **Output**: `references/protocol_asset_audit.md` artifact.

## 5. Verification Plan

**Definition of Done**:

1. `references/protocol_asset_audit.md` created.
2. Prompt `02_protocol_assets_compilation_P.md` Queued.

---

## On Completion

- [x] Create `02_protocol_assets_compilation_P.md` (Type P)
- [x] Mark this prompt complete in batch README and set status to ✅ Completed
