# Agent Prompt: Theme CSS Variable Fixes

**Status:** 🟡 Not Started
**Priority:** P1 (Pre-Merge)
**Difficulty:** Easy
**Category:** UI Consistency

---

## Overview

This is a **Recon-Plan-Feedback-Execute** workflow for fixing components that are NOT using correct CSS theme variables. This affects:

1. **Protocol Detail Colors** - The popup when clicking a protocol in Protocol Manager
2. **Settings Page** - The entire settings feature

These should be quick fixes but are highly visible and must be consistent with the rest of the app.

**CRITICAL:** Before proceeding to each subsequent phase, present your findings and await user approval.

---

## Phase 1: RECON

### Persona

Use the **Recon** persona for this phase.

### Objectives

1. **Find Protocol Detail Component** - Locate the popup/modal shown when clicking a protocol
2. **Find Settings Component** - Locate all settings-related styles
3. **Audit for Hardcoded Colors** - Find all instances of hardcoded colors in these components
4. **Map to Theme Variables** - Determine which theme variable should replace each hardcoded value

### Search Targets

```bash
# Find Protocol Detail (the popup when clicking a protocol)
grep -r "protocol.*detail\|ProtocolDetail" --include="*.ts" praxis/web-client/src/
find praxis/web-client/src -name "*protocol*detail*" -o -name "*detail*dialog*"

# Find Settings components
find praxis/web-client/src/app/features/settings -type f
ls praxis/web-client/src/app/features/settings/

# Find hardcoded colors in these areas
grep -rE "#[0-9a-fA-F]{3,6}|rgb\(|rgba\(" praxis/web-client/src/app/features/settings/
grep -rE "#[0-9a-fA-F]{3,6}|rgb\(|rgba\(" praxis/web-client/src/app/features/protocol-manager/

# Find what theme variables exist
grep -r "var(--theme" praxis/web-client/src/styles/
grep -r ":root" praxis/web-client/src/styles.scss
```

### Files to Examine

| Area | Likely Files |
|:-----|:-------------|
| Protocol Detail | `protocol-manager/components/protocol-detail*` or similar |
| Settings Page | `features/settings/*.component.scss` |
| Theme Definitions | `src/styles.scss`, `src/styles/*.scss` |

### Output Format

```xml
<recon_report>
<protocol_detail>
  <location>[Path to component]</location>
  <hardcoded_colors>
    <color file="[file]" line="[N]" value="[#abc123]" context="[What it styles]"/>
  </hardcoded_colors>
  <suggested_replacements>
    <replacement from="[hardcoded]" to="[var(--theme-X)]"/>
  </suggested_replacements>
</protocol_detail>

<settings_page>
  <location>[Path to component(s)]</location>
  <hardcoded_colors>
    <color file="[file]" line="[N]" value="[#abc123]" context="[What it styles]"/>
  </hardcoded_colors>
  <suggested_replacements>
    <replacement from="[hardcoded]" to="[var(--theme-X)]"/>
  </suggested_replacements>
</settings_page>

<theme_variables_available>
  <variable name="--theme-X">[Description/usage]</variable>
</theme_variables_available>
</recon_report>
```

### Gate 1

**STOP HERE.** Present your recon report and await approval.

---

## Phase 2: PLAN

### Persona

Use the **Designer** persona for this phase.

### Objectives

1. **Create Replacement Map** - Exact mapping of hardcoded → theme variable
2. **Prioritize by Visibility** - Which fixes have highest visual impact
3. **Verify Replacements** - Ensure replacements make semantic sense

### Key Considerations

Theme variable semantic meaning:

- `--theme-background` → Main page/section backgrounds
- `--theme-surface` → Card/panel backgrounds
- `--theme-surface-elevated` → Hover/elevated surfaces
- `--theme-border` → All borders
- `--theme-text-primary` → Main readable text
- `--theme-text-secondary` → Muted/secondary text
- `--theme-text-tertiary` → Disabled/placeholder text
- `--theme-accent` → Primary action color
- `--theme-accent-muted` → Secondary accent uses
- `--theme-success`, `--theme-warning`, `--theme-error` → Status colors

### Output Format

```xml
<plan_summary>
<protocol_detail_fixes count="[N]">
  <fix file="[file]" line="[N]">
    <from>[Current CSS]</from>
    <to>[New CSS with theme var]</to>
  </fix>
</protocol_detail_fixes>

<settings_page_fixes count="[N]">
  <fix file="[file]" line="[N]">
    <from>[Current CSS]</from>
    <to>[New CSS with theme var]</to>
  </fix>
</settings_page_fixes>

<estimated_effort>[X minutes]</estimated_effort>
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

### Execution Rules

1. Replace hardcoded colors with corresponding theme variables
2. Verify the replacement makes visual sense (don't just blindly replace)
3. Run lint after each file
4. Test in both light and dark mode if themes exist

### Verification

```bash
# Check for any remaining hardcoded colors
grep -rE "#[0-9a-fA-F]{3,6}" praxis/web-client/src/app/features/settings/
grep -rE "#[0-9a-fA-F]{3,6}" [path-to-protocol-detail]

# Lint check
cd praxis/web-client && npm run lint
```

Visual verification:

1. Open Protocol Manager, click a protocol to see detail popup
2. Open Settings page
3. Verify colors match rest of app
4. Toggle dark mode if available

### Output Format

```xml
<execution_report>
<protocol_detail>
  <file path="[path]">
    <changes>[Summary of changes]</changes>
  </file>
</protocol_detail>

<settings_page>
  <file path="[path]">
    <changes>[Summary of changes]</changes>
  </file>
</settings_page>

<verification>
  <remaining_hardcoded>[None or list]</remaining_hardcoded>
  <lint>pass|fail</lint>
  <visual_check>pass|fail - [notes]</visual_check>
</verification>

<summary>
[What was fixed]
</summary>
</execution_report>
```

---

## Context & References

**Theme Variable Reference:**

```scss
// Colors - Use these!
var(--theme-background)        // Page backgrounds
var(--theme-surface)           // Card/panel backgrounds  
var(--theme-surface-elevated)  // Hover states, elevated elements
var(--theme-border)            // Borders
var(--theme-text-primary)      // Main text
var(--theme-text-secondary)    // Secondary/muted text
var(--theme-text-tertiary)     // Disabled/placeholder
var(--theme-accent)            // Primary actions
var(--theme-accent-muted)      // Secondary accent
var(--theme-success)           // Success states
var(--theme-warning)           // Warning states
var(--theme-error)             // Error states
```

**Good Examples in Codebase:**

- `praxis/web-client/src/styles/cards.scss` - Uses theme variables correctly
- `praxis/web-client/src/styles/praxis-select.scss` - Uses theme variables correctly

---

## On Completion

- [ ] All hardcoded colors in Protocol Detail replaced
- [ ] All hardcoded colors in Settings replaced
- [ ] Lint passes
- [ ] Visual verification complete
- [ ] Changes committed with message like: `style: replace hardcoded colors with theme variables`

---

## References

- `.agent/skills/theme-factory/SKILL.md` - Theme patterns
- `.agent/skills/frontend-design/SKILL.md` - Design implementation

Do not use the browser subagent. If screenshots are needed, use playwright (with timeout _ & ... and --reporter=list) to obtain them. Proceed.
