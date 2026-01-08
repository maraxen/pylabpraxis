# Final Visual QA & Test Suite Backlog

**Priority**: P2 (High)
**Owner**: Frontend + QA
**Created**: 2026-01-04
**Status**: Planning

---

## Overview

Comprehensive visual and interaction testing combining automated Playwright tests with a manual QA checklist. This ensures the application looks correct and behaves properly across different scenarios.

---

## Part 1: Automated E2E Tests (Playwright)

### Critical User Flows

- [ ] **Protocol Execution Flow**
  - Select protocol
  - Configure parameters
  - Select machine
  - Setup deck
  - Start execution
  - Verify run completes

- [ ] **Asset Management Flow**
  - View machines list
  - Add new machine
  - View resources list
  - Add new resource
  - Delete asset

- [ ] **REPL Session Flow**
  - Open REPL
  - Execute code
  - View output
  - (After JupyterLite migration) Notebook cell operations

- [ ] **Execution Monitor Flow**
  - View run history
  - Apply filters
  - View run details
  - Cancel running execution

### Visual Regression Tests

- [ ] **Setup Playwright Visual Regression**
  - Configure screenshot comparison
  - Set up baseline screenshots
  - Define acceptable diff threshold

- [ ] **Key Views to Screenshot**
  - Home page
  - Asset Management (each tab)
  - Run Protocol (each step)
  - Execution Monitor
  - REPL panel
  - Settings page

- [ ] **Theme Variations**
  - Light mode screenshots
  - Dark mode screenshots
  - Compare both for each view

### Responsive Tests

- [ ] **Desktop (1920x1080)**
  - All views render correctly
  - Sidebar fully visible

- [ ] **Tablet (1024x768)**
  - Views adapt to narrower width
  - Collapsible elements work

- [ ] **Mobile (375x667)**
  - If supported, views are usable
  - Or appropriate "desktop required" message

---

## Part 2: Manual QA Checklist

### Visual Inspection

#### Spacing & Alignment

- [ ] Consistent padding in cards
- [ ] Proper alignment in tables
- [ ] Accordion items evenly spaced
- [ ] Form fields aligned
- [ ] Button groups consistent

#### Typography

- [ ] Headers appropriately sized
- [ ] Body text readable
- [ ] Labels clearly visible
- [ ] No text truncation issues

#### Colors & Theme

- [ ] Light mode colors consistent
- [ ] Dark mode colors consistent
- [ ] Sufficient contrast for accessibility
- [ ] Status colors (success/warning/error) clear

#### Icons

- [ ] Icons appropriately sized
- [ ] Consistent icon style (Material Symbols)
- [ ] Clear meaning (not ambiguous)

### Interaction Testing

#### Scrolling

- [ ] Long lists scroll smoothly
- [ ] Scroll containers have proper overflow
- [ ] No content hidden due to scroll issues
- [ ] Sticky headers work correctly

#### Flex Container Behavior

- [ ] Items wrap appropriately
- [ ] No overflow breaking layout
- [ ] Proper flex grow/shrink behavior

#### Hover & Focus States

- [ ] Buttons have hover effect
- [ ] Links have hover effect
- [ ] Focus visible for keyboard navigation
- [ ] Active states clear

#### Loading States

- [ ] Skeletons appear during load
- [ ] Spinners for async operations
- [ ] No flash of empty content

#### Error States

- [ ] Validation errors clearly shown
- [ ] Error messages helpful
- [ ] Network error handling

### Feature-Specific Checks

#### Home Page

- [ ] Summary cards display correctly
- [ ] Quick actions work
- [ ] Recent items show

#### Asset Management

- [ ] Tab switching works
- [ ] Accordions expand/collapse
- [ ] Add/Edit dialogs work
- [ ] Delete confirmation works

#### Run Protocol

- [ ] Stepper navigation works
- [ ] Form validation works
- [ ] Deck visualizer renders
- [ ] Execution starts correctly

#### Execution Monitor

- [ ] Filters apply correctly
- [ ] Run list updates
- [ ] Run details accessible
- [ ] Status indicators accurate

#### REPL

- [ ] Code execution works
- [ ] Output displays correctly
- [ ] Theme matches app theme
- [ ] Inventory panel works

#### Settings

- [ ] Theme toggle works
- [ ] Settings persist
- [ ] All options functional

---

## Part 3: Browser Agent Review

### Automated Interaction Testing

Use browser automation to systematically test interactions:

- [ ] **Navigation Testing**
  - Visit every route
  - Verify no console errors
  - Check page loads successfully

- [ ] **Click Testing**
  - Click all buttons
  - Click all links
  - Verify expected behavior

- [ ] **Form Testing**
  - Fill all forms
  - Submit and verify
  - Test validation

### Performance Checks

- [ ] **Load Time**
  - Initial load < 3s
  - Route transitions < 500ms

- [ ] **Memory**
  - No memory leaks on navigation
  - Long sessions stable

- [ ] **Animation**
  - Smooth 60fps animations
  - No jank during scroll

---

## Test Execution Plan

### Phase 1: Automated Test Suite

1. Set up Playwright test structure
2. Write critical flow tests
3. Add visual regression baseline
4. Integrate into CI pipeline

### Phase 2: Manual QA

1. Complete checklist for light mode
2. Complete checklist for dark mode
3. Document any issues found

### Phase 3: Browser Agent Review

1. Run automated interaction tests
2. Review console for errors
3. Performance audit

---

## Related Documents

- [code_quality_plan.md](./code_quality_plan.md) - Overall quality strategy
- [ui_visual_tweaks.md](./ui_visual_tweaks.md) - Specific UI fixes

---

## Success Criteria

1. [ ] All critical E2E flows pass
2. [ ] Visual regression tests established
3. [ ] Manual QA checklist completed with no blockers
4. [ ] No critical console errors
5. [ ] Performance within acceptable limits
6. [ ] Both themes fully tested
