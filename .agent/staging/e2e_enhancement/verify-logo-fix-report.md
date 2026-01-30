# SDET Audit Report: verify-logo-fix.spec.ts

**File:** `praxis/web-client/e2e/specs/verify-logo-fix.spec.ts`  
**Audit Date:** 2026-01-30  
**Auditor:** Senior SDET Agent  
**Lines of Code:** 27

---

## 1. Test Scope & Coverage

### What is Tested

This test file verifies a **single, narrow concern**: the correct rendering of the application's logo by validating CSS custom properties (CSS variables) applied to the logo element.

**Functionality Verified:**
- Navigation to the Praxis application splash/shell page
- Presence of a logo element (`.logo-mark` or `.logo-image`)
- Correct application of the `--logo-svg` CSS custom property
- SVG data URI format integrity (must contain `data:image/svg+xml`)
- Security sanitization (must NOT contain `unsafe:` prefix)

**UI Elements Targeted:**
- `.logo-mark` (used in `SplashComponent`)
- `.logo-image` (used in `UnifiedShellComponent`)

### Key Assertions

| # | Assertion | Purpose |
|---|-----------|---------|
| 1 | `computedStyle.logoSvg` is not `'none'` | Confirms CSS variable is set and not default |
| 2 | `computedStyle.logoSvg` contains `url("data:image/svg+xml` | Validates correct SVG data URI format |
| 3 | `computedStyle.logoSvg` does NOT contain `'unsafe:'` | Confirms Angular's DomSanitizer bypass worked correctly |

---

## 2. Code Review & Best Practices (Static Analysis)

### 2.1 Critical Issues

| Issue | Severity | Location | Description |
|-------|----------|----------|-------------|
| **Hardcoded URL** | 🔴 High | Line 5 | Uses `http://localhost:8080/praxis/` instead of Playwright's `baseURL` configuration |
| **Deprecated Selector Pattern** | 🟡 Medium | Lines 8, 10 | Uses `waitForSelector` (deprecated) + CSS class selectors instead of user-facing locators |
| **Timeout Magic Number** | 🟡 Medium | Line 8 | Hardcoded `10000` timeout without constant or configuration |
| **No Test Isolation** | 🟡 Medium | N/A | No `beforeEach`/`afterEach` hooks for cleanup |
| **No Page Object Model** | 🟡 Medium | N/A | Inline locator logic without abstraction |

### 2.2 Modern Standards (2026)

#### User-Facing Locators Assessment

| Current | Recommended | Status |
|---------|-------------|--------|
| `page.waitForSelector('.logo-mark, .logo-image')` | `page.getByTestId('app-logo')` or `page.getByRole('img', { name: /praxis/i })` | ❌ Fails |
| `page.locator('.logo-mark, .logo-image').first()` | Same as above | ❌ Fails |

**Critique:** The test relies on internal CSS implementation details (`.logo-mark`, `.logo-image`) that are prone to change during refactoring. These are styling concerns, not semantic element identifiers.

#### Test Isolation

- **Cleanup:** ❌ No cleanup logic present
- **Side Effects:** ⚪ Minimal (read-only test, no mutations)
- **State Dependency:** ⚠️ Depends on app initial route rendering

#### Page Object Model (POM) Usage

- **Status:** ❌ Not used
- **Impact:** Low for a single-assertion regression test, but inconsistent with project conventions

#### Async Angular State Handling

- **App Ready Wait:** ❌ Uses generic `waitForSelector` instead of service-based readiness
- **Animation Consideration:** ❌ No consideration for Angular animations on logo fade-in
- **Signal-Based State:** ❌ No detection of Angular's `logoCssVar()` computed signal

### 2.3 Code Quality Metrics

| Metric | Score | Notes |
|--------|-------|-------|
| Readability | 7/10 | Clear intent, good console.log for debugging |
| Maintainability | 4/10 | Hardcoded values, no abstraction |
| Robustness | 3/10 | Brittle selectors, no retry logic |
| Standards Compliance | 3/10 | Violates multiple 2026 best practices |

---

## 3. Test Value & Classification

### Scenario Relevance

| Criterion | Assessment |
|-----------|------------|
| **User Journey?** | ❌ No. Users see the logo but don't interact with CSS variables |
| **Critical Path?** | 🟡 Partial. Branding is visible but not functional |
| **Regression Risk?** | ✅ Yes. Validates a specific bug fix related to Angular's DomSanitizer |
| **Business Value?** | 🟡 Low-Medium. Visual regression only |

**Classification:** This is a **Targeted Regression Test** for a specific bug fix, not a true user journey test.

### Test Classification Matrix

