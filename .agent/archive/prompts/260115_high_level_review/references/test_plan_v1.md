# Interaction Test Plan V1

**Objective**: Expand Playwright coverage to include "High-Value" interactions that critical user flows rely on, specifically focusing on runtime controls, visualization, and error handling which are currently under-tested.

## 1. Configuration Changes

**Goal**: Enforce Headless Chromium as the primary test environment to reduce flake and improve speed.

#### Updated `playwright.config.ts` Snippet

```typescript
import { defineConfig, devices } from '@playwright/test';

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  globalSetup: require.resolve('./e2e/global-setup'),
  timeout: 60000,
  testDir: './e2e/specs',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: 'html',
  
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:4200',

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
    
    /* Force Headless Mode */
    headless: true,
    
    /* Capture screenshot on failure */
    screenshot: 'only-on-failure',
  },

  /* Configure projects for major browsers - RESTRICTED TO CHROMIUM */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run start:browser -- --port 4200',
    url: 'http://localhost:4200',
    reuseExistingServer: true,
    timeout: 180000,
  },
});
```

## 2. Directory Structure

We will introduce a dedicated `interactions` directory within `specs` to distinguish these deep interaction tests from the high-level "User Journeys" (which are often happy-path only).

```text
praxis/web-client/e2e/specs/
├── 01-onboarding.spec.ts         (Existing)
├── 02-asset-management.spec.ts   (Existing)
├── 03-protocol-execution.spec.ts (Existing)
├── interactions/                 (NEW)
│   ├── 01-execution-controls.spec.ts
│   ├── 02-deck-view.spec.ts
│   ├── 03-asset-forms.spec.ts
│   └── 04-error-handling.spec.ts
```

## 3. High-Value Test Scenarios

These scenarios fill the gaps identified in `02` and `03` specs.

### A. Execution Controls (`interactions/01-execution-controls.spec.ts`)

1. **Pause and Resume**:
    * **Action**: Start a simulated protocol. Click "Pause".
    * **Verify**: Status changes to "PAUSED". "Resume" button becomes active.
    * **Action**: Click "Resume".
    * **Verify**: Status changes back to "RUNNING".
2. **Emergency Stop / Abort**:
    * **Action**: Start protocol. Click "Abort" (or Stop).
    * **Verify**: Dialog confirmation appears. Confirm. Status changes to "ABORTED" or "CANCELLED".

### B. Deck View Interaction (`interactions/02-deck-view.spec.ts`)

3. **Labware Hover & Click**:
    * **Pre-condition**: Run a protocol with known labware layout.
    * **Action**: Hover over a plate on the Deck Map.
    * **Verify**: Tooltip or highlight indicates the labware name.
    * **Action**: Click the plate.
    * **Verify**: A detail panel or modal opens showing well status (e.g., "96 wells").

### C. Asset Form Logic (`interactions/03-asset-forms.spec.ts`)

4. **Machine IP Validation**:
    * **Action**: Open "Add Machine". Enter invalid IP (e.g., `999.999.999`).
    * **Verify**: "Save" button is disabled or validation error is shown.
2. **Duplicate Resource Prevention**:
    * **Action**: Create a resource named "Ethanol". Try to create another "Ethanol".
    * **Verify**: Error message "Resource name must be unique" appears.

### D. Error Handling & Resilience (`interactions/04-error-handling.spec.ts`)

6. **Backend Disconnect Simulation**:
    * **Action**: (Mock) Simulate a 500 error on a critical API call.
    * **Verify**: Application shows a user-friendly Snackbar/Toast ("Server Error") rather than crashing or freezing.
2. **Navigation Resilience**:
    * **Action**: Start execution. Navigate to "Settings" tab. Navigate back to "Monitor".
    * **Verify**: Execution state is still visible and live (not reset to empty).

### E. Advanced Filtering

8. **Asset List Filtering**:
    * **Action**: Have 10 items in inventory. Type a search term matching only 1.
    * **Verify**: List filters to show exactly 1 item. Clear search -> show 10 items.
