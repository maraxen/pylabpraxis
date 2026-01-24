# Jules Dispatch Table - 2026-01-23

## Overview

| Category | Count | Priority Mix |
|:---------|:------|:-------------|
| **REFACTOR** (import aliases) | 3 | P2 |
| **SPLIT** (file decomposition) | 6 | P2 |
| **E2E-AUDIT** | 1 | P1 |
| **E2E-NEW** (create tests) | 3 | P1-P2 |
| **E2E-RUN** (fix tests) | 3 | P1 |
| **E2E-VIZ** (visual audit) | 4 | P2 |
| **JLITE** (JupyterLite) | 3 | P1 |
| **OPFS** (persistence review) | 3 | P2 |
| **TOTAL** | **26** | |

---

## Complete Task List

| ID | Title | Priority | Skills/Prompts | Target |
|:---|:------|:---------|:---------------|:-------|
| **REFACTOR-01** | Convert relative imports → @core aliases | P2 | `fixer.md` | `src/app/core/*` (excl. api-generated) |
| **REFACTOR-02** | Convert relative imports → @features aliases | P2 | `fixer.md` | `src/app/features/*` |
| **REFACTOR-03** | Convert relative imports → @shared aliases | P2 | `fixer.md` | `src/app/shared/*` |
| **SPLIT-01** | Decompose run-protocol.component.ts | P2 | `fixer.md`, `senior-architect` | 1,477 lines → modular |
| **SPLIT-02** | Decompose playground.component.ts | P2 | `fixer.md`, `senior-architect` | 1,324 lines → modular |
| **SPLIT-03** | Decompose data-visualization.component.ts | P2 | `fixer.md`, `senior-architect` | 932 lines → modular |
| **SPLIT-04** | Decompose scheduler.py | P2 | `fixer.md`, `senior-architect` | 732 lines → modular |
| **SPLIT-05** | Decompose plr_inspection.py | P2 | `fixer.md`, `senior-architect` | 716 lines → modular |
| **SPLIT-06** | Decompose resource_type_definition.py | P2 | `fixer.md`, `senior-architect` | 701 lines → modular |
| **E2E-AUDIT-01** | Audit E2E test coverage gaps | P1 | `recon.md`, `playwright-skill` | Route coverage analysis |
| **E2E-NEW-01** | Create OPFS migration E2E tests | P1 | `playwright-skill`, `fixer.md` | OPFS persistence |
| **E2E-NEW-02** | Create monitor detail E2E tests | P2 | `playwright-skill`, `fixer.md` | `/app/monitor/:id` |
| **E2E-NEW-03** | Create workcell dashboard E2E tests | P2 | `playwright-skill`, `fixer.md` | `/app/workcell/*` |
| **E2E-RUN-01** | Run & fix asset management E2E | P1 | `playwright-skill`, `designer.md`, `ui-ux-pro-max` | `02-asset-management.spec.ts` |
| **E2E-RUN-02** | Run & fix protocol execution E2E | P1 | `playwright-skill`, `designer.md`, `ui-ux-pro-max` | `03-protocol-execution.spec.ts` |
| **E2E-RUN-03** | Run & fix browser persistence E2E | P1 | `playwright-skill`, `designer.md` | `04-*.spec.ts`, `05-*.spec.ts` |
| **E2E-VIZ-01** | Visual audit - Asset pages | P2 | `playwright-skill`, `designer.md`, `ui-ux-pro-max` | `/app/assets/*` |
| **E2E-VIZ-02** | Visual audit - Run protocol pages | P2 | `playwright-skill`, `designer.md`, `ui-ux-pro-max` | `/app/run/*` |
| **E2E-VIZ-03** | Visual audit - Data & Playground | P2 | `playwright-skill`, `designer.md`, `ui-ux-pro-max` | `/app/data/*`, `/app/playground` |
| **E2E-VIZ-04** | Visual audit - Settings & Workcell | P2 | `playwright-skill`, `designer.md`, `ui-ux-pro-max` | `/app/settings/*`, `/app/workcell/*` |
| **JLITE-01** | Audit simulate-ghpages.sh structure | P1 | `investigator.md`, `recon.md` | 404 root cause |
| **JLITE-02** | Audit & fix theme CSS path doubling | P1 | `fixer.md`, `investigator.md` | Path resolution issue |
| **JLITE-03** | Fix Pyodide kernel auto-init | P1 | `fixer.md`, `investigator.md` | Kernel startup |
| **OPFS-01** | Audit protocol via Pyodide under OPFS | P2 | `investigator.md` | Pyodide integration |
| **OPFS-02** | Review asset instantiation under OPFS | P2 | `investigator.md`, `recon.md` | Asset CRUD |
| **OPFS-03** | Review hardware discovery under OPFS | P2 | `investigator.md`, `recon.md` | HW discovery service |

---

## System Prompts Used

| Agent Mode | Description | File |
|:-----------|:------------|:-----|
| **fixer.md** | Fast implementation specialist for well-defined changes | `.agent/agents/fixer.md` |
| **investigator.md** | Deep investigation and root cause analysis | `.agent/agents/investigator.md` |
| **designer.md** | Frontend UI/UX visual design evaluation | `.agent/agents/designer.md` |
| **recon.md** | Fast codebase search and navigation | `.agent/agents/recon.md` |

## Skills Injected

| Skill | Description | File |
|:------|:------------|:-----|
| **playwright-skill** | Complete browser automation and E2E testing | `.agent/skills/playwright-skill/SKILL.md` |
| **ui-ux-pro-max** | Visual quality criteria, 50 styles, accessibility | `.agent/skills/ui-ux-pro-max/SKILL.md` |
| **senior-architect** | System design patterns, modularization | `.agent/skills/senior-architect/SKILL.md` |

---

## Server Configuration

All E2E and visual audit tasks should use:

```bash
npm run start:browser
```

For JupyterLite GH-Pages simulation:

```bash
./scripts/simulate-ghpages.sh
```

---

## Review Strategy

### P1 Tasks (Review First)

1. E2E-AUDIT-01 - Coverage gap analysis informs other E2E work
2. E2E-RUN-01/02/03 - Fix broken tests before adding new ones
3. JLITE-01/02/03 - JupyterLite blockers

### P2 Tasks (Review Second)

1. E2E-VIZ-* - Visual findings feed design improvements
2. OPFS-* - Ensure migration is complete
3. SPLIT-* - Large refactors, careful merge needed
4. REFACTOR-* - Mechanical changes, likely auto-mergeable

---

## Dispatch Command

```bash
cd /Users/mar/Projects/praxis/.agent/tasks/jules_batch_20260123
chmod +x dispatch.sh

# Preview
./dispatch.sh --dry-run

# Dispatch all
./dispatch.sh

# Dispatch category
./dispatch.sh --filter "E2E"
./dispatch.sh --filter "JLITE"
```
