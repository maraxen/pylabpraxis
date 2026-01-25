# AUDIT-04: Playground & Data Visualization

## Target

**Jules**

## System Prompt

`general`

## Skills

`playwright-skill`, `systematic-debugging`

---

## Scope

Audit the Playground and Data features at:

- `/Users/mar/Projects/praxis/praxis/web-client/src/app/features/playground/` (17 files)
- `/Users/mar/Projects/praxis/praxis/web-client/src/app/features/data/` (2 files)

## Existing E2E Coverage

Review and analyze coverage gaps in:

- `e2e/specs/data-visualization.spec.ts`
- `e2e/specs/playground-direct-control.spec.ts`
- `e2e/specs/viz-review.spec.ts`
- `e2e/playground.spec.ts`

---

## Objectives

### 1. User Journey Analysis

Map data exploration workflows:

- Access playground/sandbox
- Direct machine control
- Data visualization rendering
- Experiment with parameters
- View results

### 2. Component Inventory

List visualization components:

- Charts/graphs
- Data tables
- Control interfaces
- Parameter inputs

### 3. Expected vs Actual Behaviors

- Data loading and rendering
- Chart interactivity
- Direct control commands
- Error handling for invalid data

### 4. Gap Analysis

Identify:

- Rendering issues (empty states, loading)
- Performance concerns (large datasets)
- Missing interactivity
- Accessibility for data viz

### 5. Test Coverage Assessment

What visualization scenarios are tested vs missing?

---

## Deliverables

Create audit report at:
`/Users/mar/Projects/praxis/docs/audits/AUDIT-04-playground.md`

Report must contain:

1. **Component Map** - Files with purposes (table)
2. **User Flow Diagram** - Mermaid diagram
3. **Gap/Limitation List** - With severity (🔴/🟠/🟡)
4. **Recommended Test Cases** - Atomic descriptions
5. **Shipping Blockers** - Critical issues

---

## IMPORTANT

> ⚠️ **DO NOT** fix any code  
> ⚠️ **DO NOT** create actual tests  
> ⚠️ **DO NOT** debug issues  
> ⚠️ **DO** provide specific file/line references
