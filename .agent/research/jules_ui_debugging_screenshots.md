# Research: Jules UI Debugging - Playwright Screenshot Analysis

This document summarizes research findings on leveraging Playwright's screenshot and debugging capabilities to assist AI agents in debugging Angular UI failures.

## 1. Playwright Screenshot and Debugging Options

Playwright offers a robust set of features to capture test execution details, which are invaluable for debugging. These features can be configured in the `use` section of `playwright.config.ts`.

### 1.1. Screenshots

Screenshots provide a static image of the UI at a specific moment. They are essential for identifying visual bugs and understanding the state of the application at the time of a failure.

-   **`screenshot: 'on'`**: Captures a screenshot automatically whenever a test fails.
-   **`screenshot: 'only-on-failure'`**: An alias for `'on'`.
-   **`screenshot: 'off'`**: Disables automatic screenshots.
-   **Manual Screenshots**: `page.screenshot({ path: 'path/to/screenshot.png' })` can be called at any point to capture a screenshot. This is useful for capturing the UI at key points, even if the test doesn't fail.

### 1.2. Video Recording

Videos provide a dynamic view of the test execution, which is invaluable for understanding the context of a failure.

-   **`video: 'on'`**: Records a video for every test.
-   **`video: 'off'`**: Disables video recording.
-   **`video: 'retain-on-failure'`**: Records a video for every test, but deletes it if the test passes. **This is the recommended setting for CI environments.**
-   **`video: 'on-first-retry'`**: Records a video only when a test is retried.

### 1.3. Tracing

Tracing provides a comprehensive view of a test's execution, including screenshots, network requests, and console logs. The output is a `.zip` file that can be viewed in the Playwright Trace Viewer.

-   **`trace: 'on'`**: Records a trace for every test.
-   **`trace: 'off'`**: Disables tracing.
-   **`trace: 'on-first-retry'`**: Records a trace only when a test is retried. This is the current setting in `praxis/web-client/playwright.config.ts`.
-   **`trace: 'retain-on-failure'`**: Records a trace for every test, but deletes it if the test passes. **This is the recommended setting for CI environments.**

## 2. Recommendations for AI Agent Debugging

To effectively leverage these features for AI agent debugging, we recommend the following:

### Recommendation 1: Enable `'retain-on-failure'` for Video and Tracing

The current configuration only captures screenshots on failure and traces on the first retry. To provide the maximum context for debugging, we recommend enabling `'retain-on-failure'` for video and tracing. This will ensure that a complete record of the test execution is available for any test that fails, without cluttering the output with successful test runs.

```typescript
// playwright.config.ts
export default defineConfig({
  // ...
  use: {
    // ...
    screenshot: 'on', // Keep this as is
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },
});
```

### Recommendation 2: Standardize Artifact Paths and Naming

To make it easier for an agent to find and use the debugging artifacts, we recommend standardizing the output paths and using a consistent naming convention.

```typescript
// playwright.config.ts
export default defineConfig({
  // ...
  outputDir: 'e2e/test-results',
  // ...
});
```

By default, Playwright will save artifacts in the `outputDir` with the following naming convention:

-   **Screenshots**: `test-results/<test-name>-<retry>-<platform>.png`
-   **Videos**: `test-results/<test-name>-<retry>-<platform>.webm`
-   **Traces**: `test-results/<test-name>-<retry>-<platform>.zip`

### Recommendation 3: Attach Artifacts to Agent Prompts

When a test fails, the agent should be provided with the paths to the screenshot, video, and trace file. The paths to these artifacts are typically available in the test runner's output.

## 3. Best Format/Resolution for AI Visual Analysis

For AI visual analysis, the following are recommended:

-   **Format**: PNG is the preferred format for screenshots as it is a lossless format that preserves image quality.
-   **Resolution**: A resolution of 1920x1080 is recommended as it is a standard desktop resolution that will provide a clear view of the UI.

## 4. Using Trace Files

Playwright trace files are a powerful debugging tool that can provide a wealth of information to an agent. The trace viewer provides a timeline of the test execution, including screenshots, network requests, and console logs.

To use a trace file, an agent would need to:

1.  Be provided with the path to the `.zip` file.
2.  Be able to unzip the file.
3.  Be able to parse the contents of the trace file (e.g., `trace.json`, `network.json`, `console.json`).

Given the complexity of parsing the trace file, a simpler approach would be to provide the agent with a summary of the trace file's contents. However, for a more advanced agent, direct access to the trace file would be ideal.
