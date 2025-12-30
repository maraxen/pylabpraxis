# Backend Development Status

**Phase**: PLR Introspection & Modes
**Last Updated**: 2025-12-30

---

## 🎯 Current Priorities

### 1. PLR Introspection (High) - COMPLETED

* **Goal**: Dynamically enumerate `pylabrobot` classes.
* **Implementation**: LibCST-based static analysis (`praxis/backend/utils/plr_static_analysis/`)
* **Tasks**:
  * [x] Identify `LiquidHandler` vs `Backend` classes via AST parsing.
  * [x] Extract metadata (Channels, Optional Modules) from method/attribute analysis.
  * [x] MachineTypeDefinitionService updated to use static analysis.
  * [x] Deprecation warnings added to old runtime inspection functions.

### 2. Application Modes

* **Goal**: Support Browser/Lite/Production variants.
* **Tasks**:
  * [ ] **Lite**: SQLite configuration testing.
  * [ ] **Production**: Redis/Postgres set up docs.
  * [ ] **Validation**: Scripts to verify mode constraints.

---

## ✅ Stable Modules

* **Orchestrator**: Execution engine (100% coverage).
* **WebSockets**: Log streaming & status.
* **Auth**: Keycloak integration (Production).

---

## 📋 Coverage Targets

* `services/scheduler.py`: 0% -> 80%
* `services/discovery_service.py`: 21% -> 80% (Critical for PLR work)

---

## Quick Commands

```bash
make db-test
uv run pytest
```
