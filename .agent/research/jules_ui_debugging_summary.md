# Jules UI Debugging Research - Executive Summary

**Date**: 2026-01-23  
**Sessions**: 5 parallel research investigations  
**Objective**: Determine the best way to set up Jules for UI debugging in E2E testing

---

## 🎯 Key Findings

### 1. Screenshot & Artifact Strategy (Session 11419599189273601124)

**Current State**:

- Screenshots: `on` (capture on failure) ✅
- Video: Not enabled ❌
- Trace: `on-first-retry` (only on retry) ⚠️

**Recommendations**:

1. **Enable `video: 'retain-on-failure'`** - Provides temporal context that static screenshots miss
2. **Change `trace: 'retain-on-failure'`** - Trace files contain screenshots, network, console logs in one `.zip`
3. **Standardize output**: Use `outputDir: 'e2e/test-results'` for predictable artifact paths
4. **Format/Resolution**: PNG at 1920x1080 for optimal AI visual analysis

**Playwright Config Changes**:

```typescript
export default defineConfig({
  outputDir: 'e2e/test-results',
  use: {
    screenshot: 'on',
    video: 'retain-on-failure',        // NEW
    trace: 'retain-on-failure',        // CHANGED from 'on-first-retry'
  },
});
```

---

### 2. DOM Snapshot Extraction (Session 6111085162851566240)

**Three Approaches Evaluated**:

| Format | Best For | Pros | Cons |
|--------|----------|------|------|
| **Limited HTML** | Human inspection | Complete DOM details | Verbose, hard to parse |
| **Accessibility Tree** | **AI analysis** ⭐ | Structured, semantic, focused on interactions | May miss styling/layout |
| **Selector Tree** | Middle ground | More concise than HTML | Custom implementation |

**Winner**: **Accessibility Tree** (`page.accessibility.snapshot()`)

- Structured semantic representation
- Easy for AI to parse and reason about
- Focuses on user-interactable elements

**Implementation**:

```typescript
// praxis/web-client/e2e/utils/dom-snapshot.ts
export async function getAccessibilityTree(page: Page, selector?: string) {
  const target = selector ? page.locator(selector).first() : page.locator('body').first();
  if (await target.count() > 0) {
    return await page.accessibility.snapshot({ 
      root: target.elementHandle() ?? undefined 
    });
  }
  return null;
}
```

**Smart Root Selection**:

- Prioritize `mat-dialog-container` (where failures often happen)
- Fall back to `body` if no dialog present

---

### 3. Error Context Aggregation (Session 15734123070030868127)

**Proposed Schema** for `error-context.md`:

```markdown
# Test Failure Context

## Test Information
- **Test**: {test suite} > {test name}
- **Status**: {failed/timedOut/interrupted}
- **Duration**: {ms}
- **Timestamp**: {ISO 8601}

## Screenshot
![Failure Screenshot]({relative/path/to/screenshot.png})

## DOM Snapshot
```json
{accessibility tree or selector tree}
```

## Console Logs

{filtered console messages}

## Network Requests

{failed requests or suspicious activity}

## Playwright Trace

Trace file: {path/to/trace.zip}
View: npx playwright show-trace {path}

```

**Implementation Strategy**:
Create a **custom Playwright reporter** that auto-generates `error-context.md` on test failure by:
1. Collecting screenshot path from `testInfo.attachments`
2. Running `getAccessibilityTree()` in `afterEach` hook
3. Filtering console logs for errors/warnings
4. Capturing failed network requests
5. Linking to trace file

---

### 4. Live Server Requirements (Session 14698875562686202009)

**Key Decision**: **Use `npm run start:browser`** (not Docker)

**Rationale**:
- Simpler: No container management overhead
- Faster: Direct ng serve startup
- Flexible: Easy port configuration

**Playwright `webServer` Config**:
```typescript
export default defineConfig({
  webServer: {
    command: 'npm run start:browser',
    url: 'http://localhost:4200',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,  // 2min for Angular compilation
  },
});
```

**Port Conflict Handling**:

- Use `reuseExistingServer: true` in local dev
- Kill existing servers in CI: `kill $(lsof -t -i :4200) || true`

---

### 5. Prototype Testing (Session 1636396114364386573)

**Test Executed**: `04-browser-persistence.spec.ts`

**Critical Discovery**: 🚨 **"Welcome to Praxis" dialog blocks UI interactions**

**Root Cause**:

- Dialog overlay intercepts button clicks
- `app.fixture.ts` attempts to dismiss but logic is unreliable
- Causes test timeouts ("Timeout 30000ms exceeded")

**Artifacts Generated**:

- ✅ Screenshot: `test-results/{test-name}/test-failed-1.png`
- ✅ Error Context: `test-results/{test-name}/error-context.md` (with DOM snapshot)
- ❌ Console logs: Not captured in artifact bundle

**3 Specific Gaps Identified**:

1. **No console log persistence** - Console output lost after test run
2. **Unreliable dialog dismissal** - Needs robust `beforeEach` logic with retry
3. **Screenshot not attached to error output** - Path shown but image not in prompt context

---

## 🛠️ Recommended Implementation Plan

### Phase 1: Enhance Playwright Config (30 min)

- [ ] Enable `video: 'retain-on-failure'`
- [ ] Change `trace: 'retain-on-failure'`
- [ ] Standardize `outputDir: 'e2e/test-results'`

### Phase 2: Create DOM Snapshot Utilities (45 min)

- [ ] Implement `praxis/web-client/e2e/utils/dom-snapshot.ts`
- [ ] Add `getAccessibilityTree()`, `getLimitedHTML()`, `getSelectorTree()`
- [ ] Integrate into `app.fixture.ts` `afterEach` hook

### Phase 3: Build Custom Reporter (1-2 hours)

- [ ] Create `praxis/web-client/e2e/reporters/error-context-reporter.ts`
- [ ] Auto-generate `error-context.md` on failure
- [ ] Include screenshot, DOM, console, network, trace link

### Phase 4: Fix Welcome Dialog Issue (30 min)

- [ ] Strengthen `app.fixture.ts` dismissal logic
- [ ] Add retry mechanism for dialog detection
- [ ] Ensure CDK overlays fully clear before tests start

---

## 📊 Success Metrics

After implementation, Jules should be able to:

1. ✅ Access failure screenshots without file system navigation
2. ✅ Parse accessibility tree to understand UI state
3. ✅ Review console errors and network failures
4. ✅ Diagnose UI blocking issues (overlays, animations)
5. ✅ Propose fixes based on comprehensive error context

---

## 🔥 Immediate Next Steps

**High Priority**:

1. Fix "Welcome to Praxis" dialog blocking in `app.fixture.ts`
2. Implement accessibility tree snapshot in `afterEach` hook
3. Enable video recording for temporal context

**Medium Priority**:
4. Build custom error context reporter
5. Document Jules dispatch template for UI debugging tasks

---

## 📝 Lessons Learned

- **Jules `.agent/` Unreliability**: Jules struggles with `.agent/` directory edits (path duplication, persistence failures). Use `/tmp` or main codebase for Jules-generated artifacts, then manually move.
- **Accessibility Tree > Raw HTML**: For AI analysis, structured semantic data beats verbose markup.
- **Trace Files are Gold**: A single `.zip` contains everything (screenshots, network, console, timeline).
