# AUDIT-02: Asset Management & Inventory

## Target

**Jules**

## System Prompt

`general`

## Skills

`playwright-skill`, `systematic-debugging`

---

## Scope

Audit the Asset Management feature at:

- `/Users/mar/Projects/praxis/praxis/web-client/src/app/features/assets/` (34 files)

## Existing E2E Coverage

Review and analyze coverage gaps in:

- `e2e/specs/02-asset-management.spec.ts`
- `e2e/specs/asset-inventory.spec.ts`
- `e2e/specs/asset-wizard.spec.ts`
- `e2e/specs/asset-wizard-visual.spec.ts`
- `e2e/specs/inventory-dialog.spec.ts`
- `e2e/specs/verify-inventory.spec.ts`

---

## Objectives

### 1. User Journey Analysis

Map CRUD operations for each asset type:

- **Machines**: Create, view, edit, delete
- **Resources**: Create, view, edit, delete
- **Labware**: Create, view, edit, delete
- **Deck Configurations**: Setup, modify

### 2. Component Inventory

List all components (dialogs, wizards, lists) with:

- File path
- Purpose
- CRUD operations supported

### 3. Expected vs Actual Behaviors

For each operation:

- Form validations
- Error handling
- Success feedback
- Persistence (does data survive refresh?)

### 4. Gap Analysis

Identify:

- Missing CRUD operations (e.g., edit not implemented)
- Validation gaps
- Error handling missing
- Duplicate name handling
- Import/export gaps

### 5. Test Coverage Assessment

What user flows are tested vs missing?

---

## Deliverables

Create audit report at:
`/Users/mar/Projects/praxis/docs/audits/AUDIT-02-asset-management.md`

Report must contain:

1. **Component Map** - Files with purposes (table)
2. **User Flow Diagram** - Mermaid diagram of CRUD flows
3. **Gap/Limitation List** - With severity (🔴/🟠/🟡)
4. **Recommended Test Cases** - Atomic descriptions
5. **Shipping Blockers** - Critical issues

---

## IMPORTANT

> ⚠️ **DO NOT** fix any code  
> ⚠️ **DO NOT** create actual tests  
> ⚠️ **DO NOT** debug issues  
> ⚠️ **DO** provide specific file/line references
