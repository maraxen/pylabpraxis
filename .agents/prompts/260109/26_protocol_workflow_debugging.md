# Agent Prompt: 26_protocol_workflow_debugging

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260109](./README.md)  
**Backlog:** [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md)  

---

## Task

Investigate and debug protocol workflow issues identified during user testing. **Report findings and proposed solutions before implementing fixes**.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md) | Workflow backlog |
| [run-protocol.component.ts](../../../praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts) | Main workflow component |
| [parameter-config.component.ts](../../../praxis/web-client/src/app/features/run-protocol/components/parameter-config/parameter-config.component.ts) | Parameter form component |
| [schema.sql](../../../praxis/web-client/src/assets/db/schema.sql) | Database schema reference |

---

## Investigation Items

### 1. Parameter Selection Form Issue

**Symptom**: Parameter selection form incorrectly includes machine and resource categories for selection.

**Investigation Steps**:

- [ ] Trace the form generation in `parameter-config.component.ts`
- [ ] Identify where parameter types are being determined
- [ ] Check if `inferred_requirements_json` or `protocol_asset_requirements` are being incorrectly merged with parameters
- [ ] Verify separation between `parameter_definitions` and `protocol_asset_requirements` tables

**Possible Causes**:

- Asset requirements being rendered as form parameters
- Incorrect filtering of parameter types during form generation
- Type inference including machine/resource types in parameter list

### 2. First Step Layout & Scrolling

**Symptom**: Protocol description text takes up too much space, needs constrained width in scrollable flex container.

**Requirements**:

- [ ] Limit description text to a reasonable max-height (e.g., 200px)
- [ ] Wrap in scrollable flex container with vertical scrolling
- [ ] Move "Back to Selection" button to top of the first step display
- [ ] Move "Continue" button to top as well (navigation at top)
- [ ] Ensure responsive behavior

### 3. Name & Notes Section

**Requirement**: Add a name and notes section where users can customize run details.

**Database Investigation**:

- [ ] Confirm `protocol_runs.name` exists and can store user-provided names
- [ ] Check if there's a `notes` field or if `properties_json` can be used
- [ ] Investigate if `protocol_runs` row is created on workflow entry or on execution start

**Questions to Answer**:

- Is a `protocol_runs` record created when user starts the workflow, or only on execution?
- If user navigates away and comes back, can configured state be preserved?
- Do we need a "draft" status for in-progress configurations?

### 4. Skip Setup Functionality

**Symptom**: "Skip Setup" button does not work in the deck setup step.

**Investigation Steps**:

- [ ] Locate the skip logic in deck setup component
- [ ] Trace what happens when "Skip Setup" is clicked
- [ ] Identify if stepper navigation is being blocked
- [ ] Check for any conditions that prevent skipping

---

## Execution Strategy

**Phase 1: Investigation Only**

1. Systematically investigate each issue
2. Document findings for each item
3. Report back to user with:
   - Root cause for each issue
   - Proposed solution(s)
   - Any schema changes required
   - Estimated complexity

**Phase 2: Implementation (After User Approval)**

1. Implement approved fixes
2. Test each fix in isolation
3. Verify no regressions

---

## Report Format

When reporting back, use this structure:

```markdown
## Issue: [Issue Name]

**Root Cause**: [What is causing the problem]

**Evidence**: [Code locations, log output, or behavior observed]

**Proposed Fix**: [What changes are needed]

**Files to Modify**:
- [file1.ts] - [what changes]
- [file2.html] - [what changes]

**Schema Changes Required**: [Yes/No - if yes, describe]

**Complexity**: [S/M/L]
```

---

## Technical Debt Items

> These items should be added to backlog but are out of scope for initial investigation:

- **Markdown Support for Protocol Descriptions**: Allow description text to be rendered as markdown with proper linebreak handling
- **Draft Protocol Run Persistence**: Create `protocol_runs` record in "DRAFT" status to preserve configuration across navigation

---

## Expected Outcome

- Detailed investigation report for all 4 issues
- User approval before proceeding with fixes
- Clear implementation plan with estimated effort

---

## On Completion

- [ ] Investigation report delivered to user
- [ ] User approval obtained for proposed fixes
- [ ] Fixes implemented and tested
- [ ] Update run_protocol_workflow.md backlog
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
- [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md) - Related backlog
- [ui_consistency.md](../../backlog/ui_consistency.md) - Layout patterns
