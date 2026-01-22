# Development Matrix

| ID | Status | Priority | Difficulty | Mode | Description | Created | Updated |
|---|---|---|---|---|---|---|---|
| 260120200035 | IN_PROGRESS | P2 | medium | fixer | Phase 6 E2E Test Fix: Two issues identified:

1. **FIXED** - BroadcastChannel registration: web_bridge now properly registers the channel for USER_INTERACTION messages
2. **NEW ISSUE** - Test keyboard input: The iframe keyboard focus issue causes the first line of typed code to be lost. The import statement `from praxis.interactive import pause, confirm, input` doesn't appear in the cell.

Root causes:

- Channel issue: web_bridge.py checked js._praxis_channel but channel was a Python local variable
- Keyboard issue: page.keyboard sends to main page, not the iframe where the editor lives | 2026-01-20 | 2026-01-21 01:36:10 |
| 260120204145 | DONE | P2 | medium | librarian | Machine Frontend Analysis: Use ast-grep and ripgrep to identify all Machine frontend class files. Document: (1) All classes extending Machine/MachineFrontend abstract base, (2) Method signatures and types, (3) Constraints/limitations in the abstract base, (4) Current UI rendering patterns. Output: Comprehensive inventory markdown in .agent/research/ | 2026-01-20 | 2026-01-21 01:45:26 |
| 260120204151 | TODO | P2 | medium | deep-researcher | Research: Bespoke Machine Frontend UI - Investigate approaches for generating/rendering custom UI for each machine type based on its methods and capabilities. Consider: dynamic form generation, method introspection, capability flags, production vs browser mode differences. | 2026-01-20 | 2026-01-20 |
| 260120204444 | DONE | P3 | medium | deep-researcher | Research: Lite Mode Strategy - Evaluate SQLite support options for standalone/offline operation. Compare: (1) Browser-only with IndexedDB (current), (2) SQLite via sql.js/absurd-sql, (3) Hybrid approach. Consider use cases: education/demos, air-gapped labs, offline-first scenarios. Output: Decision document with pros/cons and recommendation. | 2026-01-20 | 2026-01-21 02:05:16 |
| 260121002630 | TODO | P2 | easy | code | Validate 1-of-each labware seeding in browser mode. Source: DEVELOPMENT_MATRIX.md P2 Feature Enhancements. | 2026-01-21 | 2026-01-21 |
| 260121002631 | TODO | P2 | medium | code | Sync tests with schema changes. Source: DEVELOPMENT_MATRIX.md P2 Technical Debt. | 2026-01-21 | 2026-01-21 |
| 260121002632 | TODO | P2 | medium | code | Validation, Vantage deck, and UX improvements. Source: DEVELOPMENT_MATRIX.md P2 Technical Debt. | 2026-01-21 | 2026-01-21 |
| 260121002633 | TODO | P2 | hard | code | WebSerial/WebUSB device enumeration in browser. Source: DEVELOPMENT_MATRIX.md P2 Hardware Validation. | 2026-01-21 | 2026-01-21 |
| 260121002634 | TODO | P2 | hard | code | Validate with Hamilton hardware. Source: DEVELOPMENT_MATRIX.md P2 Hardware Validation. | 2026-01-21 | 2026-01-21 |
| 260121002635 | TODO | P3 | medium | code | Test maintenance system. Source: DEVELOPMENT_MATRIX.md P3 State & Monitoring. | 2026-01-21 | 2026-01-21 |
| 260121002638 | TODO | P2 | medium | code | PostgreSQL verification, SQLModel warnings. Source: DEVELOPMENT_MATRIX.md P2 Technical Debt. | 2026-01-21 | 2026-01-21 |
| 260121002639 | TODO | P2 | medium | code | Validation, Vantage deck, and UX improvements. Source: DEVELOPMENT_MATRIX.md P2 Technical Debt. | 2026-01-21 | 2026-01-21 |
| 260121002640 | TODO | P2 | medium | code | Connections persist across sessions. Source: DEVELOPMENT_MATRIX.md P2 Hardware Validation. | 2026-01-21 | 2026-01-21 |
| 260121002641 | TODO | P2 | hard | code | Interactive hardware control from playground. Source: DEVELOPMENT_MATRIX.md P2 Hardware Validation. | 2026-01-21 | 2026-01-21 |
| 260121002644 | TODO | P2 | medium | code | Audit and replace 'as any' usage. Source: DEVELOPMENT_MATRIX.md P2 Technical Debt. | 2026-01-21 | 2026-01-21 |
| 260121002646 | TODO | P2 | easy | code | Add is_reusable to ResourceDefinition. Source: DEVELOPMENT_MATRIX.md P2 Technical Debt. | 2026-01-21 | 2026-01-21 |
| 260121002648 | TODO | P2 | medium | code | Validation, Vantage deck, and UX improvements. Source: DEVELOPMENT_MATRIX.md P2 Technical Debt. | 2026-01-21 | 2026-01-21 |
| 260121002650 | TODO | P2 | medium | code | Connections persist across sessions. Source: DEVELOPMENT_MATRIX.md P2 Hardware Validation. | 2026-01-21 | 2026-01-21 |
| 260121002654 | TODO | P2 | hard | code | Validate with Hamilton hardware. Source: DEVELOPMENT_MATRIX.md P2 Hardware Validation. | 2026-01-21 | 2026-01-21 |
| 260121002656 | TODO | P2 | hard | code | Interactive hardware control from playground. Source: DEVELOPMENT_MATRIX.md P2 Hardware Validation. | 2026-01-21 | 2026-01-21 |
| 260121002658 | TODO | P3 | medium | code | Implement multi-stage (Inspect -> Plan -> Exec) development workflow. Source: DEVELOPMENT_MATRIX.md P3 Agentic Infrastructure. | 2026-01-21 | 2026-01-21 |
| 260121132339 | TODO | P1 | easy | fixer | Fix and apply Linked Indices Tracer: Fix InvalidWellSetsError definition bug in errors.py (defined 3x, references PraxisError before definition), then apply the tracer from session 16296747416823548932 | 2026-01-21 | 2026-01-21 |
| 260121132341 | TODO | P1 | medium | fixer | Review and apply Multi-Vendor Deck diff: Session 6138709097205002465 creates DeckConfigurationService and DeckVisitor. Verify no conflicts with existing DeckTypeDefinitionService, then apply selectively. | 2026-01-21 | 2026-01-21 |
| 260121132343 | TODO | P2 | easy | fixer | Create @simulate_output decorator: Implement Python decorator in praxis/backend/core/decorators/ that declares simulation metadata (shape, range, strategy) per the Browser Simulation research spec. | 2026-01-21 | 2026-01-21 |
| 260121132344 | TODO | P2 | medium | fixer | Create praxis/simulators/ module: Implement PlateReaderSimulator and LiquidHandlerSimulator classes per Browser Simulation research spec. These mirror PLR APIs but generate fake data. | 2026-01-21 | 2026-01-21 |
| 260121132347 | DONE | P2 | easy | fixer | Extend PraxisRunContext with simulation_state: Add is_simulation flag, simulation_state dict, get_simulation_state() and update_simulation_state() methods per Browser Simulation research spec. | 2026-01-21 | 2026-01-21 18:30:43 |
| 260121132355 | TODO | P1 | medium | deep-researcher | Research Infinite Consumables (Browser Mode): Locate where tip rack/consumable depletion happens in browser mode. Implement option to skip DB depletion in simulation + allow runtime unique ID creation for tip racks. | 2026-01-21 | 2026-01-21 |
| 260121144246 | TODO | P1 | easy | fixer | Fix backend API test fixture: test_resource_filtering.py uses 'client' fixture that doesn't exist. Either add conftest.py with TestClient fixture or refactor test to use direct function calls. File: praxis/backend/tests/api/test_resource_filtering.py | 2026-01-21 | 2026-01-21 |
| 260121144248 | TODO | P1 | easy | code | E2E Smoke Test Verification: Run praxis/web-client e2e/smoke.spec.ts in headless mode, capture screenshots of key pages (landing, dashboard, protocol list), save to /tmp/e2e-smoke/. Report pass/fail status and any console errors. | 2026-01-21 | 2026-01-21 |
| 260121144249 | TODO | P1 | medium | code | E2E Browser Execution Test: Run praxis/web-client e2e/execution-browser.spec.ts in headless mode. Capture screenshots at: protocol load, run start, run completion. Save to /tmp/e2e-browser-exec/. Report any failures with stack traces. | 2026-01-21 | 2026-01-21 |
| 260121144251 | TODO | P1 | easy | code | E2E Asset Inventory Test: Run praxis/web-client e2e/asset-inventory.spec.ts in headless mode. Capture screenshots of: asset list view, asset detail view, filter interactions. Save to /tmp/e2e-asset/. Report pass/fail with details. | 2026-01-21 | 2026-01-21 |
| 260121144253 | TODO | P1 | medium | code | E2E User Journeys Test: Run praxis/web-client e2e/user-journeys.spec.ts in headless mode. This covers critical user flows. Capture screenshots at key checkpoints. Save to /tmp/e2e-journeys/. Report comprehensive pass/fail results. | 2026-01-21 | 2026-01-21 |
| 260121144254 | TODO | P1 | medium | code | E2E Deck Setup Test: Run praxis/web-client e2e/specs/deck-setup.spec.ts in headless mode. Capture screenshots of: empty deck, deck with placements, deck configuration dialog. Save to /tmp/e2e-deck/. Report all assertions. | 2026-01-21 | 2026-01-21 |
| 260121144256 | TODO | P1 | medium | code | E2E Protocol Execution Test: Run praxis/web-client e2e/specs/protocol-execution.spec.ts AND e2e/specs/03-protocol-execution.spec.ts in headless mode. Capture execution flow screenshots. Save to /tmp/e2e-protocol/. This is critical path for v0.1-alpha. | 2026-01-21 | 2026-01-21 |
| 260121144301 | TODO | P1 | easy | code | Frontend Build Verification: Run 'npm run build' in praxis/web-client. Capture any TypeScript errors, bundle size stats. Verify build succeeds without errors. Report full build output summary. | 2026-01-21 | 2026-01-21 |
| 260121151719 | TODO | P1 | medium | code | Create shared Playwright fixture for universal welcome dialog handling. Create e2e/fixtures/app.fixture.ts that exports a custom test object with beforeEach hook that: 1) Waits for app shell to load, 2) Detects and dismisses "Welcome to Praxis" dialog if present, 3) Waits for overlays to clear, 4) Sets localStorage flag to disable tours. Update existing specs to import this fixture instead of plain @playwright/test. | 2026-01-21 | 2026-01-21 |
| 260121151722 | TODO | P1 | easy | code | Enable Playwright globalSetup and add tour disablement. In playwright.config.ts: 1) Uncomment line 7 to enable globalSetup, 2) In e2e/global-setup.ts, add localStorage.setItem calls to disable welcome tour/onboarding before tests run. This prevents the tour overlay from blocking all tests. | 2026-01-21 | 2026-01-21 |
| 260121151724 | TODO | P1 | easy | fixer | Fix smoke.spec.ts selector drift. In e2e/specs/smoke.spec.ts line 35: Change expect(page.locator('app-main-layout')) to use a more resilient selector that works with either app-unified-shell or app-main-layout, or use the sidebar-rail which is already checked. The app now uses UnifiedShellComponent (app-unified-shell) as the main shell. | 2026-01-21 | 2026-01-21 |
| 260121151726 | TODO | P1 | easy | fixer | Fix smoke.spec.ts Assets navigation test. In e2e/specs/smoke.spec.ts lines 40-53: The test navigates to /assets and expects app-machine-list to be visible immediately, but /assets now defaults to Overview tab. Fix by: 1) Click the "Machines" tab explicitly after navigation, OR 2) Navigate to /assets?type=machines or equivalent query param. Verify the table appears after correct tab navigation. | 2026-01-21 | 2026-01-21 |
| 260121151729 | TODO | P1 | easy | code | Rename duplicate test suite names for clear reporting. Files: 1) e2e/specs/protocol-execution.spec.ts - change test.describe name from "Protocol Execution Flow" to "Protocol Wizard Flow", 2) e2e/specs/03-protocol-execution.spec.ts - change test.describe.serial name from "Protocol Execution Flow" to "Protocol Execution E2E". This eliminates report collisions. | 2026-01-21 | 2026-01-21 |
| 260121151732 | TODO | P1 | medium | code | Add Configure Simulation dialog handler to wizard.page.ts. In e2e/page-objects/wizard.page.ts: Add a method handleConfigureSimulationDialog() that: 1) Detects if the "Configure Simulation" dialog is visible (look for dialog with title containing "Simulation" or "Configure"), 2) Fills any required fields (instance name), 3) Clicks "Create Simulation" or equivalent confirm button, 4) Waits for dialog to close. Integrate this into the selectMachine or proceedToNextStep flow. | 2026-01-21 | 2026-01-21 |
| 260121151735 | TODO | P1 | medium | code | Add Angular Material stepper animation handling to wizard tests. Issue: mat-form-field elements appear as "hidden" during stepper transitions due to Angular animations. Fix: In wizard.page.ts, add a waitForStepContent() method that waits for the active step content to be fully visible: 1) Wait for .mat-step-content with ng-reflect-expanded="true" or aria-expanded="true", 2) Add 300ms buffer after step transitions for animations, 3) Use more specific locators scoped to the active step panel. | 2026-01-21 | 2026-01-21 |
| 260121151748 | TODO | P1 | medium | code | Enhance base.page.ts overlay handling for CDK backdrops. In e2e/page-objects/base.page.ts: Improve waitForOverlay() method to: 1) Handle multiple overlays (.cdk-overlay-backdrop), 2) Add retries with exponential backoff, 3) Optionally dismiss overlays by pressing Escape if they persist >5s, 4) Log when force-dismissal is used. This prevents overlays from blocking button clicks. | 2026-01-21 | 2026-01-21 |
| 260121151753 | TODO | P2 | easy | recon | RECON: Audit hardcoded CSS values vs themed CSS variables. Major violator is the Settings page. Scan praxis/web-client/src for: 1) Hardcoded color values (#hex, rgb(), rgba()) that should use CSS variables, 2) Hardcoded font-sizes/spacing that should use design tokens, 3) Components not respecting the theme system. Output: Report listing each file, line numbers, and the hardcoded values that need migration to CSS variables. Focus on *.component.scss and*.component.css files. | 2026-01-21 | 2026-01-21 |
| 260121151902 | TODO | P1 | medium | deep-researcher | INVESTIGATE: Protocol Run Wizard simulation selection is still buggy despite prior fixes. Deep-dive into the simulation machine setup flow to identify root causes. Verify the correct pipeline: 1) User selects machine type in frontend, 2) Frontend queries backend/database for available backends, 3) User configures simulation parameters. Check for: hardcoded machine sets instead of database-driven queries, race conditions in MachineService.getSimulators(), frontend state not reflecting backend truth, ConfigureSimulationDialog not properly creating MachineInstance records. Files to audit: wizard.component.ts, machine.service.ts, machine-selection components, simulation dialog. Output: Root cause analysis with specific code locations and fix recommendations. | 2026-01-21 | 2026-01-21 |
| 260121151940 | TODO | P1 | medium | deep-researcher | INVESTIGATE: "Create Simulation" button not working in Execute Protocol flow. Related to simulation selection bugs. Debug the button click handler: 1) Find the Create Simulation button component/template, 2) Trace the click event handler, 3) Check if it's calling MachineService correctly, 4) Verify dialog opens and form submits, 5) Check if MachineInstance is being created in DB. May be related to overlay/z-index issues or broken event bindings. Files: machine-selection.component.ts, configure-simulation-dialog.component.ts, machine.service.ts. | 2026-01-21 | 2026-01-21 |
| 260121152034 | TODO | P1 | medium | deep-researcher | INVESTIGATE: Run Protocol wizard shows wrong machine types for protocols. Example: Plate Reader Assay only shows LiquidHandlers in Select Machine step, not PlateReaders. Root cause: Machine filtering logic not matching protocol requirements to machine capabilities. Check: 1) How protocol.required_machines is defined, 2) How machine selection filters by capability/type, 3) Whether MachineDefinition.machine_type is being used correctly, 4) Database seeding of machine types. Files: machine-selection.component.ts, protocol.service.ts, machine.service.ts. | 2026-01-21 | 2026-01-21 |
| 260121152037 | TODO | P1 | medium | deep-researcher | INVESTIGATE: No per-machine argument configuration in Select Machine step of Run Protocol wizard. Users should be able to configure machine-specific parameters (ports, connection settings, simulation options) for each machine they select. Check: 1) What happens after machine is selected - is there a config step?, 2) MachineInstance vs MachineDefinition parameter handling, 3) Whether machine args are being passed to execution context. This may be a missing feature or broken UI. | 2026-01-21 | 2026-01-21 |
| 260121152041 | TODO | P1 | easy | recon | INVESTIGATE: Asset selection inspection not working in Run Protocol wizard. Users cannot click to inspect/view details of selected assets. Check: 1) Asset cards/list items - do they have click handlers?, 2) Is there an asset detail dialog/panel?, 3) Are click events being captured by parent overlay?, 4) What SHOULD happen when user clicks an asset in selection? | 2026-01-21 | 2026-01-21 |
| 260121152841 | TODO | P1 | easy | recon | RECON: 404 Docs Error for production markdown files. Error: Http failure response for /assets/docs/getting-started/quickstart-production.md: 404. Tasks: 1) List all expected *-production.md paths being requested, 2) Check if these files exist in src/assets/docs/, 3) Determine if we need to create them OR prevent the request, 4) Find where these requests originate (docs service, routing). Output: List of missing files and recommendation (create vs suppress). | 2026-01-21 | 2026-01-21 |
| 260121152845 | TODO | P1 | easy | recon | RECON: Playground Add Inventory Wizard current implementation analysis. The wizard is described as 'UGLY and unlike other components'. Tasks: 1) Find the component files (add-inventory-dialog or similar), 2) Screenshot/document current UI structure, 3) Compare against app design patterns (cards, chips, etc.), 4) List specific UI violations (spacing, colors, responsiveness). Prepare handoff for designer agent. | 2026-01-21 | 2026-01-21 |
| 260121152847 | TODO | P1 | medium | deep-researcher | INVESTIGATE: Categories STILL showing backend types in Playground inventory adder. This was supposedly fixed days ago. Tasks: 1) Find the original fix commit/PR, 2) Check if fix was actually merged, 3) Verify the category filtering logic in current code, 4) Trace data flow from API to UI, 5) Identify why backends are still visible. Output: Root cause + whether fix was reverted, never applied, or insufficient. | 2026-01-21 | 2026-01-21 |
| 260121152849 | TODO | P1 | medium | deep-researcher | INVESTIGATE: 'No definitions matching search' in Playground inventory adder. When searching, no results appear. Tasks: 1) Check ResourceDefinition/MachineDefinition seed data in browser SQLite, 2) Verify definitions are being loaded on app init, 3) Check search/filter logic in the component, 4) Determine if this is data issue or UI filtering bug. Output: Root cause analysis. | 2026-01-21 | 2026-01-21 |
| 260121152851 | TODO | P1 | medium | deep-researcher | INVESTIGATE: No simulation definition on-the-fly creation in Playground inventory. Feature gap: Users should be able to create simulation definitions dynamically for all categories (machines, resources). Tasks: 1) Check if create-definition UI exists anywhere, 2) Identify what API endpoints would be needed, 3) Document what on-the-fly creation means for each category, 4) Assess effort to implement. Output: Feature spec + implementation estimate. | 2026-01-21 | 2026-01-21 |
| 260121152852 | TODO | P1 | medium | recon | INVESTIGATE: Resources cannot be added in Playground inventory. Similar to machines issue. Tasks: 1) Check ResourceDefinition availability, 2) Check the add-resource flow vs add-machine flow, 3) Identify any differences that might cause one to fail, 4) Test both flows side by side. Output: Comparison analysis. | 2026-01-21 | 2026-01-21 |
| 260121152858 | TODO | P1 | medium | designer | DESIGN: Playground Add Inventory Wizard redesign spec. Current wizard is ugly and inconsistent with app design. Create a comprehensive design spec including: 1) Card-based layout for category selection, 2) Chip components for filters/tags, 3) Responsive grid for definition browsing, 4) Search with autocomplete, 5) Quick-create simulation option, 6) Visual consistency with existing dialogs (Asset dialogs, Run Wizard). Output: Design spec document with component hierarchy, mock descriptions, and interaction patterns. | 2026-01-21 | 2026-01-21 |
| 260121153043 | BLOCKED | P2 | easy | code | BLOCKED: Verify Configuration Menu functionality in Playground. Cannot test until resources can be added to the deck. Depends on: investigation of 'No definitions matching search' (260121152849) and 'Resources cannot be added' (260121152852) being resolved first. | 2026-01-21 | 2026-01-21 |
| 260121153047 | BLOCKED | P2 | easy | code | BLOCKED: Verify Direct Control functionality in Playground. Cannot test until machines/resources can be added to the deck. Depends on: investigation of 'No definitions matching search' (260121152849) and machine/resource add issues being resolved first. | 2026-01-21 | 2026-01-21 |
| 260121160424 | TODO | P1 | easy | fixer | FIX: Simulation backend matching logic in Run Protocol wizard.

