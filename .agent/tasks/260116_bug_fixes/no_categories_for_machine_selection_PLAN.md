# No Categories for Machine Selection Plan

## Goal

Fix the issue where "No categories" appear in the Inventory Dialog when adding a machine in a fresh Browser Mode session. The user requested a "Include Simulated" toggle that allows selecting Machine Definitions directly from the catalog to be used as simulated machines, without requiring prior instantiation.

## User Review Required
>
> [!NOTE]
> We will NOT seed any default machines. Instead, the Inventory Dialog will have a toggle (checked by default) to show all "Simulated" options (derived from the Machine Definition Catalog).
> Selecting one of these will dynamically create a simulated instance for the notebook session.

## Proposed Changes

### Inventory Dialog (UX Improvement)

#### [MODIFY] [inventory-dialog.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts)

1. **Add `includeSimulated` Signal**:
    - Create a signal `includeSimulated = signal(true)` to track toggle state.
    - Add a checkbox/toggle in the filter header (Tab 1 and/or Tab 2) to control this.

2. **Fetch Machine Definitions**:
    - Inject `AssetService` and call `getMachineDefinitions()`.
    - Create a signal `machineDefinitions` to hold these.

3. **Update `availableCategories`**:
    - If `includeSimulated()` is true, include categories from `machineDefinitions()` in the list.
    - This ensures attributes like "LiquidHandler" appear even if no actual instances exist.

4. **Update `filteredAssets`**:
    - If `includeSimulated()` is true and type is 'machine':
        - Map `machineDefinitions` to `Machine` objects (mocked).
        - Set `is_simulation_override: true` on these objects.
        - Set `status: 'SIMULATED_DEF'` (or similar) to distinguish them visually (maybe use a specific icon or badge).
        - Append them to the `machines` list.
    - Ensure `frontend_fqn` is preserved (mapped to `plr_definition.frontend_fqn` or similar structure Expected by `PlaygroundComponent`).

5. **Empty State Message**:
    - If `filteredAssets` is still empty despite the toggle, or if toggle is off and list is empty:
        - Show a message: "No machines found. Create a new machine in Assets to use custom hardware."

## Verification Plan

### Manual Verification

1. **Launch App**: Open Browser Mode (clean DB).
2. **Open Inventory**: Click "Add Machine".
3. **Verify Toggle**:
    - Check "Include Simulated" (should be on by default).
    - Verify categories like "LiquidHandler", "PlateReader" appear.
4. **Verify Selection**:
    - Select "LiquidHandler".
    - Should see "LiquidHandler" (Definition) in the list.
    - Select it and click "Add".
5. **Verify Instantiation**:
    - Click "Insert Assets into Notebook".
    - Verify `Playground` generates the correct Python code for a simulated Liquid Handler.
6. **Verify Toggle Off**:
    - Uncheck "Include Simulated".
    - Verify distinct empty state message advising creation.
