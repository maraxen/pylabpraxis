# Implement Capability Tracking Phase 4 (MVP)

**Objective**: Implement the MVP for automated matching between Protocol requirements and Machine capabilities (Phase 4 of Capability Tracking).

**Context**:
We have successfully implemented Phase 3 (User-Configurable Capabilities). Machines now have both discovered `capabilities` AND `user_configured_capabilities`. We need to implement the logic to check if a specific Machine satisfies the hardware requirements of a specific Protocol.

**Key References**:

- `@[.agents/backlog/capability_tracking.md]` (Phase 4 section)
- `praxis/backend/services/discovery_service.py` (Current protocol discovery)
- `praxis/backend/utils/plr_static_analysis/` (Static analysis infrastructure)
- `praxis/backend/models/orm/machine.py` (`MachineOrm` definition)

**Implementation Steps (MVP)**:

1. **Define Requirement Types (`models.py`)**:
    - Create a `CapabilityRequirement` Pydantic model.
    - Structure: `req.capability_name` (e.g., "has_core96"), `req.expected_value` (e.g., `True` or `> 8`).

2. **Implement Protocol Static Analysis (`ProtocolRequirementExtractor`)**:
    - Create a new LibCST visitor (or extend `DiscoveryService` logic) to analyze `@protocol_function` decorated functions.
    - **Inference Logic (MVP)**:
        - Analyze the function body for calls that imply specific hardware needs.
        - *Example 1*: `lh.pick_up_tips96()` call implies `has_core96=True`.
        - *Example 2*: `lh.move_plate()` implies `has_iswap=True`.
        - *Example 3*: Usage of `PLR.resource.PlateReader` type hint implies need for a plate reader.
    - Store these extracted requirements in the `FunctionProtocolDefinition` (you may need to add a `requirements` JSON field to the ORM/Pydantic models).

3. **Implement Matching Logic (`CapabilityMatcherService`)**:
    - Create a service that takes a `Protocol` and a `Machine`.
    - Logic:
        - Merge Machine's `capabilities` (discovered) and `user_configured_capabilities` (user overrides).
        - Check if all Protocol `requirements` are met by the merged capabilities.
    - Return a result object: `is_compatible: bool`, `missing_capabilities: list[str]`.

4. **API Integration**:
    - Add an endpoint (e.g., `GET /api/protocols/{id}/check-compatibility?machine_id={id}`) that uses the service.

5. **Testing**:
    - Add unit tests for `ProtocolRequirementExtractor` with sample protocol code.
    - Add unit tests for `CapabilityMatcherService` covering various match/mismatch scenarios.

**Notes**:

- Keep it purely static for now (no runtime execution of protocols).
- Focus on the "Implicit" requirements derived from code usage for this MVP. Explicit definition via decorator arguments can be a future enhancement.
