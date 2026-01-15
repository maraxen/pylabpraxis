# Maintenance Prompt: DRY Audit

**Purpose:** Identify and consolidate repeated code/logic  
**Frequency:** Quarterly  

---

## Prompt

```markdown
Examine .agent/README.md for development context.

## Task

Identify duplicated code and logic patterns, consolidate into shared utilities.

## Phase 1: Triage

1. **Search for Similar Patterns**:

   ```bash
   # Find duplicate error handling patterns
   grep -rn "raise HTTPException" praxis/backend --include="*.py" | wc -l
   
   # Find duplicate validation patterns
   grep -rn "if.*is None:" praxis/backend --include="*.py" | wc -l
   ```

1. **Review Service Layer for Patterns**:

   ```bash
   ls praxis/backend/services/*.py
   ```

## Phase 2: Categorize and Strategize

1. **Identify Duplication Types**:

   | Type | Examples | Consolidation |
   |:-----|:---------|:--------------|
   | **Utility functions** | String formatting, date parsing | Move to `utils/` |
   | **Validation logic** | Input validation patterns | Create validators |
   | **Error handling** | Exception patterns | Use decorators |
   | **CRUD operations** | Similar service methods | Use base classes |
   | **Frontend patterns** | Similar component logic | Create shared services |

2. **Document Extract Candidates**.

3. **Get User Input**: ⏸️ PAUSE for approval.

## Phase 3: Apply Fixes

1. **Extract Shared Utilities**:
   - Create utility functions in `praxis/backend/utils/`
   - Create shared Angular services

2. **Use Decorators**: For cross-cutting concerns.

3. **Apply Base Classes**: For similar service patterns.

4. **Update Imports**: Reference new shared code.

## Phase 4: Verify and Document

1. **Run Tests**: Ensure refactoring didn't break anything.

   ```bash
   uv run pytest tests/ -v
   cd praxis/web-client && npm test -- --run
   ```

2. **Update Health Audits**.

## DRY Checklist

- [ ] No duplicate utility functions
- [ ] Error handling uses decorators
- [ ] CRUD services extend base class
- [ ] Validation logic is centralized
- [ ] Frontend services don't duplicate logic

## References

- Existing utilities: `praxis/backend/utils/`
- Existing base classes: `praxis/backend/services/crud_base.py`

```

---

## Customization

This prompt is pre-configured for Praxis. No placeholders needed.
