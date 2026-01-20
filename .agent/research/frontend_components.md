# Frontend Components Research

## 1. Asset Dialog
- **File**: `praxis/web-client/src/app/shared/dialogs/add-asset-dialog/add-asset-dialog.component.ts`
- **Steps Definition**: The dialog uses an Angular Material Stepper (`<mat-stepper>`) with three defined steps:
  1.  **Type Selection** (`TypeSelectionStepComponent`): User selects 'Machine' or 'Resource'.
  2.  **Definition Selection** (`DefinitionSelectionStepComponent`): User picks the specific asset definition.
  3.  **Configuration** (`ConfigurationStepComponent`): User configures the asset (name, connection info, etc.).
- **Splitting Type/Category**:
  - Currently, Type selection is Step 1.
  - Category selection is likely implicit within the Definition step or missed.
  - **Can we easily split?**: Yes. The `AddAssetDialogComponent` structure allows inserting a new `<mat-step>` for Category selection between Type and Definition. You would need to:
    1.  Create a `CategorySelectionStepComponent`.
    2.  Update `AddAssetDialogComponent` to handle the new step and pass the selected category to the Definition step (to filter definitions).
    3.  Update `DefinitionSelectionStepComponent` to accept an input for filtering by category.

## 2. Inventory
- **File**: `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts`
- **Same Dialog?**: No. The Inventory uses its own component (`InventoryDialogComponent`) which implements a completely separate Stepper workflow (Type -> Category -> Selection -> Specs).
- **Filtering**:
  - **Mechanism**: **Frontend filtering**.
  - The component loads all machines and resources via `AssetService` signals.
  - It uses Angular `computed` signals (`filteredAssets`, `filteredQuickAssets`) to filter the in-memory lists based on:
    - Type (Machine/Resource)
    - Category (e.g., 'LiquidHandler', 'Plate')
    - Search Query (Name matching)

## 3. Deployment
- **.github/workflows/docs.yml**:
  - **Build Command**: `make docs` (This builds the documentation, likely via Sphinx/MkDocs).
- **package.json** (Angular App):
  - **Build Command**: `ng build`
  - **Specific Script**: `npm run build:gh-pages` executes `ng build --configuration=gh-pages`.

## 4. Protocol UI ("Transfer Pattern")
- **Search Term**: "Transfer pattern" usually refers to the "Selective Transfer" UI behavior.
- **Location**: `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts`
- **Findings**:
  - The component identifies "Selective Transfer" protocols via `isSelectiveTransferProtocol()`.
  - **Source**:
    - Standard parameters are rendered using **Formly** in `ParameterConfigComponent`.
    - However, the **Transfer/Well Selection** logic is **custom** and separate from Formly.
    - It is handled in a dedicated Stepper step ("Step 5: Well Selection") which is conditionally shown (`@if (wellSelectionRequired())`).
    - It triggers `openWellSelector()` which opens `WellSelectorDialogComponent`.
    - It manually injects `source_wells` and `target_wells` parameters if they are missing from the protocol definition.
