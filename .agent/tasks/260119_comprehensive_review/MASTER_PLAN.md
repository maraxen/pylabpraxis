# Comprehensive Master Plan (v4 - Verified & Skilled)

## 0. Development Philosophy & Verification Workflow

### 0.1 Core Principles
*   **Skill-Based Execution**: Every task MUST identify and utilize the relevant agent skill (e.g., `playwright-skill`, `senior-fullstack`).
*   **Workflow Standard**: Follow the **Inspect $\rightarrow$ Plan $\rightarrow$ Execute $\rightarrow$ Test** cycle for every major task.
*   **Documentation**: Update `.agent/research` and `docs/` as features are implemented.

### 0.2 Frontend Verification Workflow (MANDATORY)
*   **Tools**: `playwright-skill` (via `omo_skill_mcp`), `multimodal-looker` (via `Task`).
*   **Process**:
    1.  **Write Test First**: Create a Playwright test spec (e2e or component) for the feature.
    2.  **Visual Verification**:
        *   Run Playwright test with a reporter or explicit screenshot capture.
        *   Use `multimodal-looker` to analyze screenshots and verify UI state (rendering correctness, widget appearance).
        *   **CRITICAL**: Use a short delay in tests to account for rendering time before capture.
    3.  **Functional Verification**: Ensure the test passes functionally (assertions green).
    4.  **Loop**: Fix $\rightarrow$ Verify $\rightarrow$ Repeat until both visual and functional requirements are met.

---

## 1. Architecture: Execution Engine & Machine Logic
*Relevant Skills: `senior-architect`, `backend-dev-guidelines`, `systematic-debugging`*

*   [x] **Pyodide Execution Strategy**:
    *   *Skills*: `senior-architect`, `python-dev`
    *   **Research**: Validate `runPythonAsync` behavior with complex closures.
    *   **Implementation**: Switch to `runPython()`/`runPythonAsync()`.
    *   **Serialization**: Implement `cloudpickle` strategy: Serialize backend protocol functions (stripping Praxis dependencies) -> Deserialize in Pyodide.
    *   **Constraint**: Browser execution environment must depend *only* on `pylabrobot` and Python primitives.
*   [x] **Refactor Machine & LiquidHandler Instantiation**:
    *   *Skills*: `backend-dev-guidelines`, `pylabrobot-planning`
    *   **Principle**: *All* machine frontends require backends.
    *   **Arg Injection**: Update code generation to **always** inject `backend` and `deck` arguments.
    *   **Auto-Configuration**:
        *   **Deck**: If `allowed_decks` metadata shows only one compatible definition, auto-select it.
        *   **Connection**: Auto-configure connection args where possible.
        *   **User Args**: Expose configurable backend args (e.g., ports) in the UI.

## 2. Protocol Logic & Generalized Inference
*Relevant Skills: `senior-architect`, `backend-dev-guidelines`*

*   [x] **Consolidate Protocol Arguments**:
    *   *Skills*: `backend-dev-guidelines`
    *   **Remove** "Transfer Pattern" user argument.
    *   **Consolidate**: Replace `source_wells`/`dest_wells` with a single **`ItemizedResourceSelection`** argument.
*   [ ] **Enhance Tracer Inference (Generalized)**:
    *   *Skills*: `python-dev`, `test-driven-development`
    *   **Rename**: Change inferred type from `WellSelection` to **`ItemizedResourceSelection`**.
    *   **Logic**: Update `tracers.py` (specifically `TracedContainerElementCollection`) to detect when an argument indexes *any* container.
    *   **Type Inference**: Inspect the `ItemizedResource[T]` type variable (e.g., `Well`, `TipSpot`, `Tube`) to generate UI labels.
    *   **Multi-Use**: If an arg indexes multiple types, log all types. UI should show "Index Selection" and list usage context.
*   [ ] **Dictionary Arguments (Formly)**:
    *   *Skills*: `frontend-design`
    *   **Implementation**: Create a `dict-input` Formly type.
    *   **UI**: Use a "Key-Value" repeater for simple dicts, or a validated JSON text area for complex nested objects.

