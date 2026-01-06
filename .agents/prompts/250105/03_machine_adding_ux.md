# Prompt 3: Machine Adding UX - Frontend Then Backend

Fix Machine Adding UX to show frontend type selection before backend.

## Context

Currently the Add Machine dialog only shows backends. Need to show machine category first, then compatible backends.

## Tasks

1. Restructure Add Machine dialog into steps:
   - **Step 1**: Select Machine Category (Liquid Handler, Plate Reader, Heater Shaker, etc.)
   - **Step 2**: Select specific MachineDefinition (Hamilton STAR, OT-2, etc.)
   - **Step 3**: Select Backend (filtered by compatible_backends)
   - **Step 4**: Configure Capabilities (if applicable)

2. Query MachineDefinitions grouped by `machine_category` for Step 1

3. Filter `compatible_backends` based on selected definition for Step 3

4. Default to "Simulator" backend in browser mode
   - For machines without explicit Simulator backend, note that IO layer will be patched

5. Show capability form only if definition has configurable capabilities

6. Add `is_simulated` flag when creating machine with sim backend

7. Test full flow with Hamilton Starlet (96-head, iSwap capabilities)

## Files to Modify

- `praxis/web-client/src/app/features/assets/dialogs/add-machine-dialog/`

## Reference

- `.agents/backlog/browser_mode_defaults.md` (Machine Adding UX Fix section)
