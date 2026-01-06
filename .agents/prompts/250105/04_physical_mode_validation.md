# Prompt 4: Physical Mode Machine Validation

Ensure users cannot proceed with Physical execution mode without a real (non-simulated) machine.

## Context

When "Physical" mode is selected in the Run Protocol wizard, the user must select a real machine instance, not a simulated one.

## Tasks

1. In `run-protocol.component.ts`, add validation:
   - If `store.simulationMode() === false` (Physical mode selected)
   - And selected machine has `is_simulated === true` or backend contains "Simulator"
   - Block progression to next step

2. Show clear error message:
   - "Physical execution requires a real machine. The selected machine is simulated."
   - Suggest: "Switch to Simulation mode or select a physical machine."

3. Visual indicators:
   - In MachineSelectionComponent, gray out simulated machines when in Physical mode
   - Or show warning icon next to simulated machines

4. Update "Continue" button disabled state to check this condition

5. Test scenarios:
   - Physical mode + simulated machine → blocked
   - Physical mode + real machine → allowed
   - Simulation mode + any machine → allowed

## Files to Modify

- `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts`
- `praxis/web-client/src/app/features/run-protocol/components/machine-selection/`

## Reference

- `.agents/backlog/browser_mode_defaults.md`
