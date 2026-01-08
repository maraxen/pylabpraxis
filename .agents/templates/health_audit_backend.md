# Backend Health Audit

**Last Updated**: YYYY-MM-DD  
**Auditor**: [Agent/Human]  
**Overall Status**: 🟢 Healthy | 🟡 Needs Attention | 🔴 Critical Issues

---

## Quick Summary

| Category | Status | Issues | Notes |
| :--- | :--- | :--- | :--- |
| Linting (Ruff) | 🟢/🟡/🔴 | 0 | |
| Type Checking (Pyright) | 🟢/🟡/🔴 | 0 | |
| Tests (pytest) | 🟢/🟡/🔴 | 0 passed, 0 failed, 0 skipped | |
| Imports | 🟢/🟡/🔴 | 0 | |
| Dependencies | 🟢/🟡/🔴 | 0 | |

---

## Linting Issues

**Command**: `uv run ruff check praxis/backend`  
**Status**: 🟢/🟡/🔴

### Summary

[Brief description of linting state]

### Outstanding Issues

| File | Rule | Description | Priority |
| :--- | :--- | :--- | :--- |
| `path/to/file.py` | `E501` | Line too long | Low |

### Configuration Notes

[Any relevant pyproject.toml configurations, ignored rules, etc.]

---

## Type Checking Issues

**Command**: `uv run pyright praxis/backend`  
**Status**: 🟢/🟡/🔴

### Summary

[Brief description of type checking state]

### Outstanding Issues

| File | Error | Description | Priority |
| :--- | :--- | :--- | :--- |
| `path/to/file.py` | `reportGeneralTypeIssues` | Description | Medium |

### Configuration Notes

[Any pyright configuration, type stubs needed, etc.]

---

## Test Failures

**Command**: `uv run pytest tests/ -v`  
**Status**: 🟢/🟡/🔴

### Summary

- **Passed**: 0
- **Failed**: 0
- **Skipped**: 0
- **Errors**: 0

### Failing Tests

| Test | Error Type | Description | Priority |
| :--- | :--- | :--- | :--- |
| `test_module::TestClass::test_name` | `TypeError` | Brief description | High |

### Skipped Tests

| Test | Reason | Action Needed |
| :--- | :--- | :--- |
| `test_module::test_name` | Missing dependency | Install `package` |

---

## Import Issues

**Status**: 🟢/🟡/🔴

### Circular Imports

| Files | Description |
| :--- | :--- |
| `module_a.py` ↔ `module_b.py` | Description |

### Missing/Broken Imports

| File | Import | Error | Fix |
| :--- | :--- | :--- | :--- |
| `file.py` | `from package import X` | `ModuleNotFoundError` | Install/fix path |

---

## Dependency Issues

**Status**: 🟢/🟡/🔴

### Missing Dependencies

| Package | Required By | Resolution |
| :--- | :--- | :--- |
| `package` | `module.py` | Add to `pyproject.toml` |

### Version Conflicts

| Package | Required | Installed | Resolution |
| :--- | :--- | :--- | :--- |
| `pylabrobot` | `>=0.2.0` | `0.1.5` | Upgrade |

---

## Other Audits

| Audit Type | Last Run | Status | Notes |
| :--- | :--- | :--- | :--- |
| **Docstrings** | YYYY-MM-DD | 🟢/🟡/🔴 | [Coverage %, compliance check] |
| **Dead Code** | YYYY-MM-DD | 🟢/🟡/🔴 | [Unused functions/files found] |
| **DRY Audit** | YYYY-MM-DD | 🟢/🟡/🔴 | [Duplications found, consolidations made] |
| **TODO Audit** | YYYY-MM-DD | 🟢/🟡/🔴 | [TODOs found, migrated to tech debt] |
| **Security** | YYYY-MM-DD | 🟢/🟡/🔴 | [Vulnerability scan results] |

---

## Action Items

### High Priority

- [ ] Fix `test_x` - causes CI to fail
- [ ] Resolve `ModuleNotFoundError` in `module.py`

### Medium Priority

- [ ] Address type errors in `types.py`
- [ ] Update deprecated API usage

### Low Priority

- [ ] Clean up linting warnings
- [ ] Add missing type hints

---

## Audit History

| Date | Auditor | Changes |
| :--- | :--- | :--- |
| YYYY-MM-DD | Agent | Initial audit |

---

## Notes

[Any additional context, environment-specific issues, known limitations, or workarounds]
