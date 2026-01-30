# Improvement Plan: verify-logo-fix.spec.ts

**Source Report:** `verify-logo-fix-report.md`  
**Current Score:** 3.65 / 10 (Critical Failure)  
**Target Score:** 7.5+ (Production Grade)

---

## Executive Summary

The `verify-logo-fix.spec.ts` test is a narrow regression test for a specific Angular DomSanitizer bug fix. While it serves its purpose of catching the `unsafe:` prefix issue, it violates multiple modern E2E best practices and provides minimal confidence in the overall logo rendering experience.

**Recommendation:** This test should be **refactored into the component testing layer** (vitest) and **supplemented with visual regression testing** in E2E.

---

## Phase 1: Critical Fixes (Score Target: 5.0)

### 1.1 Remove Hardcoded URL

**Current (Line 5):**
```typescript
await page.goto('http://localhost:8080/praxis/');
```

**Improved:**
```typescript
// Uses baseURL from playwright.config.ts
await page.goto('/', { waitUntil: 'domcontentloaded' });
```

**Rationale:** The hardcoded URL breaks CI/CD flexibility and ignores subdirectory configuration.

### 1.2 Replace Deprecated waitForSelector

**Current (Line 8):**
```typescript
await page.waitForSelector('.logo-mark, .logo-image', { timeout: 10000 });
```

**Improved:**
```typescript
const logo = page.getByTestId('app-logo');
await expect(logo).toBeVisible({ timeout: 15000 });
```

**Prerequisite:** Add `data-testid="app-logo"` to both logo elements in the components.

### 1.3 Add Test ID to Components

**SplashComponent (src/app/features/splash/splash.component.ts, line 47):**
```typescript
// Before
<div class="logo-mark" [style]="logoCssVar()"></div>

// After
<div class="logo-mark" data-testid="app-logo" [style]="logoCssVar()"></div>
```

**UnifiedShellComponent (src/app/layout/unified-shell.component.ts, line 42):**
```typescript
// Before
<div class="logo-image" [style]="logoCssVar()"></div>

// After
<div class="logo-image" data-testid="app-logo" [style]="logoCssVar()"></div>
```

---

## Phase 2: Best Practice Alignment (Score Target: 6.5)

### 2.1 Create Page Object Model

**New file: `e2e/pages/logo.po.ts`**
```typescript
import { Page, Locator, expect } from '@playwright/test';

export class LogoPageObject {
  private readonly page: Page;
  readonly logoElement: Locator;

  constructor(page: Page) {
    this.page = page;
    this.logoElement = page.getByTestId('app-logo');
  }

  async waitForLogoVisible(timeout = 15000): Promise<void> {
    await expect(this.logoElement).toBeVisible({ timeout });
  }

  async getLogoSvgCssVariable(): Promise<string> {
    return this.logoElement.evaluate((el) => {
      const style = window.getComputedStyle(el);
      return style.getPropertyValue('--logo-svg');
    });
  }

  async getMaskImage(): Promise<string> {
    return this.logoElement.evaluate((el) => {
      const style = window.getComputedStyle(el);
      return style.getPropertyValue('mask-image') || 
             style.getPropertyValue('-webkit-mask-image');
    });
  }

  async assertLogoRenderedCorrectly(): Promise<void> {
    const logoSvg = await this.getLogoSvgCssVariable();
    
    // 1. CSS variable is not default
    expect(logoSvg).not.toBe('none');
    expect(logoSvg).not.toBe('');
    
    // 2. Valid SVG data URI format
    expect(logoSvg).toContain('url("data:image/svg+xml');
    
    // 3. Not marked as unsafe by Angular
    expect(logoSvg).not.toContain('unsafe:');
  }
}
```

### 2.2 Refactor Test to Use POM

**Refactored: `verify-logo-fix.spec.ts`**
```typescript
import { test, expect } from '@playwright/test';
import { LogoPageObject } from '../pages/logo.po';

test.describe('Logo Rendering Verification', () => {
  let logo: LogoPageObject;

  test.beforeEach(async ({ page }) => {
    logo = new LogoPageObject(page);
  });

  test('logo displays with correct CSS variable on splash page', async ({ page }) => {
    await page.goto('/');
    await logo.waitForLogoVisible();
    await logo.assertLogoRenderedCorrectly();
  });

  test('logo displays with correct CSS variable in app shell', async ({ page }) => {
    await page.goto('/app/home');
    await logo.waitForLogoVisible();
    await logo.assertLogoRenderedCorrectly();
  });
});
```

