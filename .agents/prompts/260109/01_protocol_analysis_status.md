# Agent Prompt: 01_protocol_analysis_status

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md)  

---

## Task

Investigate and fix the issue where all protocols persistently display "Not Analyzed" status even after analysis should have completed.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md) | Work item tracking |
| [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md) | Issue reference |
| `praxis/backend/services/protocol_definition.py` | Protocol analysis service |
| `praxis/web-client/src/app/features/protocols/` | Protocol list UI |

---

## Investigation Steps

1. **Trace Analysis Flow**:
   - Locate where protocol analysis status is set/updated
   - Verify analysis triggers (on upload, on demand)
   - Check if status is persisted correctly to DB

2. **Frontend Display**:
   - Verify `protocol.analyzed` / `protocol.status` fields are correctly bound
   - Check if API response includes the expected status

3. **Backend Analysis**:
   - Examine `ProtocolDefinitionService.analyze_protocol()` or equivalent
   - Verify the analysis result is committed to the database

---

## Project Conventions

- **Commands**: Use `uv run` for all Python commands
- **Backend Tests**: `uv run pytest tests/ -v`
- **Frontend Tests**: `cd praxis/web-client && npm test`
- **Linting**: `uv run ruff check praxis/backend --fix`

---

## On Completion

- [x] Commit changes with descriptive message referencing the backlog item
- [x] Update backlog item status in `run_protocol_workflow.md`
- [x] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md) if applicable
- [x] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
- [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md) - Known issues
