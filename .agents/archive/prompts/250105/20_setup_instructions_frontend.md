# Prompt 20: Protocol Setup Instructions - Frontend (COMPLETED)

**Status**: ✅ Completed
**Date**: 2026-01-05

Display protocol setup instructions in the Deck Setup wizard step.

## Context

Protocols can now specify `setup_instructions` via decorator. Display these to users.

## Tasks

1. Update ProtocolDefinition TypeScript interface:
   - Add `setup_instructions: SetupInstruction[] | null`

2. Create SetupInstruction interface:

   ```typescript
   interface SetupInstruction {
     message: string;
     severity: 'required' | 'recommended' | 'info';
     position?: string;
     resource_type?: string;
   }
   ```

3. Create `SetupInstructionsComponent`:
   - Display list of instructions with checkboxes
   - Color-code by severity (required=accent, recommended=primary, info=muted)
   - Show position badges when applicable
   - Track checked state
   - Show "X / Y completed" summary

4. Integrate into `DeckSetupWizardComponent`:
   - Show SetupInstructionsComponent before deck configuration
   - Parse setup_instructions_json from protocol

5. Handle empty state gracefully (no panel if no instructions)

6. Update browser mode schema if needed

## Files to Create

- `praxis/web-client/src/app/features/run-protocol/components/setup-instructions/`

## Files to Modify

- `praxis/web-client/src/app/features/run-protocol/components/deck-setup-wizard/`
- `praxis/web-client/src/app/features/protocols/models/protocol.models.ts`

## Reference

- `.agents/backlog/protocol_setup_instructions.md`
