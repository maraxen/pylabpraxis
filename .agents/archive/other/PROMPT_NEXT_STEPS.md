# Prompt for Next Agent: Path to "Solid Demo"

## 🎯 Mission Overview

Complete the remaining work for a polished, demo-ready PyLabPraxis. This involves finishing the **First Light** milestone and executing **parallel tracks** for visualization and data insights.

**Current State (Dec 24, 2025):**

* Backend: `localhost:8000` ✅
* Frontend: `localhost:4200` ✅
* Database seeded with resources and machine ✅
* Asset reservation bug fixed ✅
* Command Palette navigation fixed ✅
* `DeckVisualizerComponent` (static mock) exists ✅
* `TelemetryChartComponent` (Plotly) exists ✅

---

## 🚦 Dependency Map

```
                    ┌─────────────────────────────────────────────────────────┐
                    │           GOLDEN PATH (Demo Script)                     │
                    │        Depends on All Tracks Below                      │
                    └──────────────────────────┬──────────────────────────────┘
                                               │
         ┌─────────────────────────────────────┼─────────────────────────────────────┐
         │                                     │                                     │
         ▼                                     ▼                                     ▼
┌─────────────────────┐             ┌─────────────────────┐             ┌─────────────────────┐
│   FIRST LIGHT Ph4   │             │   INTERACTIVE DECK  │             │   DATA INSIGHTS     │
│   (WebSocket Logs)  │             │   (Realistic Viz)   │             │   (Plate Heatmap)   │
│   [CRITICAL PATH]   │             │   [PARALLEL]        │             │   [PARALLEL]        │
└─────────────────────┘             └─────────────────────┘             └─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   MOCK DATA EMITTER │
│   (Backend Service) │
│   [SEQUENTIAL]      │
└─────────────────────┘
```

---

## ⏳ Execution Order

| Order | Task | Can Parallelize? |
|---|---|---|
| 1️⃣ | **First Light Ph4**: Fix WebSocket, E2E Run | **No** - Blocking |
| 2️⃣ | **Mock Data Emitter**: Backend service for telemetry | Sequential after (1) |
| 🔀 | **Interactive Deck**: Realistic PLR visualization | **Yes** - Parallel with (1) |
| 🔀 | **Data Insights**: Plate Heatmap component | **Yes** - Parallel with (1) |
| 🔀 | **Command Palette Polish** (optional) | **Yes** - Parallel |
| 3️⃣ | **Golden Path**: Demo script & dry runs | After all above |

---

# 🔴 Prompt 1: First Light Phase 4 (Critical Path)

> **Objective:** Verify End-to-End protocol execution with live log streaming.
>
> **Status (Dec 24, 2025):**
>
> * ✅ WebSocket URL path fixed (added `/execution/` segment)
> * ✅ Cancel endpoint fixed (`/stop` → `/cancel`)
> * ❌ **BLOCKING**: 500 error on `POST /api/v1/protocols/runs`
> * ❌ **BLOCKING**: Plotly.js config error in `LiveDashboardComponent`
>
> **Context:**
>
> * Backend and frontend are running.
> * Database is seeded.
> * Asset reservation logic is fixed.
> * The Execution Monitor is at `/app/run/live`.
>
> **Remaining Tasks:**
>
> 1. **Debug Backend 500 Error:**
>     * Check backend logs for error on `POST /api/v1/protocols/runs`.
>     * Fix the issue preventing run creation.
>
> 2. **Fix Plotly.js Configuration:**
>     * The `/app/run/live` page is blank due to: `Invalid PlotlyJS object`.
>     * Ensure Plotly.js is correctly imported in `LiveDashboardComponent`.
>
> 3. **Verify Log Streaming:**
>     * Ensure backend sends log messages via WebSocket during protocol execution.
>     * Verify frontend receives and displays logs in real-time.
>
> 4. **Run `simple_transfer.py` E2E:**
>     * Go to `/app/run`, select `simple_transfer`.
>     * Ensure "Simulation Mode" is ON.
>     * Execute the run.
>     * **Success Criteria:** Status transitions `QUEUED` → `PREPARING` → `RUNNING` → `COMPLETED`.
>
> **Reference:** `conductor/tracks/first_light_20251222/plan.md` (Phase 4)

---

# 🟡 Prompt 2: Mock Data Emitter (Sequential after Prompt 1)