## 3. Asset Management (Unified Dialogs)
*Relevant Skills: `frontend-design`, `ui-ux-pro-max`, `playwright-skill`*

*   [x] **Unified `AssetWizardComponent`**:
    *   *Skills*: `frontend-design`, `ui-ux-pro-max`
    *   **Structure**: 4 Steps:
        1.  **Type** (Machine vs Resource) - *Skippable*.
        2.  **Category** (Liquid Handler, Plate Reader).
        3.  **Definition** (Specific Model).
        4.  **Config** (Parameters, Ports, Backend selection).
    *   **Refactor Targets**: Replace `add-asset-dialog`, `inventory-dialog`, and specific "Add" actions.
*   [x] **Strict Frontend/Backend UX**:
    *   *Skills*: `frontend-design`
    *   **Inventory View**: Show only **Frontend** assets (User-facing names).
    *   **Metadata**: Display technical details (Backend Name, "Simulated") as informational chips.
    *   **Filtering**: Hide raw Backends from the inventory list.
    *   **Cleanup**: Fix "Unknown" categories and debug naming ("Starlet 74").

## 4. Run Protocol Session (Deck & State)
*Relevant Skills: `frontend-design`, `playwright-skill`, `state-management`*

*   [x] **Deck Setup Logic**:
    *   *Skills*: `frontend-design`, `webapp-testing`
    *   **Validation**: Update `DeckStateService` to validate placement.
    *   **Serialization Readiness**: Ensure state can be serialized to a PLR `Deck` object immediately.
    *   **Non-Deck Machines**: Implement readiness checks for non-deck machines.
*   [x] **Interaction**:
    *   *Skills*: `ui-ux-pro-max`
    *   **Placement**: Allow drag-and-drop or re-selection with overlap validation.
    *   **Visuals**: Use Cards/Chips (Red "Unplaced" -> Green "Placed").
    *   **Consistency**: `DeckView` must render the *exact* `DeckDefinition` used for simulation.

## 5. Deployment & Polish
*Relevant Skills: `ci-integration`, `git-pushing`, `frontend-design`*

*   [x] **GitHub Pages**:
    *   *Skills*: `ci-integration`, `git-pushing`
    *   Rewrite `.github/workflows/docs.yml` to build and deploy the Angular app (`dist/praxis-web-client`).
*   [ ] **UI Polish (Formly)**:
    *   *Skills*: `frontend-design`, `ui-ux-pro-max`
    *   **New Widgets**: Implement **Slider**, **Stepper**, and **DictInput**.
    *   **Metadata**: Map `ui_hint` to these widgets.
    *   **Generalized Selector**: Update `WellSelector` to **`ItemizedResourceSelector`**, rendering a grid based on `num_items_x/y` and labeling items based on inferred type.
*   [x] **Fake Data**:
    *   *Skills*: `code-maintenance`
    *   Remove hardcoded mocks.

## 6. Interactive Protocols
*Relevant Skills: `python-dev`, `frontend-design`, `web-workers`*

*   [x] **Implementation**:
    *   Backend: `web_bridge` interactions.
    *   Worker: Bi-directional messaging.
    *   Frontend: `InteractionDialogComponent` & Service.
*   [ ] **Verification**:
    *   Fix E2E test failures (Dialog not appearing).

---

### **Prioritized Execution Order**

1.  **Phase 1: Architecture & Execution** (Unblock Protocol Runs) [Complete]
    *   Fix Pyodide/Cloudpickle.
    *   Fix LiquidHandler/Backend instantiation.
2.  **Phase 2: Asset Management** (Fix Configuration UX) [Complete]
    *   Build `AssetWizardComponent`.
    *   Refactor Inventory & Add Dialogs.
3.  **Phase 3: Run Session & Deck** (Fix Setup UX) [Complete]
    *   Implement Deck Serialization & Readiness.
    *   Improve Setup Visuals.
4.  **Phase 4: Deployment** (Visibility) [Complete]
    *   Switch GitHub Pages to App.
5.  **Phase 6: Interactive Protocols** [In Progress]
    *   Implement & Verify.
