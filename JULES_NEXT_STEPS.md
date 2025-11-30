# ORM Test Failures Analysis

## Import/Circular Dependency Errors
*   **Missing Enum Attributes**: `AttributeError: type object 'ProtocolSourceStatusEnum' has no attribute 'SYNCING'` and `INACTIVE`. This indicates that the `ProtocolSourceStatusEnum` definition in `praxis/backend/models/enums.py` (or where it is defined) is missing these members, which are expected by the tests or ORM models.

## Database Schema/Constraint Errors
*   **None Observed (Masked)**: No explicit `IntegrityError`, `UniqueViolationError`, or `ForeignKeyViolationError` were found in the logs. However, this is likely because the tests fail at the object instantiation stage (before database persistence) due to the initialization errors below.

## Pydantic/Validation Errors
*   **ORM Initialization Mismatches (MappedAsDataclass Strictness)**: The majority of failures are `TypeError`s during ORM object instantiation. This is due to `MappedAsDataclass` enforcing strict `__init__` signatures that do not match the arguments provided in tests.
    *   **Unexpected `accession_id`**: `TypeError: __init__() got an unexpected keyword argument 'accession_id'`. The `accession_id` field is likely marked as `init=False` in the model (or handled by a default factory), but tests are explicitly passing it.
    *   **Missing Required Arguments**:
        *   `TypeError: __init__() missing 1 required keyword-only argument: 'name'`. The `name` field (inherited from `AssetOrm` or similar) is required but not provided.
        *   `TypeError: __init__() missing 2 required keyword-only arguments: 'source_repository' and 'file_system_source'`.
    *   **Unexpected Relationship Arguments**:
        *   `TypeError: __init__() got an unexpected keyword argument 'protocol_run'`.
        *   `TypeError: __init__() got an unexpected keyword argument 'has_deck'`.
        *   `TypeError: __init__() got an unexpected keyword argument 'created_by'`.
    *   **Field Mismatches**: Tests are treating ORM models like Pydantic models or standard classes, but the `MappedAsDataclass` configuration requires specific argument patterns (e.g., `kw_only=True` for fields following defaults, no `init=False` fields in constructor).
