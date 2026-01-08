# Task: Fix OT2 Slot Type Rendering

**Dispatch Mode**: 🧠 **Planning Mode**

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P1 item "OT2 Slot Type Not Rendering"
- `.agents/backlog/deck_view.md`

## Problem

Opentrons OT-2 deck rendering does not display slot type information correctly, even though the task was marked as complete.

## Implementation

1. Investigate the OT-2 deck definition in `praxis.db` or the static analysis parser.
2. Update the `DeckViewComponent` or related service to correctly infer and display slot types (e.g., standard vs rails vs specialized slots for plate sized objects).
3. Ensure slot labels and types are visually distinct in the UI.

## Testing

1. Select an OT-2 machine in the deck view and verify all slots are labeled with their standard OT-2 names/types.

## Definition of Done

- [ ] OT-2 slots display correct type and label information.
- [ ] The fix is NOT a patch specific to OT-2 and the actual inference and rendering logic is robust to position type of check.
- [ ] Update `.agents/backlog/deck_view.md` - Mark as ✅ Complete
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "OT2 Slot Type Not Rendering" as complete

## Files Likely Involved

- `praxis/web-client/src/app/shared/components/deck-view/`
- `praxis/backend/utils/plr_static_analysis/`