**Problem**: "Create Simulation" button silently fails because backend matching uses exact name comparison that never matches.

**File**: `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts`

**Issue**: In `configureSimulationTemplate`, the code tries to match:

- `result.simulation_backend_name` (e.g., `pylabrobot.liquid_handling.backends.ChatterboxBackend`)
- Against `b.name` (e.g., `Simulated Liquid Handler`) or `b.fqn`

**Fix options**:

1. Relax matching to fallback to any simulator backend if exact match fails
2. Add backend class names as searchable aliases in PLR_BACKEND_DEFINITIONS
3. Use `backend_type === 'simulator'` as primary match, name as secondary

**Report**: .agent/reports/simulation_selection_investigation.md | 2026-01-21 | 2026-01-21 |
| 260121160429 | TODO | P1 | medium | designer | STYLE: Implement Inventory Wizard (AssetWizard) CSS from design spec.

**Problem**: ~20+ CSS classes in HTML are unimplemented, making wizard visually broken.

**Files**:

- `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.scss`
- `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.html` (minor adjustments)

**Missing classes to implement**:

- `.asset-wizard-container` - Layout container
- `.type-selection`, `.type-card` - Card grid for Machine/Resource selection
- `.category-selection` - Category dropdown area
- `.results-grid`, `.result-card` - Search results grid with cards
- `.step-content`, `.step-actions` - Stepper content areas
- `.search-container`, `.form-grid` - Form layouts

