# Frontend Visual Polish Workflow

A systematic approach to identifying, analyzing, and resolving UI and visual design issues to ensure a high-quality, polished user interface.

## 1. Overview

- **Purpose**: To provide a repeatable, structured pipeline for catching visual regressions, improving UI consistency, and refining the overall aesthetic quality of the application.
- **When to Use**:
    - Following completion of major feature work.
    - Prior to production releases or milestones.
    - During dedicated "polish sprints" or technical debt sessions.
    - When visual inconsistencies are reported across different viewports or themes.

## 2. Pipeline Stages

The workflow follows a 4-stage linear progression:

```
CAPTURE → ANALYZE → FIX → VALIDATE
```

| Stage | Primary Agent | Tool/Mechanism | Primary Input | Primary Output |
|-------|---------------|----------------|---------------|----------------|
| **CAPTURE** | `flash` | Playwright | Component/Route list | Screenshots (.png) |
| **ANALYZE** | `multimodal-looker` | Visual Analysis | Screenshots | Issue Report + CSS Fixes |
| **FIX** | `flash` | Code Editor | Analysis Report | Refactored UI Code |
| **VALIDATE** | `multimodal-looker` | Visual Comparison | Before/After Screenshots | Validation Sign-off |

---

## 3. Capture Stage Details

The goal is to generate a comprehensive visual record of the target UI.

- **Tool**: Playwright
- **Command**:
  ```bash
  cd praxis/web-client
  npx playwright test e2e/specs/viz-review.spec.ts --project=chromium
  ```
- **Capture Checklist**:
    - [ ] **Themes**: Light mode and Dark mode.
    - [ ] **States**: Empty states, loading skeletons, and populated data.
    - [ ] **Responsive**: Desktop (1440px), Tablet (768px), and Mobile (375px) viewports.
    - [ ] **Interactions**: Hover states, active/focused inputs, and open dropdowns/dialogs.
- **Screenshot Organization**:
  Store images in `praxis/web-client/e2e/screenshots/<category>/` (e.g., `dialogs/`, `dashboards/`, `forms/`).

---

## 4. Analyze Stage Details

Using the `multimodal-looker` agent to perform a deep visual audit.

- **Dispatch Pattern**:
  ```javascript
  // Example Dispatch
  background_task(
    agent: "multimodal-looker",
    prompt: "Analyze screenshots in e2e/screenshots/viz-review/. 
             Evaluate against the Polish Criteria Checklist. 
             Provide a structured report including: 
             1. Issue Description 
             2. Severity (High/Med/Low) 
             3. Specific CSS/Styling recommendations.",
    sync: true
  )
  ```
- **Analysis Criteria Checklist**:
    - [ ] **Layout & Spacing**: Padding/margin consistency, grid alignment.
    - [ ] **Typography**: Font weights, sizes, line heights, and readability.
    - [ ] **Accessibility**: Color contrast, focus indicators, touch target sizes.
    - [ ] **Visual Hierarchy**: Do the most important elements stand out?
    - [ ] **Empty States**: Are they helpful and visually aligned?
    - [ ] **Control Styling**: Button consistency, input borders, shadow usage.
    - [ ] **Edge Cases**: Text truncation, container overflows, weird wrapping.
    - [ ] **Dark Mode**: Check for "muddy" colors, lost shadows, or hardcoded white backgrounds.

---

## 5. Fix Stage Details

The `flash` agent applies the recommended changes from the analysis.

- **Dispatch Pattern**:
  ```javascript
  // Example Dispatch
  task(
    subagent_type: "flash",
    prompt: "Fix visual issues in src/app/features/dashboard/dashboard.component.ts. 
             Apply these CSS changes: 
             - Change card border-radius to 12px 
             - Update shadow to var(--shadow-md)
             - Ensure title uses font-weight: 600.
             Provide a summary of all modified lines."
  )
  ```
- **Best Practices**:
    - Provide **specific file paths** to avoid searching.
    - Use **exact CSS values** or design tokens (e.g., `var(--primary-color)`) recommended in analysis.
    - Request a **change summary** to track what was actually modified.

---

## 6. Validate Stage Details

Final verification to ensure the fixes achieved the desired result without regressions.

- **Process**:
    1. Re-run the **Capture Stage** to get new "after" screenshots.
    2. Provide both "before" and "after" images to the `multimodal-looker` agent.
- **Validation Criteria**:
    - [ ] **Issue Resolution**: Is the original problem fixed?
    - [ ] **Visual Improvement**: Does it look objectively better?
    - [ ] **No Regressions**: Did the fix break something nearby? (e.g., spacing of adjacent elements).
    - [ ] **Code Quality**: Are the styles applied using variables/tokens rather than hardcoded hex values?

---

## 7. Quick Reference

### Agent Usage
| Agent | Role in Polish |
|-------|----------------|
| `flash` | Running Playwright, applying CSS/HTML fixes, linting. |
| `multimodal-looker` | Visual auditing of screenshots, before/after comparison. |
| `investigator` | Debugging complex CSS inheritance or layout shift issues. |

### Common Commands
```bash
# Capture everything
npx playwright test e2e/specs/viz-review.spec.ts

# Capture specific component
npx playwright test e2e/specs/viz-review.spec.ts -g "Deck View"

# Run dev server for capture
npm run start:browser
```

### Key File Locations
- **Screenshots**: `praxis/web-client/e2e/screenshots/`
- **Capture Specs**: `praxis/web-client/e2e/specs/`
- **Global Styles**: `praxis/web-client/src/styles.scss`
- **Theme Variables**: `praxis/web-client/src/styles/variables.scss`

---

## 8. Batching Strategy

To maintain efficiency, group polish items logically.

- **By Component**: Fix all issues (typography, spacing, dark mode) for a single component at once.
- **By Category**: Fix a specific type of issue (e.g., "All Dialog Sizing") across the entire application.
- **Priority Matrix Template**:

| Priority | Criteria | Example |
|----------|----------|---------|
| **Critical** | Breaks usability or brand perception | Unreadable text, overlapping buttons |
| **High** | Major inconsistency or polish gap | Misaligned headers, wrong theme colors |
| **Medium** | Minor visual refinement | Shadow depth, subtle padding tweaks |
| **Low** | "Nice to have" polish | Micro-animations, subtle hover transitions |
