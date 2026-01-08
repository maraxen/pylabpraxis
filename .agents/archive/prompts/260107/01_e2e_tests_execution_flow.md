# Agent Prompt: 01_e2e_tests_execution_flow

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260107](./README.md)
**Backlog:** [quality_assurance.md](../../backlog/quality_assurance.md)

---

## Task

Implement Playwright E2E tests for the Protocol Execution flow in Browser Mode. This covers selecting a protocol, navigating the setup wizard, starting execution, and monitoring status.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [quality_assurance.md](../../backlog/quality_assurance.md) | Work item tracking |
| [e2e/](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/e2e/) | Existing E2E test directory |
| [playwright.config.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/playwright.config.ts) | Playwright configuration |
| [page-objects/](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/e2e/page-objects/) | Existing Page Object Models |

---

## Implementation Details

### 1. Create/Enhance Page Object Models

Extend or create POMs for:

- `ProtocolPage` - Protocol library and selection
- `WizardPage` - Setup wizard navigation
- `ExecutionMonitorPage` - Execution status monitoring

### 2. Test Scenarios

```typescript
// e2e/execution-flow.spec.ts
describe('Protocol Execution Flow', () => {
  test('select protocol from library');
  test('complete setup wizard steps');
  test('start execution');
  test('monitor execution status updates');
  test('view completed execution details');
});
```

### 3. Browser Mode Considerations

- Tests should run against Browser Mode (Pyodide)
- Use simulated backends (no physical hardware)
- Verify IndexedDB persistence of execution records

---

## Project Conventions

- **Commands**: Use `uv run` for all Python commands
- **E2E Tests**: `cd praxis/web-client && npx playwright test`
- **Frontend Tests**: `cd praxis/web-client && npm test`

See [codestyles/](../../codestyles/) for language-specific guidelines.

---

## On Completion

- [ ] Update backlog item status in [quality_assurance.md](../../backlog/quality_assurance.md)
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
- [02_e2e_tests_asset_management.md](../260108/02_e2e_tests_asset_management.md) - Related Asset E2E prompt
