# Protocol Inference: The "Sharp Bits"

This document outlines the subtle details and edge cases of how PyLabPraxis handles protocol inference, resource inheritance, and argument linking.

## 1. Resource inheritance (Well -> Plate -> Deck)

When a protocol is analyzed, the system often identifies specific low-level resources like `Well` or `TipSpot`. However, these are rarely managed as independent assets in the inventory.

### How it works

1. **Detection**: The static analyzer finds a `Well` object in the protocol code.
2. **Path Resolution**: The system uses LibCST to trace the parent attribute access (e.g., `plate_1.wells[0]`).
3. **Inheritance**:
    - If a `Well` is passed to a method, the system automatically infers that the containing `Plate` must be acquired.
    - If the `Plate` is on a `Carrier`, which is on a `Deck`, the system builds a hierarchical requirement chain.
4. **Acquisition**: The `AssetManager` ensures that when a `Well` is "required" for a protocol step, the physical `Plate` instance is appropriately locked and tracked.

> [!NOTE]
> Resource inference always prioritizes the highest-level movable object that can be uniquely identified in the inventory.

---

## 2. Well & Tip Index Mapping

Indices in protocols can be tricky due to different coordinate systems and zero-based vs. one-based indexing.

### Mapping Logic

- **Internal Storage**: All indices are stored as **0-based integers**.
- **UI Display**: The frontend converts these to standard alphanumeric notation (e.g., `0` becomes `A1`, `11` becomes `A12` for a 96-well plate).
- **Coordinate Systems**: The system assumes the standard PyLabRobot column-major ordering (`A1, B1, C1...`) unless explicitly overridden in the protocol metadata.

---

## 3. Linked Arguments (Synchronized Selection)

Linked arguments allow the UI to synchronize selections between two or more parameters (e.g., a "Source Well" and a "Destination Well" that must always match).

### Configuration

In the `@protocol` decorator, use the `linked_to` parameter in the `parameter_options`:

```python
@protocol(
    parameter_options={
        "source_well": {"type": "Well", "linked_to": "dest_well"},
        "dest_well": {"type": "Well"}
    }
)
def simple_transfer(source_well: Well, dest_well: Well):
    pass
```

### Behavior

- **Bi-directional Sync**: Changing `source_well` will update `dest_well`, and vice versa.
- **Unlink Toggle**: Users can manually break the link in the UI if they need to deviate from the synchronized selection.
- **Validation**: The backend verifies that the linked objects are technically compatible (e.g., you cannot link a `Well` to a `LiquidHandler`).

---

## 4. Common "Sharp Bits" (Gotchas)

- **Unresolved Types**: If a variable's type cannot be statically inferred (e.g., passed through a complex wrapper function), the system defaults to requiring manual asset selection at runtime.
- **Dynamic Loops**: If assets are selected inside a loop whose bounds are unknown at static analysis time, the system may overestimate the required inventory to ensure run stability.
- **Deck Collisions**: While the system validates that assets fit on the deck, it does not currently simulate the physical reach of the robot arms during the *inference* phase. Use the **Simulation** view to verify arm movements.
