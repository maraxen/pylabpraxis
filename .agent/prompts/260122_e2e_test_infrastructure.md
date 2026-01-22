# Agent Prompt: E2E Test Infrastructure with Screenshots

**Status:** 🟡 Not Started
**Priority:** P1 (Pre-Merge)
**Difficulty:** Medium
**Category:** Testing Infrastructure

---

## Overview

This is a **Recon-Plan-Feedback-Execute** workflow for setting up proper E2E test infrastructure with:

1. **Screenshots enabled** - Capture on every run for visual pipelines
2. **Error context preservation** - Save browser console, network logs
3. **Gitignored output directory** - Keep test artifacts out of commits
4. **Headless with list reporter** - For CI/agent execution

**CRITICAL REQUIREMENTS:**

- Playwright config must run **headless** by default
- Use **list reporter** (`--reporter=list`) for clean agent output
- **Screenshots MUST be taken** - Configure automatic screenshot capture
- All test artifacts saved to a **gitignored directory**

**CRITICAL:** Before proceeding to each subsequent phase, present your findings and await user approval.

---

## Phase 1: RECON

### Persona

Use the **Recon** persona for this phase.

### Objectives

1. **Find Current Playwright Config** - Locate and understand current setup
2. **Audit Existing Tests** - See what E2E tests exist
3. **Check .gitignore** - Verify or add test output directories
4. **Understand Current Screenshot Setup** - If any exists

### Search Targets

```bash
# Find Playwright config
find . -name "playwright.config.*" -type f
find . -name "playwright*" -type f

# Find existing E2E tests
find . -path "*e2e*" -name "*.spec.ts" -o -path "*e2e*" -name "*.test.ts"
ls -la praxis/web-client/e2e/ 2>/dev/null || echo "No e2e folder"

# Check gitignore for test artifacts
grep -r "screenshot\|test-results\|playwright" .gitignore

# Find any existing screenshot logic
grep -r "screenshot\|toHaveScreenshot" praxis/web-client/
```

### Files to Examine

| Path | Description |
|:-----|:------------|
| `praxis/web-client/playwright.config.ts` | Main config (if exists) |
| `praxis/web-client/e2e/` | Test directory |
| `.gitignore` | Global gitignore |
| `praxis/web-client/.gitignore` | Web client gitignore |

### Output Format

```xml
<recon_report>
<playwright_config>
  <location>[Path or "not found"]</location>
  <current_settings>
    <headless>[true|false|unset]</headless>
    <reporter>[current reporter config]</reporter>
    <screenshots>[current screenshot config]</screenshots>
    <output_dir>[current output directory]</output_dir>
  </current_settings>
</playwright_config>

<existing_tests>
  <count>[N tests found]</count>
  <locations>
    <test path="[path]">[Brief description]</test>
  </locations>
</existing_tests>

<gitignore_status>
  <test_results_ignored>[true|false]</test_results_ignored>
  <screenshots_ignored>[true|false]</screenshots_ignored>
  <suggested_additions>[Patterns to add]</suggested_additions>
</gitignore_status>

<current_screenshot_behavior>
  [Description of current screenshot handling if any]
</current_screenshot_behavior>
</recon_report>
```

### Gate 1

**STOP HERE.** Present your recon report and await approval.

---

## Phase 2: PLAN

### Persona

Use the **Oracle** persona for this phase.

### Skills to Reference

- `playwright-skill/SKILL.md` - For Playwright best practices
- `webapp-testing/SKILL.md` - For testing patterns

### Objectives

1. **Configure Playwright for Agent Execution**
   - Headless by default
   - List reporter for clean output
   - Automatic screenshots (set to `on` for pipelines)

2. **Set Up Artifact Directory Structure**

   ```
   test-results/          # Gitignored
   ├── screenshots/       # Failure screenshots
   ├── traces/            # Playwright traces
   └── reports/           # Test reports
   ```

3. **Update .gitignore**

4. **Create Test Utility Helpers** (if needed)

### Playwright Config Requirements

```typescript
// playwright.config.ts - Required settings
export default defineConfig({
  // REQUIRED: Headless for CI/agent execution
  use: {
    headless: true,
    
    // REQUIRED: Screenshots for visual pipelines (even on success)
    screenshot: 'on',
    
    // Optional: Video on failure for debugging
    video: 'retain-on-failure',
    
    // Trace for debugging
    trace: 'retain-on-failure',
  },
  
  // REQUIRED: List reporter for agent-friendly output
  reporter: [
    ['list'],
    ['html', { outputFolder: 'test-results/reports' }]
  ],
  
  // REQUIRED: Output to gitignored directory
  outputDir: 'test-results',
});
```

