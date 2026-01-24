# Jules Batch Dispatch - 2026-01-23

Bulk dispatch of autonomous tasks to Jules for overnight processing.

## Dispatch Categories

| Category | Count | Description |
|:---------|:------|:------------|
| **REFACTOR** | 3 | Convert relative imports to @ aliases |
| **SPLIT** | 6 | Decompose large files into modular components |
| **E2E-AUDIT** | 1 | Audit E2E coverage gaps |
| **E2E-NEW** | 3 | Create new E2E tests for uncovered paths |
| **E2E-RUN** | 3 | Run and fix existing E2E tests |
| **E2E-VIZ** | 4 | Visual audit via screenshot analysis |
| **JLITE** | 3 | JupyterLite GH-Pages issue resolution |
| **OPFS** | 3 | OPFS migration review and validation |
| **TOTAL** | **26** | All dispatches |

## Directory Structure

```
jules_batch_20260123/
├── README.md           # This file
├── dispatch.sh         # Automated dispatch script
├── dispatch_log.md     # Session IDs and status (generated)
└── prompts/            # Individual task prompts
    ├── REFACTOR-01.md
    ├── REFACTOR-02.md
    └── ...
```

## Usage

```bash
# Preview what will be dispatched
./dispatch.sh --dry-run

# Dispatch all tasks
./dispatch.sh

# Dispatch specific category
./dispatch.sh --filter "REFACTOR"
```

## After Dispatch

1. Session IDs logged to `dispatch_log.md`
2. Review high-priority sessions first (P1)
3. Use `/jules-morning-checkin` workflow for results
