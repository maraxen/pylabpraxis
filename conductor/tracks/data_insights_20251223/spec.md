# Specification: Data Insights (Visualization)

## 1. Overview
The value of lab automation isn't just in moving liquid—it's in the data generated. This track introduces scientific visualization to PyLabPraxis using **Plotly.js**, the industry standard for scientific plotting. This allows users to see run telemetry (e.g., temperature over time) and results (e.g., plate heatmaps).

## 2. Goals
*   **Native TypeScript Plotting:** Use `angular-plotly.js` to render interactive charts.
*   **Run Telemetry:** Visualize sensor data streams during and after a run.
*   **Result Visualization:** Display plate maps (heatmaps) representing well contents.

## 3. Minimal Implementation (Demo Ready)
*   **Plate Heatmap:** A specific component `<app-plate-heatmap>` that accepts a 2D array of values (e.g., volume, absorbance) and renders a Plotly heatmap or grid.
*   **Live Telemetry Chart:** A line chart component that updates in real-time (or near real-time via polling/websockets) to show a metric like "Temperature" or "Shaker Speed".

## 4. Full Implementation (Post-Demo)
*   **Dashboard Builder:** Allow users to create custom dashboards with drag-and-drop widgets.
*   **Data Export:** Robust export options (CSV, Excel, JSON, PDF).
*   **Comparison Views:** Overlay data from multiple runs to identify trends or outliers.

## 5. Constraints
*   **Performance:** Plotting should be efficient, even with thousands of data points.
*   **Responsiveness:** Charts must resize correctly within the layout.
*   **Consistency:** Plot colors and fonts should match the Material Design theme.
