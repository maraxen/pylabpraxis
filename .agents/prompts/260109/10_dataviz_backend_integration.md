# Agent Prompt: 10_dataviz_backend_integration

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [dataviz_well_selection.md](../../backlog/dataviz_well_selection.md)  

---

## Task

Design and implement API endpoints for visualization configuration persistence, leveraging the existing `WellDataOutput` ORM for data retrieval.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [dataviz_well_selection.md](../../backlog/dataviz_well_selection.md) | Work item tracking (Phase 1) |
| `praxis/backend/models/orm/outputs.py` | WellDataOutput ORM |
| `praxis/backend/api/` | API routers |

---

## Implementation

1. **Pydantic Models**:

   ```python
   class VisualizationConfig(BaseModel):
       chart_type: Literal["heatmap", "scatter", "bar"]
       color_scale: str
       well_selection: list[str]
       # ... other config options
   ```

2. **API Endpoints**:
   - `GET /api/v1/visualizations/` - List saved visualizations
   - `POST /api/v1/visualizations/` - Save visualization config
   - `GET /api/v1/visualizations/:id` - Get specific config
   - `GET /api/v1/well-data/:run_id` - Get well data for visualization

3. **ORM Integration**:
   - Leverage `WellDataOutput` for data retrieval
   - Add `VisualizationConfigOrm` if needed for persistence

4. **Service Layer**:
   - Create `VisualizationService` for config CRUD
   - Add data aggregation methods for chart rendering

---

## Expected Outcome

- REST API for saving/loading visualization configurations
- Well data accessible for chart rendering
- Pydantic models for type-safe API contracts

---

## Project Conventions

- **Commands**: Use `uv run` for all Python commands
- **Backend Tests**: `uv run pytest tests/ -v`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
