# Maintenance Prompt: Docstring Audit

**Purpose:** Standardize docstrings, clean up comments  
**Frequency:** Per health audit  

---

## Prompt

```markdown
Examine .agents/README.md for development context.

## Task

Audit and standardize docstrings in the backend codebase.

## Phase 1: Triage

1. **Identify Files Without Docstrings**:

   ```bash
   grep -rL '"""' praxis/backend --include="*.py" | grep -v __pycache__ | head -n 30
   ```

1. **Count Module-Level Docstrings**:

   ```bash
   grep -r '^"""' praxis/backend --include="*.py" | wc -l
   ```

2. **Prioritize**: Start with core modules (`core/`, `services/`, `api/`).

## Phase 2: Categorize and Strategize

1. **Review Files by Module**:

   ```bash
   find praxis/backend/core -name "*.py" | head -n 10
   ```

2. **Categorize Issues**:

   | Issue | Action |
   |:------|:-------|
   | Missing module docstring | Add brief description |
   | Missing class docstring | Add class purpose |
   | Missing function docstring | Add for public functions |
   | Inline comment clutter | Move to docstrings or remove |
   | TODO/FIXME comments | Migrate to TECHNICAL_DEBT.md |

3. **Document Strategy** before applying fixes.

4. **Get User Input**: ⏸️ PAUSE for approval.

## Phase 3: Apply Fixes

### Docstring Standards

**Module Docstring**:

```python
"""Brief description of module purpose.

Extended description if needed.
"""
```

**Class Docstring**:

```python
class MyClass:
    """Brief description of class purpose.
    
    Attributes:
        attr1: Description of attr1.
    """
```

**Function Docstring**:

```python
def my_function(arg1: str, arg2: int) -> bool:
    """Brief description of function.
    
    Args:
        arg1: Description of arg1.
        arg2: Description of arg2.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When arg1 is empty.
    """
```

## Phase 4: Verify and Document

1. **Sample Verification**: Spot-check updated files.

2. **Update Health Audit**: `.agents/health_audit_backend.md`

## References

- [codestyles/python.md](../../../codestyles/python.md)

```

---

## Customization

This prompt targets Python backend only. For frontend, adapt to TSDoc format.
