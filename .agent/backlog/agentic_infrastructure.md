# Backlog: Agentic Infrastructure Improvements

**Status:** 🟢 Planned
**Difficulty:** 🟡 Intricate
**Area:** Agentic/Process
**Created:** 2026-01-15

---

## Goal

Improve the `.agent/` workflow structure, consolidate I-P-E-T phases, and establish clear separation of concerns for project management artifacts.

---

## Items

### 501 - Maintenance Audit Prompt

**Priority:** Low

Create a generic reusable prompt that audits `.agent/` health:
- Check if `.agent/archive` needs cleanup
- Identify stale prompts/tasks
- Suggest maintenance actions

### 502 - Structured Multi-Stage Workflow

**Priority:** Medium

Formalize the end-to-end development cycle:
1. Clarifying Questions → Specification
2. Inspection → Discovery artifacts
3. Planning → Implementation plan
4. Execution → Code changes

**Action**: Create artifact template `.agent/templates/artifact.md`

### 503 - Project Management Separation of Concerns

**Priority:** Low

Establish single sources of truth:
- `ROADMAP.md`: Strategic phases
- `DEVELOPMENT_MATRIX.md`: Current iteration
- `backlog/`: Detailed issue tracking
- `artifacts/`: Design documents
- `prompts/` or `tasks/`: Execution units

### 504 - .agent Folder Optimization

**Priority:** Medium

Consolidate I-P-E-T into unified task directories:
- Move from flat `prompts/YYMMDD/` to `tasks/task_name/`
- Single README per task with all phases
- Include `tracking/` and `artifacts/` subdirectories

**Status:** Partially implemented (see `unified_task.md` template)

---

## Notes

- Items 502 and 504 are partially addressed by `pylabpraxis-planning` skill
- These are meta-improvements that enhance agent productivity
- Low urgency but high leverage for future work

---

## References

- Technical Debt IDs: 501, 502, 503, 504
- [pylabpraxis-planning skill](./../skills/pylabpraxis-planning/SKILL.md)
- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md)
