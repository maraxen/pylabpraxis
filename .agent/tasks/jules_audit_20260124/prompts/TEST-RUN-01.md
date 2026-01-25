# TEST-RUN-01: Run Full Playwright E2E Suite

## Target

**CLI / Antigravity**

## System Prompt

`none`

## Skills

none

---

## Objective

Run the complete Playwright E2E test suite and collect results. **DO NOT debug or fix any failures** - only document them.

## Prerequisites

```bash
cd /Users/mar/Projects/praxis/praxis/web-client
npm run start:browser  # Must be running in another terminal
```

## Commands

```bash
cd /Users/mar/Projects/praxis/praxis/web-client
timeout 600 npx playwright test --reporter=list 2>&1 | tee /tmp/playwright-results.txt | head -500
```

## Expected Output Format

Provide a structured failure report:

### Summary

- Total tests: {N}
- Passed: {N}
- Failed: {N}
- Skipped: {N}

### Failing Tests

| Test Name | File | Error Category |
|:----------|:-----|:---------------|
| {test name} | {file path} | timeout / assertion / element-not-found / other |

### Notes

- Any tests that are flaky (sometimes pass/fail)
- Any tests that timeout consistently
- Overall health assessment

---

## IMPORTANT

> ⚠️ **DO NOT** attempt to fix or debug any failures  
> ⚠️ **DO NOT** modify any test files  
> ⚠️ **ONLY** collect and categorize the results  
> ⚠️ Save full output to `/tmp/playwright-results.txt`