**Requirements**:

1. Use CSS variables (var(--mat-sys-*)) for theming/dark mode
2. Implement hover/focus states for interactive cards
3. Responsive grid (3-4 cols desktop, 2 cols tablet, 1 col mobile)
4. Match styling of other dialogs (Asset Management, Run Wizard)

**Reports**:

- .agent/reports/inventory_wizard_recon.md
- .agent/reports/inventory_wizard_design_spec.md | 2026-01-21 | 2026-01-21 |
| 260121160439 | DONE | P1 | easy | fixer | FIX: SqliteService plr_category seeding - Root cause of all "No definitions matching search" bugs.

**Problem**: The `plr_category` column is NULL in browser SQLite for both machines and resources. Frontend filters expect this field.

**Files to modify**: `praxis/web-client/src/app/core/services/sqlite.service.ts`

**Changes needed**:

1. In machine_definitions INSERT: Add `plr_category = 'Machine'` for all machine definitions
2. In resource_definitions INSERT: Map `plr_category = def.resource_type` or `def.category`
3. Ensure both tables have the column populated during initDb()

**Verification**: After fix, AssetWizard should show machine/resource definitions when searching.

**Reports**:

- .agent/reports/inventory_search_investigation.md
- .agent/reports/resource_vs_machine_flow_investigation.md
- .agent/reports/backend_categories_investigation.md | 2026-01-21 | 2026-01-21 21:07:48 |
| 260121160521 | TODO | P1 | medium | fixer | FIX: Machine type filtering - Plate Reader Assay shows wrong machine types.

