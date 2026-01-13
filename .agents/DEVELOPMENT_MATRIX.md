# Praxis Development Matrix

**Last Updated**: 2026-01-13 (Archival Cleanup)
**Purpose**: Current iteration work items with priority and difficulty ratings.

---

## Legend

### Priority

| Priority | Description |
|----------|-------------|
| **P1** | Critical - Blocking alpha release |
| **P2** | High - Required for alpha quality |
| **P3** | Medium - Should have for alpha |
| **P4** | Low - Nice to have / post-alpha |

### Difficulty

| Difficulty | Description |
|------------|-------------|
| **Hard** | Complex architecture, multi-system, likely debugging |
| **Medium** | Well-defined but substantial work |
| **Easy** | Straightforward, minimal ambiguity |

---

## P1 - Critical (Alpha Blockers)

| Item | Difficulty | Backlog | Description |
|------|------------|---------|-------------|
| Registry UI | Medium | [asset_management.md](./backlog/asset_management.md) | "Definitions precinct in browser mode" error; needs redesign |

---

## P2 - High Priority (Alpha Quality)

### UI/UX Issues

| Item | Difficulty | Backlog | Description |
|------|------------|---------|-------------|
| Simulated Backend Clarity | Medium | [simulation.md](./backlog/simulation.md) | Unclear simulated backend behavior; demo naming persists |
| Protocol Library Filters | Medium | [protocol_workflow.md](./backlog/protocol_workflow.md) | No filters implemented |
| Protocol Library Filters | Medium | [protocol_workflow.md](./backlog/protocol_workflow.md) | No filters implemented |

### Visualization Issues

...

### Documentation Issues

| Item | Difficulty | Backlog | Description |
|------|------------|---------|-------------|
| API Docs Broken | Medium | [docs.md](./backlog/docs.md) | API documentation not rendering |
| Architecture View Expansion | Medium | [docs.md](./backlog/docs.md) | Shows text instead of visual diagrams |
| Mode Separation in Docs | Medium | [docs.md](./backlog/docs.md) | Separate browser-lite vs production tabs |
| Tutorial Updates | Medium | [docs.md](./backlog/docs.md) | Bring tutorial up to date |
| Docs Accuracy Audit | Medium | [docs.md](./backlog/docs.md) | Verify all docs are current |

### Playground Issues

| Item | Difficulty | Backlog | Description |
|------|------------|---------|-------------|
| Resource Filter Broken | Medium | [playground.md](./backlog/playground.md) | Filters not working, inconsistent styling |
| Browser Tab Blank | Medium | [playground.md](./backlog/playground.md) | Categories shows blank area |
| WebUSB/Polyfill Audit | Hard | [playground.md](./backlog/playground.md) | Audit polyfill/webusb communication |

### Hardware Validation (Required for Alpha)

| Item | Difficulty | Backlog | Description |
|------|------------|---------|-------------|
| Hardware Discovery | Hard | [hardware.md](./backlog/hardware.md) | WebSerial/WebUSB device enumeration in browser |
| Connection Persistence | Medium | [hardware.md](./backlog/hardware.md) | Connections persist across sessions |
| Plate Reader Validation | Medium | [hardware.md](./backlog/hardware.md) | Validate plate reader (may need debugging) |
| Hamilton Starlet Validation | Hard | [hardware.md](./backlog/hardware.md) | Validate with Hamilton hardware |
| Frontend Protocol Execution | Hard | [hardware.md](./backlog/hardware.md) | Full protocol execution from browser UI |
| Playground Hardware | Hard | [hardware.md](./backlog/hardware.md) | Interactive hardware control from playground |

---

## P3 - Medium Priority (Should Have for Alpha)

### Testing

| Item | Difficulty | Backlog | Description |
|------|------------|---------|-------------|
| Maintenance Tracking Tests | Medium | [testing.md](./backlog/testing.md) | Test maintenance system |

---

## P4 - Low Priority (Post-Alpha / Beta)

| Item | Difficulty | Description |
|------|------------|-------------|
| Production Mode Validation | Hard | Document what's needed for full production validation |
| Workcell UI Redesign | Hard | Rethink and rework workcell interface |
| Frontend/Backend Separation | Hard | Better architectural separation for simulation |

---

---

## Completed Items

| Item | Priority | Date | Description |
|------|----------|------|-------------|
| [Historical Items (Jan 2026)](./archive/COMPLETED_ITEMS_ARCHIVE_JAN_2026.md) | - | 2026-01-12 | Consolidated archive of previous completions |
| Model Unification (SQLModel) | P2 | 2026-01-13 | Massive refactor to unified SQLModel domain models, removed legacy ORM/Pydantic duplication |
| [Frontend Schema Sync](./archive/backlog/frontend_schema_sync.md) | P1 | 2026-01-13 | Aligned frontend with SQLModel backend, fixed API client, removed build warnings |
| Assets View Controls (Machines, Resources, Registry) | P2 | 2026-01-13 | Implemented unified `ViewControlsComponent`, refactored all Assets tabs for standardized filtering, sorting, and grouping |
| Asset Filtering / Registry UI Redesign | P1/P2 | 2026-01-13 | Standardized filtering and resolved browser-mode registry errors |

---

## Summary

| Priority | Count | Focus |
|----------|-------|-------|
| **P1** | 0 | Alpha blockers |
| **P2** | 19 | Alpha quality (including hardware) |
| **P3** | 1 | Should have for alpha |
| **P4** | 3 | Post-alpha / beta |

**Total Active Items**: 23

---

## Related Documents

- [ROADMAP.md](./ROADMAP.md) - Strategic milestones
- [backlog/](./backlog/) - Detailed issue tracking
