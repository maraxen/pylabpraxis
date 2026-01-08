# Agent Prompt: 10_browser_schema_scripts

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260108](./README.md)  
**Backlog:** [browser_mode.md](../../backlog/browser_mode.md)  
**Priority:** P2

---

## Task

Fix the `generate_browser_schema.py` and `generate_browser_db.py` scripts that are failing due to SQLAlchemy metadata initialization issues.

---

## Problem Statement

The browser mode schema generation scripts fail during execution:

```bash
uv run scripts/generate_browser_schema.py
# Error: SQLAlchemy metadata not properly initialized
```

This prevents schema updates from being applied to the browser-mode SQLite database.

---

## Implementation Steps

### 1. Investigate Script Failures

Run the scripts and capture detailed error output:

```bash
uv run scripts/generate_browser_schema.py 2>&1 | head -50
uv run scripts/generate_browser_db.py 2>&1 | head -50
```

### 2. Debug SQLAlchemy Metadata Initialization

Check how the ORM models are being imported and whether metadata is accessible:

```python
# Look for issues like:
# - Circular imports preventing model loading
# - Missing Base.metadata configuration
# - Async engine vs sync engine mismatch
```

### 3. Fix Script Initialization

Ensure proper model import order and metadata access:

```python
# Correct pattern:
from praxis.backend.models.orm import Base
# All ORM models should be imported before accessing Base.metadata
```

### 4. Verify Fix

```bash
uv run scripts/generate_browser_schema.py && echo "Schema generated successfully"
uv run scripts/generate_browser_db.py && echo "DB generated successfully"
```

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [browser_mode.md](../../backlog/browser_mode.md) | Backlog tracking |
| [scripts/generate_browser_schema.py](file:///Users/mar/Projects/pylabpraxis/scripts/generate_browser_schema.py) | Schema generation script |
| [scripts/generate_browser_db.py](file:///Users/mar/Projects/pylabpraxis/scripts/generate_browser_db.py) | DB generation script |
| [praxis/backend/models/orm/**init**.py](file:///Users/mar/Projects/pylabpraxis/praxis/backend/models/orm/__init__.py) | ORM base |

---

## Project Conventions

- **Commands**: Use `uv run` for all Python commands

See [codestyles/python.md](../../codestyles/python.md) for conventions.

---

## On Completion

- [ ] Commit changes with message: `fix(scripts): resolve browser schema generation failures`
- [ ] Update [browser_mode.md](../../backlog/browser_mode.md) - mark Browser Schema Scripts complete
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
