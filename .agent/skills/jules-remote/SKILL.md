---
name: jules-remote
description: Use this skill when dispatching atomic, isolated development tasks to Jules, a remote AI coding agent.
---

# Jules Remote Agent

Jules is for **atomic, isolated, non-urgent** tasks where we don't need immediate results.

## When to Use Jules

| ✅ Good Fit | ❌ Bad Fit |
|------------|-----------|
| Fix lint errors in 1-3 files | Large refactoring |
| Resolve type checking issues | Multi-file architecture |
| Add missing docstrings | Subjective design work |
| Write unit tests for existing code | Needs immediate results |
| Update import statements | Complex debugging |
| Simple bug fixes with clear repro | Vague requirements |

## Quick Reference

```bash
# List recent sessions
jules remote list --session 2>&1 | cat | head -20

# Create task with full context
jules remote new --session "Title: Fix lint errors in src/auth/

## Context
Files: src/auth/login.py, src/auth/session.py
Related: See .agent/codestyles/python.md for conventions

## Requirements
- Fix all ruff lint errors
- Ensure mypy passes with --strict
- Don't change public API

## Acceptance Criteria
- \`ruff check src/auth/\` returns 0 errors
- \`mypy src/auth/\` returns 0 errors"

# Check status
jules remote list --session 2>&1 | cat | grep "task_id"

# Pull completed task (review only)
jules remote pull --session <task_id>

# Pull and apply patch
jules remote pull --session <task_id> --apply
```

## Task Template (Standard)

```
Title: {Action} {Target}

## Context
Files: {exact file paths}
Related: {reference docs or backlog items}
Current State: {what exists now}

## Requirements
- {specific requirement 1}
- {specific requirement 2}
- Don't: {anti-requirement}

## Acceptance Criteria
- {verifiable criterion 1}
- {verifiable criterion 2}
```

## Task Templates by Type

### Lint/Type Fix

```
Title: Fix lint errors in {path}

## Context
Files: {exact paths}
Tool: ruff / mypy / eslint

## Requirements
- Fix all errors reported by {tool}
- Preserve existing functionality
- Follow .agent/codestyles/{lang}.md conventions

## Acceptance Criteria
- `{tool command}` returns 0 errors
```

### Unit Test Addition

```
Title: Add unit tests for {module}

## Context
Files: {source file}
Create: {test file path}
Framework: pytest / vitest / jest

## Requirements
- Cover all public functions
- Include edge cases
- Mock external dependencies

## Acceptance Criteria
- All tests pass with `{test command}`
- Coverage > 80% for the module
```

### Docstring/Documentation

```
Title: Add docstrings to {module}

## Context
Files: {exact paths}
Style: Google / NumPy / JSDoc

## Requirements
- Document all public functions/classes
- Include parameter types and descriptions
- Add usage examples where helpful

## Acceptance Criteria
- `pydoc {module}` shows complete documentation
- No "missing docstring" lint warnings
```

## Best Practices

1. **Include exact file paths** - Never be vague about locations
2. **Reference conventions** - Point to `.agent/codestyles/` or `.agent/references/`
3. **Verifiable acceptance** - Use commands that return pass/fail
4. **Atomic scope** - One logical change, 1-3 files max
5. **Clear anti-requirements** - What NOT to do

## Gotchas

- **"In Progress" may be complete**: Always check with `jules remote pull <id>`
- **Pull quickly**: File modifications conflict if local dev continues
- **New files apply cleanly**: Modifications to existing files may conflict
- **Extract intent from conflicts**: Don't force-apply, manually apply logic

## Integration with Dev Matrix

When Jules task is created, add to matrix:

```markdown
| {id} | QUEUED | P3 | easy | jules | - | - | - | @jules | {description} | {date} | {date} |
```

When pulled and applied, update to DONE.

## Comparison with Other Dispatch

| Mechanism | Urgency | Complexity | Isolation |
|-----------|---------|------------|-----------|
| Gemini CLI | Immediate | Low-Med | Any |
| Manual Task | Later | High | Any |
| **Jules** | Hours+ | Low | Must be atomic |

Jules = "fire and forget" for well-defined atomic work.
