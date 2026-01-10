# Agent Prompt: Consumable Assignment Service Tests

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P3
**Batch:** [260109](./README.md)
**Backlog Reference:** [testing.md](../../backlog/testing.md)

---

## 1. The Task

Extend test coverage for the `ConsumableAssignmentService`. The existing tests cover basic scenarios but need additional coverage for:

- The `_is_consumable()` method type detection logic
- Type matching patterns in `_type_matches()`
- Edge cases for volume matching and candidate scoring
- Expiration date handling and warnings
- Multi-candidate selection with varying scores

**User Value:** Confidence that consumable auto-assignment correctly matches requirements to available resources based on volume, type compatibility, and availability.

---

## 2. Technical Implementation Strategy

### Architecture

**Core Service:** `ConsumableAssignmentService`

- Located at: `praxis/backend/core/consumable_assignment.py`
- Scores candidates using `CompatibilityScore` with factors:
  - `volume_match` - Volume capacity vs. requirements
  - `availability` - Not reserved by another run
  - `expiration` - Warnings for expired consumables
- Key methods:
  - `find_compatible_consumable()` - Main entry point
  - `auto_assign_consumables()` - Batch assignment
  - `_is_consumable()` - Type detection from `type_hint_str`
  - `_type_matches()` - FQN pattern matching
  - `_score_candidate()` - Multi-factor scoring
  - `_get_reserved_asset_ids()` - Reservation filtering

**Existing Tests:** `tests/backend/core/test_consumable_assignment.py`

- 4 test functions covering:
  - Basic volume matching
  - No-match when volume too small
  - Expired consumable warnings
  - Reserved resource exclusion

### Test Gaps to Address

1. **`_is_consumable()` method:**
   - Test all keyword patterns: `plate`, `tip`, `tiprack`, `trough`, `reservoir`, `tube`, `well`
   - Test non-consumable types return `False`

2. **`_type_matches()` pattern matching:**
   - Test `plate` patterns match `plate`, `well_plate`, `microplate`
   - Test `tip` patterns match `tip`, `tiprack`, `tip_rack`
   - Test `trough` patterns match `trough`, `reservoir`, `container`
   - Test fallback substring matching

3. **Scoring edge cases:**
   - Multiple candidates with different scores
   - Tie-breaking behavior
   - Zero-volume candidates rejected
   - All candidates reserved (no match)

4. **Workcell filtering:**
   - Test `workcell_id` constraint narrows search

### Test File Updates

```python
# tests/backend/core/test_consumable_assignment.py - ADD to existing file

class TestIsConsumable:
    """Tests for _is_consumable type detection."""

    @pytest.fixture
    def service(self, mock_db_session):
        return ConsumableAssignmentService(mock_db_session)

    @pytest.mark.parametrize("type_hint,expected", [
        ("pylabrobot.resources.Plate", True),
        ("pylabrobot.resources.TipRack", True),
        ("pylabrobot.resources.Trough", True),
        ("pylabrobot.resources.Reservoir", True),
        ("pylabrobot.resources.Tube", True),
        ("pylabrobot.resources.Well", True),
        ("pylabrobot.machines.LiquidHandler", False),
        ("pylabrobot.resources.Deck", False),
        ("str", False),
    ])
    def test_is_consumable_type_detection(self, service, type_hint, expected):
        """Verify type hint detection for consumables."""
        req = AssetRequirementModel(
            accession_id=uuid7(),
            name="test",
            fqn=type_hint,
            type_hint_str=type_hint.split(".")[-1]  # Just the class name
        )
        assert service._is_consumable(req) == expected


class TestTypeMatches:
    """Tests for _type_matches FQN pattern matching."""

    @pytest.fixture
    def service(self, mock_db_session):
        return ConsumableAssignmentService(mock_db_session)

    @pytest.mark.parametrize("required,resource_fqn,expected", [
        ("plate", "pylabrobot.resources.corning.Cor_96_wellplate", True),
        ("plate", "pylabrobot.resources.microplate", True),
        ("tip", "pylabrobot.resources.tip_rack", True),
        ("tip", "pylabrobot.resources.tiprack", True),
        ("trough", "pylabrobot.resources.reservoir", True),
        ("plate", "pylabrobot.machines.LiquidHandler", False),
    ])
    def test_type_matching_patterns(self, service, required, resource_fqn, expected):
        """Verify FQN pattern matching logic."""
        assert service._type_matches(required, resource_fqn) == expected


class TestCandidateScoring:
    """Tests for multi-factor candidate scoring."""

    @pytest.mark.asyncio
    async def test_multiple_candidates_best_score_wins(self, service, mock_db_session):
        """Verify highest scoring candidate is selected."""
        # Create two candidates: one with better volume match
        candidate_good = create_mock_resource(
            "res1", "pylabrobot.resources.Plate", "Good Plate",
            nominal_volume_ul=500
        )
        candidate_ok = create_mock_resource(
            "res2", "pylabrobot.resources.Plate", "OK Plate",
            nominal_volume_ul=200
        )
        
        req = AssetRequirementModel(
            accession_id=uuid7(),
            name="plate",
            fqn="pylabrobot.resources.Plate",
            type_hint_str="Plate",
            constraints=AssetConstraintsModel(min_volume_ul=400)
        )
        
        service._get_reserved_asset_ids = AsyncMock(return_value=[])
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [candidate_ok, candidate_good]
        mock_db_session.execute.return_value = mock_result
        
        result = await service.find_compatible_consumable(req)
        assert result == "res1"  # Better volume match wins
```

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `tests/backend/core/test_consumable_assignment.py` | Extend existing test file |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/backend/core/consumable_assignment.py` | Service under test (455 lines) |
| `praxis/backend/models/orm/resource.py` | `ResourceOrm`, `ResourceDefinitionOrm` with `is_consumable` flag |
| `praxis/backend/models/pydantic_internals/protocol.py` | `AssetRequirementModel`, `AssetConstraintsModel` |

**Key Model Fields:**

- `ResourceDefinitionOrm.is_consumable` (bool) - Flag on definition
- `ResourceDefinitionOrm.nominal_volume_ul` (float) - Volume capacity
- `ResourceOrm.properties_json` - May contain `expiration_date`

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run pytest` for testing
- **Backend Path**: `praxis/backend`
- **Test Path**: `tests/backend/core/`
- **Fixtures**: Follow existing `create_mock_resource()` helper pattern
- **Async**: Use `pytest-asyncio` and `@pytest.mark.asyncio`
- **Mocking**: Use `unittest.mock.AsyncMock` for DB session

---

## 5. Verification Plan

**Definition of Done:**

1. Existing tests still pass:

   ```bash
   uv run pytest tests/backend/core/test_consumable_assignment.py -v
   ```

2. New tests pass:

   ```bash
   uv run pytest tests/backend/core/test_consumable_assignment.py -v -k "TestIsConsumable or TestTypeMatches or TestCandidateScoring"
   ```

3. Coverage improved:

   ```bash
   uv run pytest tests/backend/core/test_consumable_assignment.py --cov=praxis.backend.core.consumable_assignment --cov-report=term-missing
   ```

---

## On Completion

- [ ] Commit changes with message: `test: extend consumable assignment service tests`
- [ ] Update backlog item status in [testing.md](../../backlog/testing.md)
- [ ] Mark this prompt complete in batch README, update DEVELOPMENT_MATRIX.md if applicable, and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `tests/TESTING_PATTERNS.md` - Project testing conventions
- `.agents/codestyles/python.md` - Python conventions
