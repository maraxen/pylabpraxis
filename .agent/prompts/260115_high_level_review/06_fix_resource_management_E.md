# Agent Prompt: Fix Resource Management & Asset Creation


**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Low
**Dependencies:** None
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Fix the broken "Add Asset" flow by implementing explicit type discrimination in `AssetsComponent` and ensuring `AddAssetDialog` returns clear signal.
**Problem**: `AssetsComponent` blindly defaults to `createResource` if `machine_definition_accession_id` is missing, causing Machine creation failures.
**Goal**: Refactor `AssetsComponent` to strictly respect the Asset Type returned by the dialog.

## 2. User Review Required

> [!IMPORTANT]
> This change modifies how the application routes Asset creation. It requires `AddAssetDialogComponent` to contractually guarantee an `asset_type` field.

## 3. Technical Implementation Strategy

**Execution Phase**:

1. **Modify `AddAssetDialogComponent`**:
    - Ensure the `close()` payload includes an explicit `type: 'MACHINE' | 'RESOURCE'` field.
    - Current code does this loosely; make it explicit and typed.

2. **Refactor `AssetsComponent`**:
    - Update `openUnifiedDialog` to check `result.type` (or `result.assetType`).
    - `case 'MACHINE'`: call `this.assetService.createMachine(result)`.
    - `case 'RESOURCE'`: call `this.assetService.createResource(result)`.
    - `default`: log error or throw.

3. **Verification**:
    - Manually verify "Add Machine" and "Add Resource" dialogs work in Browser Mode (using SQLite).

## 4. Context & References

- **Reference Log**: `references/resource_error_log.md` (Created in previous step).
- **Core Files**:
  - `praxis/web-client/src/app/features/assets/assets.component.ts`
  - `praxis/web-client/src/app/shared/dialogs/add-asset-dialog/add-asset-dialog.component.ts`

## 5. Verification Plan

**Automated Tests**:

- Run `vitest` for `AssetsComponent` if tests exist.
- If not, rely on manual verification described below.

**Manual Verification**:

1. Open App in Browser Mode.
2. Click "Add Asset" -> Select "Machine".
3. Create a Simulated Machine. Verify it appears in the list.
4. Click "Add Asset" -> Select "Resource".
5. Create a generic Resource. Verify it appears.

---

## On Completion

- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed
