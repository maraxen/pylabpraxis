# Maintenance Prompt: Dead Code Cleanup

**Purpose:** Identify and remove unused code  
**Frequency:** Quarterly  

---

## Prompt

```markdown
Examine .agents/README.md for development context.

## Task

Identify and remove unused code, deprecated features, and dead imports.

## Phase 1: Triage

1. **Find Unused Imports**:

   ```bash
   uv run ruff check praxis/backend --select F401 2>&1 | head -n 30
   ```

1. **Find Unused Variables/Functions** (requires vulture or manual review):

   ```bash
   # Using grep to find potentially unused functions
   grep -rn "^def " praxis/backend --include="*.py" | head -n 50
   ```

2. **Frontend Unused Exports**:

   Check for components/services not imported elsewhere.

## Phase 2: Categorize and Strategize

1. **Categorize Dead Code**:

   | Category | How to Identify | Action |
   |:---------|:----------------|:-------|
   | **Unused imports** | Ruff F401 | Remove |
   | **Unused functions** | No callers | Verify and remove |
   | **Unused variables** | Ruff F841 | Remove or prefix `_` |
   | **Commented code** | `# old_code()` | Remove |
   | **Deprecated features** | `# DEPRECATED` | Remove after verification |

2. **Document Strategy** before making changes.

3. **Get User Input**: ⏸️ PAUSE for approval.

## Phase 3: Apply Fixes

1. **Auto-fix Unused Imports**:

   ```bash
   uv run ruff check --fix praxis/backend --select F401
   ```

2. **Manual Removal**: Review and remove unused functions.

3. **Clean Up Comments**: Remove commented-out code blocks.

## Phase 4: Verify and Document

1. **Run Tests**: Ensure nothing broke.

   ```bash
   uv run pytest tests/ -x
   ```

2. **Update Health Audits**.

## References

- [codestyles/python.md](../../../codestyles/python.md)

```

---

## Customization

This prompt is pre-configured for Praxis. No placeholders needed.
