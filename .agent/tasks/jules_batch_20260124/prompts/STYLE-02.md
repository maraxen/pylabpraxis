# STYLE-02: Theme Variables in live-dashboard

## Context

**File**: `praxis/web-client/src/app/features/run-protocol/components/live-dashboard/live-dashboard.component.ts`
**Issue**: Uses hardcoded Tailwind color classes instead of theme variables

## Requirements

Replace Tailwind color classes with CSS theme variables:

| Find | Replace With |
|------|--------------|
| `text-green-600` | `var(--theme-status-success)` |
| `text-gray-400` | `var(--theme-text-tertiary)` |
| `bg-green-100` | `var(--theme-status-success-muted)` |
| `bg-red-100` | `var(--theme-status-error-muted)` |
| `bg-gray-900` | `var(--mat-sys-surface-container)` |
| `text-gray-500` | `var(--theme-text-secondary)` |
| `dark:text-green-400` | (remove, theme handles dark mode) |

For template inline styles:

```typescript
// Before
class="text-green-600"

// After  
[style.color]="'var(--theme-status-success)'"
```

Do NOT:

- Add new theme variables
- Modify dashboard logic
- Change any functionality

## Acceptance Criteria

- [ ] All Tailwind color classes replaced
- [ ] Component renders correctly in light mode
- [ ] Component renders correctly in dark mode
- [ ] No TypeScript errors
