# Agent Prompt: 37_protocol_hydration_fix

Examine `.agents/README.md` for development context.

**Status:** ✅ Done
**Batch:** [260109](./README.md)
**Backlog:** [ux_issues_260109.md](../../backlog/ux_issues_260109.md)
**Priority:** P1 - Critical (blocks core workflow)

---

## Completion Summary

**Completed:** 2026-01-09

### What Was Done

1. **Backend Eager Loading** - Verified `get()` and `get_multi()` in `protocol_definition.py` use `selectinload()` for parameters and assets (already working)

2. **Pydantic Model Fix** - Added `validation_alias=AliasPath("protocol_definition_accession_id")` to `ParameterMetadataModel` in `protocol.py` to ensure proper field mapping

3. **Frontend Parameter Filtering** - Implemented `isAssetParameter()` method in `parameter-config.component.ts` that filters out:
   - Parameters whose names match asset names in the protocol
   - Parameters whose FQNs match asset FQNs
   - Parameters with type hints containing machine patterns (`pylabrobot.machines`, `LiquidHandler`, `Machine`, etc.)
   - Parameters with type hints containing resource patterns (`pylabrobot.resources`, `Plate`, `TipRack`, `Carrier`, `Deck`, etc.)

4. **Browser Mode** - Assets were already being loaded correctly in SQLite service; issue was stale IndexedDB cache that user cleared

5. **Tests** - Added test for `isAssetParameter()` filtering in `parameter-config.component.spec.ts` (all tests passing)

### Files Modified

- `praxis/backend/models/pydantic/protocol.py` - Added validation_alias
- `praxis/web-client/src/app/features/run-protocol/components/parameter-config/parameter-config.component.ts` - Added `isAssetParameter()` method
- `praxis/web-client/src/app/features/run-protocol/components/parameter-config/parameter-config.component.spec.ts` - Added test for filtering

---

## Task

Fix protocol data hydration so that `parameters` and `assets` are always included when fetching protocol definitions. Also filter out machine/resource arguments from the parameter form to prevent them appearing as user-configurable parameters.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [protocol.py (pydantic)](../../../praxis/backend/models/pydantic/protocol.py) | Response model definitions |
| [protocols.py (api)](../../../praxis/backend/api/protocols.py) | API endpoints |
| [protocol_definition.py](../../../praxis/backend/services/protocol_definition.py) | Service with eager loading |
| [protocol.service.ts](../../../praxis/web-client/src/app/features/protocols/services/protocol.service.ts) | Frontend service |
| [sqlite.service.ts](../../../praxis/web-client/src/app/core/services/sqlite.service.ts) | Browser mode (already works) |
| [parameter-config.component.ts](../../../praxis/web-client/src/app/features/run-protocol/components/parameter-config/parameter-config.component.ts) | Parameter form |

---

## Part 1: Protocol Hydration (Backend)

### Problem

Backend API returns protocols without `parameters` and `assets` arrays, even though:
- ORM relationships are defined correctly
- Service uses `selectinload()` to eager-load relationships
- Browser mode SQLite correctly hydrates these fields

### Investigation Steps

1. Check `FunctionProtocolDefinitionResponse` Pydantic model:
   ```python
   # Does it include these fields?
   parameters: list[ParameterDefinitionResponse] = []
   assets: list[AssetRequirementResponse] = []
   ```

2. Check if response serialization includes relationships:
   ```python
   # In CRUD router or endpoint
   response_model=FunctionProtocolDefinitionResponse
   # Does model_config have from_attributes=True?
   ```

3. Trace the data flow:
   ```
   ORM Query (with selectinload)
   → ORM Object (has .parameters, .assets)
   → Pydantic Model (should serialize relationships)
   → JSON Response (should include arrays)
   ```

### Fix Implementation

#### 1. Update Pydantic Response Model

```python
# praxis/backend/models/pydantic/protocol.py

class FunctionProtocolDefinitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accession_id: UUID
    name: str
    description: str | None = None
    # ... other fields ...

    # Add relationship fields (always included)
    parameters: list[ParameterDefinitionResponse] = []
    assets: list[AssetRequirementResponse] = []
```

#### 2. Verify Service Eager Loading

```python
# praxis/backend/services/protocol_definition.py

async def get_multi(self, ...):
    stmt = select(self.model).options(
        selectinload(self.model.parameters),  # ✓ Should exist
        selectinload(self.model.assets),       # ✓ Should exist
        # ...
    )
```

