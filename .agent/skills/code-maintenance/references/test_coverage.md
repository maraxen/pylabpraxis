# Maintenance Prompt: Test Coverage

**Purpose:** Analyze test coverage and identify gaps  
**Frequency:** Per health audit  

---

## Prompt

```markdown
Examine .agent/README.md for development context.

## Task

Run tests on backend and frontend, resolve failures, and address coverage gaps.

## Phase 1: Triage and Prioritize

1. **Run Tests**:

   **Backend (pytest)**:
   ```bash
   uv run pytest tests/ --tb=short > pytest_backend.log 2>&1
   ```

   **Frontend Unit (Vitest)**:

   ```bash
   cd praxis/web-client && npm test -- --run > ../vitest_frontend.log 2>&1
   ```

   **Frontend E2E (Playwright)**:

   ```bash
   cd praxis/web-client && npx playwright test > ../playwright_e2e.log 2>&1
   ```

1. **Count Failures**:

   ```bash
   tail -n 10 pytest_backend.log vitest_frontend.log playwright_e2e.log
   ```

2. **Prioritize**: Start with the test suite that has fewest failures.

## Phase 2: Categorize and Strategize

1. **Review Failures**:

   ```bash
   grep -A 20 "FAILED\|ERROR" pytest_backend.log | head -n 50
   ```

2. **Categorize Failures**:

   | Category | Pattern | Action |
   |:---------|:--------|:-------|
   | Import errors | `ImportError`, `ModuleNotFoundError` | Fix imports or dependencies |
   | Type errors | `TypeError`, `AttributeError` | Check API changes |
   | Assertion failures | `AssertionError` | Investigate logic |
   | Fixture issues | `fixture not found` | Check fixture scope |
   | Skipped tests | `@pytest.mark.skip` | Review if skip is still valid |

3. **Document Strategy** before applying fixes.

4. **Get User Input**: ⏸️ PAUSE for approval.

## Phase 3: Apply Fixes (Targeted Testing)

**Important**: Do NOT run full test suites until final verification.

1. **Target Individual Tests**:

   **Backend**:

   ```bash
   uv run pytest tests/path/to/test_file.py -v
   uv run pytest tests/test_file.py::test_function_name -v
   ```

   **Frontend**:

   ```bash
   cd praxis/web-client && npm test -- --run src/app/path/to/file.spec.ts
   cd praxis/web-client && npx playwright test e2e/specific.spec.ts
   ```

2. **Use Verbosity Appropriately**:

   | Flag | Use Case |
   |:-----|:---------|
   | `-v` | See test names |
   | `--tb=short` | Compact tracebacks |
   | `-x` | Stop on first failure |
   | `--lf` | Run only last failed |

## Phase 4: Verify and Document

1. **Final Verification**:

   ```bash
   uv run pytest tests/ -v 2>&1 | tail -n 20
   cd praxis/web-client && npm test -- --run 2>&1 | tail -n 20
   ```

2. **Coverage Report** (optional):

   ```bash
   uv run pytest tests/ --cov=praxis/backend --cov-report=term-missing
   ```

3. **Update Health Audit**:
   - Backend: `.agent/health_audit_backend.md`
   - Frontend: `.agent/health_audit_frontend.md`

## References

- [codestyles/python.md](../../../codestyles/python.md)
- [codestyles/typescript.md](../../../codestyles/typescript.md)

```

---

## Customization

This prompt is pre-configured for Praxis. No placeholders needed.
