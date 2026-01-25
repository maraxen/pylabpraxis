# AUDIT-03: Protocol Library & Execution Monitor

## Target

**Jules**

## System Prompt

`general`

## Skills

`playwright-skill`, `systematic-debugging`

---

## Scope

Audit the Protocol Library and Execution features at:

- `/Users/mar/Projects/praxis/praxis/web-client/src/app/features/protocols/` (10 files)
- `/Users/mar/Projects/praxis/praxis/web-client/src/app/features/execution-monitor/` (29 files)

## Existing E2E Coverage

Review and analyze coverage gaps in:

- `e2e/specs/protocol-library.spec.ts`
- `e2e/specs/protocol-execution.spec.ts`
- `e2e/specs/execution-browser.spec.ts`
- `e2e/specs/monitor-detail.spec.ts`

---

## Objectives

### 1. User Journey Analysis

Map protocol workflow:

- Browse/search protocol library
- View protocol details
- Start execution
- Monitor live execution
- View execution history
- Handle execution errors

### 2. Component Inventory

List components for:

- Protocol display (cards, lists, details)
- Execution control (start, pause, stop, resume)
- Live monitoring (status, progress, logs)
- History/results viewing

### 3. Expected vs Actual Behaviors

- Protocol loading states
- Execution state transitions
- Real-time updates (WebSocket/polling)
- Error recovery

### 4. Gap Analysis

Identify:

- Missing execution states
- Incomplete error handling
- UI feedback gaps
- State synchronization issues

### 5. Test Coverage Assessment

What execution scenarios are tested vs missing?

---

## Deliverables

Create audit report at:
`/Users/mar/Projects/praxis/docs/audits/AUDIT-03-protocol-execution.md`

Report must contain:

1. **Component Map** - Files with purposes (table)
2. **User Flow Diagram** - Mermaid diagram of execution flow
3. **State Machine Diagram** - Execution states and transitions
4. **Gap/Limitation List** - With severity (🔴/🟠/🟡)
5. **Recommended Test Cases** - Atomic descriptions
6. **Shipping Blockers** - Critical issues

---

## IMPORTANT

> ⚠️ **DO NOT** fix any code  
> ⚠️ **DO NOT** create actual tests  
> ⚠️ **DO NOT** debug issues  
> ⚠️ **DO** provide specific file/line references
