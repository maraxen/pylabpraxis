# Agent Prompt: Fix Remaining Test Failures in Domain Models

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P3
**Batch:** [260112_2](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md) (Phase 7.1)
**Dependencies:** P1_01 must be completed first

---

## 1. The Task

Resolve the 92 remaining test failures in `tests/models/test_domain/` after P1 adds the missing Relationship fields.

**User Value**: Completes the SQLModel migration testing suite, ensuring domain models work correctly with the new unified architecture. Achieves 100% test pass rate for domain models.

**Context**: Once P1 adds Relationship fields to `FunctionProtocolDefinition`, the 16 setup errors will be resolved. However, 92 test failures remain due to:

- Schema serialization/deserialization issues
- Model creation with default values
- Polymorphic identity tests
- Relationship navigation patterns

---

## 2. Technical Implementation Strategy

**Architecture**: Systematic test debugging and fixture updates.

**Investigation Phase:**

1. **Run Full Test Suite** to get current status:

   ```bash
   uv run pytest tests/models/test_domain/ -v --tb=short > test_results.txt 2>&1
   ```

2. **Categorize Failures** by error type:
   - Import errors (should be fixed by P1)
   - Schema validation errors
   - Relationship navigation errors
   - Model instantiation errors
   - Serialization/deserialization errors

3. **Identify Patterns**:
   - Common error messages
   - Affected model types
   - Test fixture issues

**Fix Strategy by Category:**

**Category 1: Schema Serialization Issues** (~30 failures in test_deck.py, test_resource.py, test_workcell.py)

- Pattern: `test_*_response_serialization_to_dict`
- Likely cause: Missing fields in Read schemas
- Fix: Add missing fields to `*Read` schema classes

**Category 2: Model Creation with Defaults** (~20 failures)

- Pattern: `test_*_creation_defaults`, `test_*_orm_creation_minimal`
- Likely cause: Required fields without defaults
- Fix: Add sensible defaults or update test fixtures

**Category 3: Polymorphic Identity** (~5 failures in test_asset_sqlmodel.py)

- Pattern: `test_polymorphic_identity`, `test_asset_creation_defaults`
- Likely cause: Asset inheritance issues (Table-Per-Class pivot)
- Fix: Update tests to reflect Table-Per-Class pattern (no shared `assets` table)

**Category 4: Relationship Navigation** (~15 failures)

- Pattern: Tests accessing `.related_model` attributes
- Likely cause: Missing back_populates or wrong fixture setup
- Fix: Ensure bidirectional relationships are properly configured

**Category 5: JSONB Field Handling** (~10 failures)

- Pattern: Tests with `_json` suffix fields
- Likely cause: Dict validation or JSON serialization
- Fix: Update test data to match expected JSON structures

**Category 6: Constraint Violations** (~12 failures)

- Pattern: `test_*_unique_constraint`, IntegrityError
- Likely cause: Test isolation issues or missing cleanup
- Fix: Ensure unique values in test data

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `tests/models/test_domain/test_deck.py` | 22 failures - schema & relationship tests |
| `tests/models/test_domain/test_asset_sqlmodel.py` | 3 failures - polymorphic tests |
| `tests/models/test_domain/test_file_system_protocol_source.py` | 8 failures |
| `tests/models/test_domain/test_asset_requirement.py` | 3 failures |
| `tests/models/test_domain/test_machine.py` | 5 failures |
| `tests/models/test_domain/test_machine_definition.py` | 9 failures |
| `tests/models/test_domain/test_function_protocol_definition.py` | 12 failures |
| `tests/models/test_domain/test_parameter_definition.py` | 3 failures |
| `tests/models/test_domain/test_protocol_source_repository.py` | 6 failures |
| `tests/models/test_domain/test_resource.py` | 7 failures |
| `tests/models/test_domain/test_resource_definition.py` | 2 failures |
| `tests/models/test_domain/test_workcell.py` | 8 failures |
| `tests/models/test_domain/test_sqlmodel_base.py` | 2 failures |

**Reference Files:**

| Path | Description |
|:-----|:------------|
| `domain_model_pytest.log` | Full test output log with all errors |
| `praxis/backend/models/domain/*.py` | Domain models (after P1 & P2 fixes) |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run pytest` for testing
- **Test Path**: `tests/models/test_domain/`
- **Debugging**: Use `--tb=short` for concise tracebacks, `-v` for verbose output
- **Isolation**: Run single test files first before full suite
- **Fixtures**: Prefer updating fixtures over changing tests
- **Coverage**: Don't worry about coverage threshold (11%) until tests pass

---

## 5. Verification Plan

**Definition of Done:**

1. All 92+ test failures resolved
2. Test collection succeeds with 0 errors:

   ```bash
   uv run pytest tests/models/test_domain/ --collect-only --quiet
   ```

3. Full test suite passes:

   ```bash
   uv run pytest tests/models/test_domain/ -v
   ```

4. No regression in other test suites:

   ```bash
   uv run pytest tests/api/ tests/services/ --collect-only --quiet
   ```

5. Coverage improves significantly (target: >80%):

   ```bash
   uv run pytest tests/models/test_domain/ --cov=praxis/backend/models/domain --cov-report=term-missing
   ```

**Incremental Verification**:

```bash
# Fix by category, verify after each:
uv run pytest tests/models/test_domain/test_deck.py -v -k "response_serialization"
uv run pytest tests/models/test_domain/test_asset_sqlmodel.py -v
uv run pytest tests/models/test_domain/ -v --maxfail=5  # Stop after 5 failures
```

---

## On Completion

- [ ] All domain model tests passing
- [ ] Commit changes with message: "test(models): fix domain model test suite after relationship additions"
- [ ] Update [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md) Phase 7.1 status
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md) with completion
- [ ] Mark this prompt complete in [batch README](./README.md)
- [ ] Set status to 🟢 Completed in this file
- [ ] Document any discovered patterns in `.agents/NOTES.md`

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Migration context
- `domain_model_pytest.log` - Full test failure analysis
- [Pytest Documentation](https://docs.pytest.org/)
- [SQLModel Testing Best Practices](https://sqlmodel.tiangolo.com/tutorial/testing/)
