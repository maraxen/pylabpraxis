# STYLE-01: Theme Variables in protocol-summary

## Context

**File**: `praxis/web-client/src/app/features/run-protocol/components/protocol-summary/protocol-summary.component.ts`
**Issue**: Uses hardcoded Tailwind color classes instead of theme variables

## Requirements

Replace Tailwind color classes with CSS theme variables:

| Find | Replace With |
|------|--------------|
| `bg-green-500/10` | `var(--theme-status-success-muted)` |
| `text-green-500` | `var(--theme-status-success)` |
| `border-green-500/20` | `var(--theme-status-success-border)` |
| `text-red-500` | `var(--status-error)` |
| `bg-red-500/10` | `var(--theme-status-error-muted)` |

For inline template styles, update like:

```typescript
// Before
class="bg-green-500/10 text-green-500"

// After
[style.background-color]="'var(--theme-status-success-muted)'"
[style.color]="'var(--theme-status-success)'"
```

Or use a CSS class if available.

Do NOT:

- Add new theme variables (use existing ones)
- Modify component logic
- Change any functionality

## Acceptance Criteria

- [ ] All Tailwind color classes replaced
- [ ] Component renders correctly
- [ ] Both light and dark themes work
- [ ] No TypeScript errors
