# AUDIT-09: Direct Control Interface

## Target

**Jules**

## System Prompt

`general`

## Skills

`playwright-skill`, `systematic-debugging`

---

## Scope

Audit the Direct Control feature at:

- `/Users/mar/Projects/praxis/praxis/web-client/src/app/features/playground/components/direct-control/`
- Related services for machine command execution

## Existing E2E Coverage

Review and analyze coverage gaps in:

- `e2e/specs/playground-direct-control.spec.ts`

---

## Objectives

### 1. User Journey Analysis

Map direct control workflows:

- Select machine/resource
- Browse available methods
- Input parameters
- Execute command
- View response/results
- Handle errors

### 2. Component Inventory

List direct control components:

- Method browser/picker
- Parameter input forms
- Execution controls
- Response display
- Error handling UI

### 3. Expected vs Actual Behaviors

- Method listing and filtering
- Parameter validation
- Command execution flow
- Response parsing and display
- Error state handling

### 4. Gap Analysis

Identify:

- Missing parameter validations (e.g., `method.args` undefined - known bug FIX-04)
- Error handling gaps
- UX issues for complex parameters
- Timeout handling
- Disconnection recovery

### 5. Test Coverage Assessment

What direct control scenarios are tested vs missing?

---

## Deliverables

Create audit report at:
`/Users/mar/Projects/praxis/docs/audits/AUDIT-09-direct-control.md`

Report must contain:

1. **Component Map** - Files with purposes (table)
2. **User Flow Diagram** - Mermaid diagram
3. **Parameter Types Matrix** - What input types are supported
4. **Gap/Limitation List** - With severity (🔴/🟠/🟡)
5. **Recommended Test Cases** - Atomic descriptions
6. **Shipping Blockers** - Critical issues

---

## IMPORTANT

> ⚠️ **DO NOT** fix any code  
> ⚠️ **DO NOT** create actual tests  
> ⚠️ **DO NOT** debug issues  
> ⚠️ **DO** provide specific file/line references
