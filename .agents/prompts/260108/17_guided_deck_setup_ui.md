# Agent Prompt: 17_guided_deck_setup_ui

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260108](./README.md)
**Backlog:** [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md)

---

## Task

Fix the Guided Deck Setup UI issues in the Run Protocol workflow. User verification on 2026-01-08 confirmed:

1. **Continue Button Not Visible**: After adding carriers to the deck, the Continue/Next button is not visible. Users cannot proceed.
2. **"Confirm & Continue" Action Broken**: Clicking "Confirm & Continue" does not trigger the next step or any apparent action. Investigate event handling and validation state.
3. **Scrolling Issues**: Container scrolling behavior is unclear; content may overflow without proper scroll indicators.
4. **Flex Container Fix**: Ensure the deck setup wizard uses a proper flex container layout with:
   - Scrollable content area
   - Fixed/sticky navigation buttons (always visible)
   - Proper overflow handling

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
