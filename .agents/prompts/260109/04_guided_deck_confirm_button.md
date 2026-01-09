# Agent Prompt: 04_guided_deck_confirm_button

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md)  

---

## Task

Fix the "Confirm & Continue" button in the Guided Deck Setup wizard that triggers no action when clicked. User verified this issue persists as of 2026-01-08.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md) | Work item tracking |
| [17_guided_deck_setup_ui.md](../260108/17_guided_deck_setup_ui.md) | Related prompt from 260108 |
| `praxis/web-client/src/app/features/run-protocol/components/guided-setup/` | Guided setup component |
| `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts` | Parent component |

---

## Investigation Steps

1. **Event Handler Binding**:
   - Verify `(click)` handler is correctly bound to the button
   - Check for typos in method names

2. **Form Validation**:
   - Check if button is disabled due to form validation state
   - Verify `formGroup.valid` state when button is clicked

3. **Component Communication**:
   - Verify `@Output()` emitter is correctly connected
   - Check if parent component receives the event

4. **Stepper Integration**:
   - Confirm stepper advances to next step on confirmation
   - Check `MatStepper.next()` or equivalent is called

---

## Expected Outcome

- Clicking "Confirm & Continue" advances the wizard to the next step
- Deck configuration is saved and passed to subsequent steps
- Clear user feedback on successful confirmation

---

## Project Conventions

- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
