# Prompt 14: State Resolution Backend

Implement backend infrastructure for error handling with state resolution.

## Context

When errors occur, use computation graph and state tracers to identify uncertain states.

## Tasks

1. Create StateResolutionService:
   - `identifyUncertainStates(operation, graph, stateSnapshot)` → `list[UncertainStateChange]`
   - Fast path: query method contract for known effects
   - Fallback: analyze operation args, enumerate mutable properties of touched resources

2. Create UncertainStateChange model:
   - state_key: str
   - current_value: Any
   - description: str
   - resolution_type: str

3. Create StateResolution model:
   - operation_id: str
   - resolution_type: str
   - resolved_values: dict[str, Any] (arbitrary user-specified values)
   - resolved_by: str
   - resolved_at: datetime
   - notes: str | None

4. Create StateResolutionLog ORM model for audit trail

5. Add API endpoints:
   - `GET /api/v1/runs/{id}/uncertain-state`
   - `POST /api/v1/runs/{id}/resolve-state`
   - `POST /api/v1/runs/{id}/resume`

6. Implement `applyResolution()` to update simulation state

## Files to Create

- `praxis/backend/core/simulation/state_resolution.py`
- `praxis/backend/services/state_resolution_service.py`
- `praxis/backend/models/orm/resolution.py`

## Files to Modify

- `praxis/backend/api/runs.py`

## Reference

- `.agents/backlog/error_handling_state_resolution.md`
