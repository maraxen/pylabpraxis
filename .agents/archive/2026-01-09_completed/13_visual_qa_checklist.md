# Agent Prompt: 13_visual_qa_checklist

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260109](./README.md)  
**Backlog:** [quality_assurance.md](../../backlog/quality_assurance.md)  

---

## Task

Complete the visual QA checklist covering critical flows, theme testing, responsive design, and accessibility.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [quality_assurance.md](../../backlog/quality_assurance.md) | Work item tracking (Section 3) |

---

## Checklist

### Critical Flows

- [ ] First-time user experience (welcome dialog, tutorial steps)
- [ ] Asset CRUD (add/edit/delete resources and machines)
- [ ] Protocol selection and execution
- [ ] Playground (REPL) interaction

### Theme Testing

- [ ] Light mode consistency across all pages
- [ ] Dark mode consistency across all pages
- [ ] Theme toggle works everywhere

### Responsive Design

- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (1024x768)

### Accessibility

- [ ] Keyboard navigation (tab order, focus indicators)
- [ ] Screen reader compatibility (ARIA labels)
- [ ] Color contrast ratios (WCAG AA compliance)

### Layout & Flex Container Audit

> Ensure content is properly contained in flex containers with appropriate constraints.

#### Protocol Workflow Steps

- [ ] **First Step (Protocol Overview)**: Description text constrained width in scrollable flex container
- [ ] **Parameter Config Step**: Form fields not stretching beyond 600px width
- [ ] **Asset Selection Step**: Cards contained in responsive grid
- [ ] **Deck Setup Step**: Wizard content properly contained
- [ ] **Review Step**: Summary content constrained width

#### General Layout Patterns

- [ ] Long text blocks (descriptions, notes) have `max-width` constraint
- [ ] Form containers use `display: flex; flex-direction: column;` with reasonable max-widths
- [ ] Card grids use `flex-wrap: wrap` with consistent gap spacing
- [ ] Dialog content uses scrollable container when content exceeds viewport
- [ ] Navigation buttons at top of step content (not buried at bottom)

#### Known Issues to Verify Fixed

- [ ] Protocol description on first step not too broad (should be ~600-800px max)
- [ ] Asset requirement cards have consistent widths
- [ ] Machine/resource selectors constrained appropriately

### Scrolling Behavior

> Define when to use auto-scroll with wrapping vs. allowing users to scroll.

#### Guidelines

| Content Type | Recommended Behavior |
|:-------------|:---------------------|
| **Long Text (descriptions, notes)** | Max-height with scroll (`max-height: 200px; overflow-y: auto`) |
| **Lists of Items (parameters, assets)** | Scroll within container if > 5-6 items visible |
| **Horizontal Chips/Tags** | Wrap to next line, not horizontal scroll |
| **Tables/Data Grids** | Fixed header, scrollable body |
| **Dialogs** | Body scrolls, footer fixed |

#### Scrolling Checklist

- [ ] **Protocol Description**: Has max-height with vertical scroll when text is long
- [ ] **Parameter Lists**: Scrollable container if many parameters
- [ ] **Asset Requirements List**: Scrollable if more than 6 items
- [ ] **Filter Chips**: Wrap to next line (flex-wrap: wrap)
- [ ] **Deck Position List**: Scrollable independent of deck preview
- [ ] **Run History Table**: Fixed header, scrollable body

### Technical Debt (UI/UX)

> Items to track for future improvement.

- [ ] **Markdown Support for Protocol Descriptions**: Allow description text to be rendered as markdown with proper formatting <!-- id: td-1 -->
- [ ] **Automatic Linebreak Support**: Respect `\n` in source text as `<br>` or paragraphs in rendered output <!-- id: td-2 -->
- [ ] **Full Markdown Parsing**: Support paragraphs, headers, lists, code blocks in description fields <!-- id: td-3 -->
- [ ] **Consistent Text Container Styling**: Create reusable CSS class for scrollable text containers with consistent max-height <!-- id: td-4 -->

---

## Implementation

1. **Manual Testing**:
   - Use browser dev tools for responsive testing
   - Use Lighthouse for accessibility audit
   - Document screenshots of issues

2. **Issue Logging**:
   - Create detailed bug reports for each issue found
   - Categorize by severity

3. **Playwright Automation**:
   - Add visual regression tests for critical flows
   - Screenshot comparison baselines

---

## Expected Outcome

- Documented QA results with screenshots
- Bug reports for any issues found
- Visual regression test suite foundation

---

## On Completion

- [ ] Create QA report in `.agents/reports/visual_qa_260109.md`
- [ ] Log any bugs found to appropriate backlog
- [ ] Update quality_assurance.md checklist
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
