# Plan: Deck Layout Auto-Optimization (MVP)

## Phase 1: Implicit Carrier Management & Greedy Packing
*   [ ] Task: Implement Carrier Compatibility Logic.
    *   [ ] Subtask: Write failing unit tests for checking if a resource (Plate/TipRack) fits a specific carrier site.
    *   [ ] Subtask: Implement the compatibility check logic in `AssetManager` or a dedicated layout service.
*   [ ] Task: Implement Greedy Packing Strategy.
    *   [ ] Subtask: Write failing unit tests for packing resources into the minimum number of compatible carriers.
    *   [ ] Subtask: Implement the greedy packing algorithm (fill existing carriers before instantiating new ones).
    *   [ ] Subtask: Document the strategy in the code as "Greedy Packing Strategy."
*   [ ] Task: Conductor - User Manual Verification 'Implicit Carrier Management' (Protocol in workflow.md)

## Phase 2: First-Available Layout Optimization
*   [ ] Task: Implement Slot Uniqueness and Capacity Validation.
    *   [ ] Subtask: Write failing unit tests for ensuring unique slot assignments and detecting capacity overflow.
    *   [ ] Subtask: Implement validation logic that throws `DeckCapacityError` when the deck is full.
*   [ ] Task: Implement "First Available" Placement Algorithm.
    *   [ ] Subtask: Write failing unit tests for placing carriers in the first valid empty slot index.
    *   [ ] Subtask: Implement the placement logic using the "First Available Slot" strategy.
*   [ ] Task: Conductor - User Manual Verification 'First-Available Layout' (Protocol in workflow.md)

## Phase 3: Orchestrator Integration & User Constraints
*   [ ] Task: Integrate Layout Resolution into Orchestrator.
    *   [ ] Subtask: Write failing integration tests for executing a protocol with implicit assets.
    *   [ ] Subtask: Update the `Orchestrator` to resolve implicit carriers and inject the full deck state into the `LiquidHandler` object.
*   [ ] Task: Support User-Defined Positioning Constraints.
    *   [ ] Subtask: Write failing unit tests for enforcing constraints defined in the `@protocol_function` decorator.
    *   [ ] Subtask: Update the layout engine to respect explicit user-provided constraints during the optimization phase.
*   [ ] Task: Visualizer Integration.
    *   [ ] Subtask: Verify the generated deck layout is correctly serialized and accessible to the frontend `DeckVisualizer`.
*   [ ] Task: Conductor - User Manual Verification 'Orchestrator Integration' (Protocol in workflow.md)