**Problem**: Plate Reader Assay shows LiquidHandlers instead of PlateReaders despite `requires_deck=False` logic.

**Hypothesis**: `requires_deck` property is lost during SqliteService mapping.

**Files**:

- `praxis/web-client/src/app/core/services/sqlite.service.ts` - check getProtocols() mapping

**Report**: .agent/reports/machine_type_filtering_investigation.md | 2026-01-21 | 2026-01-21 |
| 260121161814 | TODO | P1 | hard | deep-researcher | DEEP INVESTIGATION: Frontend vs Backend Type Confusion Across Codebase

**Overview**: Multiple UI components are incorrectly displaying backend types instead of frontend machine types. This appears to be a systemic architectural issue affecting:

1. Run Protocol machine selection
2. Asset Wizard categories  
3. Simulation configuration
4. Deck selection

**Key Symptoms**:

- Categories show backend types (ChatterboxBackend) instead of frontend (LiquidHandler)
- Simulation backends render as "[", "]" or individual letters (JSON parse error?)
- "UNIQUE constraint failed: machines.serial_number" when creating simulation
- Multi-machine selection not supported
- +Machine/+Resource doesn't bypass type step
- "Slot-based layout editing coming soon" always shown for non-Hamilton decks

**Investigation Scope**:

1. Map data flow from PLR_BACKEND_DEFINITIONS → SqliteService → UI components
2. Identify where frontend vs backend distinction is lost
3. Document the correct architecture: Frontend Types → Backend Selection
4. Find all places Backend types leak into user-facing UI

