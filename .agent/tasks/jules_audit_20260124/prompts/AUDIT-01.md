# AUDIT-01: Run Protocol & Wizard

## Target

**Jules**

## System Prompt

`general`

## Skills

`playwright-skill`, `systematic-debugging`

---

## Scope

Audit the Run Protocol feature at:

- `/Users/mar/Projects/praxis/praxis/web-client/src/app/features/run-protocol/` (40 files)

## Existing E2E Coverage

Review and analyze coverage gaps in:

- `e2e/specs/run-protocol-machine-selection.spec.ts`
- `e2e/specs/interactive-protocol.spec.ts`
- `e2e/specs/03-protocol-execution.spec.ts`

---

## Objectives

### 1. User Journey Analysis

Map how a user would actually interact with the run-protocol wizard:

- Step 1: Protocol selection
- Step 2: Machine/workcell configuration
- Step 3: Deck setup (if applicable)
- Step 4: Parameter input
- Step 5: Execution launch
- Step 6: Live monitoring

### 2. Component Inventory

List all components with:

- File path
- Purpose
- Dependencies on other components
- Services injected

### 3. Expected vs Actual Behaviors

For each wizard step, document:

- What SHOULD happen (expected behavior)
- What actually happens (observed behavior)
- Edge cases handled
- Edge cases NOT handled

### 4. Gap Analysis

Identify:

- Missing validations
- Error states not handled
- UX friction points
- Keyboard navigation gaps
- Accessibility issues

### 5. Test Coverage Assessment

For each existing test:

- What user flow does it cover?
- What's missing?
- Is it testing the right thing?

---

## Deliverables

Create audit report at:
`/Users/mar/Projects/praxis/docs/audits/AUDIT-01-run-protocol.md`

Report must contain:

1. **Component Map** - Files with purposes (table)
2. **User Flow Diagram** - Mermaid diagram of wizard steps
3. **Gap/Limitation List** - With severity:
   - 🔴 **Blocker**: Prevents shipping
   - 🟠 **Major**: Significant UX issue
   - 🟡 **Minor**: Polish item
4. **Recommended Test Cases** - Atomic, actionable descriptions
5. **Shipping Blockers** - Critical issues list

---

## IMPORTANT

> ⚠️ **DO NOT** fix any code  
> ⚠️ **DO NOT** create actual tests (just recommend them)  
> ⚠️ **DO NOT** debug issues (just document them)  
> ⚠️ **DO** provide specific file/line references  
> ⚠️ **DO** be thorough and honest about gaps
