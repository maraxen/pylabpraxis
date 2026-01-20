# Status: Complete
# Phase 2.6: Legacy Cleanup & Playground Architecture

**Goal**: Cleanup legacy code and ensure the Playground uses the new architecture (DeckState, AssetWizard, etc.).

## Tasks

### Task 1: Playground Refactor
- [x] **Update `PlaygroundComponent`**
    - [x] Replace usage of `InventoryDialog` with `AssetWizardComponent`.
    - [x] Ensure `AssetWizardComponent` properly updates the `DeckStateService`.
- [x] **Refactor `addMachineToNotebook`**
    - [x] Update the generated Python code to use `create_configured_backend` instead of the hardcoded `SimulatorBackend`.
    - [x] Ensure `machine_config` (from `DeckStateService`) is properly serialized and passed to the REPL context.
- [x] **Verify REPL Context**
    - [x] Confirm `machine_config` is accessible in the Pyodide environment.

### Task 2: Deck Setup Serialization
- [x] **Update `DeckStateService` (or `RunProtocolService`)**
    - [x] Implement `serializeDeckToPLR()`:
        - [x] Iterate through `DeckStateService` state (carriers, labware).
        - [x] Generate Python code or JSON compatible with `pylabrobot` to reconstruct the deck layout.
    - [x] Ensure `serializeDeckToPLR()` output is injected into the Python runtime before `runProtocol` executes the user's script.

### Task 3: Fake Data Cleanup
- [x] **Remove `praxis/web-client/src/assets/browser-data/protocols.ts`**
    - [x] Verify no references remain before deletion.
- [x] **Remove Legacy Dialogs**
    - [x] Delete `praxis/web-client/src/app/features/playground/components/inventory-dialog`.
    - [x] Delete `praxis/web-client/src/app/shared/dialogs/add-asset-dialog`.
    - [x] Remove `InventoryDialogComponent` and `AddAssetDialogComponent` from `AppModule` or their respective module declarations.

## Verification
- [ ] **Build Check**: Ensure `npm run build` passes after deletions.
- [ ] **Runtime Check**:
    - [ ] Add a machine/labware using `AssetWizard`.
    - [ ] Verify the "generated code" for backend setup reflects the new configuration.
    - [ ] Run a simple protocol and verify the deck setup is respected in the simulation.

## Status
- Playground updated to use AssetWizard and Factory.
- Deck Setup serialization implemented.
- Legacy dialogs and mock data removed.