**Files of Interest**:

- run-protocol.component.ts (machine selection, simulation creation)
- asset-wizard.ts (category handling)
- sqlite.service.ts (data seeding)
- plr-definitions.ts (source of truth)
- execution.service.ts (compatibility logic)

**Reports to create**: .agent/reports/frontend_backend_type_architecture.md | 2026-01-21 | 2026-01-21 |
| 260121161816 | TODO | P1 | easy | fixer | FIX: Simulation backend dropdown shows corrupted strings ("[", "]", individual letters)

**Symptom**: In Run Protocol wizard, simulation backend selection shows malformed options like "[" and "]" or individual characters instead of backend names.

**Root Cause Hypothesis**: JSON array is being rendered directly as options, OR string is being split character-by-character.

**Files to check**:

- run-protocol.component.ts - how available_simulation_backends is processed
- simulation-config-dialog.component.ts - how dropdown options are built

**Expected**: Dropdown should show "ChatterboxBackend", "SimulatorBackend", etc.

**Report**: .agent/reports/simulation_backend_dropdown_bug.md | 2026-01-21 | 2026-01-21 |
| 260121161821 | TODO | P1 | easy | fixer | FIX: "UNIQUE constraint failed: machines.serial_number" on simulation creation

**Error**: run-protocol.component.ts:1150 - UNIQUE constraint failed

**Root Cause**: Simulation machine creation uses the same serial_number for multiple instances, OR doesn't generate unique serial numbers.

**Fix needed**: Generate unique serial_number (UUID or timestamp-based) for each simulation machine instance.

**File**: sqlite.service.ts or MachineRepository.create() | 2026-01-21 | 2026-01-21 |
| 260121161825 | TODO | P2 | easy | fixer | FIX: Asset Wizard +Machine/+Resource should bypass first step

**Issue**: When clicking "+Machine" or "+Resource" in Playground, wizard should start at category selection (step 2), not type selection (step 1).

**Current behavior**: Shows unnecessary Machine vs Resource selection
**Expected**: Skip to category/definition selection with type pre-selected

**File**: asset-wizard.ts - check for mode/type input and stepper initialization

**Changes**:

1. Accept optional input for pre-selected type (Machine/Resource)
2. If provided, skip first step using MatStepper.selectedIndex = 1
3. PlaygroundComponent should pass the type when opening dialog | 2026-01-21 | 2026-01-21 |
| 260121161826 | TODO | P2 | medium | recon | INVESTIGATE: Deck layout "coming soon" message always shown for non-Hamilton decks

**Symptom**: After selecting a deck in simulation, message "Slot-based layout editing is coming soon. For now, a standard layout is provided." appears for all non-Hamilton/rails decks.

**Questions**:

1. What determines if a deck supports slot-based editing?
2. Is this a feature flag or deck capability?
3. Should this message be hidden, or is the feature actually missing?

**Files**: deck-setup components, deck service, deck type definitions | 2026-01-21 | 2026-01-21 |
| 260121161831 | TODO | P2 | easy | fixer | REMOVE: Transfer pattern argument in selective transfer protocol

**Requested**: Eliminate transfer_pattern arg from selective transfer protocol.

**Action**: Remove the parameter from protocol definition and any calling code.

**Files**: selective_transfer.py or relevant protocol file | 2026-01-21 | 2026-01-21 |
| 260121162014 | TODO | P1 | medium | designer | FIX: Asset Wizard card styling must match Protocol cards (gold standard)

**Problem**: Asset Wizard cards don't match the visual styling of Protocol cards. Category selection uses dropdown instead of chips.

**Requirements**:

1. Audit Protocol card styling in protocol-list or protocol-card components
2. Update Asset Wizard result-card and type-card to use same patterns
3. Replace category dropdown with chip selection or card-based grid
4. Ensure visual consistency across all card-based UIs

**Files**:

- asset-wizard.scss (update styles)
- Protocol card components (reference for gold standard)

**Visual goals**: Same elevation, border-radius, hover effects, typography as protocol cards | 2026-01-21 | 2026-01-21 |
| 260121162018 | DONE | P1 | easy | fixer | FIX: Docs 404 errors from speculative -production.md loading

**Problem**: Docs pages trigger 404s when speculatively loading non-existent *-production.md files, causing ErrorInterceptor to display errors.

**Solution from investigation**: Implement HttpContext token to suppress error handling for these specific speculative requests.

**Files**:

- docs service or doc loader component
- error.interceptor.ts

**Report**: .agent/reports/docs_404_investigation.md

**Implementation**:

1. Add HttpContext token: SUPPRESS_ERROR_HANDLING
2. Set token on speculative doc requests
3. ErrorInterceptor checks for token and skips error display | 2026-01-21 | 2026-01-21 21:24:34 |
| 260121162021 | TODO | P1 | easy | fixer | FIX: Asset Wizard category selection - use chips instead of dropdown

**Problem**: Category selection in Asset Wizard is a dropdown, which is unintuitive. Should use chip selection or card-based selection like other parts of the app.

**Requirements**:

1. Replace mat-select dropdown with mat-chip-listbox or card grid
2. Show all categories at once for quick visual scanning
3. Allow single selection with clear visual feedback
4. Match the interaction pattern used in Run Protocol wizard

