# Maintenance Prompt: Dependency Audit

**Purpose:** Review dependency freshness and security  
**Frequency:** Quarterly  

---

## Prompt

```markdown
Examine .agent/README.md for development context.

## Task

Audit dependencies for freshness, security vulnerabilities, and unused packages.

## Phase 1: Triage

1. **Check Outdated Dependencies**:

   **Backend (Python)**:
   ```bash
   uv pip list --outdated 2>&1 | head -n 30
   ```

   **Frontend (npm)**:

   ```bash
   cd praxis/web-client && npm outdated 2>&1 | head -n 30
   ```

1. **Security Audit**:

   **Backend**:

   ```bash
   uv pip audit 2>&1 | head -n 30
   ```

   **Frontend**:

   ```bash
   cd praxis/web-client && npm audit 2>&1 | head -n 30
   ```

## Phase 2: Categorize and Strategize

1. **Categorize Updates**:

   | Priority | Type | Action |
   |:---------|:-----|:-------|
   | **Critical** | Security vulnerabilities | Update immediately |
   | **High** | Major version behind + breaking changes | Plan migration |
   | **Medium** | Minor/patch updates | Update in batch |
   | **Low** | Optional updates | Defer |

2. **Document Update Plan**.

3. **Get User Input**: ⏸️ PAUSE for approval.

## Phase 3: Apply Fixes

1. **Update Dependencies**:

   **Backend**:

   ```bash
   uv pip install --upgrade <package>
   uv pip freeze > requirements.txt  # or update pyproject.toml
   ```

   **Frontend**:

   ```bash
   cd praxis/web-client && npm update <package>
   ```

2. **Run Tests After Updates**:

   ```bash
   uv run pytest tests/ -x
   cd praxis/web-client && npm test -- --run
   ```

## Phase 4: Verify and Document

1. **Re-run Audit**: Confirm vulnerabilities resolved.
2. **Update Health Audits**.

## References

- `pyproject.toml`
- `praxis/web-client/package.json`

```

---

## Customization

This prompt is pre-configured for Praxis. No placeholders needed.
