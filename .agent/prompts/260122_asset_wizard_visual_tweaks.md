# Agent Prompt: Asset Wizard Visual Tweaks

**Status:** 🟡 Not Started
**Priority:** P1 (Pre-Merge)
**Difficulty:** Easy-Medium
**Category:** UI/UX Polish

---

## Overview

This is a **Recon-Plan-Feedback-Execute** workflow for fixing the Asset Wizard's visual issues. The main problems are:

1. **Grid is way too big** - The item grid takes up excessive space
2. **UI looks clunky** compared to the rest of the app

**CRITICAL:** Before proceeding to each subsequent phase, present your findings and await user approval.

---

## Phase 1: RECON

### Persona

Use the **Recon** persona for this phase.

### Objectives

1. **Audit Grid Layout** - Understand current grid sizing and why it's too large
2. **Compare to Other Components** - Find polished components to use as reference
3. **Identify Spacing Issues** - Find padding/margin inconsistencies
4. **Catalog All Visual Issues** - Create comprehensive issue list

### Search Targets

```bash
# Asset Wizard files
view: praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.ts
view: praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.scss
view: praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.html

# Compare to polished components
ls praxis/web-client/src/app/shared/components/

# Find grid-related styles
grep -r "grid" praxis/web-client/src/app/shared/components/asset-wizard/
grep -r "display.*grid\|grid-template" praxis/web-client/src/app/shared/components/asset-wizard/
```

### Known Issues (From User)

1. Grid is way too big
2. UI looks clunky compared to everything else

### Output Format

```xml
<recon_report>
<grid_analysis>
  <current_sizing>
    <property>[grid-template-columns, gap, etc.]</property>
    <value>[Current value]</value>
    <issue>[Why this is problematic]</issue>
  </current_sizing>
</grid_analysis>

<spacing_issues>
  <issue location="[selector]" property="[padding|margin|gap]">
    <current>[Value]</current>
    <problem>[Why it looks wrong]</problem>
  </issue>
</spacing_issues>

<comparison_to_polished>
  <component name="[reference component]">
    <pattern>[What makes it look good]</pattern>
    <applicable_here>[How to apply this pattern]</applicable_here>
  </component>
</comparison_to_polished>

<full_issue_list>
  <issue priority="high|medium|low">[Description]</issue>
</full_issue_list>
</recon_report>
```

### Gate 1

**STOP HERE.** Present your recon report and await approval.

---

## Phase 2: PLAN

### Persona

Use the **Designer** persona for this phase.

### Skills to Reference

- `frontend-design/SKILL.md` - Design patterns
- `ui-ux-pro-max/SKILL.md` - For grid and layout patterns

### Objectives

1. **Fix Grid Sizing** - Propose specific size/column changes
2. **Improve Spacing** - Define consistent spacing scale usage
3. **Match App Polish** - Align with other polished components
4. **Responsive Considerations** - Ensure it works on different screen sizes

### Key Decisions

For the grid, consider:

- Smaller card sizes (current is likely too large)
- Better use of available horizontal space
- Appropriate gap between items
- Max-width constraint if needed

### Output Format

```xml
<plan_summary>
<grid_fix>
  <current>[Current grid definition]</current>
  <proposed>[New grid definition]</proposed>
  <rationale>[Why this is better]</rationale>
</grid_fix>

<spacing_fixes>
  <fix selector="[selector]" property="[property]">
    <from>[Current]</from>
    <to>[Proposed]</to>
  </fix>
</spacing_fixes>

<additional_polish>
  <task>[Description of additional polish item]</task>
</additional_polish>
</plan_summary>
```

### Gate 2

**STOP HERE.** Present your plan and await approval.

---

## Phase 3: EXECUTE

### Persona

Use the **Fixer** persona for this phase.

### Skills to Reference

- `verification-before-completion/SKILL.md` - Verify before claiming done

### Execution Checklist

1. [ ] Reduce grid item sizes
2. [ ] Adjust grid-template-columns for better density
3. [ ] Fix excessive gaps/padding
4. [ ] Ensure theme variables are used
5. [ ] Verify responsive behavior
6. [ ] Run lint check
7. [ ] Visual verification in browser

### Verification

```bash
cd praxis/web-client && npm run lint
```

Then visually verify:

1. Open Asset Wizard in browser
2. Confirm grid looks appropriately sized
3. Check on different viewport sizes
4. Compare visual polish to rest of app

### Output Format

```xml
<execution_report>
<changes>
  <file path="asset-wizard.scss">
    [Specific CSS changes made]
  </file>
  <file path="asset-wizard.html">
    [Template changes if any]
  </file>
</changes>

<verification>
  <lint>pass|fail</lint>
  <visual_check>
    <before>[Description or screenshot path]</before>
    <after>[Description or screenshot path]</after>
  </visual_check>
</verification>

<summary>
[What was fixed and remaining items if any]
</summary>
</execution_report>
```

---

## Context & References

**Asset Wizard Files:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.ts` | Component logic |
| `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.scss` | Styles (PRIMARY TARGET) |
| `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.html` | Template |

**Reference for Good Grid Patterns:**

- Cards should typically be 200-280px wide max
- Grid gap of 16-24px is usually appropriate
- Use `minmax()` for responsive grids
- Example: `grid-template-columns: repeat(auto-fill, minmax(240px, 1fr))`

---

## On Completion

- [ ] Grid sizing reduced to appropriate scale
- [ ] Spacing is consistent with app design system
- [ ] Theme variables used throughout
- [ ] Lint passes
- [ ] Visual verification complete
- [ ] Changes committed

---

## References

- `.agent/skills/ui-ux-pro-max/SKILL.md` - Advanced UI patterns
- `.agent/skills/frontend-design/SKILL.md` - Design implementation

Do not use the browser subagent. If screenshots are needed, use playwright (with timeout _ & ... and --reporter=list) to obtain them. Proceed.
