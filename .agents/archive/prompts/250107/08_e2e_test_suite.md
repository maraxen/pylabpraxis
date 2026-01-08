# Prompt: E2E Test Suite (Playwright)

**Priority**: P2 (High)
**Backlog**: [quality_assurance.md](../../backlog/quality_assurance.md)

## Context

We need a robust E2E test suite to verify critical user flows, especially for "Browser Mode" where logic differs significantly from "Server Mode". We have chosen **Playwright** as the primary tool.

## Objective

Implement a core set of Playwright tests covering the following scenarios:

### 1. First-Time User Experience (Lite Mode)

- Verify the "Welcome" splash screen or tutorial appears for new users.
- Ensure the app initializes the SQLite database correctly in IndexDB.

### 2. Asset Management Flow

- **Create**: Add a new machine and a new resource.
- **Read**: Verify they appear in the Registry and Inventory tabs.
- **Update**: Edit asset metadata (name, tags).
- **Delete**: Remove an asset and ensure it's gone from the UI.

### 3. Protocol Execution Flow

- Select a protocol from the list.
- Navigate through parameters and deck setup (if applicable).
- Start execution and verify the "Execution Monitor" displays status changes.
- Verify completion or cancellation works as expected.

### 4. Browser Mode Specifics

- Export the database, delete local storage, import the database, and verify data persistence.
- Test hardware authorization mocks for "Simulated" devices.

## Requirements

- Use `npx playwright test` for execution.
- Tests should be written in TypeScript.
- Define reusable page objects in `praxis/web-client/e2e/page-objects/`.
- Ensure tests run against the `npm run dev` server.
- Coverage should include both Light and Dark themes.

## Verification

- All tests must pass consistently across Chromium, Firefox, and WebKit.
- Generate a summary report showing 0 failures.
