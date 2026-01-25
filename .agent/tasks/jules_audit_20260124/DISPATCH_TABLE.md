# Jules Audit Dispatch Table - 2026-01-24

## Overview

| Category | Count | Target | Priority |
|:---------|:------|:-------|:---------|
| **TEST-RUN** (test execution) | 1 | CLI/Antigravity | P1 |
| **AUDIT** (component audits) | 9 | Jules | P1 |
| **TOTAL** | **10** | | |

---

## Complete Task List

| ID | Title | Priority | Target | System Prompt | Skills |
|:---|:------|:---------|:-------|:--------------|:-------|
| **TEST-RUN-01** | Run Full Playwright Suite | P1 | CLI | `none` | none |
| **AUDIT-01** | Run Protocol & Wizard Audit | P1 | Jules | `general` | `playwright-skill`, `systematic-debugging` |
| **AUDIT-02** | Asset Management Audit | P1 | Jules | `general` | `playwright-skill`, `systematic-debugging` |
| **AUDIT-03** | Protocol Library & Execution Audit | P1 | Jules | `general` | `playwright-skill`, `systematic-debugging` |
| **AUDIT-04** | Playground & Data Viz Audit | P1 | Jules | `general` | `playwright-skill`, `systematic-debugging` |
| **AUDIT-05** | Workcell Dashboard Audit | P1 | Jules | `general` | `playwright-skill`, `systematic-debugging` |
| **AUDIT-06** | Browser Persistence Audit | P1 | Jules | `general` | `playwright-skill`, `systematic-debugging` |
| **AUDIT-07** | JupyterLite Integration Audit | P1 | Jules | `general` | `playwright-skill`, `systematic-debugging` |
| **AUDIT-08** | GH-Pages Config Audit | P1 | Jules | `general` | `playwright-skill`, `systematic-debugging` |
| **AUDIT-09** | Direct Control Interface Audit | P1 | Jules | `general` | `playwright-skill`, `systematic-debugging` |

---

## Session Tracking

| ID | Session ID | Status | Report Created |
|:---|:-----------|:-------|:---------------|
| TEST-RUN-01 | | blocked | build errors |
| AUDIT-01 | | pending | |
| AUDIT-02 | | pending | |
| AUDIT-03 | | pending | |
| AUDIT-04 | | pending | |
| AUDIT-05 | | pending | |
| AUDIT-06 | | pending | |
| AUDIT-07 | | pending | |
| AUDIT-08 | | pending | |
| AUDIT-09 | | pending | |

---

## Important Notes

1. **No Debugging**: Agents should DOCUMENT issues, not fix them
2. **No Test Creation**: Agents should RECOMMEND tests, not write them
3. **Output Location**: All audit reports go to `/docs/audits/AUDIT-{NN}-{name}.md`
4. **Server Mode**: Use `npm run start:browser` for all browser testing

## ⚠️ Build Errors Blocking Tests

See [/docs/audits/BUILD_ERRORS.md](../../../docs/audits/BUILD_ERRORS.md) for details.
