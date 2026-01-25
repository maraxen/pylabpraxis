# AUDIT-06: Browser Persistence (OPFS/SQLite)

## Target

**Jules**

## System Prompt

`general`

## Skills

`playwright-skill`, `systematic-debugging`

---

## Scope

Audit the Browser Persistence layer at:

- `/Users/mar/Projects/praxis/praxis/web-client/src/app/core/workers/` (OPFS workers)
- `/Users/mar/Projects/praxis/praxis/web-client/src/app/core/services/` (database services)

Look for:

- `sqlite-opfs.worker.ts`
- `database.service.ts` or similar
- Any persistence-related services

## Existing E2E Coverage

Review and analyze coverage gaps in:

- `e2e/specs/04-browser-persistence.spec.ts`
- `e2e/specs/browser-export.spec.ts`

---

## Objectives

### 1. Architecture Analysis

Map the OPFS-based SQLite persistence layer:

- Worker initialization
- Message passing patterns
- OPFS file structure

### 2. Initialization Flow

Document:

- Database creation
- Schema migrations
- Seed data loading
- Error recovery

### 3. Expected vs Actual Behaviors

- CRUD operations
- Transaction handling
- Concurrent access
- Data export/import

### 4. Gap Analysis

Identify:

- Race conditions
- Data loss scenarios
- Sync issues between tabs
- Migration failure handling
- Recovery from corruption

### 5. Test Coverage Assessment

What persistence scenarios are tested vs missing?

---

## Deliverables

Create audit report at:
`/Users/mar/Projects/praxis/docs/audits/AUDIT-06-persistence.md`

Report must contain:

1. **Architecture Diagram** - Mermaid diagram of components
2. **Initialization Sequence** - Mermaid sequence diagram
3. **Data Flow Diagram** - CRUD operations
4. **Gap/Limitation List** - With severity (🔴/🟠/🟡)
5. **Recommended Test Cases** - Atomic descriptions
6. **Shipping Blockers** - Critical issues

---

## IMPORTANT

> ⚠️ **DO NOT** fix any code  
> ⚠️ **DO NOT** create actual tests  
> ⚠️ **DO NOT** debug issues  
> ⚠️ **DO** provide specific file/line references
