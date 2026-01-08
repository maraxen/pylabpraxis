# Task: Fix Deck Display Inconsistency in Run Protocol

**Dispatch Mode**: 🧠 **Planning Mode**

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P2 item "Deck Display Inconsistency"
- `.agents/backlog/run_protocol_workflow.md`

## Problem

The deck visualization during protocol execution does not match the standalone Deck View component and often defaults to a hardcoded layout instead of dynamically loading based on the machine/deck definition.

## Implementation

1. Investigate `DeckGeneratorService` to ensure it uses the machine's specific deck definition.
2. Ensure the `DeckViewComponent` is used consistently across both standalone and workflow contexts.
3. Verify that different deck types (OT2 slots vs Hamilton rails) render correctly based on their definitions.

## Testing

1. Verify the deck display updates when a different machine is selected in the workflow.
2. Compare side-by-side with the standalone deck view for the same machine.

## Definition of Done

- [ ] Workflow deck display is dynamic and consistent with the standalone component.
- [ ] Correct rendering of rails vs slots for all supported machine types.
- [ ] Update `.agents/backlog/run_protocol_workflow.md` - Mark tasks complete
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "Deck Display Inconsistency" as complete

## Files Likely Involved

- `praxis/web-client/src/app/features/run-protocol/services/deck-generator.service.ts`
- `praxis/web-client/src/app/shared/components/deck-view/`
