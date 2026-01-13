# Coverage Verification

**Purpose:** Verify all 32 user feedback items are covered in group initialization prompts.

---

## Original User Feedback → Group Mapping

| # | User Feedback (Direct Quote) | Group | Init File | Status |
|---|------------------------------|-------|-----------|--------|
| 1 | "No protocols showing up" | G | G-01 Investigation | ✅ |
| 2 | "machines (not great frontend vs backend separation...users can select chatterbox or another simulated backend of their choosing when instantiating simulated machines" | C | C-P1 Planning | ✅ |
| 3 | "add new asset display should be better presented, plates, tips, on new lines" | B | B-01 Quick Wins | ✅ |
| 4 | "add resource screen have the category also be a dropdown instead of chips" | B | B-01 Quick Wins | ✅ |
| 5 | "make sure chips z axis is aligned" | B | B-01 Quick Wins | ✅ |
| 6 | "for multiselect, make sure y axis is a FIXED size...chips display below is scrollable" | B | B-02 Filter Fixes | ✅ |
| 7 | "add back button in add asset dialog" | B | B-01 Quick Wins | ✅ |
| 8 | "unify add asset add machine dialog routes" | A | A-02 Dialog Unification | ✅ |
| 9 | "quick add autocomplete for both" | A | A-03 Autocomplete | ✅ |
| 10 | "when filters are open in spatial view...i cannot scroll within that" | B | B-02 Filter Fixes | ✅ |
| 11 | "overlap in spatial view cards" | B | B-02 Filter Fixes | ✅ |
| 12 | "toggle for view type in spatial machines resources and registry" | A | A-01 Shared Controls | ✅ |
| 13 | "unclear what the role of spatial view is" | A | A-P1 Planning | ✅ |
| 14 | "distance from top of application to first text should be eliminated" | B | B-01 Quick Wins | ✅ |
| 15 | "discovery seems to be working" | - | N/A (Working) | ✅ |
| 16 | "some inconsistency on how the y and x axis are fixed for multiselects" | B | B-02 Filter Fixes | ✅ |
| 17 | "backend select in machines tab, only for the final segment of the fqn" | B | B-01 Quick Wins | ✅ |
| 18 | "resource display should be consistent" | A | A-04 Adopt Controls | ✅ |
| 19 | "consistent set of 'view' controls...shared component...groupby and filterby" | A | A-01 Shared Controls | ✅ |
| 20 | "no deck state available. we should have simulated deck states" | F | F-01+ Implementation | ✅ |
| 21 | "workcell menu needs a lot of improvement...first planning out what the best UX would be" | F | F-P1 Planning | ✅ |
| 22 | "well selector...chips in the selected a bit smaller" | E | E-02 Quick Wins | ✅ |
| 23 | "programmatic selection (put in technical debt)" | E | Tech Debt Item | ✅ |
| 24 | "filter bar in data viz...rounded corner and hover above and dismissable" | H | H-01 Filter Bar | ✅ |
| 25 | "404 on installation-production.md" | G | G-02 Doc Fixes | ✅ |
| 26 | "system diagrams and mermaid not rendering" | G | G-02 Doc Fixes | ✅ |
| 27 | "state inspection does not appear to be detecting everything (dispense volume)" | D | D-01 State Display | ✅ |
| 28 | "input parameters in monitor does not have a nice display" | D | D-01 State Display | ✅ |
| 29 | "playground loading skeleton...on theme" | E | E-02 Quick Wins | ✅ |
| 30 | "WebSerial NameError" | E | E-01 Bug Fix | ✅ |
| 31 | "categories in the playground inventory adder are not good" | E | E-P1 Planning | ✅ |
| 32 | "stepper looks off...themed css" | E | E-02 Quick Wins | ✅ |
| 33 | "Settings headers can be moved to the left" | B | B-01 Quick Wins | ✅ |
| 34 | "end of tutorial resetting, also auditing tutorial" | G | G-P1 Tutorial Audit | ✅ |

---

## Summary

- **Total user feedback items:** 34 (1 was "working" - discovery)
- **Items covered:** 33/33 actionable items ✅
- **Planning tasks (spawn more prompts):** 5
  - A-P1: Spatial View UX Analysis
  - C-P1: Simulation Architecture Audit
  - E-P1: Inventory/Asset Selector UX
  - F-P1: Workcell UX Redesign
  - G-P1: Tutorial Audit
- **Tech debt items:** 1 (Programmatic well selection)