**File**: asset-wizard.html, asset-wizard.ts, asset-wizard.scss | 2026-01-21 | 2026-01-21 |
| 260121165407 | TODO | P1 | easy | fixer | FIX: Normalize plr_category values in generate_browser_db.py - ensure Title Case (Plate, TipRack, Deck, Carrier) and filter out method entries (get_*, set_*) | 2026-01-21 | 2026-01-21 |
| 260121165409 | TODO | P1 | medium | fixer | REFACTOR: Remove backends from machine_definitions table - backends should only exist in machine_backend_definitions, not pollute machine_definitions with plr_category='Backend' | 2026-01-21 | 2026-01-21 |
| 260121165411 | DONE | P1 | easy | fixer | FIX: Asset Wizard category dropdown should filter out plr_category='Backend' values - only show frontend-friendly categories (Machine, LiquidHandler, PlateReader, etc.) | 2026-01-21 | 2026-01-21 22:00:24 |
| 260121165416 | TODO | P1 | easy | fixer | FIX: Asset Dashboard bypass - AssetsComponent openUnifiedDialog should pass preselectedType like Playground when clicking +Machine or +Resource buttons | 2026-01-21 | 2026-01-21 |
| 260121165418 | TODO | P2 | easy | designer | STYLE: Asset Wizard category selection - replace mat-select dropdown with mat-chip-listbox for quick visual scanning and selection | 2026-01-21 | 2026-01-21 |
| 260121165421 | TODO | P2 | easy | designer | STYLE: Asset Wizard type cards spacing - reduce horizontal card width and improve responsive grid layout | 2026-01-21 | 2026-01-21 |
| 260121171535 | TODO | P1 | medium | designer | STYLE: Asset Wizard categories - replace chips with icon cards grid (max 4 columns, flex container with max-width), include appropriate category icons | 2026-01-21 | 2026-01-21 |
| 260121171536 | TODO | P1 | easy | fixer | FIX: Asset Wizard dialog size - prevent dialog from expanding when selection is made, use fixed/max height container | 2026-01-21 | 2026-01-21 |
| 260121171537 | TODO | P1 | medium | fixer | FIX: Run Protocol asset selection render bug - autocomplete updates but UI doesn't reflect new selection visually | 2026-01-21 | 2026-01-21 |
| 260121171538 | TODO | P2 | easy | fixer | FIX: Run Protocol asset clear button - add explicit clear action per asset row to reset selection | 2026-01-21 | 2026-01-21 |
| 260121171541 | TODO | P2 | easy | fixer | FIX: Run Protocol hover tooltip - extend tooltip area to cover entire asset row instead of only the selection chip | 2026-01-21 | 2026-01-21 |
| 260121173038 | TODO | P2 | easy | fixer | FIX: Playground Asset Wizard dialog size - match width/height to Assets page dialog | 2026-01-21 | 2026-01-21 |
| 260121173042 | TODO | P2 | easy | fixer | FIX: Playground Asset Wizard dialog size - match width/height to Assets page dialog | 2026-01-21 | 2026-01-21 |
| 260121173046 | TODO | P1 | medium | fixer | FIX: Asset autocomplete display value - after selection, show selected asset name instead of original search text | 2026-01-21 | 2026-01-21 |
| 260121173051 | DONE | P1 | easy | fixer | FIX: Asset autocomplete easy clear - allow clearing selected text easily to search and reselect a different asset | 2026-01-21 | 2026-01-21 22:41:06 |
| 260121173053 | TODO | P2 | easy | fixer | FIX: Asset autocomplete dropdown positioning - fix left-aligned dropdown, should be centered or right-aligned with input | 2026-01-21 | 2026-01-21 |
| 260121173054 | TODO | P1 | easy | fixer | FIX: Add Clear All Selections button for asset form - single button to reset all asset selections, not duplicated per autocomplete | 2026-01-21 | 2026-01-21 |
| 260121173055 | TODO | P1 | medium | fixer | FIX: Add Auto-fill buttons - global Auto-fill All button plus per-asset Auto-fill button in each requirement card | 2026-01-21 | 2026-01-21 |
| 260121173056 | TODO | P1 | easy | fixer | FIX: protocol_runs schema - add missing protocol_definition_accession_id column to schema.sql and praxis.db | 2026-01-21 | 2026-01-21 |
| 260121173057 | TODO | P1 | medium | fixer | FIX: Selective transfer single indices parameter - protocol shows source_wells and target_wells separately when should show single indices param with one well selection | 2026-01-21 | 2026-01-21 |
| 260121173058 | TODO | P2 | easy | fixer | FIX: Tooltip hover delay - increase matTooltipShowDelay for information-dense tooltips in asset selection step | 2026-01-21 | 2026-01-21 |
| 260121173104 | DONE | P1 | medium | fixer | FIX: Deck Setup ghosted items not rendering - resources confirmed in guided deck setup should appear on deck visualization after Done click | 2026-01-21 | 2026-01-21 22:40:59 |
| 260121173253 | DONE | P1 | easy | fixer | FIX: 'Live Experiments' and 'View Run Details' links incorrect destination - should navigate to Execution Monitor (e.g. /runs/:id) instead of Run Protocol wizard | 2026-01-21 | 2026-01-21 22:42:01 |
| 260121180700 | TODO | P1 | hard | oracle | 🔴 CRITICAL BLOCKER: Deep Reconnaissance - 'No definitions found' in Asset Wizard

SYMPTOM: Asset Wizard Step 2 shows 'No definitions found matching ""' for all Machine/Resource searches.

IMPACT: Cannot add machines/resources in Asset Wizard, blocks testing live instrument interface and REPL hardware connection.

INVESTIGATION SCOPE:

1. Verify generate_browser_db.py correctly populates plr_category
2. Check DB state: sqlite3 praxis.db "SELECT COUNT(*), plr_category FROM machine_definitions GROUP BY plr_category"
3. Trace AssetWizard.searchResults$ Observable chain in asset-wizard.ts
4. Examine SqliteService query methods for filtering logic
5. Check AssetService.searchDefinitions() or similar
6. Verify sqlite-repository.ts handles category filtering correctly
7. Look for any frontend transformation/filtering that could drop results

KEY FILES:

- praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.ts
- praxis/web-client/src/app/features/assets/services/asset.service.ts
- praxis/web-client/src/app/core/services/sqlite.service.ts
- praxis/web-client/src/app/core/db/sqlite-repository.ts
- scripts/generate_browser_db.py

DELIVERABLE: Root cause analysis report with specific code locations and recommended fix. | 2026-01-21 | 2026-01-21 |
| 260121181800 | TODO | P1 | hard | oracle | 🔴 Run Protocol Machine/Resource Selection UI Issues

MULTIPLE ISSUES in the Run Protocol asset selection flow:

1. **Missing Simulated Toggle**: Need a toggle to switch between simulated vs real backends
2. **Category Filtering Broken**: Definitions shown should be filtered based on selected category (Machine vs Resource)
3. **Scope**: Fix must apply to BOTH machine AND resource selection workflows
4. **Simulated Showing as Real**: Some simulated backends are incorrectly appearing in the real options list
5. **Chatterbox vs Simulated Ambiguity**: Redundancy/confusion between 'simulated backend' and 'chatterbox' terminology in run protocol context

INVESTIGATION NEEDED:

- How is the asset list populated for Run Protocol?
- Where should the simulated/real toggle live?
- How is category filtering supposed to work?
- What distinguishes a 'simulated backend' from 'chatterbox'?
- What's the data model for is_simulated or similar flags?

KEY FILES:

- praxis/web-client/src/app/features/run-protocol/
- praxis/web-client/src/app/features/run-protocol/components/guided-setup/
- Asset selection components
- Backend/machine definition models

