# Agent Prompt: 30_demo_to_browser_mode

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260109](./README.md)
**Backlog:** [ux_issues_260109.md](../../backlog/ux_issues_260109.md)

---

## Task

Eliminate "demo" terminology throughout the codebase. Rename the demo interceptor to browser-mode interceptor and update all related strings.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [demo.interceptor.ts](../../../praxis/web-client/src/app/core/interceptors/demo.interceptor.ts) | **PRIMARY TARGET** - Main interceptor file |
| [app.config.ts](../../../praxis/web-client/src/app/app.config.ts) | Interceptor registration |
| [mode.service.ts](../../../praxis/web-client/src/app/core/services/mode.service.ts) | Mode detection logic |
| [sqlite.service.ts](../../../praxis/web-client/src/app/core/services/sqlite.service.ts) | Demo data imports |

---

## Required Changes

### 1. Rename Interceptor File

```
demo.interceptor.ts → browser-mode.interceptor.ts
```

### 2. Rename Constants and Functions

```typescript
// Before
export const demoInterceptor = ...
function handleDemoRequest() ...

// After
export const browserModeInterceptor = ...
function handleBrowserModeRequest() ...
```

### 3. Update String Literals

| Current | Replace With |
|---------|--------------|
| `'Demo User'` | `'Local User'` |
| `'Demo Workcell'` | `'Default Workcell'` |
| `'demo@praxis.example'` | `'local@praxis.local'` |
| `'Opentrons OT-2 (Demo)'` | `'Opentrons OT-2 (Simulated)'` |
| `'Hamilton STAR (Demo)'` | `'Hamilton STAR (Simulated)'` |
| `'Demo mode - PLR definitions loaded'` | `'Browser mode - PLR definitions loaded'` |

### 4. Update app.config.ts Import

```typescript
// Before
import { demoInterceptor } from './core/interceptors/demo.interceptor';

// After
import { browserModeInterceptor } from './core/interceptors/browser-mode.interceptor';
```

### 5. Update mode.service.ts

Keep `browserMode` property but remove any `demo` terminology:

```typescript
// Ensure no references to 'demo' mode
// Replace env.demo checks with env.browserMode
```

### 6. Update Demo Data Folder (Optional)

Consider renaming:
```
src/assets/demo-data/ → src/assets/browser-data/
```

Or keep as-is since it's an internal implementation detail.

---

## Search Commands

```bash
# Find all "demo" references
grep -r "demo\|Demo\|DEMO" praxis/web-client/src/app --include="*.ts" | grep -v "node_modules"

# Find demo data imports
grep -r "demo-data" praxis/web-client/src/app --include="*.ts"
```

---

## Testing

1. Browser mode should still work after rename
2. No "Demo" text visible in UI (user names, workcell names, machine names)
3. All API interception still functions correctly

---

## On Completion

- [ ] File renamed: `demo.interceptor.ts` → `browser-mode.interceptor.ts`
- [ ] All constants/functions renamed
- [ ] All user-visible "Demo" strings replaced
- [ ] app.config.ts updated
- [ ] Browser mode still functional
- [ ] Update backlog status
- [ ] Mark this prompt complete in batch README

---

## References

- [ux_issues_260109.md](../../backlog/ux_issues_260109.md) - Section 8.1
- [browser_mode.md](../../backlog/browser_mode.md) - Browser mode architecture
