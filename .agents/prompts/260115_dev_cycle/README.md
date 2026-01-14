# Batch 260115: Development Cycle Prompts

**Status:** 🟡 In Progress  
**Created:** 2026-01-15  
**Source:** `audit_notes_260114.md`

---

## Prompt Categories

### Phase 1: Inspection Prompts (I-XX)

Generate detailed findings artifacts before implementation.

| ID | Title | Status | Target Artifact |
|:---|:------|:-------|:----------------|
| I-01 | [ViewControls DOM/CSS Inspection](I-01_viewcontrols_inspection.md) | 🟢 Not Started | `viewcontrols_inspection_findings.md` |
| I-02 | [Playground Regression Inspection](I-02_playground_inspection.md) | ✅ Complete | `playground_inspection_findings.md` |
| I-03 | [ViewControls Adoption Audit](I-03_viewcontrols_adoption.md) | ✅ Complete | Updates existing pages |
| I-04 | [Card Visual Audit](I-04_card_visual_audit.md) | ✅ Complete | `card_audit_findings.md` |
| I-05 | [Documentation Audit](I-05_docs_audit.md) | ✅ Complete | `docs_audit_findings.md` |

### Phase 2: Planning Prompts (P-XX)

In-depth design work based on inspection findings.

| ID | Title | Status | Target Artifact |
|:---|:------|:-------|:----------------|
| P-01 | [Settings UX Planning](P-01_settings_ux_planning.md) | 🟢 Not Started | `settings_ux_design.md` |
| P-02 | [Deck View UX Planning](P-02_deck_view_planning.md) | 🟢 Not Started | `deck_view_ux_design.md` |
| P-03 | [Protocol Execution UX Planning](P-03_protocol_execution_planning.md) | 🟢 Not Started | Updates existing artifact |

### Phase 3: Implementation Prompts (X-XX)

Actionable implementation tasks.

| ID | Title | Status | Dependencies |
|:---|:------|:-------|:-------------|
| A-01 | [Simulation Frontend Consolidation](A-01_simulation_frontend.md) | 🟢 Not Started | None |
| B-01 | [ViewControls Visual Polish](B-01_viewcontrols_polish.md) | 🟢 Not Started | I-01 |
| B-02 | [ViewControls Toggle/Chip Logic](B-02_viewcontrols_logic.md) | 🟢 Not Started | I-01 |
| C-01 | [Remove Breadcrumbs](C-01_remove_breadcrumbs.md) | ✅ Complete | None |
| C-02 | [Protocol Library ViewControls](C-02_protocol_library_viewcontrols.md) | ✅ Complete | I-03 |
| C-03 | [Execution Monitor ViewControls](C-03_execution_monitor_viewcontrols.md) | 🟢 Not Started | I-03 |
| C-04 | [DataViz ViewControls](C-04_dataviz_viewcontrols.md) | 🟢 Not Started | I-03 |
| D-01 | [Playground Kernel Load Fix](D-01_playground_kernel.md) | ✅ Complete | I-02 |
| D-02 | [Playground Theme Sync](D-02_playground_theme.md) | ✅ Complete | I-02 |
| D-03 | [Playground Loading Overlay](D-03_playground_loading.md) | ✅ Complete | I-02 |
| D-04 | [WebSerial/WebUSB Builtins Fix](D-04_webserial_fix.md) | ✅ Complete | I-02 |
| E-01 | [Well Arguments Cleanup](E-01_well_arguments.md) | ✅ Complete | None |
| E-02 | [Well Selector Performance](E-02_well_selector_perf.md) | 🟢 Not Started | None |
| E-03 | [Asset Autocomplete Redesign](E-03_asset_autocomplete.md) | 🟢 Not Started | P-03 |
| E-04 | [Guided Deck Setup Empty Start](E-04_guided_deck_empty.md) | 🟢 Not Started | None |
| F-01 | [Installation Docs Split](F-01_installation_docs.md) | ✅ Complete | I-05 |
| F-02 | [Mermaid Rendering Fix](F-02_mermaid_fix.md) | 🟢 Not Started | I-05 |
| G-01 | [Home Recent Activity Mock Data](G-01_home_recent_activity.md) | 🟢 Not Started | None |
| H-01 | [Card Visual Polish](H-01_card_polish.md) | ✅ Complete | I-04 |

### Phase 4: Workcell Redesign (K-XX)

Implementation of the new Workcell Dashboard and Explorer.

| ID | Title | Status | Dependencies |
|:---|:------|:-------|:-------------|
| K-01 | [Workcell View Models](K-01_workcell_models.md) | ✅ Complete | None |
| K-02 | [Workcell View Service](K-02_workcell_service.md) | ✅ Complete | K-01 |
| K-03 | [Workcell Dashboard Container](K-03_workcell_dashboard.md) | ✅ Complete | K-02 |
| K-04 | [Workcell Explorer](K-04_workcell_explorer.md) | ✅ Complete | K-02 |
| K-05 | [Machine Status Badge](K-05_machine_status_badge.md) | ✅ Complete | None |
| K-06 | [Machine Card Component](K-06_machine_card.md) | ✅ Complete | K-04, K-05 |
| K-07 | [Machine Focus View](K-07_machine_focus_view.md) | ✅ Complete | K-06 |
| K-08 | [Simulated Deck States](K-08_simulated_deck_states.md) | ✅ Complete | K-07 |

---

## Execution Order

1. **Inspection Phase** (I-01 to I-05): Generate findings artifacts
2. **Planning Phase** (P-01 to P-03): Design complex features
3. **Quick Wins** (C-01, E-01, G-01): Low-dependency implementations
4. **Core Implementations** (A-01, B-XX, D-XX, E-XX): Based on inspection findings
5. **Polish** (H-01, F-XX): Final cleanup
