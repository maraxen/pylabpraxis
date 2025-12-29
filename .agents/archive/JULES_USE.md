# Jules Usage Guide

This document guides the use of Jules for dispatching development tasks. Updated iteratively based on successes and failures.

## Quick Reference

```bash
# Create a new Jules task
jules remote new "Task title" --description "Detailed task description"

# List active tasks
jules remote list

# Check task status  
jules remote status <task_id>
```

## Best Practices

### ✅ What Works Well

1. **Atomic Tasks**: Small, focused tasks with clear acceptance criteria
2. **Test-First Tasks**: "Write tests for X, then implement X"
3. **Clear File Paths**: Always include exact file paths in task descriptions
4. **Context Links**: Reference `conductor/tracks/<track>/plan.md` for context

### ❌ What Doesn't Work

1. **Vague Descriptions**: "Fix the bug" without specifics
2. **Multiple Unrelated Changes**: Keep tasks focused on one area
3. **Missing Context**: Always include relevant file paths and specs

## Task Templates

### Backend Unit Test Task

```
Title: "Add unit tests for <Module>"
Description:
- File: praxis/backend/<path>/<file>.py
- Create: tests/backend/<path>/test_<file>.py
- Context: conductor/tracks/<track>/plan.md
- Acceptance: All tests pass with `uv run pytest <test_path>`
```

### Frontend Component Task

```
Title: "Implement <Component> component"
Description:
- File: praxis/web-client/src/app/<path>/<component>.component.ts
- Context: conductor/tracks/<track>/spec.md
- Acceptance: Component renders correctly, no lint errors
```

### Bug Fix Task

```
Title: "Fix <issue description>"
Description:
- Issue: <specific error or behavior>
- File(s): <exact paths>
- Steps to reproduce: <steps>
- Expected: <behavior>
- Acceptance: <how to verify fix>
```

## Track-Specific Guidelines

| Track | Focus | Task Type |
|-------|-------|-----------|
| first_light | E2E execution | Integration, debugging |
| workflow_velocity | UX polish | Component, keyboard nav |
| data_insights | Visualization | Plotly charts, data display |
| golden_path | Demo content | Protocols, mock data |
| interactive_deck | Visualizer | Canvas/3D components |
| hardware_bridge | Connectivity | WebSerial, network |

## Lessons Learned

### Session: 2025-12-25 (Initial Dispatch)

**Tasks Dispatched:** 15  
**CLI Version:** v0.1.42  
**Command Syntax:** `jules remote new --session "task description"`

**Key Learnings:**

- ✅ Use `--session` flag, NOT `--description`
- ✅ Include file paths in the session text
- ✅ Keep descriptions concise but complete
- ✅ Reference conductor track spec.md for context

**Dispatched Task IDs:**

| ID | Task |
|---|---|
| 17501031474016936547 | Fix 500 error on POST /protocols/runs |
| 16166737436160178785 | Fix Plotly.js configuration |
| 9022153531935329840 | WebSocket log reception tests |
| 6849380947438220668 | Real-time log streaming verification |
| 5504792999786232435 | 96-well plate heatmap component |
| 9994894263152590209 | Mock telemetry data service |
| 14654287976603204221 | Enhance simple_transfer.py |
| 4848900467701596764 | Mock data generator backend |
| 1147878655740355381 | Document demo narrative flow |
| 2018483486353036781 | Fix command palette navigation |
| 13592632197674260968 | Safe keyboard shortcuts |
| 17187202815358803296 | Loading skeletons for protocol cards |
| 12364093375820506759 | Reservation inspection API |
| 8164906329227431094 | Startup recovery for stale reservations |
| 10313850461911995554 | Asset auto-selection ranking |

### Session: 2025-12-26 (Integration Pull)

**Tasks Attempted to Pull:** 9  
**Successfully Applied:** 3  
**Failed (Conflicts):** 6  

**Command Syntax:** `jules remote pull --session <id> --apply`

**Successfully Applied:**

| ID | Task | Files Added |
|---|---|---|
| 9994894263152590209 | Mock telemetry data service | `mock-telemetry.service.ts` |
| 5504792999786232435 | 96-well plate heatmap component | `plate-heatmap/` component |
| 1147878655740355381 | Document demo narrative flow | `DEMO_SCRIPT.md` |

**Failed Due to Conflicts (Already Integrated or File Structure Changed):**

| ID | Task | Reason |
|---|---|---|
| 17501031474016936547 | Fix 500 error on POST /protocols/runs | Already in codebase |
| 16166737436160178785 | Fix Plotly.js configuration | package.json/component conflicts |
| 9022153531935329840 | WebSocket log reception tests | Test file already exists |
| 13592632197674260968 | Safe keyboard shortcuts | keyboard.service.ts exists |
| 17187202815358803296 | Loading skeletons for protocol cards | Component file not found |
| 8164906329227431094 | Startup recovery for stale reservations | main.py/scheduler.py modified |

**Key Learnings:**

- ⚠️ Jules patches often conflict when local development has continued
- ✅ New file additions (services, components) apply cleanly
- ⚠️ File structure changes break Jules patches (renamed/moved files)
- ✅ Documentation tasks always apply cleanly

**Recommendation:** Pull Jules tasks promptly after completion to minimize conflicts.

---

*Update this file after each Jules dispatch session to capture what worked and what didn't.*
