# Handoff: Audit Remediation & Jules Dispatch

**Date**: 2026-01-25  
**From**: Previous session (rate-limited on gemini-cli)  
**Priority**: P1

---

## Phase 1: Review & Atomic Commits

### Modified Files Requiring Review

Review each file, group by logical change, and create atomic commits:

#### Group A: AUDIT-01 - Simulation Validation Guard (READY TO COMMIT)

```bash
git add praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts
git add praxis/web-client/src/app/features/run-protocol/services/execution.service.ts
git commit -m "feat(run-protocol): add simulation/physical validation guard (AUDIT-01)

- Add UI validation in startRun() to prevent physical runs with simulated machines
- Add defense-in-depth check in ExecutionService.startRun()
- Display error snackbar when validation fails

Refs: docs/audits/AUDIT-01-run-protocol.md"
```

#### Group B: Core Infrastructure Changes

Review these files for unrelated changes from previous sessions:

- `.agent/DEVELOPMENT_MATRIX.md` - Task tracking updates
- `.agent/NOTES.md` - Session notes
- `.agent/prompts/orchestrator_v01alpha_merge.md`
- `.agent/reports/orchestrator_session_summary_20260121.md`
- `.agent/reports/v01alpha_orchestrator_handoff_20260121_1845.md`
- `.gitignore`
- `AGENTS.md`

```bash
git add .agent/DEVELOPMENT_MATRIX.md .agent/NOTES.md
git commit -m "chore(agent): update development matrix and notes"

git add .gitignore AGENTS.md
git commit -m "chore: update gitignore and agent documentation"
```

#### Group C: Angular DI & API Improvements

- `praxis/web-client/src/app/core/api-generated/core/request.ts`
- `praxis/web-client/src/app/core/http/custom-request.ts`
- `praxis/web-client/src/app/core/interceptors/browser-mock-router.ts`
- `praxis/web-client/src/app/core/services/sqlite/sqlite.service.ts`
- `praxis/web-client/src/main.ts`
- `praxis/web-client/src/app/core/utils/global-injector.ts` (NEW)

```bash
git add praxis/web-client/src/app/core/
git add praxis/web-client/src/main.ts
git commit -m "refactor(core): modernize DI patterns with GlobalInjector utility

- Add GlobalInjector for non-DI context dependency resolution
- Update request handlers and mock router"
```

#### Group D: Playground Component Fixes

- `praxis/web-client/src/app/features/playground/components/playground-header/playground-header.component.ts`
- `praxis/web-client/src/app/features/playground/components/playground-machine-selector/playground-machine-selector.component.ts`

```bash
git add praxis/web-client/src/app/features/playground/
git commit -m "fix(playground): minor component improvements"
```

#### Group E: Untracked Files

Add relevant new files:

```bash
git add docs/audits/BUILD_ERRORS.md docs/audits/PLAN_FOR_REMEDIATION.md
git commit -m "docs(audits): add build errors log and remediation plan"

git add .agent/tasks/jules_audit_20260124/
git add .agent/tasks/jules_batch_20260123/REVIEW_PLAN.md
git add .agent/tasks/jules_batch_20260123/scripts/
git add .agent/tasks/jules_batch_20260124/
git commit -m "chore(tasks): add jules batch and audit task directories"
```

---

## Phase 2: Jules Dispatch for Remaining Audits

Create prompts in `.agent/tasks/jules_audit_remediation_20260125/prompts/` and dispatch to Jules.

### AUDIT-03: PAUSE/CANCEL Execution Controls

**File**: `AUDIT-03-execution-controls.md`

```markdown
# AUDIT-03: Implement PAUSE/CANCEL Execution Controls

## Problem
The UI provides no PAUSE, RESUME, or CANCEL controls for running protocols.

## Target Files
- `praxis/web-client/src/app/features/execution-monitor/components/run-detail.component.ts`
- `praxis/web-client/src/app/features/execution-monitor/components/run-detail.component.html`

## Requirements
1. Add PAUSE and CANCEL buttons to the run-detail template
2. Wire buttons to call executionService methods
3. Update UI to show PAUSED state visually
4. Add error messages when WebSocket disconnects

## Reference
See `docs/audits/AUDIT-03-protocol-execution.md` for state diagram and test cases.

## Verification
- `npm run test --prefix praxis/web-client`
- `npx playwright test e2e/specs/execution-monitor.spec.ts`
```

### AUDIT-06: OPFS Schema Migrations

**File**: `AUDIT-06-schema-migrations.md`

```markdown
# AUDIT-06: Implement OPFS SQLite Schema Migrations

## Problem
No schema versioning or migration path for OPFS SQLite.

## Target Files
- `praxis/web-client/src/app/core/workers/sqlite-opfs.worker.ts`
- `praxis/web-client/src/app/core/services/sqlite/sqlite-opfs.service.ts`
- `praxis/web-client/src/app/core/services/sqlite/sqlite.service.ts`

## Requirements
1. Add PRAGMA user_version tracking constant
2. On init, check version against expected
3. On mismatch, show dialog to guide Factory Reset
4. Add 10s timeout to init() with error display

## Reference
See `docs/audits/AUDIT-06-persistence.md` for architecture diagrams.

## Verification
- `npm run test --prefix praxis/web-client`
- Manual browser devtools verification
```

### AUDIT-07: JupyterLite Bootstrap Fix

**File**: `AUDIT-07-jupyterlite-bootstrap.md`

```markdown
# AUDIT-07: Fix JupyterLite Bootstrap URL Length

## Problem
Bootstrap code passed via URL param risks 431 errors.

## Target Files
- `praxis/web-client/src/app/features/playground/playground.component.ts`
- `praxis/web-client/src/assets/jupyterlite/bootstrap.py` (NEW)

## Requirements
1. Create static bootstrap.py file in assets
2. Modify playground.component.ts to load from file OR use postMessage
3. Remove URL-encoded bootstrap approach
4. Ensure GH-Pages deployment works

## Reference
See `docs/audits/AUDIT-07-jupyterlite.md`

## Verification
- `npm run build:gh-pages --prefix praxis/web-client`
- Manual browser test
```

### AUDIT-09: Direct Control Real Methods

**File**: `AUDIT-09-direct-control.md`

```markdown
# AUDIT-09: Replace Mock Methods with Real Introspection

## Problem
Direct Control uses hardcoded mock methods.

## Target Files
- `praxis/web-client/src/app/features/playground/components/direct-control/direct-control.component.ts`

## Requirements
1. Replace getMockMethodsForCategory() with real introspection
2. Add response/error handling for executed commands
3. Add loading state while command is in progress
4. Improve parameter type support for list/dict/enum

## Reference
See `docs/audits/AUDIT-09-direct-control.md`

## Verification
- `npm run test --prefix praxis/web-client`
```

---

## Dispatch Commands

After creating prompt files, dispatch to Jules:

```bash
# Create dispatches using jules-remote skill or manual API calls
# Each dispatch should reference the prompt file and target the praxis repo
```

---

## Status Summary

| Audit | Status | Notes |
|-------|--------|-------|
| AUDIT-01 | ✅ Implemented | Needs test verification, ready to commit |
| AUDIT-03 | 📋 Prompt Ready | Dispatch to Jules |
| AUDIT-06 | 📋 Prompt Ready | Dispatch to Jules |
| AUDIT-07 | 📋 Prompt Ready | Dispatch to Jules |
| AUDIT-09 | 📋 Prompt Ready | Dispatch to Jules |
