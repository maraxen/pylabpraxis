# Agent Prompt: 16_stepper_navigation_relaxation

Examine `.agents/README.md` for development context.

**Status:** ⚪ Not Pursued (Decided on different behavior)
**Batch:** [260109](./README.md)  
**Backlog:** [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md)  

---

## Task

Relax stepper restrictions in the Run Protocol workflow to allow broader navigation between steps.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md) | Work item tracking |
| `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts` | Run workflow component |
| `praxis/web-client/src/app/features/run-protocol/run-protocol.component.html` | Stepper template |

---

## Current Behavior

- Stepper enforces linear progression
- Cannot return to previous steps easily
- "Continue" button sometimes not visible (related issue)

---

## Implementation

1. **Allow Step Navigation**:
   - Enable clicking on completed step headers to return
   - Add `[linear]="false"` or conditional linearity
   - Preserve form state when navigating back

2. **Validation on Advance**:
   - Keep validation requirements for advancing
   - Allow review/edit of previous steps

3. **UI Indicators**:
   - Show completed checkmarks on finished steps
   - Highlight current step clearly

---

## Expected Outcome

- Users can navigate freely between completed steps
- Form state preserved when going back
- Clear visual feedback on step status

---

## Project Conventions

- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
