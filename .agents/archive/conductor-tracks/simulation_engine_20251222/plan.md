# Plan: Protocol Simulation and Scheduling Engine

## Phase 1: Core Data Structures
*   [ ] Task: Define the `ProtocolGraph` and `ProtocolNode` models.
    *   [ ] Subtask: Write tests for DAG validation (detecting cycles, disconnected graphs).
    *   [ ] Subtask: Implement the Pydantic models for protocol steps and dependencies.
*   [ ] Task: Define the `VirtualWorkcell` and `Resource` models.
    *   [ ] Subtask: Write tests for resource state transitions (idle -> busy -> idle).
    *   [ ] Subtask: Implement models to represent machine capabilities (e.g., "can_pipette", "can_read_absorbance").
*   [ ] Task: Conductor - User Manual Verification 'Core Data Structures' (Protocol in workflow.md)

## Phase 2: The Scheduler Logic
*   [ ] Task: Implement a basic Topological Sort scheduler.
    *   [ ] Subtask: Write tests for single-protocol scheduling on infinite resources.
    *   [ ] Subtask: Implement the logic to flatten a DAG into a valid execution sequence.
*   [ ] Task: Implement Resource-Constrained Scheduling.
    *   [ ] Subtask: Write tests for scheduling a protocol on a finite set of workcells.
    *   [ ] Subtask: Implement the logic to assign tasks to specific `VirtualWorkcell` instances based on capability matching.
*   [ ] Task: Conductor - User Manual Verification 'The Scheduler Logic' (Protocol in workflow.md)

## Phase 3: The Simulation Engine
*   [ ] Task: Build the Discrete Event Simulation (DES) driver.
    *   [ ] Subtask: Write tests for the event queue and clock advancement.
    *   [ ] Subtask: Implement the main simulation loop that processes "TaskStarted" and "TaskCompleted" events.
*   [ ] Task: Integrate Scheduler with Simulation.
    *   [ ] Subtask: Write integration tests verifying that the simulation correctly estimates total makespan.
    *   [ ] Subtask: Connect the `Scheduler` decisions to the `SimulationEngine` event generation.
*   [ ] Task: Conductor - User Manual Verification 'The Simulation Engine' (Protocol in workflow.md)
