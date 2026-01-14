# Agent Prompt: ViewControls DOM/CSS Inspection

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Medium  
**Dependencies:** None  
**Backlog Reference:** [audit_notes_260114.md](../../artifacts/audit_notes_260114.md) Section B

---

## 1. The Task

Conduct a comprehensive inspection of the `ViewControlsComponent` and its sub-components to identify all styling, spacing, and theming issues. This inspection will generate a findings artifact that drives implementation prompts.

**User-Reported Issues:**

- Weird spacing on desktop and mobile
- Too long/cluttered appearance  
- View type toggle shows text (should be icons only)
- Add Filters menu text invisible (dark mode confirmed, light mode unknown)
- General theme compliance concerns (hardcoded colors vs tokens)

**Goal:** Document all issues with specific line numbers, CSS selectors, and proposed fixes.

## 2. Technical Inspection Strategy

### Step 1: Static Code Review

Review the following files for styling issues:

| File | Focus Areas |
|:-----|:------------|
| `view-controls.component.ts` | Inline styles, template structure |
| `view-controls.component.scss` (if exists) | Spacing, theming tokens |
| `view-type-toggle.component.ts` | Button labels, icon-only rendering |
| `group-by-select.component.ts` | Dropdown styling |
| `praxis-multiselect.component.ts` | Filter chip rendering |

### Step 2: Theme Token Audit

Search for hardcoded colors:

```bash
cd praxis/web-client/src/app/shared/components/view-controls
grep -rn "#[0-9a-fA-F]\\{3,6\\}" .
grep -rn "rgb(" .
grep -rn "rgba(" .
```

### Step 3: Browser Agent Visual Inspection

Use browser agent to:

1. Navigate to `/app/assets`
2. Capture screenshot of ViewControls in light mode
3. Toggle to dark mode, capture screenshot
4. Open "Add Filters" menu, capture screenshot
5. Resize to mobile width (375px), capture screenshot

## 3. Output Artifact

Create `.agents/artifacts/viewcontrols_inspection_findings.md` with:

```markdown
# ViewControls Inspection Findings

## Summary
[X issues found across Y components]

## Issue Catalog

### Issue 1: [Title]
- **File:** [path]
- **Line:** [number]
- **Problem:** [description]
- **Screenshot:** [if applicable]
- **Fix:** [proposed solution]

[Repeat for each issue]

## Theme Token Violations
[List of hardcoded color usages]

## Responsive Issues
[Mobile-specific problems]

## Recommended Fix Order
[Prioritized list]
```

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **Styling**: Document violations of theme token usage.
- **Screenshots**: Save to `.agents/tmp/` with descriptive names.

## 5. Verification Plan

**Definition of Done:**

1. `viewcontrols_inspection_findings.md` artifact created
2. All issues catalogued with specific file/line references
3. At least 4 screenshots captured (light, dark, menu, mobile)
4. Theme token violations identified

---

## On Completion

- [x] Create `.agents/artifacts/viewcontrols_inspection_findings.md`
- [x] Update this prompt status to 🟢 Completed
- [x] Note any blocking issues discovered

---

## References

- `.agents/README.md` - Environment overview
- `.agents/artifacts/audit_notes_260114.md` - Source requirements
