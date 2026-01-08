# Task: Add Machine Selection Step to Protocol Workflow

**Dispatch Mode**: 🧠 **Planning Mode**

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P2 item "Machine Selection Step"
- `.agents/backlog/run_protocol_workflow.md`

## Problem

The protocol execution workflow needs a dedicated "Machine Selection" step before deck configuration.

## Implementation

1. Create `MachineSelectionStepComponent`.
2. Update `RunProtocolComponent` to include the new step in the `mat-stepper`.
3. Restructure step order: Parameters → Machine Selection → Asset Selection → Deck Setup.
4. Move current guided deck setup dialog into the inline Deck Setup step.

## Testing

1. Navigate through the full workflow and verify each step collects the correct data.
2. Verify only compatible machines are shown in the selection step.

## Definition of Done

- [ ] Workflow contains "Machine Selection" as a distinct step.
- [ ] Deck setup wizard is integrated inline in the workflow.
- [ ] Update `.agents/backlog/run_protocol_workflow.md` - Mark tasks complete
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "Machine Selection Step" as complete

## Files Likely Involved

- `praxis/web-client/src/app/features/run-protocol/*`
