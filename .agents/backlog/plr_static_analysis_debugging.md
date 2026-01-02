# PLR Static Analysis Debugging Backlog

**Priority**: HIGH
**Owner**: Backend
**Created**: 2026-01-01
**Status**: ✅ COMPLETE

---

## Problem Summary (RESOLVED)

| Type | Before | After |
|------|--------|-------|
| Resources | 15 | **181** |
| Machine frontends | 0 | **21** |
| Backends | 0 | **52** |
| Decks | 2 | 2 |

---

## Phase 1: Immediate Bug Fixes ✅

- [x] Fix `PLRClassType.ARM` → `PLRClassType.SCARA`
- [x] Add missing machine types (PUMP_ARRAY, PEELER, etc.)
- [x] Fix hex literal parsing (`int(node.value, 0)`)
- [x] Fix schema column mismatch

## Phase 2: Resource Factory Discovery ✅

- [x] Created `ResourceFactoryVisitor`
- [x] Integrated into `PLRSourceParser.discover_resource_factories()`
- [x] Combined with class-based discovery in generate_browser_db.py

---

## Phase 2: Resource Discovery Investigation

### 2.1 Understand PLR Resource Patterns

PLR defines resources in multiple ways:

1. **Class-based** (rare): `class MyPlate(Plate): ...`
2. **Factory functions** (common): `def Cor_96_wellplate() -> Plate: ...`
3. **Module-level instances** (common): `some_plate = Plate(...)`

Current static analysis only finds class-based definitions.

### 2.2 Strategy Decision Required

| Option | Description | Effort | Coverage |
|--------|-------------|--------|----------|
| A | Accept class-only (~30 resources) | None | Low |
| B | Add factory function detection | M | Medium |
| C | Hybrid runtime inspection | L | High |
| D | Prebuilt resource catalog JSON | S | Full |

> **Recommendation**: Option D - extract all resources once via runtime, save as JSON, embed in browser DB.

---

## Related Files

- `scripts/generate_browser_db.py`
- `praxis/backend/utils/plr_static_analysis/parser.py`
- `praxis/backend/utils/plr_static_analysis/visitors/class_discovery.py`
- `praxis/backend/utils/plr_static_analysis/models.py`

---

## Success Criteria

1. [ ] Machine definitions: 20+ inserted
2. [ ] Deck definitions: 4+ inserted
3. [ ] Resource strategy decided and documented
4. [ ] No runtime errors in `generate_browser_db.py`
