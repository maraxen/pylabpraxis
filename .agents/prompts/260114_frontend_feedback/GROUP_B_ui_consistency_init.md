# Group B: UI/UX Consistency - Initialization

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2-P3
**Batch:** [260114_frontend_feedback](../README.md)
**Type:** 🟢 Implementation (Quick Wins + Medium Fixes)

---

## Overview

This group addresses UI consistency issues: chip styling, filter behavior, spacing, and display formatting. Many are quick wins that can be batched together.

---

## Critical Dependencies

> [!IMPORTANT]
> **Group B depends on Group A.** Multiselect, filter, and chip patterns should adopt the shared view controls component from Group A-01. Wait for Group A reconnaissance before finalizing these prompts.

> [!NOTE]
> **No B-* prompts generated yet.** This group is blocked until Group A shared controls are complete. B-01 and B-02 prompts will be generated after A-01 and A-04 are finished.

---

### 1. Add Asset Display - Items on New Lines (P3, Easy)

**User Feedback:**
> "add new asset display should be better presented, plates, tips, on new lines"

**Scope:**

- In add asset dialog, display plates, tips, etc. on separate lines
- Improve visual hierarchy and scannability

---

### 2. Category Dropdown vs Chips (P3, Easy)

**User Feedback:**
> "add resource screen have the category also be a dropdown instead of chips"

**Scope:**

- Replace chip-based category selection with dropdown
- More compact, familiar interaction pattern

---

### 3. Chips Z-Axis Alignment (P3, Easy)

**User Feedback:**
> "make sure chips z axis is aligned (more filters seems to be single select vs vendor is multi)"

**Scope:**

- Ensure consistent chip z-index across filter types
- Single-select and multi-select chips should align visually

---

### 4. Multiselect Fixed Height + Scrollable (P2, Medium)

**User Feedback:**
> "for multiselect, make sure y axis is a FIXED size at instantiation and the chips display below is scrollable"
> "again some inconsistency on how the y and x axis are fixed for multiselects"

**Scope:**

- Multiselect components have fixed container height
- Selected chips display in scrollable area below
- Consistent sizing across all multiselect instances

---

### 5. Back Button in Add Asset Dialog (P3, Easy)

**User Feedback:**
> "add back button in add asset dialog"

**Scope:**

- Add navigation back button to dialog steps
- Consistent with stepper pattern

---

### 6. Spatial View Filter Scroll Issue (P2, Medium)

**User Feedback:**
> "when filters are open in spatial view (and this might be true elsewhere) i cannot scroll within that or scroll to below it"

**Scope:**

- Fix scroll containment in filter panels
- May need overflow/position adjustments
- Test across all tabs with filters

---

### 7. Spatial View Card Overlap (P2, Easy)

**User Feedback:**
> "overlap in spatial view cards"

**Scope:**

- Fix card overlap/z-index issues in spatial view
- Ensure proper spacing between cards

---

### 8. Top Spacing to First Text (P3, Easy)

**User Feedback:**
> "distance from top of application to first text should be eliminated"

**Scope:**

- Reduce or eliminate excessive top padding
- More efficient use of vertical space

---

### 9. Backend Select - Final FQN Segment Only (P3, Easy)

**User Feedback:**
> "backend select in machines tab, only for the final segment of the fqn should be shown"

**Scope:**

- Display only the class name, not full `pylabrobot.foo.bar.ClassName`
- Show full path on hover/tooltip if needed

---

### 10. Settings Headers to Left (P3, Easy)

**User Feedback:**
> "Settings headers can be moved to the left"

**Scope:**

- Left-align settings section headers
- Consistent with standard form layouts

---

## Execution Strategy

### Batch 1: Quick Wins (P3, Easy) - Single Prompt

Items 1, 2, 3, 5, 8, 9, 10 can be combined into one "UI Polish" prompt.

### Batch 2: Filter/Multiselect Fixes (P2, Medium) - Single Prompt

Items 4, 6, 7 require more investigation and are related to filter/scroll behavior.

---

## Prompts to Generate

| # | Type | Title | Items Covered |
|---|------|-------|---------------|
| B-01 | 🟢 Implementation | UI Polish Quick Wins | 1, 2, 3, 5, 8, 9, 10 |
| B-02 | 🟢 Implementation | Filter & Multiselect Consistency | 4, 6, 7 |

---

## Reconnaissance Needed

Before generating implementation prompts, investigate:

- [ ] Add asset dialog location and structure
- [ ] Filter components in spatial view
- [ ] Multiselect component implementations
- [ ] Settings page layout components
