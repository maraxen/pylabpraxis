# CSS Hardcode Audit Report - 2026-01-09

## Summary

- **Total hardcoded values found**: ~2,654
- **Critical (colors/theme)**: ~525 (Hex: 217, RGB: 215, Names: 93)
- **Medium (spacing/sizing)**: ~1,599
- **Low (typography/misc)**: ~530 (Typography: 351, Radius: 179)

## Findings by Category

### 1. Hardcoded Colors (Priority: P1)

Hardcoded colors break dark/light mode switching and theme consistency.

**Examples:**

| File | Context | Value | Should Be |
|------|---------|-------|-----------|
| `praxis/web-client/src/app/core/components/command-palette/command-palette.component.ts` | `background-color` | `#ED7A9B` (in var fallback) | `var(--mat-sys-primary)` |
| `praxis/web-client/src/app/layout/unified-shell.component.ts` | `border-color` | `#4caf50` | `var(--mat-sys-success)` or `text-green-500` |
| `praxis/web-client/src/app/layout/unified-shell.component.ts` | `color` | `#f44336` | `var(--mat-sys-error)` or `text-red-500` |
| `praxis/web-client/src/app/features/splash/splash.component.ts` | `background` | `linear-gradient(..., #d85a7f)` | Theme gradient token |
| `praxis/web-client/src/app/layout/main-layout.component.ts` | `background` | `rgba(30, 30, 45, 0.6)` | `var(--mat-sys-surface-variant)` with opacity |
| `praxis/web-client/src/app/core/components/command-palette/command-palette.component.ts` | `box-shadow` | `rgba(0, 0, 0, 0.5)` | Shadow token / `shadow-lg` |
| `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts` | `color` | `white` | `var(--mat-sys-on-primary)` |

**Note**: Many matches for "white" are properly used in Tailwind classes (e.g., `text-white`), but usage in `.ts` styles or inline styles should be reviewed.

### 2. Hardcoded Spacing & Sizing (Priority: P2)

Hardcoded pixels for layout make responsiveness difficult and violate the grid system.

**Examples:**

| File | Context | Value | Should Be |
|------|---------|-------|-----------|
| `praxis/web-client/src/app/core/components/command-palette/command-palette.component.ts` | `width` | `600px` | `max-w-3xl` or `w-full` |
| `praxis/web-client/src/app/core/components/command-palette/command-palette.component.ts` | `padding` | `16px` | `p-4` or `var(--spacing-4)` |
| `praxis/web-client/src/app/core/components/command-palette/command-palette.component.ts` | `gap` | `12px` | `gap-3` |
| `praxis/web-client/src/app/layout/main-layout.component.ts` | `width` | `72px` | `w-[72px]` (if strict) or standard size |
| `praxis/web-client/src/app/layout/main-layout.component.ts` | `padding` | `32px` | `p-8` |

### 3. Hardcoded Border Radius (Priority: P2)

Inconsistent corner rounding.

**Examples:**

| File | Context | Value | Should Be |
|------|---------|-------|-----------|
| `praxis/web-client/src/app/core/components/command-palette/command-palette.component.ts` | `border-radius` | `12px` | `rounded-xl` / `var(--mat-sys-corner-large)` |
| `praxis/web-client/src/app/core/components/command-palette/command-palette.component.ts` | `border-radius` | `4px` | `rounded` / `var(--mat-sys-corner-small)` |
| `praxis/web-client/src/app/layout/unified-shell.component.ts` | `border-radius` | `50%` | `rounded-full` |

### 4. Hardcoded Typography (Priority: P3)

Fixed font sizes bypass user scaling preferences and theme consistency.

**Examples:**

| File | Context | Value | Should Be |
|------|---------|-------|-----------|
| `praxis/web-client/src/app/core/components/command-palette/command-palette.component.ts` | `font-size` | `1.1rem` | `text-lg` |
| `praxis/web-client/src/app/core/components/command-palette/command-palette.component.ts` | `font-size` | `0.75rem` | `text-xs` |
| `praxis/web-client/src/app/layout/main-layout.component.ts` | `font-size` | `32px` | `text-4xl` |
| `praxis/web-client/src/app/layout/main-layout.component.ts` | `font-size` | `11px` | `text-[11px]` or `text-xs` |

## Remediation Plan & Priority

1. **Phase 1: Critical Color Fixes (P1)**
    - **Goal**: Ensure all colors respond to theme changes (dark/light mode).
    - **Action**: Replace hex/rgb values in `unified-shell.component.ts`, `command-palette.component.ts` (styles), and `main-layout.component.ts` with explicit CSS variables (`var(--mat-sys-...)`) or Tailwind utility classes.
    - **Effort**: High (requires testing dark mode for each change).

2. **Phase 2: Standardization of Shape & Spacing (P2)**
    - **Goal**: Align components with the design system grid and roundedness.
    - **Action**: Replace `border-radius` with Tailwind `rounded-*` classes. Replace `padding`/`margin` pixel values with Tailwind `p-*`/`m-*` classes.
    - **Focus Areas**: `command-palette`, `main-layout`, `protocol-card`.
    - **Effort**: Medium (mostly mechanical replacements).

3. **Phase 3: Typography Cleanup (P3)**
    - **Goal**: Use semantic typography scales.
    - **Action**: Replace `font-size` with Tailwind `text-*` classes.
    - **Effort**: Low.

## Files Requiring Changes (Top Offenders)

1. `praxis/web-client/src/app/core/components/command-palette/command-palette.component.ts` (Heavy inline styles)
2. `praxis/web-client/src/app/layout/main-layout.component.ts`
3. `praxis/web-client/src/app/layout/unified-shell.component.ts`
4. `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts`
5. `praxis/web-client/src/app/features/auth/login.component.ts`

## Next Steps

- [ ] Create task to refactor `command-palette.component.ts` styles to CSS/SCSS file or Tailwind classes.
- [ ] Create task to tokenize `main-layout.component.ts`.
