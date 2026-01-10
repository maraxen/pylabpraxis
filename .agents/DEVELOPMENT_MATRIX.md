# Praxis Development Matrix

**Last Updated**: 2026-01-09 (Fresh Reset)
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
| Asset Filtering | Medium | [asset_management.md](./backlog/asset_management.md) | Autofill not filtered to appropriate PLR class |

---

## P2 - High Priority (Alpha Quality)

### UI/UX Issues

| Item | Difficulty | Backlog | Description |
|------|------------|---------|-------------|
| Simulated Backend Clarity | Medium | [simulation.md](./backlog/simulation.md) | Unclear simulated backend behavior; demo naming persists |
| Registry UI | Medium | [asset_management.md](./backlog/asset_management.md) | "Definitions precinct in browser mode" error; needs redesign |
| Protocol Library Filters | Medium | [protocol_workflow.md](./backlog/protocol_workflow.md) | No filters implemented |

### Visualization Issues

...

### Documentation Issues

| Item | Difficulty | Backlog | Description |
|------|------------|---------|-------------|
| API Docs Broken | Medium | [docs.md](./backlog/docs.md) | API documentation not rendering |
| Architecture View Expansion | Medium | [docs.md](./backlog/docs.md) | Shows text instead of visual diagrams |
| Mode Separation in Docs | Medium | [docs.md](./backlog/docs.md) | Separate browser-lite vs production tabs |
| State Management Diagram | Easy | [docs.md](./backlog/docs.md) | Improperly formatted for theming |
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
| Playground Initialization | P1 | 2026-01-10 | Removed unnecessary loading overlay |
| Protocol Well Selection | P1 | 2026-01-09 | Well selection enabled for protocol parameters |
| Backend Name Truncation | P2 | 2026-01-09 | Names truncated with tooltips in selectors |
| Duplicate Clear Button | P2 | 2026-01-09 | Removed redundant button in filter dialog |
| Protocol Dialog Assets | P2 | 2026-01-09 | Correctly classified machines as asset requirements |
| Execution Flow Diagram | P2 | 2026-01-09 | Fixed formatting in docs |
| Inventory Filter Styling | P2 | 2026-01-09 | Styled selects used in playground |
| Category Structure | P2 | 2026-01-09 | Proper hierarchy in playground quick add |
| Infinite Consumables Tests| P3 | 2026-01-09 | Comprehensive tests for consumables |
| Import/Export Tests | P3 | 2026-01-09 | Tests for backup/restore functionality |
| Backend Selector UX | P2 | 2026-01-09 | Gated selection with stepper logic |
| Add Asset Prompt | P2 | 2026-01-09 | Selection between machine/resource |
| Keyboard Shortcut Column | P2 | 2026-01-09 | Fixed formatting in docs |
| Dead Links | P2 | 2026-01-09 | Resolved broken links in docs |
| Machine Filter Backends | P2 | 2026-01-09 | Category filters now exclude backends |

---

## Summary

| Priority | Count | Focus |
|----------|-------|-------|
| **P1** | 2 | Alpha blockers |
| **P2** | 20 | Alpha quality (including hardware) |
| **P3** | 1 | Should have for alpha |
| **P4** | 3 | Post-alpha / beta |

**Total Active Items**: 26

---

## Related Documents

- [ROADMAP.md](./ROADMAP.md) - Strategic milestones
- [backlog/](./backlog/) - Detailed issue tracking
