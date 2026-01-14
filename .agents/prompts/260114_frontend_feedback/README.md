# Agent Prompt Batch: 2026-01-14 (Frontend Feedback)

**Created:** 2026-01-14
**Focus Area:** Frontend UX Feedback & Backlog Consolidation
**Status:** 🟢 Initialization Complete - Ready for Dispatch

---

## Overview

This batch addresses frontend feedback from user testing after the SQLModel refactor. Organized into 8 thematic groups, each with an initialization prompt that details items and generates implementation prompts.

---

## Group Initialization Prompts

| Group | Init File | Items | Type | Priority |
|-------|-----------|-------|------|----------|
| **A** | [GROUP_A_view_controls_init.md](GROUP_A_view_controls_init.md) | 6 | 🔵 Planning + 🟢 Implementation | P1-P2 |
| **B** | [GROUP_B_ui_consistency_init.md](GROUP_B_ui_consistency_init.md) | 10 | 🟢 Implementation (Quick Wins) | P2-P3 |
| **C** | [GROUP_C_simulation_init.md](GROUP_C_simulation_init.md) | 1 | 🔵 Planning → Implementation | P2 |
| **D** | [GROUP_D_state_inspection_init.md](GROUP_D_state_inspection_init.md) | 2 | 🟢 Implementation | P2 |
| **E** | [GROUP_E_playground_init.md](GROUP_E_playground_init.md) | 6 | 🔴 Bug + 🔵 Planning + 🟢 Impl | P1-P3 |
| **F** | [GROUP_F_workcell_init.md](GROUP_F_workcell_init.md) | 2 | 🔵 Planning → Implementation | P2 |
| **G** | [GROUP_G_documentation_init.md](GROUP_G_documentation_init.md) | 4 | 🔴 Investigation + 🟢 Implementation | P1-P2 |
| **H** | [GROUP_H_dataviz_init.md](GROUP_H_dataviz_init.md) | 1 | 🟢 Implementation | P2 |

## Chunking Strategy

Given the scope of issues spanning multiple domains, this batch is organized into **thematic prompt groups**:

| Group | Theme | Scope | Prompts |
|-------|-------|-------|---------|
| **A** | View Controls Standardization | Shared component, all tabs | 1-2 prompts |
| **B** | UI/UX Consistency | Chips, filters, scrolling, spacing | 2-3 prompts |
| **C** | Simulation Architecture | Frontend/backend separation, naming | 1-2 prompts |
| **D** | State Inspection & Monitor | Dispense tracking, parameter display | 1-2 prompts |
| **E** | Playground Improvements | Categories, theming, well selector | 2-3 prompts |
| **F** | Workcell & Deck | Deck states, menu UX | 1-2 prompts |
| **G** | Documentation & Rendering | Mermaid, 404, system diagrams | 1-2 prompts |
| **H** | Data Visualization | Filter bar, groupby controls | 1 prompt |

### Why This Chunking?

1. **Thematic coherence**: Each group can be tackled independently
2. **Dependency ordering**: Group A (shared components) unblocks B-H
3. **Parallel execution**: Multiple agents can work on different groups
4. **Scope control**: Each prompt is 1-3 files max

---

## Issue Consolidation Table

> **Source Key:**
>
> - `FF` = Frontend Feedback (user notes from 2026-01-13)
> - `260109` = Existing prompts in `.agents/prompts/260109/`
> - `BL` = Backlog items in `.agents/backlog/`
> - `DM` = DEVELOPMENT_MATRIX.md entry

