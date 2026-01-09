# Agent Prompt: 28_deck_type_dynamic

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260109](./README.md)
**Backlog:** [ux_issues_260109.md](../../backlog/ux_issues_260109.md)

---

## Task

Fix the hardcoded deck type in the guided deck setup wizard to dynamically derive the deck type from the selected machine.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [deck-setup-wizard.component.ts](../../../praxis/web-client/src/app/features/run-protocol/components/deck-setup-wizard/deck-setup-wizard.component.ts) | **Line 314** - Hardcoded `'HamiltonSTARDeck'` |
| [wizard-state.service.ts](../../../praxis/web-client/src/app/features/run-protocol/services/wizard-state.service.ts) | Wizard state management |
| [deck-catalog.service.ts](../../../praxis/web-client/src/app/features/run-protocol/services/deck-catalog.service.ts) | Deck type definitions |
| [run-protocol.component.ts](../../../praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts) | Parent component with machine selection |

---

## Issue

The `deck-setup-wizard.component.ts` initializes the wizard with a hardcoded deck type:

```typescript
// Line 314
this.wizardState.initialize(p, 'HamiltonSTARDeck', assetMap);
```

This means all protocols display a Hamilton STAR deck layout regardless of the actual machine selected.

---

## Required Changes

### 1. Pass Machine Definition to Wizard

The selected machine from `machine-selection-step.component.ts` should provide its deck type to the wizard.

**Data Flow**:
```
MachineSelectionStep → RunProtocolComponent → DeckSetupWizard → WizardState
                       ↑
                       machine.deck_type or machine.definition.deck_type_id
```

### 2. Look Up Deck Type from Machine

Options:
- **Option A**: Machine has `deck_type` field directly
- **Option B**: Machine references `deck_type_definition_id` that resolves to deck type name
- **Option C**: Derive from `machine_definition.deck_type_definitions`

**Investigation**:
1. Check `MachineOrm` for deck type fields
2. Check `MachineDefinitionOrm` for deck type relationships
3. Determine the correct source of truth

### 3. Update WizardState.initialize()

```typescript
// Before
this.wizardState.initialize(p, 'HamiltonSTARDeck', assetMap);

// After
const deckType = this.getDeckTypeFromMachine(selectedMachine);
this.wizardState.initialize(p, deckType, assetMap);
```

### 4. Add Fallback Logic

If no deck type can be determined:
- Fall back to a generic deck layout
- Or show a message that deck setup is not available for this machine

---

## Testing

1. Select Hamilton STAR machine → Verify Hamilton deck layout (rails)
2. Select Opentrons OT-2 machine → Verify OT-2 deck layout (slots)
3. Select non-deck machine (e.g., PlateReader) → Verify graceful handling

---

## On Completion

- [ ] Deck type derived from selected machine
- [ ] Hamilton and OT-2 deck types render correctly
- [ ] No regressions in deck setup workflow
- [ ] Update backlog status
- [ ] Mark this prompt complete in batch README

---

## References

- [ux_issues_260109.md](../../backlog/ux_issues_260109.md) - Section 1.1
- [deck_view_investigation.md](../../backlog/deck_view_investigation.md) - Prior investigation
