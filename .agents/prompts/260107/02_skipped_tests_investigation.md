# Agent Prompt: 02_skipped_tests_investigation

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260107](./README.md)
**Backlog:** [quality_assurance.md](../../backlog/quality_assurance.md)

---

## Task

Audit all skipped tests in the codebase, identify root causes, and either fix them or document why they remain skipped.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [quality_assurance.md](../../backlog/quality_assurance.md) | Work item tracking (Section 4) |
| [tests/](file:///Users/mar/Projects/pylabpraxis/tests/) | Backend test directory |
| [src/**/*.spec.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/) | Frontend test files |

---

## Implementation Details

### 1. Audit Backend Tests

```bash
# Find all skipped tests
uv run pytest --collect-only -q 2>/dev/null | grep -i skip
```

**Known Skipped:**

- `tests/core/test_orchestrator.py`

### 2. Audit Frontend Tests

```bash
# Find skipped/excluded tests
cd praxis/web-client
grep -r "skip\|xit\|xdescribe\|\.skip" src/**/*.spec.ts
```

**Known Skipped:**

- `welcome-dialog.component.spec.ts`
- `asset-selector.component.spec.ts`
- `wizard-state.service.spec.ts`

### 3. For Each Skipped Test

1. Identify why it was skipped (missing mock, flaky, deprecated?)
2. Attempt to fix the root cause
3. If unfixable, document the reason with a `// TODO:` comment

### 4. Success Criteria

- All tests either pass or have documented skip reasons
- No silent skips without explanation

---

## Project Conventions

- **Backend Tests**: `uv run pytest tests/ -v`
- **Frontend Tests**: `cd praxis/web-client && npm test`

See [codestyles/](../../codestyles/) for language-specific guidelines.

---

## On Completion

- [ ] Update [quality_assurance.md](../../backlog/quality_assurance.md) Section 4
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md) "Skipped Tests Investigation"
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
