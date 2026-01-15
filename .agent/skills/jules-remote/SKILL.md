---
name: jules-remote
description: Use this skill when dispatching development tasks to Jules, a remote AI coding agent. This includes creating new tasks, checking task status, pulling completed patches, and managing the Jules task queue.
---

# Jules Remote Agent

This skill guides the use of Jules for dispatching development tasks to a remote AI agent.

## Quick Reference

```bash
# List recent sessions (full IDs, most recent first)
jules remote list --session 2>&1 | cat | head -20

# Create a new Jules task
jules remote new --session "Task title and detailed description"

# Pull completed task (review only)
jules remote pull --session <task_id>

# Pull and apply patch
jules remote pull --session <task_id> --apply
```

> **Note:** The `2>&1 | cat` trick prevents terminal truncation of session IDs. Use `head -N` to limit to the N most recent tasks.

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
2. **Reference relevant design docs or backlog items** for context (see `.agent/backlog/` or `.agent/reference/` for up-to-date specs and requirements)
3. **Pull tasks promptly** after completion to avoid conflicts
4. **New files apply cleanly**; modifications to existing files often conflict

## Lessons Learned

- **"In Progress" may be complete**: When Jules shows "In Progress", the task may still have complete diff output. Always check with `jules remote pull <id>` before assuming work is ongoing.
- **Extract intent from conflicts**: When patches conflict, extract the **intent** and apply logic manually. Don't force-apply corrupted patches.
- **Pull quickly**: File modifications conflict if local development continues on the same files.

## Integration History

See [INTEGRATION_LOG.md](INTEGRATION_LOG.md) for session-by-session records.
