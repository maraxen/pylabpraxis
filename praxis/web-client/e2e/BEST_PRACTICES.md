# Playwright + Angular E2E Best Practices (2026 Edition)

This document outlines modern best practices for end-to-end testing of Angular applications using Playwright, specifically optimized for **Angular 19+ (Standalone, Signals, Zoneless)**.

---

## 1. Angular Stability & Waiting Logic

Traditionally, E2E tools (like Protractor) waited for `Zone.js` to become stable. With the move toward **Zoneless Angular** and **Signals**, detecting "stability" is harder and often less reliable than "Web-First" assertions.

### The "Web-First" Approach
Instead of waiting for the framework to be stable, wait for the **UI state** to be correct. Playwright handles this automatically with **Auto-waiting**.

```typescript
// ❌ Avoid low-level stability detection if possible
await page.waitForFunction(() => window.angularReady); 

// ✅ Preferred: Wait for the expected UI change
await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
```

### Handling Readiness Markers
For apps with heavy initialization (like SQLite Wasm in Praxis), use a custom readiness marker injected into the window.

```typescript
// in base.page.ts
async waitForAppReady() {
    await this.page.waitForFunction(() => {
        const service = (window as any).sqliteService;
        return service?.isReady$?.getValue() === true;
    }, { timeout: 30000 });
}
```

### Handling @defer & Lazy Loading
Modern Angular uses `@defer` for lazy loading components. Playwright's auto-waiting naturally handles this, but you can be explicit to avoid race conditions.

```typescript
// Wait for the placeholder to disappear OR the deferred content to appear
const deferredContent = page.getByTestId('lazy-component');
await expect(deferredContent).toBeVisible({ timeout: 10000 });
```

---

## 2. Selector Strategies for Material Components

Material Design (Angular Material) uses complex DOM structures. Avoid CSS selectors like `.mat-mdc-select-value`. Use **Aria Roles** and **Test IDs**.

### Material Select (`mat-select`)
The options for a select menu are usually rendered in a **CDK overlay**, not as children of the component.

```typescript
async selectOption(label: string, optionText: string) {
    // 1. Click the select trigger
    await this.page.getByLabel(label).click();
    
    // 2. Locate the option in the overlay (role="option")
    const option = this.page.getByRole('option', { name: optionText });
    await option.click();
    
    // 3. Verify it's closed
    await expect(option).not.toBeVisible();
}
```

### Material Dialog (`mat-dialog`)
Always scope your locators to the dialog to avoid finding elements in the background.

```typescript
const dialog = page.getByRole('dialog');
await expect(dialog).toBeVisible();
await dialog.getByRole('button', { name: 'Confirm' }).click();
```

---

## 3. Wait & Synchronization Patterns

### Avoid `waitForTimeout`
Hardcoded sleeps (e.g., `await page.waitForTimeout(1000)`) are the primary cause of flaky tests.

### Better Alternatives:
1.  **State-driven Waiting**: `await expect(locator).toBeEnabled()`.
2.  **Navigation Waiting**: `await page.waitForURL('**/dashboard')`.
3.  **Network Activity**: `await page.waitForLoadState('networkidle')` (use sparingly for SPAs with many background requests).

---

## 4. API & Network Mocking

Playwright’s `page.route()` is the standard for mocking API calls. This is more reliable than framework-level interceptors for E2E.

```typescript
test('should handle API failure', async ({ page }) => {
    // Intercept and return 500
    await page.route('**/api/v1/assets', async route => {
        await route.fulfill({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Internal Server Error' })
        });
    });

    await page.goto('/assets');
    await expect(page.getByText('Failed to load assets')).toBeVisible();
});
```

---

## 5. Test Isolation & State Management

Each test should be a **"Clean Slate"**.

### Database Reset (Praxis Pattern)
Use query parameters to trigger a database reset on the backend during navigation.
```typescript
await page.goto('/?resetdb=1&mode=browser');
```

### Injecting State via `addInitScript`
Use this to set `localStorage` or `sessionStorage` flags **before** any scripts run on the page.

```typescript
test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem('onboarding_complete', 'true');
        window.localStorage.setItem('theme', 'dark');
    });
});
```

---

## 6. Modern Tracing & Debugging

2026 E2E best practices emphasize **Observability**.

- **Tracing**: Always enable `trace: 'on-first-retry'` in `playwright.config.ts`. It provides a full post-mortem of the test run at [trace.playwright.dev](https://trace.playwright.dev).
- **Video**: Record video for failing tests to see exact animation glitches.
- **UI Mode**: Run tests with `npx playwright test --ui` for a live-reloading inspector.

---

## Summary Checklist for 2026

| Area | Practice |
| :--- | :--- |
| **Locators** | Use `getByRole` and `getByTestId`. Avoid `.mat-` CSS classes. |
| **Waiting** | Trust Playwright's auto-waiting. Use `expect` assertions. |
| **Material** | Handle overlays (Select, Dialog, Menu) as global roles. |
| **Mocking** | Use `page.route` for isolated edge-case testing. |
| **Clean Slate** | Reset DB and clear Storage in `beforeEach`. |
