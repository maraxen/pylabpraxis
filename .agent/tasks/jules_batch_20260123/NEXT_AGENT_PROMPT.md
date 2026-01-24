# Jules Batch Review - Agent Prompt

**Date**: 2026-01-23
**Objective**: Systematically review all completed Jules sessions from the Jan 23 batch, generate a comprehensive report, and provide recommendations for next steps.

---

## Context

We dispatched 26 tasks to Jules. A critical infrastructure issue (Vite prebundle conflict with `@sqlite.org/sqlite-wasm`) has been fixed and committed:

```
fix(sqlite): resolve Vite prebundle issue for OPFS worker
- Add sqlite3-opfs-async-proxy.js to assets copy in angular.json
- Exclude @sqlite.org/sqlite-wasm from Vite prebundling
- Configure explicit proxyUri in installOpfsSAHPoolVfs call
```

Many E2E tasks stalled due to this issue. Now we need to:

1. Review all **completed** sessions for mergeable work
2. Identify sessions that need **user feedback** or **plan approval**
3. Generate recommendations for re-dispatch or manual intervention

---

## Session Status Summary

### Completed Sessions (17) - PULL AND REVIEW

| Task ID | Session ID | Category | Description |
|:--------|:-----------|:---------|:------------|
| REFACTOR-02 | `3806881592450903343` | Import Refactor | Convert @features aliases |
| REFACTOR-03 | `13019827227538808257` | Import Refactor | Convert @shared aliases |
| SPLIT-02 | `1174395877673969907` | File Split | playground.component.ts |
| SPLIT-03 | `13313504630511132226` | File Split | data-visualization.component.ts |
| SPLIT-04 | `8806860709165683043` | File Split | scheduler.py |
| SPLIT-05 | `7027017935549180084` | File Split | plr_inspection.py |
| SPLIT-06 | `2939224647793981217` | File Split | resource_type_definition.py |
| E2E-AUDIT-01 | `3561513229318693513` | Test Audit | E2E coverage gaps |
| E2E-NEW-01 | `16991222562636305897` | E2E Creation | OPFS migration tests |
| E2E-NEW-02 | `16282140182043530519` | E2E Creation | Monitor detail tests |
| E2E-NEW-03 | `8998018472489986175` | E2E Creation | Workcell dashboard tests |
| E2E-VIZ-02 | `12590817473184387784` | Visual Audit | Run protocol pages |
| E2E-VIZ-03 | `16182069641460709376` | Visual Audit | Data & Playground |
| JLITE-03 | `14542845870678146245` | JupyterLite | Pyodide kernel auto-init |
| OPFS-01 | `9221878143682473760` | OPFS Review | Protocol via Pyodide |
| OPFS-03 | `14808794888910746056` | OPFS Review | Hardware discovery |

### Awaiting Plan Approval (6) - CHECK STATUS

| Task ID | Session ID | Category |
|:--------|:-----------|:---------|
| REFACTOR-01 | `235373965227071886` | Import Refactor - @core aliases |
| SPLIT-01 | `9828431918057321321` | File Split - run-protocol.component.ts |
| E2E-VIZ-01 | `14797227623251883605` | Visual Audit - Asset pages |
| E2E-VIZ-04 | `9885909361909918124` | Visual Audit - Settings & Workcell |
| JLITE-01 | `3622468687667268403` | JupyterLite - simulate-ghpages.sh audit |
| JLITE-02 | `2066802176665634912` | JupyterLite - theme CSS path doubling |
| OPFS-02 | `10846595792840874073` | OPFS Review - asset instantiation |

### Awaiting User Feedback (2) - NEEDS ATTENTION

| Task ID | Session ID | Category | Notes |
|:--------|:-----------|:---------|:------|
| E2E-RUN-02 | `18163963346804940331` | E2E Run | Protocol execution - stalled on Vite issue |
| E2E-RUN-03 | `16519572840277219101` | E2E Run | Browser persistence - stalled on Vite issue |

### Still Planning (1)

| Task ID | Session ID | Category |
|:--------|:-----------|:---------|
| E2E-RUN-01 | `3974817911567728968` | E2E Run - asset management |

---

## Instructions

### Step 1: Pull Completed Sessions

For each completed session, execute:

```bash
# Change to project root
cd /Users/mar/Projects/praxis

# Pull session (review only, don't apply yet)
jules remote pull --session <SESSION_ID> 2>&1 | cat
```

### Step 2: Extract File Lists (Filter Screenshots)

After pulling, get the list of changed files:

