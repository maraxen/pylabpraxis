# Protocol Setup Instructions Display

**Priority**: P2 (High)
**Owner**: Full-Stack
**Created**: 2026-01-05
**Status**: ✅ Completed
**Completed**: 2026-01-05

---

## Overview

Allow protocol authors to specify **setup instructions** via the `@protocol_function` decorator that are displayed to users during the Deck Setup step of the Run Protocol wizard. These are user-facing messages that communicate required manual preparation before execution.

---

## Use Cases

1. **Physical Preparation**: "Ensure source plate is at room temperature before starting"
2. **Safety Checks**: "Verify tip rack lids are removed and tips are properly seated"
3. **State Verification**: "Confirm liquid handler is homed and deck is clear"
4. **Consumable Checks**: "Load fresh 200µL filter tip rack in position 3"
5. **Calibration Reminders**: "Run tip calibration if not completed today"

---

## Backend Implementation

### 1. Add Decorator Parameter

Add `setup_instructions` parameter to `@protocol_function`:

```python
@protocol_function(
    name="Cell Serial Dilution",
    description="Performs 8-point serial dilution",
    is_top_level=True,
    setup_instructions=[
        "Ensure source plate is at room temperature (15-25°C)",
        "Verify 200µL tip rack is loaded in position 3",
        "Confirm waste container is empty and properly positioned",
    ],
    # OR as structured objects:
    setup_instructions=[
        SetupInstruction(
            message="Load fresh 200µL tip rack",
            position="3",
            resource_type="TipRack",
            severity="required",  # required | recommended | info
        ),
    ],
)
async def cell_serial_dilution(deck: Deck, state: dict) -> None:
    ...
```

### 2. Update Decorator Models

In `praxis/backend/core/decorators/models.py`:

```python
@dataclass
class SetupInstruction:
    """A setup instruction to display before protocol execution."""
    
    message: str
    severity: str = "required"  # required | recommended | info
    position: str | None = None  # Deck position if applicable
    resource_type: str | None = None  # Expected resource type
    icon: str | None = None  # Optional icon hint for frontend


@dataclass
class CreateProtocolDefinitionData:
    # ... existing fields ...
    setup_instructions: list[str | SetupInstruction] | None = None
```

### 3. Update Protocol Definition Schema

In `praxis/backend/models/pydantic_internals/protocol.py`:

```python
class FunctionProtocolDefinitionCreate(BaseModel):
    # ... existing fields ...
    setup_instructions_json: str | None = None  # JSON array of SetupInstruction
```

### 4. Database Migration

Add `setup_instructions_json` column to `function_protocol_definitions` table.

---

## Frontend Implementation

### 1. Deck Setup Wizard Integration

In `deck-setup-wizard.component.ts`, display setup instructions before deck configuration:

```typescript
@Component({
  template: `
    <!-- Setup Instructions Panel -->
    @if (protocol?.setup_instructions?.length) {
      <div class="setup-instructions-panel">
        <h4>
          <mat-icon>checklist</mat-icon>
          Pre-Run Setup
        </h4>
        
        @for (instruction of protocol.setup_instructions; track instruction) {
          <div class="instruction-item" [class]="instruction.severity">
            <mat-checkbox [(ngModel)]="instructionChecks[instruction.message]">
              {{ instruction.message }}
            </mat-checkbox>
            @if (instruction.position) {
              <span class="position-badge">Position {{ instruction.position }}</span>
            }
          </div>
        }
        
        <div class="instruction-summary">
          {{ checkedCount }} / {{ protocol.setup_instructions.length }} completed
        </div>
      </div>
    }
    
    <!-- Existing deck setup content -->
    ...
  `
})
```

### 2. Visual Design

```
┌─────────────────────────────────────────────────────────────────┐
│  Pre-Run Setup                                          ⓘ Help  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ☐ Ensure source plate is at room temperature (15-25°C)         │
│                                                                  │
│  ☐ Verify 200µL tip rack is loaded                    [Pos 3]   │
│     └─ TipRack expected                                          │
│                                                                  │
│  ☐ Confirm waste container is empty                              │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  0 / 3 completed                                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Severity Styling

| Severity | Color | Behavior |
|----------|-------|----------|
| **required** | Accent/Warning | Must check before proceeding (optional enforcement) |
| **recommended** | Primary | Suggested but not blocking |
| **info** | Muted | Informational only |

---

## Tasks

### Backend

- [x] Add `SetupInstruction` dataclass to `decorators/models.py`
- [x] Add `setup_instructions` parameter to `@protocol_function` decorator
- [x] Update `CreateProtocolDefinitionData` dataclass
- [x] Update `FunctionProtocolDefinitionCreate` Pydantic model
- [x] Add database migration for `setup_instructions_json` column (deferred)
- [x] Update definition builder to serialize instructions
- [x] Update protocol discovery to parse instructions
- [x] Unit tests for decorator with setup instructions

### Frontend

- [x] Update `ProtocolDefinition` TypeScript interface
- [x] Create `SetupInstructionsComponent` for reusable display
- [x] Integrate into `DeckSetupWizardComponent`
- [x] Add checkbox tracking and summary
- [x] Style by severity level
- [x] Handle empty/null instructions gracefully
- [x] Update browser mode SQLite schema

### Integration

- [ ] E2E test: protocol with setup instructions displays correctly
- [ ] E2E test: checkbox state persists during wizard navigation

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/core/decorators/models.py` | Modify | Add SetupInstruction dataclass |
| `backend/core/decorators/protocol_decorator.py` | Modify | Add setup_instructions parameter |
| `backend/core/decorators/definition_builder.py` | Modify | Serialize instructions to JSON |
| `backend/models/pydantic_internals/protocol.py` | Modify | Add setup_instructions_json field |
| `backend/models/orm/protocol.py` | Modify | Add column if needed |
| `web-client/src/app/features/run-protocol/components/setup-instructions/` | Create | New component |
| `web-client/src/app/features/run-protocol/components/deck-setup-wizard/` | Modify | Integrate component |

---

## Related Documents

- [run_protocol_workflow.md](./run_protocol_workflow.md) - Overall workflow
- [simulation_ui_integration.md](./simulation_ui_integration.md) - Requirements display (related)