### Agent Instructions for Screenshot Capture

**IMPORTANT:** When executing tests, agents MUST:

1. Run tests with: `npx playwright test --reporter=list`
2. If tests fail, screenshots will be in `test-results/`
3. Always check `test-results/screenshots/` after failures
4. Include screenshot paths in failure reports

### Output Format

```xml
<plan_summary>
<config_changes>
  <file path="playwright.config.ts">
    <change>[Specific change]</change>
  </file>
</config_changes>

<directory_structure>
  test-results/
    screenshots/
    traces/
    reports/
</directory_structure>

<gitignore_additions>
  <pattern>[Pattern to add]</pattern>
</gitignore_additions>

<agent_instructions>
  [Clear instructions for agents running tests]
</agent_instructions>
</plan_summary>
```

### Gate 2

**STOP HERE.** Present your plan and await approval.

---

## Phase 3: EXECUTE

### Persona

Use the **Fixer** persona for this phase.

### Skills to Reference

- `playwright-skill/SKILL.md` - Playwright implementation
- `verification-before-completion/SKILL.md` - Verify setup works

### Execution Checklist

1. [ ] Update/create `playwright.config.ts`
   - Set `headless: true`
   - Set `screenshot: 'on'` (for visual pipelines)
   - Set reporter to `list`
   - Set `outputDir: 'test-results'`

2. [ ] Create directory structure
   - `mkdir -p test-results/screenshots test-results/traces test-results/reports`

3. [ ] Update `.gitignore`
   - Add `test-results/`
   - Add any other test artifact patterns

4. [ ] Run a test to verify screenshot capture
   - Intentionally fail a test
   - Confirm screenshot was captured
   - Confirm it's in the correct directory

5. [ ] Document for agents

### Verification Commands

```bash
# Verify config exists and is valid
cat praxis/web-client/playwright.config.ts

# Run tests with list reporter
cd praxis/web-client && npx playwright test --reporter=list

# Check that test-results is created
ls -la test-results/

# Verify gitignore
grep "test-results" .gitignore
```

### Test Verification

Create a temporary failing test to verify screenshot capture:

```typescript
// e2e/screenshot-test.spec.ts (temporary)
import { test, expect } from '@playwright/test';

test('verify screenshot capture works', async ({ page }) => {
  await page.goto('/');
  // This will fail and trigger screenshot
  await expect(page.locator('h1')).toHaveText('INTENTIONAL FAILURE FOR TESTING');
});
```

Run, verify screenshot exists, then delete the test file.

### Output Format

```xml
<execution_report>
<config_changes>
  <file path="playwright.config.ts" status="created|modified">
    [Summary of changes]
  </file>
</config_changes>

<gitignore_updated>
  <additions>
    <pattern>test-results/</pattern>
  </additions>
</gitignore_updated>

<verification>
  <screenshot_capture_works>[true|false]</screenshot_capture_works>
  <screenshot_location>[Path where screenshot was saved]</screenshot_location>
  <list_reporter_works>[true|false]</list_reporter_works>
  <headless_works>[true|false]</headless_works>
</verification>

<agent_workflow>
  # How agents should run tests:
  cd praxis/web-client
  npx playwright test --reporter=list
  
  # On failure, check:
  ls test-results/screenshots/
  
  # Include screenshot paths in failure reports
</agent_workflow>

<summary>
[Overall status]
</summary>
</execution_report>
```

---

## Context & References

**Playwright Best Practices for CI:**

```typescript
// Recommended playwright.config.ts structure
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'test-results/reports' }],
  ],
  
  outputDir: 'test-results',
  
  use: {
    headless: true,
    screenshot: 'on',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
    baseURL: 'http://localhost:4200',
  },
  
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  
  webServer: {
    command: 'npm run start:browser',
    url: 'http://localhost:4200',
    reuseExistingServer: !process.env.CI,
  },
});
```

**Gitignore Patterns:**

```gitignore
# Playwright test artifacts
test-results/
playwright-report/
playwright/.cache/
```

---

## On Completion

- [ ] Playwright config updated with headless, list reporter, screenshots
- [ ] test-results/ directory structure created
- [ ] .gitignore updated
- [ ] Verified screenshot capture works
- [ ] Verified list reporter output is clean
- [ ] Documentation for agents created
- [ ] Changes committed

---

## References

- `.agent/skills/playwright-skill/SKILL.md` - Playwright patterns
- `.agent/skills/webapp-testing/SKILL.md` - Testing patterns
- <https://playwright.dev/docs/test-configuration>