```bash
# List files changed, excluding images and package files
git diff --name-only origin/main...HEAD -- . \
    ':(exclude)*.png' \
    ':(exclude)*.jpg' \
    ':(exclude)*.webp' \
    ':(exclude)package.json' \
    ':(exclude)package-lock.json'
```

### Step 3: View Filtered Diff

```bash
# Get diff without images
git diff origin/main...HEAD -- . \
    ':(exclude)*.png' \
    ':(exclude)*.jpg' \
    ':(exclude)*.webp' \
    ':(exclude)package.json' \
    ':(exclude)package-lock.json' | head -500
```

### Step 4: Evaluate Each Session

For each session, record:

1. **Files Modified**: List of paths
2. **Quality Assessment**:
   - ✅ Clean - mergeable as-is
   - ⚠️ Needs adjustment - minor fixes needed
   - ❌ Problematic - major issues, may discard
3. **Conflicts**: Any overlap with other sessions?
4. **Notes**: Specific observations

### Step 5: Group Analysis

Evaluate related tasks together:

- **REFACTOR group (01-03)**: Check for conflicting import changes
- **SPLIT group (01-06)**: Verify modularization patterns are consistent
- **E2E-NEW group (01-03)**: Test files should follow same patterns
- **E2E-VIZ group (01-04)**: Visual audit reports, check for actionable findings
- **JLITE group (01-03)**: JupyterLite fixes, may have dependencies
- **OPFS group (01-03)**: Review findings, may be outdated post-migration

### Step 6: Generate Final Report

Create `/Users/mar/Projects/praxis/.agent/tasks/jules_batch_20260123/REVIEW_REPORT.md` with:

```markdown
# Jules Batch Review Report

**Date**: 2026-01-23
**Reviewed By**: [Agent]
**Total Sessions**: 26

## Executive Summary

- **Mergeable**: X sessions
- **Needs Adjustment**: X sessions  
- **Discard**: X sessions
- **Needs User Input**: X sessions

## Detailed Review

### REFACTOR Tasks

| ID | Status | Files | Conflicts | Recommendation |
|:---|:-------|:------|:----------|:---------------|
| ... | ... | ... | ... | ... |

[Repeat for each category]

## Conflicts Detected

[List any sessions with overlapping file changes]

## Recommendations

### Immediate Actions
1. ...

### Re-dispatch Needed
1. ...

### Manual Intervention Required
1. ...

## Next Orchestration Wave

[Propose next batch of tasks based on findings]
```

### Step 7: Handle Stalled Sessions

For E2E-RUN-02 and E2E-RUN-03 (awaiting user feedback due to Vite issue):

Provide them this context:

```
The Vite prebundle issue has been fixed. The fix is:
1. angular.json now excludes @sqlite.org/sqlite-wasm from prebundling
2. sqlite3-opfs-async-proxy.js is now copied to assets/wasm/
3. proxyUri is explicitly configured in the worker

You can retry running the E2E tests with:
npm run start:browser (in one terminal)
npx playwright test e2e/specs/<spec-file>.spec.ts --project=chromium --reporter=list

Note: The OPFS toggle has been removed from Settings. All browser persistence is now OPFS-only. Tests that expect an OPFS toggle need to be updated or removed.
```

---

## Key Files Reference

- **Dispatch Table**: `.agent/tasks/jules_batch_20260123/DISPATCH_TABLE.md`
- **Dispatch Log**: `.agent/tasks/jules_batch_20260123/dispatch_log.md`
- **Task Prompts**: `.agent/tasks/jules_batch_20260123/prompts/`
- **Review Output**: `.agent/tasks/jules_batch_20260123/session_reviews/`
- **Final Report**: `.agent/tasks/jules_batch_20260123/REVIEW_REPORT.md`

---

## Important Context

1. **OPFS-Only Migration**: The app now uses OPFS exclusively for browser persistence. No legacy sql.js/IndexedDB path.

2. **Obsolete Test Expectations**: `05-opfs-persistence.spec.ts` expects an OPFS toggle that no longer exists. Sessions working on this test may have invalid recommendations.

3. **Import Aliases**: The project uses `@core`, `@features`, `@shared` path aliases. REFACTOR tasks should convert relative imports to these.

4. **File Size Targets**: SPLIT tasks aim to break files >500 lines into modular components.

5. **E2E Infrastructure**: Tests use `npm run start:browser` for dev server, Playwright for execution.

---

## Success Criteria

1. All 17 completed sessions reviewed with recommendation
2. File lists extracted (no screenshots/package files)
3. Conflicts between sessions identified
4. Final report generated with next steps
5. Stalled sessions have actionable guidance
