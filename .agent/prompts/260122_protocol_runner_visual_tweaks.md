# Agent Prompt: Protocol Runner Visual Tweaks

**Status:** 🟡 Not Started
**Priority:** P1 (Pre-Merge)
**Difficulty:** Medium
**Category:** UI/UX Polish

---

## Overview

This is a **Recon-Plan-Feedback-Execute** workflow for improving the visual presentation of the Protocol Runner feature. The Protocol Runner is critical for the v0.1-alpha release and must look polished.

**CRITICAL:** Before proceeding to each subsequent phase, present your findings and await user approval.

---

## Phase 1: RECON

### Persona

Use the **Recon** persona for this phase. You are a fast codebase navigation specialist conducting reconnaissance.

### Objectives

1. **Audit Current State** - Document all visual elements in the Protocol Runner
2. **Identify Theme Usage** - Find where CSS variables/theme tokens are used vs hardcoded values
3. **Map Component Structure** - Understand the component hierarchy
4. **Capture Screenshots** - Take before screenshots for comparison

### Search Targets

```bash
# Find Protocol Runner components
find praxis/web-client/src -name "*run-protocol*" -type f

# Find related styles
grep -r "run-protocol" --include="*.scss" --include="*.css" praxis/web-client/src/

# Find theme variable definitions
grep -r "var(--theme" praxis/web-client/src/app/features/run-protocol/

# Find hardcoded colors
grep -rE "#[0-9a-fA-F]{3,6}|rgb\(|rgba\(" praxis/web-client/src/app/features/run-protocol/
```

### Files to Examine

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts` | Main component |
| `praxis/web-client/src/app/features/run-protocol/run-protocol.component.scss` | Main styles |
| `praxis/web-client/src/app/features/run-protocol/run-protocol.component.html` | Template |
| `praxis/web-client/src/app/features/run-protocol/components/` | Sub-components |
| `praxis/web-client/src/styles/` | Global style tokens |

### Skills to Reference

- `frontend-design/SKILL.md` - For design patterns
- `ui-ux-pro-max/SKILL.md` - For advanced UI patterns
- `web-design-guidelines/SKILL.md` - For design system compliance

### Output Format

```xml
<recon_report>
<component_structure>
  <!-- List all components in run-protocol feature -->
  <component name="[name]" path="[path]">
    <styles>[path to styles]</styles>
    <visual_issues>[List of visual issues identified]</visual_issues>
  </component>
</component_structure>

<theme_audit>
  <using_theme_vars>
    <file path="[path]" count="[N]">[Examples]</file>
  </using_theme_vars>
  <hardcoded_values>
    <file path="[path]" line="[N]">[Problematic value]</file>
  </hardcoded_values>
</theme_audit>

<visual_issues priority="high|medium|low">
  <issue>[Description of visual problem]</issue>
</visual_issues>

<screenshots>
  <screenshot name="[description]" path="[if captured]"/>
</screenshots>
</recon_report>
```

### Gate 1

**STOP HERE.** Present your recon report and await approval before proceeding to Plan phase.

---

## Phase 2: PLAN

### Persona

Use the **Designer** persona for this phase. You are a frontend UI/UX specialist creating a polish plan.

### Prerequisites

- Completed Recon report from Phase 1
- User approval to proceed

### Skills to Reference

- `writing-plans/SKILL.md` - For structured plan creation
- `theme-factory/SKILL.md` - For theming patterns
- `frontend-design/SKILL.md` - For implementation patterns

### Objectives

1. **Prioritize Fixes** - Rank visual issues by impact and effort
2. **Design Solutions** - Propose specific CSS/template changes
3. **Create Mockups** - If needed, describe target visual state
4. **Define Success Criteria** - Clear before/after expectations

### Plan Structure

Create a plan with specific, actionable tasks:

```markdown
# Protocol Runner Visual Polish Plan

## High Impact Changes
1. [Description] - [Specific fix]

## Theme Variable Fixes
- [ ] [file.scss:line] - Replace `#abc123` with `var(--theme-X)`

## Layout Improvements
- [ ] [Description]

## Animation/Interaction Polish
- [ ] [Description]
```

### Output Format

```xml
<plan_summary>
<tasks count="[N]">
  <task id="1" priority="high|medium|low" effort="small|medium|large">
    <title>[Task title]</title>
    <files>[Files to modify]</files>
    <change>[Specific change description]</change>
  </task>
</tasks>

<before_after>
  <comparison area="[area]">
    <before>[Current state]</before>
    <after>[Target state]</after>
  </comparison>
</before_after>
</plan_summary>
```

### Gate 2

**STOP HERE.** Present your plan and await approval before proceeding to Execute phase.

---

## Phase 3: EXECUTE

### Persona

Use the **Fixer** persona for this phase. You are a fast, focused implementation specialist.

### Prerequisites

- Completed plan from Phase 2
- User approval to proceed

### Skills to Reference

- `verification-before-completion/SKILL.md` - Verify changes work
- `atomic-git-commit/SKILL.md` - Commit logical units

### Execution Rules

1. Make one change at a time
2. Verify each change doesn't break anything
3. Run lint checks after modifications
4. Take after-screenshots for comparison

### Verification Commands

```bash
# Lint check
cd praxis/web-client && npm run lint

# Type check
cd praxis/web-client && npm run build --configuration=browser

# Visual verification (load in browser)
# Navigate to Protocol Runner and verify changes
```

### Output Format

```xml
<execution_report>
<task id="[N]" status="complete|blocked|partial">
  <changes>
    <file path="[path]">[What changed]</file>
  </changes>
  <verification>
    <check name="lint" result="pass|fail"/>
    <check name="visual" result="pass|fail">[Description]</check>
  </verification>
</task>

<summary>
[Overall status and any remaining items]
</summary>
</execution_report>
```

---

## Context & References

**Key Theme Variables (use these):**

| Variable | Usage |
|:---------|:------|
| `--theme-background` | Page backgrounds |
| `--theme-surface` | Card/panel backgrounds |
| `--theme-surface-elevated` | Hover states, elevated surfaces |
| `--theme-border` | Border colors |
| `--theme-text-primary` | Main text |
| `--theme-text-secondary` | Muted text |
| `--theme-text-tertiary` | Disabled/placeholder |
| `--theme-accent` | Primary actions |
| `--theme-accent-muted` | Secondary actions |

**Reference Components (good examples):**

- `praxis/web-client/src/styles/cards.scss` - Card styling patterns
- `praxis/web-client/src/styles/praxis-select.scss` - Form element patterns

---

## On Completion

- [ ] All hardcoded colors replaced with theme variables
- [ ] Layout issues resolved
- [ ] Visual hierarchy improved
- [ ] Lint passes
- [ ] Before/after screenshots captured
- [ ] Changes committed with descriptive message

---

## References

- `.agent/README.md` - Environment overview
- `.agent/skills/frontend-design/SKILL.md` - Design patterns
- `.agent/skills/ui-ux-pro-max/SKILL.md` - Advanced UI patterns

Do not use the browser subagent. If screenshots are needed, use playwright (with timeout _ & ... and --reporter=list) to obtain them. Proceed.