DELIVERABLE: Root cause analysis + implementation plan for toggle and proper filtering | 2026-01-21 | 2026-01-21 |
| 260121182030 | TODO | P1 | medium | fixer | Asset Wizard Empty Search Default State Fix

BUG: Empty search bar shows 'No definitions found' instead of all items

CURRENT BEHAVIOR:

- Empty search bar → 'No definitions found matching ""'
- Type a letter → Results populate and filtering works

EXPECTED BEHAVIOR:

- Empty search bar → Show ALL definitions (default state)
- As user types → Filter the displayed list

ROOT CAUSE LIKELY:

- searchResults$ Observable only triggers on non-empty input
- OR debounce/filter logic skips empty string
- Need to emit all results when query is empty/initial

ALSO FIX:

- Backend/frontend type mixing in results (filtering by plr_category may still be incomplete)

KEY FILES:

- praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.ts
- Look for searchControl.valueChanges or similar
- Check filter/debounce operators in the Observable chain

FIX: Ensure empty query returns all definitions for the selected category | 2026-01-21 | 2026-01-21 |
| 260121182637 | TODO | P1 | medium | fixer | Asset Wizard Backend/Frontend Type Mixing

BUG: Backend types (like Chatterbox, SimulatedBackend) are appearing mixed with frontend-facing Machine/Resource definitions.

EXPECTED: Only user-facing definitions should appear, filtered by plr_category.

FIX:

- Filter results by plr_category in asset-wizard.ts
- Ensure plr_category='Machine' for machines, plr_category='Resource' for resources
- Exclude backend implementation types from user-visible lists

KEY FILES:

- praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.ts
- praxis/web-client/src/app/features/assets/services/asset.service.ts | 2026-01-21 | 2026-01-21 |
| 260121182643 | TODO | P1 | medium | fixer | Asset Wizard Backend/Frontend Type Mixing

BUG: Backend types appearing mixed with frontend-facing Machine/Resource definitions.

FIX: Filter results by plr_category in asset-wizard.ts | 2026-01-21 | 2026-01-21 |
| 260121182644 | TODO | P1 | easy | fixer | FIX: Build Error - isSelectiveTransferProtocol missing method in run-protocol.component.ts:685 | 2026-01-21 | 2026-01-21 |
| 260121182645 | TODO | P1 | easy | fixer | FIX: protocol_runs schema missing protocol_definition_accession_id column | 2026-01-21 | 2026-01-21 |
| 260121182646 | TODO | P2 | medium | fixer | Selective Transfer shows 2 well args instead of single indices parameter | 2026-01-21 | 2026-01-21 |
| 260121182647 | TODO | P2 | easy | fixer | Autocomplete display value not updating after selection | 2026-01-21 | 2026-01-21 |
| 260121182651 | TODO | P2 | easy | fixer | Autocomplete dropdown positioning - push left and maintain consistent size | 2026-01-21 | 2026-01-21 |
| 260121182653 | TODO | P2 | medium | fixer | Deck Setup Resource Dialog - add step-by-step dynamic highlighting like Step 2 | 2026-01-21 | 2026-01-21 |
| 260121182916 | TODO | P1 | easy | fixer | FIX: Machine category filter not applied in Asset Wizard

BUG: Step 2 category selection (LiquidHandler, PlateReader, etc) is ignored when searching Machine definitions.

ROOT CAUSE:

- asset-wizard.ts line 142: searchMachineDefinitions(query) doesn't pass category
- Compare to line 146 for Resources: searchResourceDefinitions(query, category) ✅

FIX:

1. Update AssetService.searchMachineDefinitions to accept optional category param
2. Filter by machine_category field when category provided
3. Update asset-wizard.ts to pass category to the search

FILES:

- praxis/web-client/src/app/features/assets/services/asset.service.ts
- praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.ts | 2026-01-21 | 2026-01-21 |
| 260121182931 | TODO | P2 | easy | fixer | Normalize Chatterbox -> Simulated terminology in UI

ISSUE: Mixed terminology confuses users. PLR uses 'Chatterbox' internally but users understand 'Simulated'.

FIX:

- Map 'Chatterbox' to 'Simulated' in UI display labels
- Keep 'Chatterbox' in code/logs for developer context
- Check asset-wizard.ts availableSimulationBackends array

FILES:

- praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.ts | 2026-01-21 | 2026-01-21 |
| 260121185629 | TODO | P1 | medium | oracle | Investigate why `transfer_pattern` and `replicate_count` parameters returned to Selective Transfer protocol.

**Investigation Path:**

1. Check protocol definition in database:

   ```sql
   sqlite3 praxis/web-client/src/assets/db/praxis.db "SELECT name, parameters FROM function_protocol_definitions WHERE name LIKE '%Selective%'"
   ```

2. If stale params exist, check `generate_browser_db.py` for parameter extraction logic
3. Check if there's a seeding or migration that reintroduces these params
4. Trace from Python protocol definition to DB seeding

**Expected:** Selective Transfer should only have `indices` parameter.

**Output:** Report with findings and cleanup steps. | 2026-01-21 | 2026-01-21 |
| 260121185643 | TODO | P1 | easy | fixer | Direct Control component crashes at line 88 when `method.args` is undefined.

**Location:** `praxis/web-client/src/app/features/playground/components/direct-control/direct-control.component.ts:88`

**Problem:**

```typescript
buildForm(method: MethodInfo) {
  const group: any = {};
  method.args.forEach(arg => {  // Crashes if args is undefined
```

**Fix:**

```typescript
buildForm(method: MethodInfo) {
  const group: any = {};
  (method.args || []).forEach(arg => {
```

Also add same guard in `runCommand()` at line 108. | 2026-01-21 | 2026-01-21 |
| 260121185649 | TODO | P1 | medium | oracle | Run Protocol shows empty machine selection list - users cannot proceed.

**Location:** `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts:935-1038`

**Investigation Path:**

1. Check browser console for `[RunProtocol] Debug Machine Filtering:` logs
2. Trace `loadCompatibility()` function
3. Check if `executionService.getCompatibility()` returns data
4. Check protocol's `assets` array for `required_plr_category`
5. Check filtering logic at lines 986-1011

**Potential Root Causes:**

- Protocol missing `required_plr_category` in assets
- `requiredCategories` set constructed but empty
- Filtering too aggressive (line 1006-1011)
- `requires_deck === false` filtering removes all machines (line 1015-1023)

