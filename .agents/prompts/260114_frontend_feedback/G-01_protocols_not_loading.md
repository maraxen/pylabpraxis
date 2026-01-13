# Agent Prompt: G-01 Protocols Not Loading Investigation

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260114_frontend_feedback](./README.md)
**Difficulty:** Medium
**Type:** 🔴 Investigation
**Dependencies:** None
**Backlog Reference:** [GROUP_G_documentation_init.md](./GROUP_G_documentation_init.md)

---

## 1. The Task

**User Feedback:**
> "No protocols showing up"

**Console Error (from Vite):**

```
[vite] http proxy error: /api/v1/protocols/definitions?limit=100
AggregateError [ECONNREFUSED]:
    at internalConnectMultiple (node:net:1139:18)
    at afterConnectMultiple (node:net:1714:7)
```

**Goal:** Diagnose why protocols aren't loading in browser mode. The error suggests API requests are being proxied instead of intercepted.

## 2. Initial Analysis (From Reconnaissance)

The browser-mode interceptor at `praxis/web-client/src/app/core/interceptors/browser-mode.interceptor.ts` **should** handle protocol loading:

```typescript
// Line 23-24
if (url.includes('/protocols/definitions') && method === 'GET') {
    return sqliteService.getProtocols();
}
```

The interceptor returns data from `SqliteService.getProtocols()` which reads from the local SQLite database.

**Hypothesis:** The interceptor is not being triggered. Possible causes:

1. `ModeService.isBrowserMode()` returning false when it should be true
2. Request URL not matching the expected pattern
3. Interceptor not registered in provider chain
4. Vite proxy intercepting before Angular HTTP client

## 3. Technical Investigation Strategy

### Phase 1: Verify Interceptor Registration

Check if the browser-mode interceptor is properly registered:

| Path | What to Check |
|:-----|:--------------|
| `praxis/web-client/src/app/app.config.ts` | Verify `provideHttpClient(withInterceptors([...browserModeInterceptor]))` |
| `praxis/web-client/src/main.ts` | Check bootstrap configuration |

### Phase 2: Verify Mode Detection

| Path | What to Check |
|:-----|:--------------|
| `praxis/web-client/src/app/core/services/mode.service.ts` | Verify `isBrowserMode()` logic |
| `praxis/web-client/src/environments/environment.ts` | Check environment flags |

### Phase 3: Verify SQLite Service

| Path | What to Check |
|:-----|:--------------|
| `praxis/web-client/src/app/core/services/sqlite.service.ts` | Verify `getProtocols()` method (line 931+) |
| `praxis/web-client/src/assets/browser-db/praxis.db` | Confirm database file exists |

### Phase 4: Check Vite Proxy Configuration

| Path | What to Check |
|:-----|:--------------|
| `praxis/web-client/vite.config.ts` | Check if `/api` proxy is too aggressive |
| `praxis/web-client/package.json` | Verify `start:browser` script |

## 4. Debugging Steps

Add console logging to diagnose:

```typescript
// In browser-mode.interceptor.ts
export const browserModeInterceptor = (...) => {
    const modeService = inject(ModeService);
    console.log('[BrowserModeInterceptor] isBrowserMode:', modeService.isBrowserMode());
    console.log('[BrowserModeInterceptor] Request URL:', req.url);
    
    if (!modeService.isBrowserMode()) {
        console.log('[BrowserModeInterceptor] SKIPPING - not browser mode');
        return next(req);
    }
    // ...
};
```

## 5. Context & References

**Primary Files to Investigate:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/core/interceptors/browser-mode.interceptor.ts` | The interceptor that should handle protocol requests |
| `praxis/web-client/src/app/core/services/mode.service.ts` | Mode detection logic |
| `praxis/web-client/src/app/core/services/sqlite.service.ts` | SQLite data access (line 931: `getProtocols()`) |
| `praxis/web-client/src/app/app.config.ts` | HTTP client configuration |

**Reference Files:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/vite.config.ts` | Vite dev server configuration |
| `praxis/web-client/src/environments/environment.ts` | Environment settings |

## 6. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **Browser Mode**: Application runs entirely client-side with SQLite WASM
- **Do not modify production behavior**: Only fix browser-mode specific issues

## 7. Verification Plan

**Definition of Done:**

1. Root cause identified and documented
2. Fix implemented OR escalation documented with findings
3. Protocols load correctly in browser mode

**Debug Commands:**

```bash
cd praxis/web-client
npm run start:browser
# Open browser console and navigate to Protocols tab
# Check console for interceptor logs
```

**Expected Behavior:**

- Console shows `[BrowserModeInterceptor] isBrowserMode: true`
- No proxy errors in terminal
- Protocol table displays loaded protocols

---

## On Completion

- [ ] Document root cause in this file
- [ ] Implement fix if possible OR create follow-up prompt for fix
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `TECHNICAL_DEBT.md` - Known issues
