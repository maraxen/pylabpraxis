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