| ID | Issue | Source | Group | Priority | Complexity | Status |
|----|-------|--------|-------|----------|------------|--------|
| 1 | No protocols showing up | FF | G | P1 | Medium | 🔴 Needs Investigation |
| 2 | Simulated backend separation (only simulated frontends, user selects backend like chatterbox) | FF | C | P2 | Hard | 🟢 New |
| 3 | Add asset display: plates/tips on new lines | FF | B | P3 | Easy | 🟢 New |
| 4 | Add resource: category as dropdown vs chips | FF | B | P3 | Easy | 🟢 New |
| 5 | Chips z-axis alignment in filters | FF | B | P3 | Easy | 🟢 New |
| 6 | Multiselect fixed height + scrollable chips | FF | B | P2 | Medium | 🟢 New |
| 7 | Back button in add asset dialog | FF | B | P3 | Easy | 🟢 New |
| 8 | Unify add asset/machine dialog routes | FF | A | P2 | Medium | 🟢 New |
| 9 | Quick add autocomplete for assets/machines | FF | A | P2 | Medium | 🟢 Completed |
| 10 | Spatial view filter scrolling issue | FF | B | P2 | Medium | 🟢 New |
| 11 | Overlap in spatial view cards | FF | B | P2 | Easy | 🟢 New |
| 12 | View type toggle (card/list) across tabs | FF | A | P2 | Medium | 🟢 New |
| 13 | Clarify spatial view purpose vs other tabs | FF | A | P3 | Medium | 🟢 Needs Discussion |
| 14 | Distance from top to first text | FF | B | P3 | Easy | 🟢 New |
| 15 | Multiselect y/x axis consistency | FF | B | P2 | Easy | 🟢 New |
| 16 | Backend select: show only final FQN segment | FF | B | P3 | Easy | 🟢 New |
| 17 | Resource display consistency | FF | A | P2 | Medium | 🟢 New |
| 18 | Shared "view controls" component (groupby/filterby) | FF | A | P1 | Medium | 🟢 New |
| 19 | No deck state available (simulated deck states) | FF | F | P2 | Hard | 🟢 New |
| 20 | Workcell column/menu improvements | FF | F | P2 | Hard | 🟢 Needs Planning |
| 21 | Well selector chips smaller | FF | E | P3 | Easy | 🟢 New |
| 22 | Well selector programmatic selection | FF | E | P4 | Medium | 🔵 Tech Debt |
| 23 | DataViz filter bar UI (rounded, dismissable) | FF | H | P2 | Medium | 🟢 New |
| 24 | 404 on installation-production.md | FF | G | P1 | Easy | 🟢 New |
| 25 | Mermaid/system diagrams not rendering | FF | G | P2 | Medium | Existing (BL:docs) |
| 26 | State inspection incomplete (dispense volume) | FF | D | P2 | Medium | ✅ Completed |
| 27 | Input parameters display in monitor | FF | D | P2 | Medium | ✅ Completed |
| 28 | Playground loading skeleton theming | FF | E | P3 | Easy | 🟢 New |
| 29 | WebSerial NameError | FF | E | P1 | Medium | 🔴 Bug |
| 30 | Playground inventory categories not good | FF | E | P2 | Medium | 🟢 New |
| 31 | Unite inventory adder with protocol selector | FF | E | P2 | Medium | 🟢 New |
| 32 | Stepper styling (themed CSS) | FF | E | P3 | Easy | 🟢 New |
| 33 | Settings headers move to left | FF | B | P3 | Easy | 🟢 New |
| 34 | Tutorial end state reset + audit | FF | G | P2 | Medium | Existing (BL:docs) |

### Existing Items Cross-Reference

| Source | Item | Matches Row(s) | Action |
|--------|------|----------------|--------|
| 260109/P0_02 | Separation of concerns audit | Row 2 (partially) | Merge context |
| 260109/P1_01 | Playground loading removal | N/A | May be resolved |
| 260109/P1_03 | Asset selection filters | Row 5, 6 | Supersede |
| BL:simulation | Simulated backend clarity | Row 2 | Primary backlog |
| BL:playground | Resource filters broken | Row 10, 30 | Supersede |
| BL:workcell | No deck visualizations | Row 19 | Primary backlog |
| BL:docs | System diagrams | Row 25 | Primary backlog |
| BL:docs | Tutorial updates | Row 34 | Primary backlog |
| DM:P1 | Asset Filtering | Row 3-7 | Resolved? |

---

## Prompt Generation Plan

### Phase 1: Reconnaissance (This Batch)

Before generating implementation prompts, each group needs codebase investigation:

1. **Identify actual file paths** for each issue
2. **Discover existing patterns** to follow
3. **Map dependencies** between issues
4. **Validate assumptions** from user feedback

### Phase 2: Prompt Scaffolding

After reconnaissance, generate detailed prompts per `.agents/templates/agent_prompt.md`:

| Prompt | Group | Title | Key Files (TBD) |
|--------|-------|-------|-----------------|
| P1_01 | A | Shared View Controls Component | `praxis/web-client/src/app/shared/` |
| P1_02 | A | Unified Add Asset/Machine Flow | `praxis/web-client/src/app/features/*/dialogs/` |
| P2_01 | B | UI Consistency: Chips & Multiselects | TBD |
| P2_02 | B | Filter Scroll & Card Overlap Fixes | TBD |
| P2_03 | B | Minor Spacing & Display Fixes | TBD |
| P2_04 | C | Simulation Architecture Clarification | `praxis/backend/models/domain/machine*.py` |
| P2_05 | D | State Inspection Improvements | TBD |
| P2_06 | E | Playground Theming & Categories | TBD |
| P2_07 | F | Workcell UX Planning | `.agents/backlog/workcell.md` |
| P2_08 | G | Documentation Fixes | `praxis/web-client/src/assets/docs/` |
| P2_09 | H | DataViz Filter Bar Redesign | TBD |
| P1_03 | E | WebSerial Bug Fix | `praxis/web-client/src/app/features/repl/` |

