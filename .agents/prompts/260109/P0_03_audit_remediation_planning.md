# Agent Prompt: Audit Remediation Planning (P0)

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P0 (Follows P0_02)
**Batch:** [260109](README.md)
**Backlog Reference:** [separation_of_concerns.md](../../backlog/separation_of_concerns.md)
**Estimated Complexity:** Medium
**Depends On:** P0_02 audit completion

---

## 1. The Task

After completing the P0_02 separation of concerns audit, use the findings to:

1. **Update existing backlog items** with specific, actionable tasks
2. **Create new prompts** for each remediation area discovered
3. **Prioritize the work** based on impact and dependencies
4. **Update the DEVELOPMENT_MATRIX.md** to reflect the new work

**User Value:** Clear, actionable path from audit findings to fixed application.

---

## 2. Prerequisites

Before starting this prompt, ensure P0_02 has been completed and you have:

- [ ] List of all files with frontend category inference logic
- [ ] List of all missing backend schema fields
- [ ] List of browser mode data that needs updating
- [ ] Understanding of dependencies between fixes

---

## 3. Deliverables

### 3.1 Update Backlog Files

Update `.agents/backlog/separation_of_concerns.md` with:

- Specific files that need changes (from audit)
- Concrete tasks with checkboxes
- Any new issues discovered during audit

### 3.2 Create Remediation Prompts

For each major work area discovered, create a focused prompt:

**Naming Convention:** `P1_XX_<area>_remediation.md`

**Example prompt structure:**

```markdown
# Agent Prompt: [Area] Remediation

**Status:** 🟢 Not Started
**Priority:** P1
**Depends On:** P0_02 (audit), P0_03 (this planning)

## Files to Modify
[List from audit]

## Specific Changes
[Detailed changes per file]

## Verification
[How to verify the fix]
```

**Suggested prompt areas** (create as needed based on audit):

| Prompt | Area | Scope |
|:-------|:-----|:------|
| `P1_10_backend_schema_update.md` | Backend schema | Add `required_plr_category` field |
| `P1_11_backend_protocol_analysis.md` | Backend services | Populate new field during analysis |
| `P1_12_frontend_filtering_cleanup.md` | Frontend components | Remove string matching |
| `P1_13_browser_data_update.md` | Browser mode | Update offline data |
| `P1_14_delete_inference_utils.md` | Cleanup | Remove deprecated utilities |

### 3.3 Update Batch README

Update `.agents/prompts/260109/README.md`:

- Add new prompts to the table
- Update execution order
- Mark dependencies

### 3.4 Update DEVELOPMENT_MATRIX.md

Add new items to the development matrix tracking the remediation work.

---

## 4. Template for New Prompts

Use this template when creating remediation prompts:

```markdown
# Agent Prompt: [Title]

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260109](README.md)
**Backlog Reference:** [separation_of_concerns.md](../../backlog/separation_of_concerns.md)
**Estimated Complexity:** [Easy/Medium/High]
**Depends On:** [List dependencies]

---

## 1. The Task

[Clear description of what needs to be done]

---

## 2. Files to Modify

| File | Change |
|:-----|:-------|
| `path/to/file.ts` | [Specific change] |

---

## 3. Implementation

[Step-by-step implementation guide]

---

## 4. Verification

- [ ] [Verification step 1]
- [ ] [Verification step 2]

---

## 5. On Completion

- [ ] Commit with message: `[type]: [description]`
- [ ] Update backlog status
- [ ] Mark prompt complete in README
```

---

## 5. Prioritization Guidelines

When prioritizing remediation prompts:

### High Priority (P1)
- Backend schema changes (blocks everything else)
- Core filtering logic fixes
- Breaking bugs

### Medium Priority (P2)
- Browser mode data updates
- Utility cleanup
- Non-critical components

### Lower Priority (P3)
- Documentation updates
- Test improvements
- Nice-to-have refactors

---

## 6. Execution Order Considerations

Typical dependency chain:

```
1. Backend Schema (migration)
   └── 2. Backend Services (populate new fields)
       └── 3. Frontend Components (use new fields)
           └── 4. Browser Data (match production schema)
               └── 5. Cleanup (delete deprecated code)
```

---

## 7. On Completion

- [ ] All backlog items updated with audit findings
- [ ] New prompts created for each remediation area
- [ ] Batch README updated with new prompts
- [ ] DEVELOPMENT_MATRIX.md updated
- [ ] Clear execution order documented
- [ ] Dependencies between prompts noted

---

## 8. Notes

- Keep prompts focused and atomic (one concern per prompt)
- Each prompt should be completable in one session
- Include verification steps in every prompt
- Link prompts to backlog items for traceability
