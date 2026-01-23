import { defineConfig, devices } from '@playwright/test';

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  globalSetup: require.resolve('./e2e/global-setup'),
  timeout: 60000,
  testDir: './e2e/specs',
  outputDir: 'test-results/',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: 'list',
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:4200',

    /* Collect trace on failure - provides comprehensive debugging context */
    trace: 'retain-on-failure',

    /* Record video on failure - helps visualize timing and interaction issues */
    video: 'retain-on-failure',

    /* Force Headless Mode */
    headless: true,

    /* Capture screenshot on all tests for visual debugging */
    screenshot: 'on',

    /* Standardized viewport for consistent AI-parseable screenshots */
    viewport: { width: 1920, height: 1080 },
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        headless: true
      },
    }
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run start:browser -- --port 4200',
    url: 'http://localhost:4200',
    reuseExistingServer: true,
    timeout: 180000,
  },
});