---

## Questions for Review

1. **Priority validation**: Are P1 items (protocols not showing, 404, WebSerial error) correctly identified as blockers?

2. **Scope**: Should "Spatial View purpose" (Row 13) be a UX discussion before implementation?

3. **Workcell planning**: Row 20 suggests "first plan best UX" - should this be a separate design prompt before implementation?

4. **Resolved items**: Has the SQLModel refactor already resolved any of the 260109 items?

5. **Quick wins**: Should P3 easy items (Rows 3, 4, 7, 14, 16, 21, 28, 32, 33) be batched into a single "UI Polish" prompt?

---

## Next Steps

After review approval:

1. [ ] Conduct reconnaissance per group
2. [ ] Update this table with actual file paths
3. [ ] Generate detailed prompts using template
4. [ ] Update DEVELOPMENT_MATRIX.md
5. [ ] Archive superseded 260109 items

---

## Files in This Batch

| File | Status | Description |
|------|--------|-------------|
| [README.md](README.md) | 📝 Draft | This file |
| [ISSUE_TABLE.md](ISSUE_TABLE.md) | 📝 Draft | Editable issue tracking table |
| **Group A: View Controls Standardization** | | |
| [A-P1_spatial_view_ux_analysis.md](A-P1_spatial_view_ux_analysis.md) | 🟢 Completed | P3 Planning: Spatial View UX Analysis |
| [A-01_shared_view_controls.md](A-01_shared_view_controls.md) | 🟢 Ready | P1 Implementation: Shared View Controls Component |
| [A-02_add_dialog_unification.md](A-02_add_dialog_unification.md) | ✅ Completed | P2 Implementation: Unified Add Asset/Machine Dialog |
| [A-03_quick_add_autocomplete.md](A-03_quick_add_autocomplete.md) | 🟢 Ready | P2 Implementation: Quick Add Autocomplete |
| [A-04_adopt_shared_controls.md](A-04_adopt_shared_controls.md) | 🟢 Ready | P2 Implementation: Adopt Shared Controls Across Tabs |
| **Group B: UI/UX Consistency** | | |
| *(Prompts pending A completion)* | ⏳ Blocked | B-01 and B-02 will be generated after Group A |
| **Group C: Simulation Architecture** | | |
| [C-P1_simulation_audit_design.md](C-P1_simulation_audit_design.md) | 🟢 Ready | P2 Planning: Simulation Architecture Audit & Design |
| **Group D: State Inspection & Monitor** | | |
| [D-01_monitor_state_and_parameters.md](D-01_monitor_state_and_parameters.md) | ✅ Completed | P2 Implementation: Monitor State & Parameter Display |
| **Group E: Playground Improvements** | | |
| [E-01_webserial_fix.md](E-01_webserial_fix.md) | 🟢 Ready | P1 Bug Fix: WebSerial NameError |
| [E-02_playground_theming.md](E-02_playground_theming.md) | 🟢 Ready | P3 Implementation: Playground Theming Quick Wins |
| [E-P1_inventory_planning.md](E-P1_inventory_planning.md) | 🟢 Ready | P2 Planning: Inventory/Asset Selector UX Design |
| **Group F: Workcell & Deck** | | |
| [F-P1_workcell_ux_planning.md](F-P1_workcell_ux_planning.md) | ✅ Completed | P2 Planning: Workcell UX Audit & Redesign. See [artifacts/](artifacts/) |
| [F-01_simulated_deck_states.md](F-01_simulated_deck_states.md) | 🟢 Ready | P2 Implementation: Simulated Deck States (unblocked by F-P1) |
| **Group G: Documentation & Rendering** | | |
| [G-01_protocols_not_loading.md](G-01_protocols_not_loading.md) | 🟢 Ready | P1 Investigation: Diagnose protocol loading in browser mode |
| [G-02_docs_404_and_mermaid.md](G-02_docs_404_and_mermaid.md) | 🟢 Ready | P1/P2 Implementation: Fix 404 for docs and mermaid rendering |
| [G-P1_tutorial_audit.md](G-P1_tutorial_audit.md) | 🟢 Ready | P2 Planning: Audit tutorial accuracy and reset issue |
| **Group H: Data Visualization** | | |
| [H-01_dataviz_filter_bar.md](H-01_dataviz_filter_bar.md) | 🟢 Ready | P2 Implementation: DataViz Filter Bar Redesign |
| [H-02_realistic_sim_data.md](H-02_realistic_sim_data.md) | 🟢 Ready | P2 Implementation: Realistic Simulated Data |