| Type | Match | Justification |
|------|-------|---------------|
| E2E Integration Test | ❌ No | No backend interaction, no full stack flow |
| Visual Regression Test | 🟡 Partial | Validates CSS but doesn't capture screenshots |
| Unit Test (in E2E container) | ✅ Yes | Tests a single component's CSS property |
| Smoke Test | ❌ No | Too narrow in scope |

**Verdict:** This is an **Interactive Unit Test** running in a browser context. It validates a single component's CSS variable application, which could be more efficiently tested with component-level testing (e.g., vitest + @angular/testing-library).

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

```
1. Navigate directly to http://localhost:8080/praxis/
   → This lands on the SplashComponent (unauthenticated) 
   → OR redirects to UnifiedShellComponent (browser mode)

2. Wait for logo element to appear in DOM (10s timeout)
   → Targets .logo-mark (SplashComponent) OR .logo-image (UnifiedShellComponent)

3. Use page.evaluate() to extract computed CSS properties
   → --logo-svg (CSS custom property)
   → mask-image / -webkit-mask-image (actual applied style)

4. Assert the CSS variable contains a valid, sanitized SVG data URI
   → Not 'none' (default)
   → Contains 'data:image/svg+xml' 
   → Does NOT contain 'unsafe:' (Angular security bypass)

5. Console.log the computed style for debugging
```

### Contextual Fit

The logo is a core branding element present in two locations:
1. **SplashComponent** (`src/app/features/splash/splash.component.ts`, line 47)
2. **UnifiedShellComponent** (`src/app/layout/unified-shell.component.ts`, line 42)

Both components use a Signal-based computed property (`logoCssVar()`) to safely inject an SVG data URI as a CSS custom property. The `unsafe:` prefix indicates Angular's DomSanitizer rejected the URL, which would break the logo rendering.

**Historical Context:** This test likely addresses a bug where the Angular compiler or runtime security checks interfered with inline SVG data URIs used for CSS masking.

---

## 5. Gap Analysis (Scientific & State Logic)

### 5.1 Missing Critical Paths

| Gap | Severity | Description |
|-----|----------|-------------|
| **No Visual Verification** | 🟡 Medium | Validates CSS variable but not actual pixel rendering |
| **No Cross-Route Coverage** | 🟡 Medium | Only tests one landing route; logo appears in multiple contexts |
| **No Theme Variation** | 🟠 Low | Logo gradient may differ in light/dark mode |
| **No Responsive Check** | 🟠 Low | Logo sizing behavior on mobile not tested |

### 5.2 Domain Specifics

#### Data Integrity

| Question | Status | Notes |
|----------|--------|-------|
| Is the SVG data validated? | 🟡 Partial | Checks format but not SVG content integrity |
| Is the logo path correct? | ❌ No | Doesn't verify the actual SVG paths match expected design |

#### Simulation vs. Reality

| Aspect | Status |
|--------|--------|
| Browser Mode Tested? | ✅ Implicitly (via /praxis/ route) |
| Production Mode Tested? | ❌ No (would require auth bypass) |
| Static Build Assets? | ❌ Not verified |

#### Serialization Verification

**N/A** - This test does not involve Pyodide worker communication or protocol serialization.

#### Error Handling

| Failure Scenario | Covered? |
|------------------|----------|
| Logo element not found | 🟡 Implicit (timeout failure) |
| CSS variable returns 'none' | ✅ Yes |
| `unsafe:` prefix present | ✅ Yes |
| Network failure loading logo | ❌ No (inline data URI) |
| Angular bootstrapping failure | ❌ No |
| DomSanitizer throws error | ❌ No |

---

## Aggregate Scoring

| Category | Score (0-10) | Weight | Weighted |
|----------|--------------|--------|----------|
| Test Scope | 3 | 20% | 0.6 |
| Best Practices | 3 | 25% | 0.75 |
| Test Value | 5 | 20% | 1.0 |
| Isolation | 6 | 15% | 0.9 |
| Domain Coverage | 2 | 20% | 0.4 |
| **TOTAL** | — | 100% | **3.65** |

**Classification:** 🔴 **Critical Failure** (Flaky/Low Coverage)

---

## Recommendations Summary

1. **Migrate to Component Testing:** This validation is better suited for `@angular/testing-library` or `vitest` with DOM rendering
2. **Add `data-testid`:** Add `data-testid="app-logo"` to both logo elements
3. **Use BaseURL:** Replace hardcoded URL with relative navigation
4. **Create LogoPOM:** Abstract logo locators into a Page Object
5. **Add Visual Regression:** Use `expect(page).toHaveScreenshot()` for pixel-perfect validation
6. **Extend Coverage:** Test logo across all entry points (splash, shell, login)