---

## Phase 3: Expand Coverage (Score Target: 7.5)

### 3.1 Add Visual Regression Testing

**Add visual snapshot test:**
```typescript
test('logo renders correctly (visual)', async ({ page }) => {
  await page.goto('/');
  await logo.waitForLogoVisible();
  
  // Capture logo-specific screenshot
  await expect(logo.logoElement).toHaveScreenshot('splash-logo.png', {
    maxDiffPixelRatio: 0.01,
  });
});
```

### 3.2 Test Theme Variations

```typescript
test.describe('Logo Theme Variants', () => {
  test('logo renders in light theme', async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.setItem('theme', 'light'));
    await page.reload();
    await logo.waitForLogoVisible();
    await logo.assertLogoRenderedCorrectly();
  });

  test('logo renders in dark theme', async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.setItem('theme', 'dark'));
    await page.reload();
    await logo.waitForLogoVisible();
    await logo.assertLogoRenderedCorrectly();
  });
});
```

### 3.3 Test Multiple Entry Points

```typescript
const entryPoints = [
  { name: 'Splash', route: '/' },
  { name: 'Login', route: '/login' },
  { name: 'App Shell', route: '/app/home' },
];

for (const entry of entryPoints) {
  test(`logo renders on ${entry.name} page`, async ({ page }) => {
    await page.goto(entry.route);
    await logo.waitForLogoVisible();
    await logo.assertLogoRenderedCorrectly();
  });
}
```

---

## Phase 4: Migrate to Component Testing (Long-term)

### 4.1 Create Vitest Component Test

**New file: `src/app/shared/logo/logo.component.spec.ts`**
```typescript
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/angular';
import { LogoComponent } from './logo.component';

describe('LogoComponent', () => {
  it('should set --logo-svg CSS variable with valid data URI', async () => {
    const { container } = await render(LogoComponent);
    const logoEl = container.querySelector('[data-testid="app-logo"]');
    
    const style = window.getComputedStyle(logoEl!);
    const logoSvg = style.getPropertyValue('--logo-svg');
    
    expect(logoSvg).not.toBe('none');
    expect(logoSvg).toContain('data:image/svg+xml');
    expect(logoSvg).not.toContain('unsafe:');
  });
});
```

### 4.2 Deprecate E2E Test After Migration

Once the component test is in place, the E2E test can be reduced to a minimal smoke check:

```typescript
test('logo is visible on app load', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('app-logo')).toBeVisible();
});
```

---

## Implementation Checklist

| Task | Priority | Effort | Assignee |
|------|----------|--------|----------|
| Add `data-testid="app-logo"` to components | 🔴 High | 15 min | — |
| Remove hardcoded URL | 🔴 High | 5 min | — |
| Create `LogoPageObject` | 🟡 Medium | 30 min | — |
| Refactor test to use POM | 🟡 Medium | 20 min | — |
| Add theme variation tests | 🟠 Low | 30 min | — |
| Add visual regression snapshot | 🟠 Low | 20 min | — |
| Create vitest component test | 🟢 Future | 1 hr | — |
| Update KI artifact | 🟢 Future | 15 min | — |

---

## Expected Outcomes

| Metric | Before | After |
|--------|--------|-------|
| Test Scope Score | 3 | 7 |
| Best Practices Score | 3 | 8 |
| Test Value Score | 5 | 7 |
| Isolation Score | 6 | 8 |
| Domain Coverage Score | 2 | 6 |
| **Aggregate Score** | **3.65** | **7.2** |

---

## Files to Modify

1. `e2e/specs/verify-logo-fix.spec.ts` — Refactor
2. `e2e/pages/logo.po.ts` — Create new
3. `src/app/features/splash/splash.component.ts` — Add testid
4. `src/app/layout/unified-shell.component.ts` — Add testid
5. `src/app/shared/logo/logo.component.spec.ts` — Create new (optional)
