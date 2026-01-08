# Prompt 19: Protocol Setup Instructions - Backend (COMPLETED)

**Status**: ✅ Completed
**Date**: 2026-01-05

Add `setup_instructions` parameter to the `@protocol_function` decorator.

## Context

Protocol authors need a way to specify pre-run setup messages that display in the Deck Setup wizard.

## Tasks

1. In `praxis/backend/core/decorators/models.py`:
   - Create SetupInstruction dataclass:
     - message: str
     - severity: str = "required" (required | recommended | info)
     - position: str | None = None (deck position)
     - resource_type: str | None = None
   - Add setup_instructions field to CreateProtocolDefinitionData

2. In `praxis/backend/core/decorators/protocol_decorator.py`:
   - Add `setup_instructions` parameter (list[str | SetupInstruction] | None)
   - Pass to CreateProtocolDefinitionData

3. In `praxis/backend/models/pydantic_internals/protocol.py`:
   - Add `setup_instructions_json: str | None` to FunctionProtocolDefinitionCreate

4. In `praxis/backend/core/decorators/definition_builder.py`:
   - Serialize setup_instructions to JSON for storage
   - Handle both string list and SetupInstruction list

5. Database migration (if ORM updated):
   - Add `setup_instructions_json` column to function_protocol_definitions

6. Unit tests for decorator parsing

## Example Usage

```python
@protocol_function(
    name="Serial Dilution",
    setup_instructions=[
        "Ensure source plate is at room temperature",
        SetupInstruction(message="Load 200µL tips", position="3", severity="required"),
    ],
)
async def serial_dilution(deck: Deck) -> None: ...
```

## Reference

- `.agents/backlog/protocol_setup_instructions.md`