#### 3. Verify API Endpoint Uses Correct Response Model

```python
# praxis/backend/api/protocols.py

@router.get("/definitions", response_model=list[FunctionProtocolDefinitionResponse])
async def get_definitions(...):
    # ...
```

---

## Part 2: Machine Argument Filtering (Frontend)

### Problem

The parameter configuration form incorrectly shows machine and resource type parameters as user-configurable inputs. These should be filtered out because they're handled by the machine/asset selection steps.

### Current Behavior

```typescript
// parameter-config.component.ts
// All parameters rendered in form, including machine/resource types
```

### Required Behavior

Filter parameters where:
- `type_hint` contains machine FQN patterns (e.g., `pylabrobot.machines.*`)
- `type_hint` contains resource FQN patterns (e.g., `pylabrobot.resources.*`)
- Parameter `fqn` matches entries in `protocol.assets`

### Implementation

```typescript
// parameter-config.component.ts

private isAssetParameter(param: ParameterDefinition, protocol: ProtocolDefinition): boolean {
  // Check if this parameter is an asset requirement
  const assetFqns = protocol.assets?.map(a => a.fqn) || [];
  if (assetFqns.includes(param.fqn)) {
    return true;
  }

  // Check for machine/resource type hints
  const machinePatterns = [
    'pylabrobot.machines',
    'pylabrobot.liquid_handling',
    'LiquidHandler',
    'Machine',
  ];

  const resourcePatterns = [
    'pylabrobot.resources',
    'Plate',
    'TipRack',
    'Carrier',
    'Deck',
  ];

  const typeHint = param.type_hint || '';

  return machinePatterns.some(p => typeHint.includes(p)) ||
         resourcePatterns.some(p => typeHint.includes(p));
}

// In form generation
userParameters = computed(() => {
  const protocol = this.protocol();
  if (!protocol?.parameters) return [];

  return protocol.parameters.filter(p => !this.isAssetParameter(p, protocol));
});
```

### Alternative: Use Backend Categorization

The `is_deck_param` field in `parameter_definitions` may already categorize these:

```typescript
userParameters = computed(() => {
  return this.protocol()?.parameters?.filter(p => !p.is_deck_param) || [];
});
```

**Investigation needed**: Check if `is_deck_param` correctly identifies machine/resource parameters.

---

## Part 3: Browser Mode Consistency

### Verify SQLite Returns Same Shape

```typescript
// sqlite.service.ts - getProtocols() already works
// Verify the returned shape matches backend response
```

### Ensure TypeScript Types Match

```typescript
// schema.ts
interface ProtocolDefinition {
  parameters: ParameterDefinition[];  // Not optional
  assets: AssetRequirement[];          // Not optional
}
```

---

## Testing

### Backend Tests

```bash
# Test protocol endpoint returns hydrated data
curl http://localhost:8000/api/v1/protocols/definitions | jq '.[0] | {name, parameters: .parameters | length, assets: .assets | length}'

# Expected: { "name": "serial_dilution", "parameters": 5, "assets": 3 }
```

### Frontend Tests

1. **Protocol List**: Verify protocols load with parameters/assets
2. **Run Protocol Wizard**:
   - Select protocol with machine arguments
   - Verify parameter form does NOT show machine/resource fields
   - Verify machine selection step shows correct machines
3. **Browser Mode**: Same tests pass in offline mode

---

## Success Criteria

- [ ] Backend API returns protocols with `parameters` and `assets` arrays
- [ ] Frontend ProtocolService receives hydrated data
- [ ] Parameter config form filters out machine/resource parameters
- [ ] WizardStateService can access `protocol.assets`
- [ ] Browser mode continues working
- [ ] No regressions in protocol selection workflow

---

## On Completion

- [ ] Backend Pydantic model updated
- [ ] Frontend parameter filtering implemented
- [ ] Both test suites pass
- [ ] Manual QA of run protocol workflow
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Update backlog status
- [ ] Mark this prompt complete in batch README

---

## References

- [ux_issues_260109.md](../../backlog/ux_issues_260109.md) - Section 8.3
- [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md) - Related workflow issues
- [26_protocol_workflow_debugging.md](./26_protocol_workflow_debugging.md) - Related debugging prompt
