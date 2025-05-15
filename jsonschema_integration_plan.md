# JSON Schema Integration Plan - Updated Architecture

## Architecture Overview

1. **Responsibility Separation**:
   - `Protocol` class handles protocol execution flow
   - `Workcell` class manages physical deck layout and asset validation
   - `Orchestrator` coordinates between multiple protocols

2. **Key Changes**:

   ```mermaid
   graph LR
     A[Protocol] -->|Delegates to| B[Workcell]
     B --> C[Deck Validation]
     B --> D[Asset Placement]
     B --> E[Head Configuration]
     A --> F[Execution Flow]
   ```

## Workcell Implementation Details

### Asset Validation Methods

- `validate_asset_requirements()`: Main entry point for validation
- `validate_asset_placement()`: Checks individual asset placement
- `_check_carrier_compatibility()`: Verifies carrier/slot availability
- `_check_single_slot_available()`: Validates non-stackable assets
- `has_96_channel_head()`: Checks 96-channel capability

### Validation Logic

```python
# Example validation flow
1. Check 96-channel head requirement
2. Verify carrier compatibility if specified
3. Validate slot availability for non-stackable assets
4. Check deck position constraints
```

## Protocol Class Changes

### Simplified Interface

```python
def _validate_and_setup_assets(self):
    # Delegates all validation to Workcell
    self.workcell.validate_asset_requirements(self._required_assets)

    # Handles protocol-specific configuration
    if needs_96_head:
        self.workcell.configure_96_head()
```

## Migration Path

1. **Phase 1 (Current)**:
   - Implement core validation in Workcell
   - Update Protocol to use Workcell methods
   - Maintain backward compatibility

2. **Phase 2 (Next Release)**:
   - Deprecate old validation methods
   - Update all protocols to use new schema
   - Add comprehensive testing

3. **Phase 3 (Future)**:
   - Remove deprecated code
   - Finalize architecture
