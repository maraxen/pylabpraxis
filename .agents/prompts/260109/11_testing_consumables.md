# Agent Prompt: Infinite Consumables Tests

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P3
**Batch:** [260109](./README.md)
**Backlog Reference:** [testing.md](../../backlog/testing.md)

---

## 1. The Task

Create tests for the consumable tracking system. This includes testing:

- Consumable inventory tracking
- Consumption during protocol execution
- Low-stock warnings
- Auto-replenishment flags (if implemented)
- "Infinite consumables" mode for simulation

**User Value:** Confidence that consumable tracking works correctly, preventing protocol failures due to untracked resource depletion.

---

## 2. Technical Implementation Strategy

### Architecture

**Core Service:** `ConsumableAssignmentService`

- Located at: `praxis/backend/core/consumable_assignment.py`
- Responsible for matching consumable requirements to available resources

**Existing Tests:** `tests/backend/core/test_consumable_assignment.py`

- Already has 5 test functions covering basic scenarios

### Test Gaps to Address

Based on backlog requirements and existing test coverage, add tests for:

1. **Consumable inventory tracking:**
   - Test `is_consumable` flag on ResourceDefinition
   - Test quantity tracking on Resource instances

2. **Consumption during execution:**
   - Test quantity decrement after use
   - Test reaching zero inventory

3. **"Infinite consumables" mode:**
   - Test flag that disables quantity tracking
   - Used in simulation mode

4. **Low-stock scenarios:**
   - Test warning threshold
   - Test rejection when inventory depleted

### Test File Structure

```python
# tests/backend/core/test_consumable_tracking.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from praxis.backend.core.consumable_assignment import ConsumableAssignmentService
from praxis.backend.models.orm.resource import ResourceOrm, ResourceDefinitionOrm

class TestConsumableTracking:
    """Tests for consumable inventory tracking."""

    @pytest.fixture
    def consumable_resource(self):
        """Create a mock consumable resource with quantity."""
        resource = MagicMock(spec=ResourceOrm)
        resource.accession_id = "res-001"
        resource.quantity = 96  # e.g., tips
        
        definition = MagicMock(spec=ResourceDefinitionOrm)
        definition.is_consumable = True
        definition.low_stock_threshold = 10
        
        resource.resource_definition = definition
        return resource

    async def test_consumable_quantity_tracked(self, consumable_resource):
        """Verify consumable quantity is properly tracked."""
        assert consumable_resource.quantity == 96
        assert consumable_resource.resource_definition.is_consumable is True

    async def test_consumption_decrements_quantity(self, service, consumable_resource):
        """Verify quantity decrements after consumption."""
        # Simulate consuming 8 tips
        initial = consumable_resource.quantity
        consumed = 8
        consumable_resource.quantity -= consumed
        assert consumable_resource.quantity == initial - consumed

    async def test_low_stock_warning(self, consumable_resource):
        """Test low stock warning when below threshold."""
        consumable_resource.quantity = 5  # Below threshold of 10
        threshold = consumable_resource.resource_definition.low_stock_threshold
        assert consumable_resource.quantity < threshold
        # Service should flag this in response

    async def test_depleted_consumable_rejected(self, service, mock_db_session):
        """Test that depleted consumables are not assigned."""
        # Create consumable with 0 quantity
        resource = create_mock_resource(
            accession_id="res-depleted",
            fqn="tips.standard",
            name="Empty Tips",
            num_items=0
        )
        resource.quantity = 0
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [resource]
        
        req = AssetRequirementModel(...)  # Request requiring tips
        result = await service.find_compatible_consumable(req)
        assert result is None  # Should not assign depleted resource


class TestInfiniteConsumablesMode:
    """Tests for infinite consumables simulation mode."""

    async def test_infinite_mode_ignores_quantity(self):
        """Verify infinite mode doesn't check quantity."""
        # When simulation mode has infinite_consumables=True,
        # quantity checks should be bypassed
        pass

    async def test_infinite_mode_flag_propagates(self):
        """Verify infinite mode setting reaches assignment service."""
        pass
```

### Integration with Existing Tests

Extend `test_consumable_assignment.py` with:

- More edge cases for quantity tracking
- Test for the `_is_consumable` method
- Test infinite consumables configuration

---

## 3. Context & References

**Primary Files to Create/Modify:**

| Path | Description |
|:-----|:------------|
| `tests/backend/core/test_consumable_tracking.py` | **NEW** - Dedicated consumable tracking tests |
| `tests/backend/core/test_consumable_assignment.py` | Extend existing tests |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/backend/core/consumable_assignment.py` | Service under test |
| `praxis/backend/models/orm/resource.py` | Resource model with `is_consumable` flag |
| `praxis/backend/models/pydantic_internals/resource.py` | Pydantic models |
| `tests/conftest.py` | Shared pytest fixtures |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run pytest` for testing
- **Backend Path**: `praxis/backend`
- **Test Path**: `tests/backend/core/`
- **Fixtures**: Use existing factory patterns from `tests/factories.py`
- **Async**: Use `pytest-asyncio` for async tests
- **Mocking**: Use `unittest.mock` for DB isolation

---

## 5. Verification Plan

**Definition of Done:**

1. All new tests pass:

   ```bash
   uv run pytest tests/backend/core/test_consumable_tracking.py -v
   ```

2. Existing consumable tests still pass:

   ```bash
   uv run pytest tests/backend/core/test_consumable_assignment.py -v
   ```

3. Full test suite passes:

   ```bash
   uv run pytest tests/ -v --ignore=tests/integration
   ```

4. Test coverage for consumable system:

   ```bash
   uv run pytest tests/backend/core/test_consumable*.py --cov=praxis.backend.core.consumable_assignment --cov-report=term-missing
   ```

---

## On Completion

- [ ] Commit changes with message: `test: add consumable tracking system tests`
- [ ] Update backlog item status in [testing.md](../../backlog/testing.md)
- [ ] Mark this prompt complete in batch README, update DEVELOPMENT_MATRIX.md if applicable, and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `tests/TESTING_PATTERNS.md` - Project testing conventions
- `.agents/codestyles/python.md` - Python conventions
