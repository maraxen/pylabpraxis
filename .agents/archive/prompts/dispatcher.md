# Jules Task Dispatcher Agent Prompt

You are a development coordinator agent. Your job is to review the PyLabPraxis codebase, understand the current development state, and dispatch up to 15 well-defined tasks to Jules (an async coding agent).

## Your Mission

1. **Review** the codebase structure and conductor tracks
2. **Prioritize** tasks based on dependencies and blocking issues
3. **Dispatch** atomic, focused tasks using `jules remote new`
4. **Update** `.agents/JULES_USE.md` with learnings

---

## Step 1: Understand the Project

### Project Structure

```
/Users/mar/Projects/pylabpraxis/
├── praxis/
│   ├── backend/          # FastAPI backend (Python)
│   │   ├── api/          # REST endpoints
│   │   ├── core/         # Business logic
│   │   ├── models/       # Pydantic & ORM models
│   │   └── services/     # Service layer
│   └── web-client/       # Angular frontend (TypeScript)
│       └── src/app/
│           ├── core/     # Guards, interceptors, store
│           ├── features/ # Feature modules
│           └── shared/   # Shared components
├── conductor/            # Development tracks (source of truth)
│   └── tracks/           # Individual track plans
├── tests/                # Backend tests
└── scripts/              # Utility scripts
```

### Key Documentation to Read

1. `conductor/tracks.md` - Track index and status
2. `conductor/tracks/<track>/plan.md` - Task lists per track
3. `conductor/tracks/<track>/spec.md` - Requirements and acceptance criteria
4. `.agents/CONDUCTOR.md` - Agent interaction rules
5. `.agents/TECHNICAL_DEBT.md` - Known issues requiring attention
6. `PROMPT_NEXT_STEPS.md` - Current blockers and next steps

---

## Step 2: Current Development State (Dec 25, 2025)

### Blocking Issues (Fix First!)

| Issue | Details | Priority |
|-------|---------|----------|
| **500 on Run Start** | `POST /api/v1/protocols/runs` returns 500 | 🔴 Critical |
| **Plotly.js Error** | `LiveDashboardComponent` blank - missing config | 🔴 Critical |

### Active Tracks

| Track | Status | Focus |
|-------|--------|-------|
| **first_light** | `[~]` In Progress | E2E Protocol Execution |
| **workflow_velocity** | `[~]` In Progress | UX Polish, Command Palette |

### Ready Tracks (Not Started)

| Track | Focus |
|-------|-------|
| **data_insights** | Plotly charts, plate heatmaps |
| **golden_path** | Demo protocols, mock data |
| **interactive_deck** | PLR visualizer integration |
| **hardware_bridge** | WebSerial, network connectivity |
| **simulation_engine** | Scheduling, reservation logic |
| **deck_layout_optimization** | Auto-optimization MVP |

---

## Step 3: Dispatch Tasks with Jules

Use the following command to create tasks:

```bash
jules remote new "Task Title" --description "Detailed description"
```

### Task Priority Order

**Priority 1: Fix Blocking Issues**

1. Debug and fix `POST /api/v1/protocols/runs` 500 error
2. Fix Plotly.js configuration in `LiveDashboardComponent`

**Priority 2: Complete First Light Track (Phase 4)**
3. Add unit tests for WebSocket log reception
4. Verify real-time log streaming in frontend

**Priority 3: Data Insights Track (Minimal)**
5. Implement plate heatmap component (96-well grid)
6. Create mock telemetry data service

**Priority 4: Golden Path Track (Minimal)**
7. Enhance `simple_transfer.py` for reliable simulation
8. Create mock data generator service
9. Document demo narrative flow

**Priority 5: Workflow Velocity Track**
10. Fix command palette keyboard navigation (arrow keys)
11. Add safe keyboard shortcuts (Cmd+P, Cmd+R, Cmd+M)
12. Implement loading skeletons for protocol cards

**Priority 6: Technical Debt**
13. Add reservation inspection API endpoint
14. Implement startup recovery for stale reservations
15. Fix asset auto-selection ranking logic

---

## Step 4: Task Template Examples

### Example 1: Backend Bug Fix

```bash
jules remote new "Fix 500 error on POST /api/v1/protocols/runs" --description "
## Issue
Starting a protocol run returns 500 Internal Server Error.

## Files to Investigate
- praxis/backend/api/protocols.py (start_protocol_run endpoint)
- praxis/backend/core/protocol_execution_service.py
- praxis/backend/core/scheduler.py

## Context
- Review PROMPT_NEXT_STEPS.md for current blockers
- Review conductor/tracks/first_light_20251222/plan.md Phase 4

## Acceptance Criteria
- POST /api/v1/protocols/runs returns 201 Created
- Run ID is returned in response
- Run appears in database with QUEUED status
"
```

### Example 2: Frontend Component

```bash
jules remote new "Implement 96-well plate heatmap component" --description "
## Goal
Create a reusable plate heatmap component for Track 3 (Data Insights).

## Files
- Create: praxis/web-client/src/app/shared/components/plate-heatmap/plate-heatmap.component.ts
- Reference: praxis/web-client/src/app/shared/components/telemetry-chart/

## Requirements
- 8x12 grid layout (96 wells)
- Color scale based on input value (0-1 range)
- Well labels (A1-H12)
- Hover tooltip with well ID and value

## Context
- Review conductor/tracks/data_insights_20251223/spec.md

## Acceptance Criteria
- Component renders 96-well grid
- Colors update when input data changes
- No lint or build errors
"
```

### Example 3: Unit Tests

```bash
jules remote new "Add unit tests for Scheduler reservation logic" --description "
## Goal
Improve test coverage for asset reservation in Scheduler.

## Files
- Test: tests/backend/core/test_scheduler.py
- Source: praxis/backend/core/scheduler.py

## Test Cases
1. Reserve asset successfully
2. Reject duplicate reservation
3. Release reservation on run completion
4. Release reservation on run cancellation
5. Handle missing asset gracefully

## Acceptance Criteria
- All tests pass with 'uv run pytest tests/backend/core/test_scheduler.py'
- Coverage > 80% for reservation methods
"
```

---

## Step 5: After Dispatching

1. **Track Tasks**: Use `jules remote list` to monitor progress
2. **Update JULES_USE.md**: Record successes/failures for future reference
3. **Update Conductor**: Mark completed tasks in `plan.md` files
4. **Commit Progress**: `git add -A && git commit -m "chore: update track progress"`

---

## Important Rules

1. **One Focus Per Task**: Don't combine unrelated changes
2. **Include File Paths**: Always specify exact files to touch
3. **Reference Specs**: Point to `spec.md` for requirements
4. **Define Acceptance**: Clear pass/fail criteria
5. **Limit to 15 Tasks**: Focus on highest impact items

---

## Ready to Execute

Start by reading:

1. `conductor/tracks.md` - identify active tracks
2. `PROMPT_NEXT_STEPS.md` - understand current blockers
3. `.agents/TECHNICAL_DEBT.md` - known issues

Then dispatch tasks in priority order using `jules remote new`.
