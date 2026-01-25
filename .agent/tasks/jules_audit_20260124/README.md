# Jules Audit Batch - 2026-01-24

GH-Pages shipping readiness audit campaign.

## Quick Start

1. **Run Test Suite First** (CLI/Antigravity):

   ```bash
   # Start browser server in one terminal
   cd /Users/mar/Projects/praxis/praxis/web-client && npm run start:browser
   
   # Run tests in another
   cd /Users/mar/Projects/praxis/praxis/web-client
   timeout 600 npx playwright test --reporter=list 2>&1 | tee /tmp/playwright-results.txt | head -500
   ```

2. **Dispatch Jules Audits**:
   Use prompts in `prompts/AUDIT-*.md` to dispatch to Jules.

## Tasks

| ID | Target | Description |
|:---|:-------|:------------|
| TEST-RUN-01 | CLI | Run Playwright suite, report failures |
| AUDIT-01 | Jules | Run Protocol & Wizard audit |
| AUDIT-02 | Jules | Asset Management audit |
| AUDIT-03 | Jules | Protocol Library & Execution audit |
| AUDIT-04 | Jules | Playground & Data Viz audit |
| AUDIT-05 | Jules | Workcell Dashboard audit |
| AUDIT-06 | Jules | Browser Persistence audit |
| AUDIT-07 | Jules | JupyterLite Integration audit |
| AUDIT-08 | Jules | GH-Pages Config audit |

## Output Location

All audit reports: `/docs/audits/AUDIT-{NN}-{name}.md`

## Key Rules

- **System Prompt**: `general` for audits, `none` for test run
- **Skills**: `playwright-skill`, `systematic-debugging`
- **DO NOT**: Fix code, create tests, debug issues
- **DO**: Document gaps, recommend tests, identify blockers
