# Agent Prompt: Protocol Well Selection Fix

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** 260109
**Backlog Reference:** Protocol well selection not triggering (P1)

---

## 1. The Task

The user cannot select wells for protocol parameters that require well input (e.g., "Source Wells"). The UI element for well selection appears to be either missing or unresponsive in the Protocol Run setup screen.

Your goal is to ensure that protocol parameters defined with a well-selection type correctly render the `WellSelectorFieldComponent` and that clicking it opens the `WellSelectorDialogComponent` to allow user selection.

## 2. Technical Implementation Strategy

**Root Cause Investigation:**

1. **Backend-Frontend Mismatch**: The backend defines parameter types (likely in `praxis/backend/models/enums/protocol.py`). The frontend `parameter-config.component.ts` maps these string types to Formly field types.
2. **Missing Mapping**: It is highly probable that the mapping logic in `parameter-config.component.ts` is missing a case for the well selection type (e.g., `ProtocolParameterType.WELL_SELECTION` or equivalent string) or maps it incorrectly.
3. **Component Integration**: Verify that `WellSelectorFieldComponent` is correctly registered in the Formly configuration (check `app.config.ts`, though this is likely correct) and that its template correctly triggers the dialog.

**Architecture & Logic:**

* **`ParameterConfigComponent`**: This is the orchestrator.
* Locate the method generating `FormlyFieldConfig[]` (e.g., `getFields()` or `createFormConfig()`).
* Inspect the `switch` statement handling `param.type`.
* **Fix**: Ensure there is a case for the well selection type that returns `{ type: 'well-selector' }`.

* **`WellSelectorFieldComponent`**:
* Ensure the `rows` and `cols` passed to the dialog are correct (currently hardcoded or TODOs). If the protocol parameter provides dimensions (e.g., in `constraints`), pass them through `templateOptions`.

**Data Flow:**

1. Backend returns `ProtocolDefinition` -> Frontend `ProtocolService` fetches it.
2. `ParameterConfigComponent` iterates over `protocol.parameters`.
3. Mapping logic converts `ProtocolParameter` -> `FormlyFieldConfig`.
4. Formly renders `WellSelectorFieldComponent`.
5. User clicks -> `WellSelectorDialogComponent` opens.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
| --- | --- |
| `praxis/web-client/src/app/features/run-protocol/components/parameter-config/parameter-config.component.ts` | Main logic for mapping protocol parameters to UI fields. |
| `praxis/web-client/src/app/shared/formly-types/well-selector-field.component.ts` | The custom form field component for well selection. |

**Reference Files (Read-Only):**

| Path | Description |
| --- | --- |
| `praxis/backend/models/enums/protocol.py` | Definition of protocol parameter types (Backend source of truth). |
| `praxis/web-client/src/app/features/protocols/models/protocol.models.ts` | Frontend interface definitions for protocols. |
| `praxis/web-client/src/app/app.config.ts` | Formly type registration configuration. |

## 4. Constraints & Conventions

* **Commands**: Use `npm` for Angular operations.
* **Backend Path**: `praxis/backend`
* **Frontend Path**: `praxis/web-client`
* **Formly**: Use standard Formly `templateOptions` to pass data (label, required, dimensions) to the component.
* **Type Safety**: Ensure the string used for matching `param.type` matches the backend exactly.

## 5. Verification Plan

**Definition of Done:**

1. The `ParameterConfigComponent` correctly creates a `well-selector` field for relevant parameters.
2. The `WellSelectorFieldComponent` spec passes.
3. The `ParameterConfigComponent` spec passes.

**Verification Commands:**

```bash
# Run unit tests for the parameter config component
npm test -- parameter-config.component.spec.ts

# Run unit tests for the well selector field
npm test -- well-selector-field.component.spec.ts

```

**Manual Verification Steps (for Agent thought process):**

* Mock a `ProtocolParameter` with type "well_selection" (or actual backend value) in the test spec.
* Assert that the resulting Formly config has `type: 'well-selector'`.

---

## On Completion

* [ ] Commit changes with message: "fix(ui): enable well selector for protocol parameters"
* [ ] Update backlog item status in `PROTOCOL_WORKFLOW.md` (or relevant backlog file)
* [ ] Mark this prompt complete in batch README and set the status in this prompt document to 🟢 Completed
