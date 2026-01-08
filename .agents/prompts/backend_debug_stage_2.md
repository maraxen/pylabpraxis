# Backend Test Debugging - Stage 2 & Beyond

**Previous Status:**
Stage 1 (Factory Infrastructure & Integrity Errors) has been successfully completed. The `NOT NULL` constraint violations in `FunctionDataOutput` and `WellDataOutput` creation are resolved by fixing `init=False` in proper models and using `Meta.exclude` in factories.

**Current Objective:**
Resolve the remaining failures in `tests/services/test_well_outputs.py` and proceed to fix the broader suite of backend tests (Resource, Machine, Deck, and API tests).

**Primary Failures (Stage 2):**

1. **Polymorphic Identity Errors:**
    - `AssertionError: No such polymorphic_identity <AssetType.ASSET: 'GENERIC_ASSET'>`
    - Occurs in `test_get_multi_well_data_output`, `test_remove_well_data_output`, `test_get_well_data_output`.
    - **Root Cause:** `ResourceFactory` is likely creating instances with `asset_type="GENERIC_ASSET"`, but SQLAlchemy's polymorphic mapper for `ResourceOrm` (or its parent `AssetOrm`) expects a specific type (e.g., `RESOURCE` or distinct types like `PLATE`, `TIP_RACK`).
    - **Task:** Update `ResourceFactory` to use a valid, mapped `asset_type` (e.g., `AssetType.RESOURCE` or a concrete subclass type). Ensure `polymorphic_on` columns are correctly populated.

2. **Plate Dimension Errors:**
    - `ValueError: Could not determine plate dimensions` in `test_create_well_data_outputs_from_flat_array`.
    - **Task:** Ensure the test setup correctly mocks or populates the resource definition with dimension data (rows/columns) so that `read_plate_dimensions` works.

3. **Validation Errors:**
    - `ValidationError` in `test_create_well_data_output_invalid_well_name`.
    - **Task:** Verify if the validation logic in the service (or Pydantic model) matches the test expectation. The test might expect a custom `ValueError` but gets a Pydantic `ValidationError`.

**Subsequent Stages (Once Stage 2 is verified):**

**Stage 3: Resource, Machine & Deck Tests**

- Run `tests/test_resources.py`, `tests/test_machines.py`, `tests/test_decks.py`.
- Fix any factory-related issues similar to Stage 1.
- Address logic errors in CRUD services for these entities.

**Stage 4: API Tests**

- Run `tests/api/test_scheduler.py` (and others).
- Ensure API endpoints correctly handle the fixed service layer logic.
- Fix any transaction/session handling issues in the API routes.

**Stage 5: Final Validation**

- Run the full backend test suite: `uv run pytest tests/`
- Ensure coverage is acceptable (if required).

**Instructions for Agent:**

1. Start by analyzing `ResourceFactory` and the `AssetOrm`/`ResourceOrm` polymorphic configuration.
2. Fix the `ResourceFactory` to produce valid polymorphic instances.
3. Debug and fix the specific test cases in `test_well_outputs.py`.
4. Once `test_well_outputs.py` passes completely, move to Stage 3.
