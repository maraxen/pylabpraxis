# Agent Prompt: 12_ty_type_checking

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [quality_assurance.md](../../backlog/quality_assurance.md)  

---

## Task

Run `ty` type checker on `praxis/backend` and fix type errors. `ty` is the preferred type checking tool over bare pyright.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [quality_assurance.md](../../backlog/quality_assurance.md) | Work item tracking |
| `praxis/backend/` | Backend code to check |

---

## Implementation

1. **Initial Check**:

   ```bash
   uv run ty praxis/backend
   ```

   - Document current error count
   - Categorize errors by severity

2. **Priority Categories**:
   - Critical: Type mismatches affecting runtime behavior
   - High: Missing return types on public functions
   - Medium: Optional type narrowing
   - Low: Stylistic type hints

3. **Fix Strategy**:
   - Fix critical errors first
   - Add missing type hints progressively
   - Use `# type: ignore` sparingly with explanation

4. **CI Integration**:
   - Consider adding `ty` check to CI pipeline
   - Set threshold for acceptable error count

---

## Success Criteria

- [ ] ty errors < 10 (from 10+)
- [ ] All critical type mismatches resolved
- [ ] Public API functions have return type hints

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
