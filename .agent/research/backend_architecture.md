# Backend Architecture Research Findings

## 1. Deck Compatibility
There is **no strict class-level mapping** within the `LiquidHandler` or `Backend` classes (in `external/pylabrobot`) that defines compatible decks. 

*   **PLR Level**: Compatibility is largely enforced by physical constraints. For example, `STARBackend.can_reach_position` checks if a coordinate is within the robot's working area. `LiquidHandler` simply accepts any `Deck` instance in its `__init__`.
*   **Praxis Level**: Compatibility is managed at the Protocol definition level. The `Protocol` domain model (`praxis/backend/models/domain/protocol.py`) includes an `allowed_decks` field (list of strings). The frontend (`LocationConstraintsModel`) mirrors this structure.

## 2. Protocol Inference
Protocol inference and argument tracing are handled by the **Tracing** module in `praxis/backend/core/tracing/tracers.py`.

*   **Tracer Classes**: 
    *   `TracedResource`: Represents resources like Plates or TipRacks.
    *   `TracedContainerElementCollection`: Represents a selection of wells/tips (e.g., `plate["A1:H1"]`).
    *   `TracedContainerElement`: Represents a single well/tip.
*   **Inference Logic**:
    *   `TracedResource._infer_element_type()` automatically determines if child elements should be treated as `Well`, `TipSpot`, or `Tube` based on the resource type string.
    *   `TracedContainerElementCollection` implements `__iter__` and `__getitem__`, allowing it to simulate "well selection" logic (slicing, indexing) during symbolic execution without actual hardware interaction.

## 3. Required Arguments
The **minimal required arguments** for initializing a `LiquidHandler` (found in `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py`) are:

1.  `backend`: An instance of `LiquidHandlerBackend` (e.g., `STARBackend`, `LiquidHandlerChatterboxBackend`).
2.  `deck`: An instance of `Deck`.

*Optional arguments:* `default_offset_head96`.

## 4. Simulated vs Chatterbox
**"Chatterbox" is the implementation; "Simulated" is the abstraction.**

*   **Chatterbox**: Defined in `external/pylabrobot/pylabrobot/liquid_handling/backends/chatterbox.py` as `LiquidHandlerChatterboxBackend`. It is a functional PLR backend that prints operations to stdout instead of controlling hardware.
*   **Simulated**: There is **no Python class** named `SimulatedBackend`. "Simulated" is a label used in the Praxis frontend and configuration to refer to the Chatterbox backend.
    *   The frontend explicitly maps "Simulated" or "Chatterbox" strings to the `ChatterboxBackend`.
    *   Docs and code comments confirm `LiquidHandlerChatterboxBackend` is the standard "simulated" backend for device-free testing.
