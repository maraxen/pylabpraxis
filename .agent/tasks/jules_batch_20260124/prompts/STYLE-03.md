# STYLE-03: Theme Variables in Settings

## Context

**File**: `praxis/web-client/src/app/features/settings/settings.component.ts`
**Issue**: Uses hardcoded Tailwind color classes instead of theme variables

## Requirements

Replace Tailwind color classes with CSS theme variables:

| Find | Replace With |
|------|--------------|
| `text-green-600` | `var(--theme-status-success)` |
| `dark:text-green-400` | (remove, theme handles dark mode automatically) |
| `text-gray-500` | `var(--theme-text-secondary)` |
| `text-gray-400` | `var(--theme-text-tertiary)` |

For template inline styles:

```typescript
// Before
class="text-green-600 dark:text-green-400"

// After
[style.color]="'var(--theme-status-success)'"
```

Note: CSS variables automatically adapt to dark/light mode via the theme system, so `dark:` prefixes become unnecessary.

Do NOT:

- Add new theme variables
- Modify settings logic or form controls
- Change any functionality or validation

## Acceptance Criteria

- [ ] All Tailwind color classes replaced
- [ ] Settings page renders correctly
- [ ] Both light and dark themes display properly
- [ ] No TypeScript errors
- [ ] Settings functionality unchanged
