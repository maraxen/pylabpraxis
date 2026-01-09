# Agent Prompt: 17_guided_deck_setup_ui

Examine `.agents/README.md` for development context.

**Status:** 🟡 In Progress
**Batch:** [260108](./README.md)
**Backlog:** [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md)

---

## Task

Fix the Guided Deck Setup UI issues in the Run Protocol workflow. User verification on 2026-01-08 confirmed:

- [x] **Continue Button Not Visible**: After adding carriers to the deck, the Continue/Next button is not visible.
- [ ] **"Confirm & Continue" Action Broken**: Clicking "Confirm & Continue" does not trigger the next step or any apparent action. Investigate event handling and validation state.
- [x] **Scrolling Issues**: Container scrolling behavior is unclear; content may overflow without proper scroll indicators.
- [x] **Flex Container Fix**: Ensure the deck setup wizard uses a proper flex container layout.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md) | Work item tracking |
| [deck-setup-wizard.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/run-protocol/components/deck-setup-wizard/) | Deck setup wizard |
| [guided-setup.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/run-protocol/components/guided-setup/) | Guided setup dialog |

---

## Project Conventions

- **Commands**: Use `uv run` for all Python commands
- **Frontend Build**: `cd praxis/web-client && npx ng build`
- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status in `run_protocol_workflow.md`
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
