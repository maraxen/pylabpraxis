# Specification: Protocol Simulation and Scheduling Engine

## 1. Overview
The goal of this track is to build the core logic for simulating and scheduling laboratory protocols. This engine will take a Directed Acyclic Graph (DAG) representation of a protocol and map it onto available virtual workcells. It must resolve dependencies, manage resources (workcells, instruments), and simulate execution time while adhering to constraints like cross-contamination prevention.

## 2. Goals
*   **DAG Resolution:** Parse protocol definitions into executable task graphs.
*   **Virtual Workcell Abstraction:** Define software representations of physical workcells (e.g., liquid handlers, plate readers).
*   **Constraint-Based Scheduling:** Implement a scheduling algorithm that respects task dependencies and resource availability.
*   **Simulation Loop:** Create a time-stepped or event-driven simulation to predict protocol execution duration and throughput.

## 3. Key Components
*   **`ProtocolGraph`:** A data structure representing the steps and dependencies of a protocol.
*   **`VirtualWorkcell`:** A stateful object representing a physical machine's capabilities and current status.
*   **`Scheduler`:** The core engine that assigns `ProtocolGraph` nodes to `VirtualWorkcell` resources over time.
*   **`SimulationEngine`:** The driver that advances the state of the scheduler and workcells to generate a predicted timeline.

## 4. Constraints & Requirements
*   **Python 3.12+:** Implementation must leverage modern Python features.
*   **Type Safety:** Strict type checking with `ty` (and `mypy`/`pyright` compliance).
*   **Test Coverage:** >80% coverage for all scheduling logic.
*   **Extensibility:** The scheduler must be designed to eventually handle complex constraints (e.g., reagent stability, incubation times) even if only basic constraints are implemented initially.

## 5. Out of Scope
*   Physical hardware actuation (this is purely simulation).
*   Frontend visualization (this track focuses on the backend logic).
*   User authentication for the simulation engine (assumed internal service usage initially).
