# Specification: Deck Layout Auto-Optimization (MVP & Full)

## 1. Overview
This track addresses the need for automated deck layout optimization in PyLabPraxis. Currently, protocols like `simple_transfer` imply the presence of hardware (carriers, tip racks) but don't explicitly manage their placement. This feature will implement logic to "fill in the blanks" by implicitly creating necessary carriers and optimizing their placement on the deck.

## 2. Goals
*   **MVP (Minimal Viable Product):** Implement a "First Available" logic for placement and "Greedy Packing" for carrier usage.
*   **Full Implementation:** Advanced optimization (travel distance minimization), learned constraints, and complex constraint solving.
*   **Implicit Handling:** Automatically instantiate carriers when protocols require resources (plates, tips) that need them.

## 3. Functional Requirements (MVP)

### 3.1 Implicit Resource Creation
*   **Carrier Instantiation:** When a protocol requests a resource (e.g., `Plate`) that requires a carrier, the system must automatically check if a compatible carrier exists with free space.
*   **Greedy Packing:** The system must attempt to fill an existing, compatible carrier (e.g., a standard 5-position plate carrier) before instantiating a new one.
*   **Constraint:** Document this choice clearly in the code/docs as "Greedy Packing Strategy."

### 3.2 Layout Optimization Strategy
*   **First Available Slot:** For the MVP, implicit carriers will be placed in the *first available compatible deck slot* (e.g., `CarrierSite`).
*   **LiquidHandler Integration:** The `LiquidHandler` object passed to the protocol function must be pre-populated with this fully resolved deck state (including the implicitly created carriers).

### 3.3 Validation & Constraints
*   **Resource Compatibility:** Verify that the resource (Plate/Tip) physically fits the carrier site.
*   **Slot Uniqueness:** Prevent multiple carriers from being assigned to the same deck slot.
*   **Deck Capacity:** Fail gracefully with a clear error if the implicit requirements exceed the total available deck slots.
*   **Visual Feedback:** The generated layout must be rendered in the `DeckVisualizer` for user verification before execution.
*   **User Constraints:** Support additional positioning constraints specified via the `@protocol_function` decorator (and prepare architecture for future inferred/learned constraints).

## 4. Acceptance Criteria
*   [ ] `simple_transfer.py` can be executed without explicitly defining carriers in the input arguments.
*   [ ] The system automatically instantiates the correct number of carriers for the required source/dest plates and tip racks.
*   [ ] Resources are packed densely onto carriers (Greedy Strategy).
*   [ ] Carriers are placed in the first valid empty slots on the deck.
*   [ ] The final deck layout is visible in the frontend visualizer.
*   [ ] If requirements exceed capacity, the system throws a readable `DeckCapacityError`.

## 5. Out of Scope (MVP)
*   Distance-minimization algorithms (e.g., placing source next to dest).
*   Dynamic re-layout during a run.
*   Complex multi-machine optimization.
