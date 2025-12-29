---
name: jules-remote
description: Use this skill when dispatching development tasks to Jules, a remote AI coding agent. This includes creating new tasks, checking task status, pulling completed patches, and managing the Jules task queue.
---

# Jules Remote Agent

This skill guides the use of Jules for dispatching development tasks to a remote AI agent.

## Quick Reference

```bash
# Create a new Jules task
jules remote new --session "Task title and detailed description"

# List all remote sessions
jules remote list --session

# Pull completed task and apply patch
jules remote pull --session <task_id> --apply

# Pull without applying (review only)
jules remote pull --session <task_id>
```

## When to Use Jules

Jules is best for:

- ✅ **Atomic, focused tasks** with clear acceptance criteria
- ✅ **Test-first tasks**: "Write tests for X, then implement X"
- ✅ **New file creation**: Services, components, documentation
- ✅ **Bug fixes** with specific reproduction steps

Jules struggles with:

- ❌ **Vague descriptions**: "Fix the bug" without specifics
- ❌ **Multiple unrelated changes**: Keep tasks focused
- ❌ **Refactoring tasks** that touch many files

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

## Best Practices

1. **Include exact file paths** in task descriptions
2. **Reference conductor tracks** for context: `conductor/tracks/<track>/spec.md`
3. **Pull tasks promptly** after completion to avoid conflicts
4. **New files apply cleanly**; modifications to existing files often conflict

## Integration Session Log

### 2025-12-29

**New Applied:**

- `4034787287612031698`: Mock data generator backend service (`mock_data_generator.py`) ✅

**Manually Integrated (from conflicting patches):**

- `8164906329227431094`: Stale run recovery → Applied `recover_stale_runs()` method + `statuses` param to `protocols.py`
- `17187202815358803296`: Loading skeletons → Created `protocol-list-skeleton.component.ts`

**Skipped (already implemented or no diff):**

- `10313850461911995554`: Asset auto-selection ranking (no diff in VM)
- `13592632197674260968`: Keyboard shortcuts (already has better implementation)
- `6849380947438220668`: Log streaming (complex conflicts with main.py)
- `633514496330525370`: Test DB fix (file already exists)

**Stalled (need manual resolution):**

- `2018483486353036781`: Command palette navigation (awaiting feedback)
- `12364093375820506759`: Reservation inspection API (awaiting plan approval)

**Lesson:** When patches conflict, extract the **intent** and apply logic manually. Don't force-apply corrupted patches.

### 2025-12-26

**Applied:** 3 tasks (mock-telemetry.service.ts, plate-heatmap component, DEMO_SCRIPT.md)
**Skipped:** 6 tasks (conflicts with modified files)

**Lesson:** Pull Jules tasks quickly. File modifications conflict if local development continues.
