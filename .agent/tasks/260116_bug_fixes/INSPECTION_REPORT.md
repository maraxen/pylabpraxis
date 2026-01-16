# Deep Inspection Report: 260116 Bug Fixes

**Date:** 2026-01-26
**Inspector:** Antigravity
**Task:** 260116_bug_fixes

## 1. Overview

This report details the findings from a deep code inspection of the bugs and UX issues listed in the `README.md` for the `260116_bug_fixes` task. The focus was on identifying the root causes in the codebase and proposing specific technical solutions.

---

## 2. Findings by Issue

### 2.1. Critical: Machine Creation Fails (NOT NULL constraint)

* **Issue:** Adding a new machine fails with `NOT NULL constraint failed: machines.maintenance_enabled` (and likely `maintenance_schedule_json`).
* **Root Cause:**
  * The `MachineRepository.create` method in `praxis/web-client/src/app/core/db/repositories.ts` executes a raw `INSERT` statement.
  * It dynamically constructs columns from the passed `entity` object.
  * The `machines` table has `NOT NULL` constraints on `maintenance_enabled` and `maintenance_schedule_json`.
  * The `AssetService.createMachine` method in `praxis/web-client/src/app/features/assets/services/asset.service.ts` constructs a `Machine` object but **does not** include default values for these maintenance fields.
* **Recommendation:**
  * Modify `AssetService.createMachine` to populate these fields with defaults (e.g., `maintenance_enabled: false`, `maintenance_schedule_json: '{}'`).
  * Alternatively, update the SQLite schema to allow `DEFAULT` values, but fixing the service is less invasive to the schema management.

### 2.2. Critical: Simulated Machines in Hardware Connect Screen

* **Issue:** The "Connect to Hardware" screen serves to connect real physical hardware via WebSerial/WebUSB, but it lists "Simulated" devices which are internal to the software and cannot be "connected" to in that sense.
* **Root Cause:**
  * `HardwareDiscoveryDialogComponent` filters devices using:

        ```typescript
        d.connectionType !== 'simulator' && !(d.plrBackend && d.plrBackend.toLowerCase().includes('simulator'))
        ```

  * This logic likely fails because the `discoveredDevices` returned by `HardwareDiscoveryService` (seeded from `machine_definitions`) might have different connection types or backend names than the filter expects (e.g., "Simulated LiquidHandler" vs "simulator" string check).
* **Recommendation:**
  * Inspect the specific properties of the "Simulated" devices being returned.
  * Strengthen the filter in `HardwareDiscoveryDialogComponent` (or the service) to explicitly exclude any device definition where `frontend_fqn` or `backend` implies simulation.

### 2.3. High: "Not Analyzed" Badge on Protocols

* **Issue:** Protocols show "Not analyzed" warning even when `simulation_result_json` is populated.
* **Root Cause:**
  * `ProtocolWarningBadgeComponent` logic determines status based on `simulation_result`, `failure_modes`, and `simulation_version`.
  * `generate_browser_db.py` seeds `simulation_result_json` with `{"status": "ready", "simulated": True}`.
  * The component likely checks for specific fields (like `simulation_version` or a specific structure for `violations`/`failure_modes`) that are missing or different in the seed script's JSON.
* **Recommendation:**
  * Update `generate_browser_db.py` to produce a full mock `simulation_result_json` structure that matches the `SimulationResult` interface in `protocol.models.ts` (including `simulation_version`, `failure_modes: []`, `inferred_requirements: []`, etc.).

### 2.4. High: No Categories for Machine Selection

* **Issue:** In inventory dialogs (e.g., Playground), trying to add a machine shows no categories.
* **Root Cause:**
  * The `InventoryDialogComponent` computes categories from `machines()` (Active Inventory Instances).
  * In a fresh Browser Mode session, the `machines` table is empty (as `generate_browser_db.py` intentionally does *not* seed instances).
  * Therefore, there are no categories to show.
  * The user likely expects to be able to "Add a Machine" by selecting from *Definitions* (the Catalog) if they haven't bought/created one yet, OR the dialog is strictly for "Add `My Lab Machine` to Playground".
* **Recommendation:**
  * If the intention is "Add to Playground from Inventory", the behavior is technically correct but UX is poor for empty states.
  * **Fix:** Add a "Create/Register New Machine" button in the empty state of the Inventory Dialog that redirects to the Asset Creation flow, OR seed a "Demo Liquid Handler" instance in `generate_browser_db.py` so the user has something to play with immediately (similar to the Demo Workcell).

### 2.5. High: GroupBy "None" Crashes Inventory

* **Issue:** Setting `groupBy` to "none" (null) causes a crash.
* **Root Cause:**
  * Likely a missing null check in the `groupBy` pipe or handling logic in `AssetListComponent` (or equivalent) when accessing properties on the group key.
* **Recommendation:**
  * Add defensive checks for `groupBy === null` or `'none'` in the template or component logic.

### 2.6. High: Missing Deck Definitions

* **Issue:** Only 2 deck definitions (Hamilton ones?) found. Missing default PLR decks.
* **Root Cause:**
  * `generate_browser_db.py` uses `PLRSourceParser` to find classes with `class_type == PLRClassType.DECK`.
  * The parser might not be correctly identifying all deck classes in the `pylabrobot` codebase if they don't inherit directly from a known base or if the static analysis visitor misses them.
* **Recommendation:**
  * Verify `PLRSourceParser` logic.
  * Manually register known critical decks in `generate_browser_db.py` if static analysis is unreliable for them.

### 2.7. High: Execution Machine Selection

* **Issue:** "Select execution machine" shows only one option.
* **Root Cause:**
  * The dropdown likely mimics the `compatible_backends` or available machine instances.
  * Since we have 0 or 1 instance, no choice is available.
* **Recommendation:**
  * Ensure "Simulated Backend" is always an available fallback choice even if a real machine is selected, to allow "Dry Run".

## 3. Plan of Action

We will address these in the following order:

1. **Fix Blockers:**
    * Patch `AssetService` to fix Machine Creation (`NOT NULL`).
    * Update `generate_browser_db.py` to fix Protocol Badges (metadata shape).
2. **Fix UX Issues:**
    * Filter simulators in Hardware Dialog.
    * Seed a default "Demo Machine" in `generate_browser_db.py` to fix the "No Categories" empty state confusion.
3. **Fix Crashes:**
    * Add null check for GroupBy.

This plan will be formally detailed in `implementation_plan.md`.
