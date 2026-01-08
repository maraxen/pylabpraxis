# Maintenance Prompts

Reusable prompts for recurring repository health checks and maintenance tasks.

---

## Overview

These prompts are designed for periodic execution. Run them as part of regular health audits or when specific issues are detected.

**All prompts follow a standardized four-phase workflow:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Phase 1: Triage                                                 │
│   • Run checks on backend and/or frontend                       │
│   • Capture output to log files                                 │
│   • Use tail to get counts (limit context flooding)             │
│   • Prioritize: fewest issues first                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase 2: Categorize & Strategize                                │
│   • Coarse-grained inspection (head -n 100)                     │
│   • Categorize issues by type                                   │
│   • Document fix strategy                                       │
│   • ⏸️  PAUSE: Get user input before proceeding                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase 3: Apply Fixes                                            │
│   • Execute following documented strategy                       │
│   • For tests: target specific files (no full runs)             │
│   • For manual audits: work through files systematically        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase 4: Verify & Document                                      │
│   • Verify with quiet/summary flags                             │
│   • Update health audit file                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Available Prompts

| Prompt | Purpose | Target | Frequency |
|:-------|:--------|:-------|:----------|
| [linting.md](linting.md) | Ruff (Python) / ESLint (TS) resolution | Both | Per-audit |
| [type_checking.md](type_checking.md) | Pyright (Python) / tsc (TS) resolution | Both | Per-audit |
| [test_coverage.md](test_coverage.md) | Testing coverage analysis | Both | Per-audit |
| [docstring_audit.md](docstring_audit.md) | Docstring standardization | Backend | Per-audit |
| [todo_audit.md](todo_audit.md) | Migrate TODOs to tech debt | Both | Per-audit |
| [ci_review.md](ci_review.md) | CI pipeline health check | Both | Quarterly |
| [docs_audit.md](docs_audit.md) | Documentation completeness | Both | Quarterly |
| [dependency_audit.md](dependency_audit.md) | Dependency freshness/security | Both | Quarterly |
| [security_audit.md](security_audit.md) | Basic security review | Both | Quarterly |
| [performance_audit.md](performance_audit.md) | Performance regression checks | Both | As needed |
| [dead_code_cleanup.md](dead_code_cleanup.md) | Unused code, deprecated features | Both | Quarterly |
| [dry_audit.md](dry_audit.md) | Identify repeated code/logic | Both | Quarterly |

---

## Usage

### Full Health Audit

Execute all per-audit prompts:

```
Run health audit:
1. linting.md (backend then frontend)
2. type_checking.md
3. test_coverage.md
4. docstring_audit.md
5. todo_audit.md
```

### Quarterly Review

Add quarterly prompts:

```
6. ci_review.md
7. docs_audit.md
8. dependency_audit.md
9. security_audit.md
10. dead_code_cleanup.md
11. dry_audit.md
```

---

## Key Principles

1. **Limit context flooding**: Use `tail` for summaries, `head -n N` for review
2. **Fewest-first prioritization**: Build momentum with quick wins
3. **Pause for feedback**: Always get user approval before Phase 3
4. **Targeted execution**: During fixes, avoid codebase-wide runs
5. **Document before executing**: Strategy should be clear before changes

---

## Tech Stack Reference

| Layer | Linting | Type Check | Tests |
|:------|:--------|:-----------|:------|
| Backend | `uv run ruff check praxis/backend` | `uv run pyright praxis/backend` | `uv run pytest tests/` |
| Frontend | `npm run lint` | `npx tsc --noEmit` | `npm test` (unit) / `npx playwright test` (e2e) |
