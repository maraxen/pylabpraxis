# SPLIT-04: Decompose scheduler.py (Backend)

## Context

**File**: `backend/core/scheduler.py`
**Current Size**: 732 lines
**Goal**: Extract into focused modules

## Architecture Analysis

Scheduler likely contains:

1. **Task Scheduling Logic**: Queuing, prioritization
2. **Resource Management**: Worker allocation
3. **State Machine**: Job states, transitions
4. **Event Handlers**: Callbacks, notifications

## Requirements

### Phase 1: Analyze Structure

1. Read the file and identify logical groupings
2. Document current responsibilities
3. Map dependencies to other modules

### Phase 2: Extract Modules

1. `scheduler_core.py` - Main scheduling algorithm
2. `scheduler_state.py` - State machine, transitions
3. `scheduler_resources.py` - Resource allocation (if applicable)
4. Keep backward-compatible imports in original file

### Phase 3: Verification

1. `uv run pytest backend/` - all tests pass
2. `uv run mypy backend/` - no type errors
3. Verify integration with calling code

## Acceptance Criteria

- [ ] Each module under 300 lines
- [ ] Clear separation of concerns
- [ ] All tests pass
- [ ] Type checking passes
- [ ] Commit: `refactor(backend/scheduler): split into focused modules`

## Anti-Requirements

- Do NOT change scheduling behavior
- Do NOT modify public API
- Keep backward-compatible imports
