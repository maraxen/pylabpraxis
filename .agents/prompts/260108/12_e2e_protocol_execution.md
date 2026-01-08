# Agent Prompt: 12_e2e_protocol_execution

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260108](./README.md)  
**Backlog:** [quality_assurance.md](../../backlog/quality_assurance.md)  
**Priority:** P2

---

## Task

Implement Playwright E2E tests for the Protocol Execution flow in Browser Mode, covering protocol selection, parameter configuration, and execution monitoring.

---

## Implementation Steps

### 1. Create Protocol Page Object

Create `praxis/web-client/e2e/page-objects/protocol.page.ts`:

```typescript
export class ProtocolPage {
  constructor(private page: Page) {}
  
  async navigateToProtocols() { /* Navigate to Protocol Library */ }
  async selectProtocol(name: string) { /* Click protocol card */ }
  async configureParameter(name: string, value: string) { /* Fill parameter */ }
  async startExecution() { /* Click Start/Run button */ }
  async getExecutionStatus() { /* Read status from Execution Monitor */ }
  async waitForCompletion(timeout?: number) { /* Wait for run to finish */ }
}
```

### 2. Implement Test Cases

Create `praxis/web-client/e2e/protocol-execution.spec.ts`:

| Test Case | Description |
|-----------|-------------|
| `should display protocol library` | Navigate to Protocols, verify cards render |
| `should select and configure protocol` | Select protocol, fill parameters |
| `should start execution` | Start run, verify status changes to Running |
| `should monitor execution progress` | Check Execution Monitor updates |
| `should complete execution` | Wait for completion, verify success state |

### 3. Handle Browser Mode Specifics

For browser mode testing:

- Protocol execution uses Pyodide worker
- Simulation data may be cached
- No real hardware interactions

```typescript
test('should complete simulated execution', async ({ page }) => {
  const protocolPage = new ProtocolPage(page);
  await protocolPage.navigateToProtocols();
  await protocolPage.selectProtocol('Simple Transfer');
  // Fill minimal parameters
  await protocolPage.startExecution();
  await expect(page.locator('[data-status]')).toContainText('Running');
});
```

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [quality_assurance.md](../../backlog/quality_assurance.md) | Backlog tracking |
| [e2e/page-objects/](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/e2e/page-objects/) | Existing POMs |
| [run-protocol/](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/run-protocol/) | Protocol feature |

---

## Project Conventions

- **E2E Tests**: `cd praxis/web-client && npx playwright test`

See [codestyles/typescript.md](../../codestyles/typescript.md) for conventions.

---

## On Completion

- [ ] Commit changes with message: `test(e2e): add protocol execution flow tests`
- [ ] Update [quality_assurance.md](../../backlog/quality_assurance.md) - mark E2E Tests - Execution complete
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
