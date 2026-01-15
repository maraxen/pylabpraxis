# Frontend Health Audit

**Last Updated**: YYYY-MM-DD  
**Auditor**: [Agent/Human]  
**Overall Status**: 🟢 Healthy | 🟡 Needs Attention | 🔴 Critical Issues

---

## Quick Summary

| Category | Status | Issues | Notes |
| :--- | :--- | :--- | :--- |
| Linting (ESLint) | 🟢/🟡/🔴 | 0 | |
| Type Checking (tsc) | 🟢/🟡/🔴 | 0 | |
| Unit Tests (Vitest) | 🟢/🟡/🔴 | 0 passed, 0 failed, 0 skipped | |
| E2E Tests (Playwright) | 🟢/🟡/🔴 | 0 passed, 0 failed, 0 skipped | |
| Build | 🟢/🟡/🔴 | 0 | |

---

## Linting Issues

**Command**: `cd praxis/web-client && npm run lint`  
**Status**: 🟢/🟡/🔴

### Summary

[Brief description of linting state]

### Outstanding Issues

| File | Rule | Description | Priority |
| :--- | :--- | :--- | :--- |
| `path/to/file.ts` | `@typescript-eslint/no-explicit-any` | Explicit any | Low |

### Configuration Notes

[Any relevant eslint.config.js configurations, ignored rules, etc.]

---

## Type Checking Issues

**Command**: `cd praxis/web-client && npx tsc --noEmit`  
**Status**: 🟢/🟡/🔴

### Summary

[Brief description of type checking state]

### Outstanding Issues

| File | Error | Description | Priority |
| :--- | :--- | :--- | :--- |
| `path/to/file.ts` | `TS2322` | Type mismatch | Medium |

### Configuration Notes

[Any tsconfig.json configurations, type definitions needed, etc.]

---

## Unit Test Failures

**Command**: `cd praxis/web-client && npm test`  
**Status**: 🟢/🟡/🔴

### Summary

- **Passed**: 0
- **Failed**: 0
- **Skipped**: 0
- **Errors**: 0

### Failing Tests

| Test | Error Type | Description | Priority |
| :--- | :--- | :--- | :--- |
| `component.spec.ts` | `Error` | Brief description | High |

### Skipped Tests

| Test | Reason | Action Needed |
| :--- | :--- | :--- |
| `service.spec.ts` | Pending implementation | Complete feature |

---

## E2E Test Failures

**Command**: `cd praxis/web-client && npx playwright test`  
**Status**: 🟢/🟡/🔴

### Summary

- **Passed**: 0
- **Failed**: 0
- **Skipped**: 0

### Failing Tests

| Test | Error Type | Description | Priority |
| :--- | :--- | :--- | :--- |
| `assets.spec.ts` | `Timeout` | Element not found | High |

---

## Build Issues

**Command**: `cd praxis/web-client && npm run build`  
**Status**: 🟢/🟡/🔴

### Summary

[Any build warnings or errors]

---

## Other Audits

| Audit Type | Last Run | Status | Notes |
| :--- | :--- | :--- | :--- |
| **Accessibility** | YYYY-MM-DD | 🟢/🟡/🔴 | [a11y issues found] |
| **Bundle Size** | YYYY-MM-DD | 🟢/🟡/🔴 | [Size metrics] |
| **Dead Code** | YYYY-MM-DD | 🟢/🟡/🔴 | [Unused components/services] |
| **TODO Audit** | YYYY-MM-DD | 🟢/🟡/🔴 | [TODOs found, migrated to tech debt] |

---

## Action Items

### High Priority

- [ ] Fix failing E2E tests
- [ ] Resolve build errors

### Medium Priority

- [ ] Address type errors
- [ ] Fix accessibility issues

### Low Priority

- [ ] Clean up linting warnings
- [ ] Reduce bundle size

---

## Audit History

| Date | Auditor | Changes |
| :--- | :--- | :--- |
| YYYY-MM-DD | Agent | Initial audit |

---

## Notes

[Any additional context, Angular-specific issues, browser compatibility notes, etc.]
