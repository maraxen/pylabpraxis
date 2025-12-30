# Backend Development Status

**Phase**: PLR Introspection & Modes
**Last Updated**: 2025-12-30

---

## 🎯 Current Priorities

### 1. PLR Introspection (High)

* **Goal**: Dynamically enumerate `pylabrobot` classes.
* **Tasks**:
  * [ ] Identify `LiquidHandler` vs `Backend` classes.
  * [ ] Extract metadata (Channels, Optional Modules).
  * [ ] Expose via `sync-all` or `discovery` endpoints.

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
