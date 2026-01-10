# Agent Prompt: Final Review — Alembic Migration + Full Integration Test

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260110](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)
**Phase:** 7.2 — Final Review & Validation
**Parallelizable:** ❌ Sequential — Final step after all other phases

---

## 1. The Task

Perform final validation of the SQLModel migration by generating an Alembic migration (to verify metadata compatibility), running the full test suite, and verifying the complete pipeline from backend models through frontend types.

**User Value:** Confidence that the unified model architecture is production-ready.

---

## 2. Technical Implementation Strategy

### Alembic Verification

Since table structures shouldn't have changed (only Python class definitions), Alembic should detect:
- No new tables (structures unchanged)
- No dropped columns (structures unchanged)
- SQLModel metadata is correctly registered

```bash
# Generate migration to verify no structural changes
uv run alembic revision --autogenerate -m "verify_sqlmodel_migration"

# Check the generated migration file
# Should be empty or have minimal changes (like enum value order)
```

### Full Test Suite

```bash
# Run all tests with coverage
uv run pytest tests/ -v --cov=praxis --cov-report=html

# Check coverage thresholds
# Target: Same or better coverage than before migration
```

### OpenAPI Pipeline Verification

```bash
# Generate OpenAPI schema
uv run python scripts/generate_openapi.py

# Generate TypeScript client
cd praxis/web-client
npm run generate-api

# Build frontend
npm run build
```

### Integration Test Checklist

1. **Backend startup**: App starts without errors
2. **API endpoints**: All CRUD operations work
3. **Database operations**: Create, read, update, delete work
4. **Frontend integration**: TypeScript compiles, UI renders

---

## 3. Context & References

**Primary Verification Targets:**

| Component | Verification Method |
|:----------|:--------------------|
| SQLModel metadata | Alembic autogenerate |
| Database operations | Test suite |
| API endpoints | API tests + smoke test |
| OpenAPI schema | Schema generation |
| TypeScript types | Frontend build |
| Full pipeline | Manual integration test |

**Reference Files:**

| Path | Description |
|:-----|:------------|
| `alembic/env.py` | Alembic environment |
| `alembic/versions/` | Migration history |
| `tests/` | Test suite |
| `scripts/generate_openapi.py` | OpenAPI generator |
| `praxis/web-client/` | Frontend app |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python, `npm` for Node.
- **Database**: Use test database for Alembic verification
- **No schema changes**: Migration should be empty or minimal

### Sharp Bits / Technical Debt

1. **Migration conflicts**: If others have added migrations, may need to merge
2. **Enum ordering**: SQLAlchemy may reorder enums; this is cosmetic
3. **Index naming**: SQLModel may generate different index names
4. **Test flakiness**: Some tests may be flaky; run multiple times

---

## 5. Verification Plan

**Definition of Done:**

1. Alembic migration generates (empty or minimal):
   ```bash
   uv run alembic revision --autogenerate -m "verify_sqlmodel_migration"
   cat alembic/versions/*verify_sqlmodel_migration*.py
   # upgrade() and downgrade() should be empty or minimal
   ```

2. Alembic upgrade succeeds:
   ```bash
   uv run alembic upgrade head
   ```

3. Full test suite passes:
   ```bash
   uv run pytest tests/ -v --tb=short
   ```

4. Coverage is maintained:
   ```bash
   uv run pytest tests/ --cov=praxis --cov-report=term-missing
   # Check coverage percentage
   ```

5. OpenAPI schema generates:
   ```bash
   uv run python scripts/generate_openapi.py
   # Verify openapi.json is valid JSON
   python -m json.tool praxis/web-client/src/assets/api/openapi.json > /dev/null
   ```

6. Frontend builds:
   ```bash
   cd praxis/web-client
   npm run generate-api
   npm run build
   ```

7. Manual smoke test:
   - Start backend: `uv run uvicorn praxis.backend.main:app`
   - Start frontend: `npm start`
   - Navigate through app
   - Test CRUD operations

---

## 6. Implementation Steps

1. **Verify Alembic sees SQLModel metadata**:
   ```bash
   uv run python -c "
   from alembic.config import Config
   from alembic import context
   from praxis.backend.models.domain import *
   from sqlmodel import SQLModel
   print(f'SQLModel tables: {list(SQLModel.metadata.tables.keys())}')
   "
   ```

2. **Generate verification migration**:
   ```bash
   uv run alembic revision --autogenerate -m "verify_sqlmodel_migration"
   ```

3. **Review migration file**:
   - If empty: Great, schema unchanged
   - If changes: Review each change carefully

4. **Apply migration to test database**:
   ```bash
   uv run alembic upgrade head
   ```

5. **Run full test suite**:
   ```bash
   uv run pytest tests/ -v --tb=short 2>&1 | tee test_results.log
   ```

6. **Generate coverage report**:
   ```bash
   uv run pytest tests/ --cov=praxis --cov-report=html
   open htmlcov/index.html  # Review coverage
   ```

7. **Verify OpenAPI pipeline**:
   ```bash
   uv run python scripts/generate_openapi.py
   cd praxis/web-client
   npm run generate-api
   npm run build
   ```

8. **Manual integration test**:
   - Start both servers
   - Test each major feature
   - Document any issues

9. **Clean up verification migration** (if empty):
   ```bash
   # If migration was empty, remove it
   rm alembic/versions/*verify_sqlmodel_migration*.py
   ```

10. **Update project documentation**:
    - Update README if needed
    - Update CONTRIBUTING.md
    - Update TECHNICAL_DEBT.md (remove SQLModel migration item)

---

## 7. Final Checklist

| Item | Status |
|:-----|:-------|
| Alembic migration empty/minimal | ⬜ |
| All 200+ tests pass | ⬜ |
| Coverage maintained (>X%) | ⬜ |
| OpenAPI schema valid | ⬜ |
| TypeScript client generated | ⬜ |
| Frontend builds | ⬜ |
| Manual smoke test passed | ⬜ |
| Documentation updated | ⬜ |
| Backlog item closed | ⬜ |

---

## 8. Rollback Plan

If critical issues are found:

1. **Revert to backup branch**:
   ```bash
   git checkout backup/pre-legacy-cleanup
   ```

2. **Document issues** in `.agents/NOTES.md`

3. **Create targeted fix prompts** for specific issues

---

## On Completion

- [ ] Commit changes with message: `docs: finalize SQLModel migration documentation`
- [ ] Update backlog item status in `sqlmodel_codegen_refactor.md` (All phases → Done)
- [ ] Close/archive the backlog item
- [ ] Update `DEVELOPMENT_MATRIX.md` if this was tracked there
- [ ] Mark this prompt complete in batch README
- [ ] Mark entire batch as ✅ Complete

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Full migration plan
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
