# Agent Prompt: Spatial View UX Analysis

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P3
**Batch:** [260114_frontend_feedback](./README.md)
**Difficulty:** Medium
**Type:** 🔵 Planning
**Dependencies:** None
**Backlog Reference:** Group A - View Controls Standardization

---

## 1. The Task

Conduct UX analysis to determine the purpose and future of the Spatial View tab. The user has expressed uncertainty about what role Spatial View serves and whether it should remain a separate tab or become a view mode within other tabs.

### User Feedback

> "it's also unclear what the role of spatial view is and why it's a separate tab. we should assess this carefully"

### Questions to Answer

1. **What unique value does Spatial View provide?** - Document features only available in Spatial View
2. **How does it differ from Machines/Resources tabs?** - Compare filter options, display format, grouping
3. **Should it be a view mode within other tabs instead?** - Evaluate pros/cons
4. **What is the mental model for users?** - When would a user navigate to Spatial View vs Machines/Resources?

## 2. Technical Implementation Strategy

This is a **planning-only task** that produces a UX recommendation document. No code changes are made.

### Analysis Steps

1. **Document Current Features**
   - Review `SpatialViewComponent` implementation
   - List all unique features (grouping, filtering, display options)
   - Identify which features overlap with Machines/Resources tabs

2. **Compare with Other Tabs**
   - Review `MachineFiltersComponent` and `ResourceFiltersComponent`
   - Document feature parity and gaps
   - Identify potential consolidation opportunities

3. **Evaluate Alternatives**
   - Option A: Keep as separate tab with clear purpose
   - Option B: Merge as "view mode" toggle in Machines/Resources
   - Option C: Rename/rebrand to clarify purpose
   - Option D: Deprecate and migrate features

4. **Make Recommendation**
   - Recommend one option with justification
   - Document required implementation work
   - Identify risks and mitigations

## 3. Context & References

**Primary Files to Analyze:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/spatial-view/spatial-view.component.ts` | Main Spatial View implementation (367 lines) |
| `praxis/web-client/src/app/features/assets/components/asset-filters/asset-filters.component.ts` | Filters used by Spatial View (285 lines) |
| `praxis/web-client/src/app/features/assets/components/filter-header/filter-header.component.ts` | Header component for filtering |

**Comparison Files:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/assets.component.ts` | Parent container with tab navigation (409 lines) |
| `praxis/web-client/src/app/features/assets/components/machine-filters/machine-filters.component.ts` | Machine tab filters (390 lines) |
| `praxis/web-client/src/app/features/assets/components/resource-filters/resource-filters.component.ts` | Resource tab filters |

## 4. Constraints & Conventions

- This is a **read-only analysis task** - no code changes
- Output should be a markdown document in `.agents/prompts/260114_frontend_feedback/`
- Include screenshots or diagrams if helpful
- Consider both technical and UX perspectives

## 5. Deliverable

Create a file: `.agents/prompts/260114_frontend_feedback/A-P1_spatial_view_recommendation.md`

### Document Structure

```markdown
# Spatial View UX Recommendation

## Executive Summary
[1-2 paragraph recommendation]

## Current State Analysis
### Spatial View Features
- [Feature list with descriptions]

### Comparison with Other Tabs
| Feature | Spatial | Machines | Resources |
|:--------|:--------|:---------|:----------|
| ... | ... | ... | ... |

## Options Evaluated
### Option A: Keep as Separate Tab
[Pros/Cons/Required Work]

### Option B: Merge as View Mode
[Pros/Cons/Required Work]

### Option C: Rename/Rebrand
[Pros/Cons/Required Work]

## Recommendation
[Detailed recommendation with justification]

## Implementation Path
[Steps if recommendation is approved]

## Risks & Mitigations
[Risk assessment]
```

## 6. Verification Plan

**Definition of Done:**

1. UX recommendation document created
2. All four questions from Section 1 are answered
3. Clear recommendation with implementation path provided
4. Document reviewed by user before proceeding

---

## On Completion

- [ ] Create recommendation document
- [ ] Mark this prompt complete in batch README
- [ ] Set status in this document to 🟢 Completed
- [ ] If recommendation spawns implementation work, create follow-up prompts

---

## References

- `.agents/README.md` - Environment overview
- `GROUP_A_view_controls_init.md` - Parent initiative
