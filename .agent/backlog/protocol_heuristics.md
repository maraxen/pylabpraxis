# Backlog: Protocol & Logic Heuristics

**Status:** 🟢 Planned
**Difficulty:** 🟡 Intricate
**Area:** Backend
**Created:** 2026-01-15

---

## Goal

Replace brittle string-matching and hardcoded values in protocol execution with proper database-driven lookups and explicit metadata.

---

## Items

### 701 - Selective Transfer Heuristic Replacement

**Priority:** Low

Replace string matching on protocol name/FQN for "Selective Transfer" detection with formal backend metadata.

- Add `requires_linked_indices: bool` to `ProtocolDefinition` model
- Remove string-based detection logic

**Reference:** `protocol_execution_ux_plan.md`

### 702 - Geometry Heuristics in web_bridge.py

**Priority:** Medium

Replace hardcoded 96-well plate assumption with database-driven lookups.

- Read dimensions from `resolved_assets_spec`
- Remove hardcoded geometry in `web_bridge.py` lines 70-100

### 703 - Hardcoded Simulation Values (web_bridge.py)

**Priority:** Low

Audit and replace hardcoded defaults/mocks in browser execution bridge.

- Use configured definitions instead of hardcoded values

### 704 - Hardcoded Simulation Values (Codebase-wide)

**Priority:** Low

Broader audit for hardcoded simulation values throughout the codebase.

---

## Notes

- Items 702-704 are related and could be combined into a single "Simulation Hardcoding Audit" task
- 701 requires schema change and is lower priority
- These issues don't block current functionality but reduce flexibility

---

## References

- Technical Debt IDs: 701, 702, 703, 704
- `praxis/backend/core/web_bridge.py` - Primary file for 702, 703
- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md)
