# Maintenance Prompt: Linting

**Purpose:** Run Ruff (Python) and ESLint (TypeScript) and resolve violations  
**Frequency:** Per health audit  

---

## Prompt

```markdown
Examine .agents/README.md for development context.

## Task

Run linting on backend and frontend, resolve all violations.

## Phase 1: Triage and Prioritize

1. **Run Linters**:

   **Backend (Python)**:
   ```bash
   uv run ruff check praxis/backend > ruff_backend.log 2>&1
   ```

   **Frontend (TypeScript)**:

   ```bash
   cd praxis/web-client && npm run lint > ../eslint_frontend.log 2>&1
   ```

1. **Count Violations**:

   ```bash
   tail -n 5 ruff_backend.log eslint_frontend.log
   ```

2. **Prioritize**: Start with the layer that has fewer violations.

## Phase 2: Categorize and Strategize

1. **Review the Log**:

   ```bash
   cat ruff_backend.log | head -n 100
   ```

2. **Categorize Issues**:

   **Python (Ruff)**:

   | Category | Codes | Action |
   |:---------|:------|:-------|
   | Unused imports | F401 | Remove or add `# noqa: F401` if re-export |
   | Undefined names | F821 | Fix missing imports |
   | Unused variables | F841 | Remove or prefix with `_` |
   | Import order | I* | Auto-fixed |
   | Complexity | C901 | Consider refactoring |

   **TypeScript (ESLint)**:

   | Category | Rule | Action |
   |:---------|:-----|:-------|
   | Explicit any | @typescript-eslint/no-explicit-any | Add proper types |
   | Unused vars | @typescript-eslint/no-unused-vars | Remove or prefix |
   | Missing return | explicit-function-return-type | Add return type |

3. **Document Strategy** before applying fixes.

4. **Get User Input**: ⏸️ PAUSE for approval.

## Phase 3: Apply Fixes

1. **Auto-fix Safe Violations**:

   **Backend**:

   ```bash
   uv run ruff check --fix praxis/backend
   uv run ruff format praxis/backend
   ```

   **Frontend**:

   ```bash
   cd praxis/web-client && npm run lint -- --fix
   ```

2. **Handle Remaining Issues Manually**.

## Phase 4: Verify and Document

1. **Verify**:

   ```bash
   uv run ruff check praxis/backend --quiet
   cd praxis/web-client && npm run lint
   ```

2. **Update Health Audit**:
   - Backend: `.agents/health_audit_backend.md`
   - Frontend: `.agents/health_audit_frontend.md`

## References

- [codestyles/python.md](../../../codestyles/python.md)
- [codestyles/typescript.md](../../../codestyles/typescript.md)

```

---

## Customization

This prompt is pre-configured for Praxis. No placeholders needed.
