# Agent Prompt Batch: 2026-01-09

**Created:** 2026-01-09
**Focus Area:** Protocol Workflow & Playground Stabilization
**Total Prompts:** 7 (+ remediation prompts TBD from P0_03)

---

## Prompts

| # | Status | Priority | Filename | Description | Complexity | Key Files | Verification |
|---|--------|----------|----------|-------------|------------|-----------|--------------|
| 0.1 | ⚠️ Superseded | **P0** | [P0_01_plr_category_audit.md](P0_01_plr_category_audit.md) | Frontend-only cleanup (superseded by P0_02) | High | frontend | `npm run build` |
| 0.2 | 🟢 Not Started | **P0** | [P0_02_separation_of_concerns_audit.md](P0_02_separation_of_concerns_audit.md) | **Audit**: Find all separation of concerns violations | High | backend + frontend | Document findings |
| 0.3 | 🟢 Not Started | **P0** | [P0_03_audit_remediation_planning.md](P0_03_audit_remediation_planning.md) | **Plan**: Create backlog items & prompts from audit | Medium | `.agents/` | Prompts created |
| 1 | 🟢 Not Started | P1 | [P1_01_playground_loading_removal.md](P1_01_playground_loading_removal.md) | Remove unnecessary loading overlay from Playground | Easy | `playground.component.ts` | `npm run build` |
| 2 | ⚠️ Superseded | P1 | [P1_02_asset_filtering_bugfix.md](P1_02_asset_filtering_bugfix.md) | Tactical fix (superseded by P0_02) | Medium | `guided-setup.component.ts` | `npm run build` |
| 3 | 🟢 Not Started | P1 | [P1_03_asset_selection_filters.md](P1_03_asset_selection_filters.md) | Add status filter chips to asset selection cards | Medium | `guided-setup.component.ts` | `npm run build` + manual test |
| 4 | 🟢 Not Started | P1 | [P1_04_autoselect_buttons.md](P1_04_autoselect_buttons.md) | Add Auto-Select buttons to Machine & Asset steps | Easy-Medium | `run-protocol.component.ts`, `guided-setup.component.ts` | `npm run build` + manual test |

---

## Execution Order

### Phase 1: Audit & Plan

```
P0_02 (Audit)
  │
  │  Findings: list of files, missing fields, violations
  │
  ▼
P0_03 (Plan)
  │
  │  Output: new backlog items, P1_XX remediation prompts
  │
  ▼
P1_XX... (Remediation prompts created by P0_03)
```

1. **P0_02** - Audit: Find all separation of concerns violations
   - Document files with frontend inference logic
   - Document missing backend schema fields
   - Document browser mode data gaps

2. **P0_03** - Plan: Create actionable work items from audit
   - Update backlog with specific tasks
   - Create focused remediation prompts (P1_10+)
   - Establish execution order for fixes

### Phase 2: Execute Fixes

3. **P1_10+** - Remediation prompts (created by P0_03)
   - Likely order: Backend schema → Backend services → Frontend → Browser data → Cleanup

4. **P1_01** - Standalone quick win (can run anytime)

5. **P1_03, P1_04** - After filtering is fixed

### Superseded Prompts

- **P0_01**: Was frontend-only; P0_02 audit is more comprehensive
- **P1_02**: Was tactical band-aid; remediation prompts will fix properly

---

## Architecture Decision

**Principle established in P0_02:**

> The backend owns all PLR inspection and classification logic. The database is the single source of truth. The frontend consumes pre-computed data and performs only display/filtering operations using explicit fields—never inference.

See [separation_of_concerns.md](../../backlog/separation_of_concerns.md) for full details.

---

## Status Legend

| Status | Meaning |
|--------|---------|
| 🟢 Not Started | Ready for agent dispatch |
| 🟡 In Progress | Currently being worked on |
| 🔴 Blocked | Waiting on dependency or clarification |
| ⚠️ Superseded | Replaced by another prompt |
| ✅ Completed | Work done and verified |

---

## Notes

- All prompts target the `angular_refactor` branch
- Build verification: `cd praxis/web-client && npm run build`
- Lint check: `cd praxis/web-client && npm run lint`
- Backend tests: `cd praxis && uv run pytest`

---

## Completion Checklist

- [ ] P0_02 executed (architectural foundation)
- [ ] P1_01 executed
- [ ] P1_03 executed
- [ ] P1_04 executed
- [ ] DEVELOPMENT_MATRIX.md updated
- [ ] Relevant backlog items marked complete
- [ ] Changes committed with descriptive messages
