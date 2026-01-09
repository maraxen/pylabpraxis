# Agent Prompt: 36_css_hardcode_audit

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260109](./README.md)
**Backlog:** [ux_issues_260109.md](../../backlog/ux_issues_260109.md)

---

## Task

Audit the codebase for hardcoded CSS values that should use design system variables, and create a remediation plan.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [styles.scss](../../../praxis/web-client/src/styles.scss) | Global styles |
| [theme.scss](../../../praxis/web-client/src/theme.scss) | Theme definitions |
| [aria-select.scss](../../../praxis/web-client/src/styles/aria-select.scss) | ARIA component styles |

---

## Audit Categories

### 1. Color Values

Search for hardcoded colors that should use CSS variables:

```bash
# Hardcoded hex colors
grep -r "#[0-9a-fA-F]\{3,6\}" praxis/web-client/src/app --include="*.ts" --include="*.scss"

# Hardcoded RGB/RGBA
grep -r "rgb\|rgba" praxis/web-client/src/app --include="*.ts" --include="*.scss"

# Common hardcoded grays
grep -r "gray-\|grey-\|#fff\|#000\|white\|black" praxis/web-client/src/app --include="*.ts"
```

**Should Use**:
- `var(--mat-sys-primary)` - Primary color
- `var(--mat-sys-surface)` - Surface background
- `var(--mat-sys-on-surface)` - Surface text
- `var(--mat-sys-outline)` - Borders
- Tailwind classes: `text-gray-400`, `bg-gray-800`, etc.

### 2. Spacing Values

Search for hardcoded pixel values:

```bash
# Hardcoded spacing
grep -r "[0-9]\+px" praxis/web-client/src/app --include="*.ts" --include="*.scss" | grep -v "node_modules"
```

**Should Use**:
- Tailwind spacing: `p-4`, `m-2`, `gap-4`
- Or CSS variables if defined in theme

### 3. Typography

Search for hardcoded font sizes:

```bash
grep -r "font-size\|text-\[" praxis/web-client/src/app --include="*.ts"
```

**Should Use**:
- Tailwind typography: `text-sm`, `text-lg`, `font-semibold`
- Material typography classes

### 4. Border Radius

```bash
grep -r "border-radius\|rounded-\[" praxis/web-client/src/app --include="*.ts"
```

**Should Use**:
- Tailwind: `rounded`, `rounded-lg`, `rounded-xl`
- `var(--mat-sys-corner-medium)` for Material consistency

---

## Audit Report Format

Create audit report at `.agents/reports/css_audit_260109.md`:

```markdown
# CSS Hardcode Audit Report - 2026-01-09

## Summary
- Total hardcoded values found: X
- Critical (colors/theme): Y
- Medium (spacing): Z
- Low (misc): W

## Findings by Category

### 1. Hardcoded Colors
| File | Line | Value | Should Be |
|------|------|-------|-----------|
| component.ts | 45 | #3b82f6 | var(--mat-sys-primary) |
| ... | ... | ... | ... |

### 2. Hardcoded Spacing
...

### 3. Hardcoded Typography
...
```

---

## Remediation Priority

1. **P1 - Theme Breaking**: Colors that don't work in dark/light mode
2. **P2 - Inconsistent**: Values that differ from design system
3. **P3 - Technical Debt**: Values that work but should use variables

---

## Exclusions

- Third-party library styles
- SVG paths and canvas drawing
- Tailwind utility classes (already design-system-aligned)
- Inline styles for dynamic calculations

---

## Deliverables

1. Audit report with all findings
2. List of files requiring changes
3. Estimated effort for remediation
4. Prioritized fix order

---

## On Completion

- [ ] Audit complete
- [ ] Report generated at `.agents/reports/css_audit_260109.md`
- [ ] Findings categorized by priority
- [ ] Update backlog status
- [ ] Mark this prompt complete in batch README

---

## References

- [ux_issues_260109.md](../../backlog/ux_issues_260109.md) - Section 8.2
- [codestyles/html-css.md](../../codestyles/html-css.md) - CSS conventions
