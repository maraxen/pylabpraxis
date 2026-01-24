# E2E-VIZ-01: Visual Audit - Asset Pages

## Context

**Routes**: `/app/assets/*`
**Goal**: Capture screenshots, analyze UI quality, report findings

## Skill Integration

This task uses the following skills in tandem:

- `playwright-skill` - Screenshot capture
- `ui-ux-pro-max` - Visual quality criteria
- `designer.md` - Design evaluation

## Requirements

### Phase 1: Screenshot Capture

Capture full-page screenshots at 1920x1080:

1. `/app/assets` - Asset list view
2. Asset creation wizard (each step)
3. Asset detail view
4. Edit mode
5. Empty state (if testable)
6. Error state (if testable)

```typescript
// Example capture script
const viewports = [
  { width: 1920, height: 1080, name: 'desktop' },
  { width: 768, height: 1024, name: 'tablet' },
  { width: 375, height: 667, name: 'mobile' }
];

for (const vp of viewports) {
  await page.setViewportSize(vp);
  await page.screenshot({ 
    path: `/tmp/assets-${vp.name}.png`,
    fullPage: true 
  });
}
```

### Phase 2: Visual Analysis

For each screenshot, evaluate:

**From ui-ux-pro-max checklist:**

- [ ] No emoji icons (use SVG)
- [ ] Hover states don't cause layout shift
- [ ] `cursor-pointer` on clickables
- [ ] Sufficient contrast (4.5:1 minimum)
- [ ] Consistent spacing and max-width
- [ ] Floating elements properly spaced

**From designer.md:**

- [ ] Typography hierarchy clear
- [ ] Color system reinforces usability
- [ ] Micro-interactions present
- [ ] Mobile-first responsive

### Phase 3: Report

Create `visual-audit-assets.md`:

```markdown
# Visual Audit: Asset Pages

## Screenshots
- [x] Asset list (desktop)
- [x] Asset list (mobile)
...

## Findings

### Critical (Must Fix)
1. **Issue**: Low contrast on disabled buttons
   **Location**: Asset wizard, step 2
   **Screenshot**: assets-wizard-step2.png
   **Recommendation**: Use slate-400 minimum for disabled text

### Improvements (Should Fix)
1. **Issue**: Missing loading skeleton
   **Location**: Asset list initial load
   **Recommendation**: Add shimmer loading state

### Polish (Nice to Have)
1. **Issue**: No hover effect on cards
   **Location**: Asset list cards
   **Recommendation**: Add subtle scale or shadow transition
```

## Acceptance Criteria

- [ ] Screenshots captured for all viewports
- [ ] Analysis using ui-ux-pro-max criteria
- [ ] Report with prioritized findings
- [ ] Screenshots saved to task artifacts
