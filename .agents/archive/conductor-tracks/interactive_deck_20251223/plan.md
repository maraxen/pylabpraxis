# Plan: Interactive Deck (Visualizer Integration)

## Phase 1: Minimal Implementation (Demo Ready)
*   [ ] Task: Investigate and Prototype PLR Embedding.
    *   [ ] Subtask: Determine the best method to extract HTML/SVG from PLR (it typically launches a separate server).
    *   [ ] Subtask: Create a backend proxy or endpoint to serve this content to the Angular app to avoid CORS/port issues.
*   [ ] Task: Build `DeckVisualizerComponent`.
    *   [ ] Subtask: Implement the component to fetch and render the visualization.
    *   [ ] Subtask: Add a "Refresh" button to force a reload of the deck state.
*   [ ] Task: Wire to Protocol Wizard.
    *   [ ] Subtask: Ensure the visualizer appears in the "Deck Verification" step of the wizard.
*   [ ] Task: Conductor - User Manual Verification 'Interactive Deck Minimal' (Protocol in workflow.md)

## Phase 2: Full Implementation
*   [ ] Task: Implement WebSocket State Sync.
*   [ ] Task: Implement Drag-and-Drop Configuration.
*   [ ] Task: Conductor - User Manual Verification 'Interactive Deck Full' (Protocol in workflow.md)
