# Plan: Data Insights (Visualization)

## Phase 1: Minimal Implementation (Demo Ready)

* [x] Task: Install and Configure Plotly.
  * [x] Subtask: Install `angular-plotly.js` and `plotly.js-dist-min`.
  * [x] Subtask: Configure the `PlotlyModule` in `app.config.ts` / `shared.module.ts`.
* [ ] Task: Build `PlateHeatmapComponent`.
  * [ ] Subtask: Create component accepting `(rows, cols, data)` inputs.
  * [ ] Subtask: Implement mapping logic from well indices (A1, B1) to grid coordinates.
  * [ ] Subtask: Style with Plotly layout to match app theme.
* [x] Task: Build `TelemetryChartComponent`.
  * [x] Subtask: Create component for time-series data.
  * [x] Subtask: Implement `updateData(point)` method for real-time appending.
* [/] Task: Conductor - User Manual Verification 'Data Insights Minimal' (Protocol in workflow.md)

## Phase 2: Full Implementation

* [ ] Task: Implement Dashboard Builder.
* [ ] Task: Implement Data Export.
* [ ] Task: Conductor - User Manual Verification 'Data Insights Full' (Protocol in workflow.md)
