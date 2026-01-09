# Agent Prompt: 15_ruff_remaining_fixes

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260109](./README.md)  
**Backlog:** [quality_assurance.md](../../backlog/quality_assurance.md)  

---

## Task

Address remaining Ruff errors manually. Current count is ~65 errors. Target: < 20 errors.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [quality_assurance.md](../../backlog/quality_assurance.md) | Work item tracking |
| `praxis/backend/` | Backend code to lint |

---

## Implementation

1. **Current State**:

   ```bash
   uv run ruff check praxis/backend
   ```

   - Document current error count
   - Categorize by rule

2. **Priority Fixes**:
   - F (Pyflakes) - Unused imports, undefined names
   - E (Errors) - Syntax and indentation
   - B (Bugbear) - Common bugs

3. **Deferred Items**:
   - Circular imports (complex to fix)
   - Stylistic issues (lower priority)

4. **Auto-fix Where Possible**:

   ```bash
   uv run ruff check --fix praxis/backend
   ```

---

## Success Criteria

- [ ] Ruff errors < 20
- [ ] All critical (F, E, B) categories resolved
- [ ] Document any deferred items with justification

---

## Project Conventions

- **Commands**: Use `uv run` for all Python commands

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
