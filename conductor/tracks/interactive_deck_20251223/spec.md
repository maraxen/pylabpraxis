# Specification: Interactive Deck (Visualizer Integration)

## 1. Overview
PyLabRobot has a built-in visualization capability (likely SVG/HTML or web server based) that is currently not integrated into PyLabPraxis. This track focuses on embedding that visualization into the Angular application to provide users with a visual representation of the robot deck.

## 2. Goals
*   **Embed Visualizer:** Display the PLR deck visualization within the Angular app layout.
*   **State Sync:** Ensure the visualization reflects the current state of the deck (resource locations, liquid levels).
*   **Interactivity:** (Phase 2) Allow users to modify the deck via the visualizer.

## 3. Minimal Implementation (Demo Ready)
*   **Component Wrapper:** Create an Angular component `<app-deck-visualizer>` that hosts the PLR visualizer.
*   **Iframe/Embed:** If PLR runs its own visualizer server, embed it via `<iframe>`. If it outputs SVG/HTML, render that directly.
*   **Static Snapshot:** Ensure the visualizer renders the *initial* deck state correctly for a selected protocol.
*   **Refresh Mechanism:** A mechanism (button or poll) to reload the view if the state changes.

## 4. Full Implementation (Post-Demo)
*   **Real-Time Sync:** Use WebSockets to push state changes (arm movements, liquid transfers) instantly to the visualizer.
*   **Drag-and-Drop:** Allow dragging resources from the library onto deck slots to configure a run.
*   **Bidirectional Control:** Clicking a resource in the visualizer opens its details or control panel.

## 5. Constraints
*   **Performance:** Visualizer loading shouldn't block the main UI thread.
*   **Responsiveness:** Should scale reasonably well on different screen sizes.
