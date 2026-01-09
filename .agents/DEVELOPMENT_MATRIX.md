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
| Protocol Well Selection | Medium | [protocol_workflow.md](./backlog/protocol_workflow.md) | Well selection not triggering in protocol run |
| Playground Initialization | Medium | [playground.md](./backlog/playground.md) | Must click reload kernel + dismiss loading; WebSerial error |
| Asset Filtering | Medium | [asset_management.md](./backlog/asset_management.md) | Autofill not filtered to appropriate PLR class |

---

## P2 - High Priority (Alpha Quality)

### UI/UX Issues

| Item | Difficulty | Backlog | Description |
|------|------------|---------|-------------|
| Simulated Backend Clarity | Medium | [simulation.md](./backlog/simulation.md) | Unclear simulated backend behavior; demo naming persists |
| Backend Selector UX | Easy | [asset_management.md](./backlog/asset_management.md) | Disable unless category selected, or use autocomplete |
| ✅ Backend Name Truncation | Easy | [asset_management.md](./backlog/asset_management.md) | Names too long to be useful |
| Machine Filter Backends | Easy | [asset_management.md](./backlog/asset_management.md) | Category filters incorrectly include backends |
| ✅ Duplicate Clear Button | Easy | [ui_polish.md](./backlog/ui_polish.md) | Remove duplicate in filter dialog |
| Add Asset Prompt | Easy | [asset_management.md](./backlog/asset_management.md) | Overview should prompt machine vs resource |
| Registry UI | Medium | [asset_management.md](./backlog/asset_management.md) | "Definitions precinct in browser mode" error; needs redesign |
| Protocol Library Filters | Medium | [protocol_workflow.md](./backlog/protocol_workflow.md) | No filters implemented |
| ✅ Protocol Dialog Assets | Easy | [protocol_workflow.md](./backlog/protocol_workflow.md) | Machines should be in asset requirements, not parameters |

### Visualization Issues

...

### Documentation Issues

| Item | Difficulty | Backlog | Description |
|------|------------|---------|-------------|
| API Docs Broken | Medium | [docs.md](./backlog/docs.md) | API documentation not rendering |
| Keyboard Shortcut Column | Easy | [docs.md](./backlog/docs.md) | Formatting broken |
| Architecture View Expansion | Medium | [docs.md](./backlog/docs.md) | Shows text instead of visual diagrams |
| Dead Links | Easy | [docs.md](./backlog/docs.md) | Fix broken documentation links |
| Mode Separation in Docs | Medium | [docs.md](./backlog/docs.md) | Separate browser-lite vs production tabs |
| State Management Diagram | Easy | [docs.md](./backlog/docs.md) | Improperly formatted for theming |
| ✅ Execution Flow Diagram | Easy | [docs.md](./backlog/docs.md) | Formatting issues |
| Tutorial Updates | Medium | [docs.md](./backlog/docs.md) | Bring tutorial up to date |
| Docs Accuracy Audit | Medium | [docs.md](./backlog/docs.md) | Verify all docs are current |

### Playground Issues

| Item | Difficulty | Backlog | Description |
|------|------------|---------|-------------|
| ✅ Inventory Filter Styling | Easy | [playground.md](./backlog/playground.md) | Use styled select components |
| ✅ Category Structure | Easy | [playground.md](./backlog/playground.md) | Proper structure in quick add filter |
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
| ✅ Infinite Consumables Tests | Easy | [testing.md](./backlog/testing.md) | Test consumable system |
| Import/Export Tests | Easy | [testing.md](./backlog/testing.md) | Test backup/restore |

---

## P4 - Low Priority (Post-Alpha / Beta)

| Item | Difficulty | Description |
|------|------------|-------------|
| Production Mode Validation | Hard | Document what's needed for full production validation |
| Workcell UI Redesign | Hard | Rethink and rework workcell interface |
| Frontend/Backend Separation | Hard | Better architectural separation for simulation |

---

## Summary

| Priority | Count | Focus |
|----------|-------|-------|
| **P1** | 3 | Alpha blockers |
| **P2** | 29 | Alpha quality (including hardware) |
| **P3** | 3 | Should have for alpha |
| **P4** | 3 | Post-alpha / beta |

**Total Active Items**: 38

---

## Related Documents

- [ROADMAP.md](./ROADMAP.md) - Strategic milestones
- [backlog/](./backlog/) - Detailed issue tracking
