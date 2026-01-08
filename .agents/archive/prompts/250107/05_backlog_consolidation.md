# Backlog Consolidation & Archive

**Backlog**: `cleanup_finalization.md`
**Priority**: P3
**Effort**: Small

---

## Goal

Consolidate overlapping backlogs and archive completed ones to reduce documentation sprawl.

## Backlogs to Archive (Marked Complete)

| File | Reason |
|------|--------|
| `simulation_ui_integration.md` | Status: Complete |
| `capability_tracking.md` | Phases 1-4 Complete, 5-6 are future/deferred |

## Backlogs to Consolidate

| Merge From | Merge Into | Reason |
|------------|------------|--------|
| `docs.md` | `cleanup_finalization.md` | Both are pre-merge cleanup |
| `ui_polish.md` | `chip_filter_standardization.md` | Overlapping UI work |

## Technical Debt Items to Close

The following items in `TECHNICAL_DEBT.md` are resolved:

- ~~Machine Frontend/Backend Separation~~ ✅
- ~~Asset Management - Machine Filter Dropdown Appearance~~ ✅
- ~~JupyterLite REPL - PyLabRobot Module Path Resolution~~ ✅
- ~~FTDI Driver Architecture Refactor~~ ✅
- ~~Protocol Queue and Reservation Management~~ ✅

## Remaining High-Priority Technical Debt

1. **Browser Mode Schema - UNIQUE Constraint on Asset Name** (Medium)
2. **Machine Definition Schema Linkage** (High)
3. **Plate Reader Only Protocols** (High)
4. **Dynamic Hardware Definitions (VID/PID Sync)** (Medium)

## Tasks

1. Move `simulation_ui_integration.md` to `archive/`
2. Move `capability_tracking.md` to `archive/`
3. Merge `docs.md` into `cleanup_finalization.md`
4. Merge `ui_polish.md` into `chip_filter_standardization.md`
5. Update `DEVELOPMENT_MATRIX.md` references
6. Update `ROADMAP.md` references

## Success Criteria

- [ ] 2 backlogs archived
- [ ] 2 backlogs consolidated into existing files
- [ ] All cross-references updated
- [ ] No broken links in documentation