**Output:** Advisory report with root cause and recommended fix. | 2026-01-21 | 2026-01-21 |
| 260121185654 | TODO | P1 | easy | fixer | Verify that backend types are properly filtered from Asset Wizard category list.

**Location:** `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.ts:143`

**Current Filter:**

```typescript
return this.assetService.searchMachineDefinitions(query, category).pipe(
  map(defs => defs.filter(d => d.plr_category === 'Machine'))
);
```

**Verification Steps:**

1. Open Asset Wizard in browser
2. Select MACHINE type
3. Check if backend types (Chatterbox*, etc.) appear in definition list
4. If backends appear, check DB values: `sqlite3 praxis/web-client/src/assets/db/praxis.db "SELECT name, plr_category FROM machine_definitions LIMIT 20"`
5. If plr_category values are wrong, regenerate: `uv run scripts/generate_browser_db.py`

**Expected:** Only definitions with `plr_category === 'Machine'` shown. | 2026-01-21 | 2026-01-21 |
| 260121185700 | TODO | P1 | medium | oracle | Investigate why `transfer_pattern` and `replicate_count` parameters returned to Selective Transfer protocol.

**Investigation Path:**

1. Check protocol definition in database:

   ```sql
   sqlite3 praxis/web-client/src/assets/db/praxis.db "SELECT name, parameters FROM function_protocol_definitions WHERE name LIKE '%Selective%'"
   ```

2. If stale params exist, check `generate_browser_db.py` for parameter extraction logic
3. Check if there's a seeding or migration that reintroduces these params
4. Trace from Python protocol definition to DB seeding

**Expected:** Selective Transfer should only have `indices` parameter.

**Output:** Report with findings and cleanup steps. | 2026-01-21 | 2026-01-21 |
| 260121185706 | TODO | P1 | hard | fixer | Asset Wizard needs to support two contexts with different flows:

**Contexts:**

- `asset-management`: Create NEW assets from definitions (current behavior)
- `playground`: SELECT EXISTING machines from DB or simulate new

**Implementation:**

1. Add `@Input() context: 'playground' | 'asset-management' = 'asset-management';` to AssetWizard
2. Add conditional logic in `ngOnInit()` for playground context
3. For playground + MACHINE: Show existing machines from `assetService.getMachines()`
4. Add 'Simulate New...' option at bottom of existing machines list
5. Skip definition/config steps unless 'Simulate New' chosen

**Files:**

- `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.ts`
- `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.html`
- Caller in playground component

**Acceptance:**

- Playground shows existing machines for selection
- Asset Management shows definitions for creation
- Both support simulation option | 2026-01-21 | 2026-01-21 |
| 260121185708 | TODO | P1 | medium | fixer | Direct Control shows backend types instead of machine methods.

**Problem:** The component attempts to load methods from `/api/v1/machines/definitions/${defId}/methods` but:

1. May not have correct definition ID
2. API endpoint may not exist in browser mode
3. Shows wrong data in template

**Location:** `praxis/web-client/src/app/features/playground/components/direct-control/direct-control.component.ts:57-79`

**Investigation:**

1. Check how `machine_definition_accession_id` is populated on machine objects
2. Check if methods API exists in browser mode
3. If not, methods need to come from machine_frontend_definitions table

**Fix Path:**

- Use SqliteService to query machine methods from frontend definitions
- OR mock methods based on machine category | 2026-01-21 | 2026-01-21 |
| 260121185711 | DONE | P2 | easy | fixer | Append unique suffix to default asset instance names to prevent UNIQUE constraint failures.

**Location:** `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.ts:177-179`

**Current:**

```typescript
this.configStepFormGroup.patchValue({
  name: def.name,  // Uses definition name directly
  description: def.description || ''
});
```

**Fix:**

```typescript
const uniqueSuffix = Math.random().toString(36).substring(2, 6).toUpperCase();
this.configStepFormGroup.patchValue({
  name: `${def.name} ${uniqueSuffix}`,
  description: def.description || ''
});
```

**Also:** Add user-friendly error toast when UNIQUE constraint fails. | 2026-01-21 | 2026-01-22 00:10:34 |
| 260121185712 | TODO | P2 | easy | fixer | Show user-friendly error messages when asset creation fails.

**Problem:** Raw errors like `UNIQUE constraint failed: resources.name` shown in console only.

**Location:** `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.ts:228-229`

**Fix:**

1. Add MatSnackBar injection
2. Catch specific error patterns in createAsset()
3. Show appropriate toast:
   - UNIQUE constraint -> 'An asset with this name already exists. Please use a different name.'
   - Generic -> 'Failed to create asset. Please try again.'

```typescript
import { MatSnackBar } from '@angular/material/snack-bar';

private snackBar = inject(MatSnackBar);

catch (error: any) {
  const msg = error?.message || '';
  if (msg.includes('UNIQUE constraint')) {
    this.snackBar.open('An asset with this name already exists.', 'OK', { duration: 5000 });
  } else {
    this.snackBar.open('Failed to create asset.', 'OK', { duration: 5000 });
  }
}
``` | 2026-01-21 | 2026-01-21 |
| 260121185717 | TODO | P3 | easy | fixer | Document SharedArrayBuffer limitation and COOP/COEP header requirements.

**Issue:** `python.worker.ts:17 Uncaught ReferenceError: SharedArrayBuffer is not defined`

**Cause:** SharedArrayBuffer requires Cross-Origin-Opener-Policy (COOP) and Cross-Origin-Embedder-Policy (COEP) headers.

**Resolution Options:**
1. Add headers to dev server in angular.json
2. Document as known limitation
3. Add fallback for non-SAB environments

**Output:** Update README or create known-issues doc with:
- Explanation of the issue
- Impact on Python worker
- Workaround or fix instructions | 2026-01-21 | 2026-01-21 |
| 260122092729 | TODO | P1 | medium | fixer | CRITICAL BUG: Protocol Runner displays 'This protocol has no machine requirements' incorrectly | 2026-01-22 | 2026-01-22 14:28:15 |
| 260122092731 | DONE | P1 | easy | recon | Recon: pylabrobot.io types not yet shimmed for browser mode | 2026-01-22 | 2026-01-22 14:37:00 |
| 260122092735 | TODO | P1 | medium | fixer | Implement plate reader open/close methods in Direct Control | 2026-01-22 | 2026-01-22 14:28:15 |
| 260122153000 | DONE | P1 | medium | fixer | Implement WebHID Shim: Created web_hid_shim.py and patched pylabrobot.io.hid for browser-mode Inheco support. | 2026-01-22 | 2026-01-22 |
