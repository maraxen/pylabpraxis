# Comprehensive Issues & Enhancements List (Revised 2026-01-19)

## 1. Deployment & Infrastructure
- [ ] **GitHub Pages Deployment**: Switch GitHub Pages deployment to deploy the **browser application** (Praxis Web Client) instead of the documentation.
  - *Action*: Update `.github/workflows` to build the Angular app and deploy the `dist/` folder.

## 2. Protocol Execution Engine (Python/Pyodide)
- [ ] **Pyodide Environment Strategy**:
  - **Constraint**: The `praxis` module cannot be imported in Pyodide (it's not pure Python).
  - **Requirement**: Use only `pylabrobot` and Python primitives as arguments.
  - **Investigation**: Research using `cloudpickle` to stage the base function with a matching Pyodide environment.
  - **Investigation**: Research the best method to set up and execute the code under these constraints.
- [ ] **Execution Bugs**:
  - Fix `SyntaxError: multiple statements found while compiling a single statement` (likely `exec` vs `eval` usage).
  - Fix `ModuleNotFoundError: No module named 'praxis'`.

## 3. Protocol Logic & Arguments
- [ ] **Argument Inference & Configuration**:
  - **Transfer Pattern**: Remove as a user-configurable argument. It should be inferred via tracer analysis or decorator metadata.
  - **Well Indices**: Consolidate "source" and "destination" well index arguments into a single "well index set" argument that controls both.
  - **Investigation**: Determine the current status of tracer analysis/inference for well index arguments.
  - **Investigation**: Identify which protocols will be impacted by these changes and if logic triggering well selection needs updates.
- [ ] **UI Hints (Formly)**:
  - Implement standard UI hints/widgets (e.g., sliders for values/replicates) based on argument type or metadata.
  - *Action*: Research standards for this in the current form library.

## 4. Hardware Architecture & Simulation
- [ ] **PLR Hierarchy & Instantiation**:
  - **Core Issue**: Address the architectural handling of PLR hierarchy, required arguments, and compatibility constraints.
  - **Instantiation**: Fix `TypeError: LiquidHandler.__init__() missing 2 required positional arguments: 'backend' and 'deck'`.
  - **Defaults**: Implement broad defaults for names and required fields where user input isn't strictly necessary.
- [ ] **Simulation & Decks**:
  - **Deck Locking**: If a LiquidHandler backend has only one compatible deck definition, auto-select/lock it.
  - **Consistency**: Ensure the Deck Definition selected during setup is the *same one* used for:
    1.  The `deck` argument in final execution.
    2.  The Deck View rendering in the UI.
  - **Investigation**: Clarify "Simulated" vs "Chatterbox" distinction and if it matters.
  - **Investigation**: Verify if "LiquidHandler Backend -> Compatible Deck Definitions" mapping is fully supported in the codebase.
- [ ] **Hardware Selection UX**:
  - Clarify "LiquidHandler" vs "Simulated LiquidHandler" (simulation backends).
  - Fix "Opentrons simulated" appearing in "Detected Hardware" dialog.

## 5. Asset Management (UI/UX)
- [ ] **Asset Dialog Refactor**:
  - **Structure**: Refactor "+ Asset" dialog into 4 distinct steps:
    1.  **Type** (Machine vs Resource)
    2.  **Category** (e.g., Liquid Handler, Plate Reader)
    3.  **Definition** (Specific Model)
    4.  **Config** (Parameters)
  - **Reuse**: This subcomponent MUST be reused for the Playground Inventory selection (with a different emission path).
- [ ] **Frontend/Backend Separation**:
  - **Strict Separation**: UI must respect Frontend (Asset) vs Backend (Hardware) definitions.
  - **Filtering**: Playground Inventory must not mix frontends and backends.
  - **Categories**: Backend definitions should not appear as independent categories.
  - **Bugs**: Fix "Unknown" category warnings and weird naming (e.g., "Starlet 74").
- [ ] **UX Polish**:
  - **Layout**: Machine and Resource buttons should appear on the same horizontal axis.
  - **Feedback**: Add Success/Failure popups for asset addition.
  - **Bugs**: Fix reselection issues and add "Retrigger Auto-select" button.

## 6. Run Protocol Session (Guided Setup)
- [ ] **Deck Visualization & Interaction**:
  - **State Updates**: Items should mark as "placed" immediately upon trigger.
  - **Visuals**: Use chips/cards to clearly show "Unplaced" vs "Placed" status.
  - **Modification**: Allow users to change item placement during setup (while respecting no-overlap constraints).
- [ ] **Consistency**: Verify that the deck view renders based on the *selected* deck definition from the simulation setup.

## 7. Data Visualization & Views
- [ ] **Grouping & Filtering**:
  - Fix `groupby` functionality (currently broken).
  - Fix Spatial View category filter.
  - Fix index-based paging.
- [ ] **View Modes**:
  - Remove "Demo Workcell" persistence.
  - Enable viewing Deck Definitions independent of machine instances.

## 8. Documentation & Debt
- [ ] **Docs**: Fix 404s (`frontend-production.md`, etc.) and audit links.
- [ ] **Tech Debt**: Add dynamic filters (e.g., plate bottom type).