> **Objective:** Create a backend service that emits simulated telemetry data during a protocol run.
>
> **Context:**
>
> * The `TelemetryChartComponent` exists and can render live line charts.
> * It needs a data source.
>
> **Tasks:**
>
> 1. **Create `MockTelemetryService`:**
>     * Location: `praxis/backend/services/mock_telemetry.py`
>     * This service should be instantiated when a run starts in simulation mode.
>     * It should emit data points (e.g., `{"timestamp": ..., "metric": "temperature", "value": ...}`) every 500ms via the existing WebSocket channel.
>
> 2. **Integrate with `ProtocolExecutionService`:**
>     * When `simulation_mode=True`, start the `MockTelemetryService`.
>     * Emit random, but realistic-looking, data (e.g., temperature fluctuating between 25-27°C).
>     * Stop the service when the run completes.
>
> 3. **Verify Frontend Display:**
>     * Confirm the `TelemetryChartComponent` updates live in the Execution Monitor.
>
> **Reference:** `conductor/tracks/golden_path_20251223/plan.md`

---

# 🔵 Prompt 3: Interactive Deck - Realistic Visualization (Parallel)

> **Objective:** Make the `DeckVisualizerComponent` render a realistic deck layout.
>
> **Context:**
>
> * A `DeckVisualizerComponent` exists with a static mock.
> * It is located at `praxis/web-client/src/app/features/run-protocol/components/deck-visualizer/`.
> * The goal is to make it look more realistic for the demo.
>
> **Tasks:**
>
> 1. **Investigate PLR SVG Output:**
>     * PyLabRobot can generate an SVG of the deck.
>     * Determine if we can call a backend endpoint to get this SVG and embed it in the Angular component.
>     * *Alternative*: Create a more detailed static SVG/HTML mockup if PLR embedding is too complex.
>
> 2. **Improve Visual Fidelity:**
>     * The current mock is a simple grid.
>     * Add visual details: slot labels, resource icons (plate, tip rack), colors for resource types.
>     * Consider using an SVG library or inline SVG for more control.
>
> 3. **Wire to Protocol Assets:**
>     * The `RunProtocolComponent` passes `mockDeckLayout()` to the visualizer.
>     * Modify this to dynamically generate the layout based on the `selectedProtocol().assets`.
>
> **Reference:** `conductor/tracks/interactive_deck_20251223/plan.md`

---

# 🟢 Prompt 4: Data Insights - Plate Heatmap (Parallel)

> **Objective:** Create a `PlateHeatmapComponent` to visualize well data.
>
> **Context:**
>
> * `angular-plotly.js` and `plotly.js-dist-min` are installed.
> * The `TelemetryChartComponent` already uses Plotly.
>
> **Tasks:**
>
> 1. **Create `PlateHeatmapComponent`:**
>     * Location: `praxis/web-client/src/app/shared/components/plate-heatmap/`
>     * Inputs: `rows` (e.g., 8 for a 96-well plate), `cols` (e.g., 12), `data` (a 2D array or object mapping well names to values).
>     * Use Plotly's `heatmap` trace type.
>
> 2. **Map Well Names to Coordinates:**
>     * Implement logic to convert well indices (A1, B1, ..., H12) to grid coordinates.
>
> 3. **Integrate into Execution Monitor:**
>     * Add a new tab or section in the Execution Monitor (or a "Results" view) to display this heatmap.
>     * Initially, use mock data to verify it renders.
>
> **Reference:** `conductor/tracks/data_insights_20251223/plan.md`

---

# 🏁 Prompt 5: Golden Path - Final Demo Script (Final Step)

> **Objective:** Create the `demo_golden_path.py` protocol and document the demo narrative.
>
> **Context:**
>
> * All prior prompts should be complete.
> * The system is now capable of: running a protocol, showing live logs, visualizing the deck, and displaying telemetry.
>
> **Tasks:**
>
> 1. **Create `demo_golden_path.py`:**
>     * Location: `praxis/protocol/protocols/demo_golden_path.py`
>     * Based on `simple_transfer.py`.
>     * Tune timing for a 2-3 minute demo run.
>     * Add steps that are visually interesting (e.g., multiple transfers, mixing).
>
> 2. **Trigger Mock Data Emission:**
>     * Ensure the protocol, when run in simulation mode, triggers the `MockTelemetryService` to emit realistic data.
>
> 3. **Document the Demo Script:**
>     * Create `docs/DEMO_SCRIPT.md`.
>     * Step-by-step click instructions.
>     * Talking points for each screen.
>
> 4. **Dry Run Verification:**
>     * Execute the full demo script 3 times.
>     * Confirm stability and timing.
>
> **Reference:** `conductor/tracks/golden_path_20251223/plan.md`

---

## 🐞 Known Bugs (Low Priority)

* **Command Palette Arrow Navigation:** Mostly fixed, but may still be slightly inconsistent. Investigate `MatDialog` focus trapping if time permits.

---

## How to Run

* **Backend:** `cd /Users/mar/Projects/pylabpraxis && uv run uvicorn main:app --reload --port 8000`
* **Frontend:** `cd /Users/mar/Projects/pylabpraxis/praxis/web-client && npm start`
* **Execution Monitor:** `http://localhost:4200/app/run/live` (after starting a run from `/app/run`)
