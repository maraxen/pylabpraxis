# Backend Development Status

**Last Updated**: 2025-12-26  
**Pass Rate**: 98.6% (1373/1393 tests)  
**Coverage**: ~42% (target: 80%)

---

## 🎯 Current Priorities

### High Priority - Production Critical

| Module | Coverage | Target | Notes |
|--------|----------|--------|-------|
| `services/scheduler.py` | 0% | 80% | Scheduler service layer |
| `services/user.py` | 0% | 80% | User management |

### Medium Priority

| Module | Coverage | Target |
|--------|----------|--------|
| `services/deck.py` | 26% | 80% |
| `services/protocol_definition.py` | 21% | 80% |
| `services/protocols.py` | 20% | 80% |
| `services/discovery_service.py` | 21% | 80% |
| `services/entity_linking.py` | 18% | 80% |

---

## ✅ Completed Modules

| Module | Coverage | Date |
|--------|----------|------|
| `api/websockets.py` | 87% | Dec 13 |
| `core/decorators/protocol_decorator.py` | 92% | Dec 14 |
| `utils/auth.py` | 100% | Dec 14 |
| `api/auth.py` | 76% | Dec 14 |
| `core/orchestrator/execution.py` | 100% | Dec 15 |
| `core/scheduler.py` | ~85% | Dec 15 |

---

## 📋 Task Tiers

### Tier 1: Simple (Any agent)

- [ ] T1.2 - Update AGENTS.md type checker ref (`pyright` → `ty`)
- [x] T1.5 - Mark slow tests ✅
- [x] T1.6 - WebSocket test coverage ✅

### Tier 2: Medium

- [ ] T2.3 - Service layer tests (workcell, resource, user)  
- [x] T2.5 - Fix test collection ✅

### Tier 3: Complex

- [ ] T3.4 - Complex service coverage (scheduler, protocols, discovery)
- [ ] T3.5 - Resolve ty type errors

---

## 🚫 Do Not Edit

- `praxis/backend/commons/` - Do not modify
- `praxis/backend/models/orm/` - MappedAsDataclass patterns are sensitive

---

## Quick Commands

```bash
# Start test database
make db-test

# Run tests
make test                    # All tests
make test-parallel-fast      # Fast in parallel
make test-cov               # With coverage

# Type checking
uv run ty check praxis/

# Linting
uv run ruff check . --fix
```

---

*See `archive/BACKEND_STATUS_HISTORY_20251215.md` for historical session logs.*
