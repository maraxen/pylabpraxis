# AUDIT-05: Workcell Dashboard

## Target

**Jules**

## System Prompt

`general`

## Skills

`playwright-skill`, `systematic-debugging`

---

## Scope

Audit the Workcell Dashboard feature at:

- `/Users/mar/Projects/praxis/praxis/web-client/src/app/features/workcell/` (12 files)

## Existing E2E Coverage

Review and analyze coverage gaps in:

- `e2e/specs/workcell-dashboard.spec.ts`

---

## Objectives

### 1. User Journey Analysis

Map workcell management workflows:

- View workcell overview/dashboard
- Check machine statuses
- Monitor connections
- Configure workcell settings
- Handle offline/error states

### 2. Component Inventory

List dashboard components:

- Status indicators
- Machine cards/tiles
- Connection status
- Control buttons

### 3. Expected vs Actual Behaviors

- Real-time status updates
- Connection state changes
- Error state display
- Recovery options

### 4. Gap Analysis

Identify:

- Missing status states
- Connection handling gaps
- UX issues for error recovery
- Refresh/polling issues

### 5. Test Coverage Assessment

What workcell scenarios are tested vs missing?

---

## Deliverables

Create audit report at:
`/Users/mar/Projects/praxis/docs/audits/AUDIT-05-workcell.md`

Report must contain:

1. **Component Map** - Files with purposes (table)
2. **User Flow Diagram** - Mermaid diagram
3. **Status State Diagram** - Machine/connection states
4. **Gap/Limitation List** - With severity (🔴/🟠/🟡)
5. **Recommended Test Cases** - Atomic descriptions
6. **Shipping Blockers** - Critical issues

---

## IMPORTANT

> ⚠️ **DO NOT** fix any code  
> ⚠️ **DO NOT** create actual tests  
> ⚠️ **DO NOT** debug issues  
> ⚠️ **DO** provide specific file/line references
