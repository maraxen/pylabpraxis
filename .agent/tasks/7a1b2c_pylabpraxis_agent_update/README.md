# Task: Update Pylabpraxis .agent/ Directory

## Matrix ID: 7a1b2c

## Status: IN_PROGRESS

## Context

- Priority: P1
- Difficulty: med
- Mode: orchestrator → fixer
- Skills: orchestration, dev-matrix
- Research: -
- Workflows: -

## Objective

Carefully update the pylabpraxis `.agent/` directory to use the new standardized infrastructure from orbitalvelocity, while preserving project-specific content.

## Pre-Requisites

- [x] Skills already synced to `pylabpraxis/.agent/skills/` (done)
- [x] Backup created before any modifications (2026-01-20)

## Phase 1: Backup (REQUIRED FIRST)

```bash
# Create dated backup
cd ~/Projects/pylabpraxis
tar -czf .agent-backup-$(date +%Y%m%d-%H%M%S).tar.gz .agent/
```

## Phase 2: Inventory Current State

Before modifying, understand what's project-specific vs generic:

### Project-Specific (PRESERVE)

- `.agent/DEVELOPMENT_MATRIX.md` - existing tasks
- `.agent/ROADMAP.md` - existing milestones
- `.agent/TECHNICAL_DEBT.md` - existing debt items
- `.agent/NOTES.md` - existing notes
- `.agent/ORCHESTRATION.md` - learned patterns
- `.agent/backlog/` contents - existing backlog
- `.agent/tasks/` contents - existing tasks
- `.agent/research/` contents - existing research
- `.agent/references/` contents - existing references
- `.agent/reports/` contents - existing reports

### Generic (CAN UPDATE)

- `.agent/README.md` - coordination hub docs
- `.agent/templates/` - document templates
- Subdirectory `README.md` files - structure docs
- `.agent/codestyles/` - coding conventions (merge carefully)
- `.agent/pipelines/` - automation sequences
- `.agent/workflows/` - process definitions

## Phase 3: Update Generic Files

1. Update subdirectory READMEs using new template
2. Update `.agent/README.md` to new format
3. Add new templates from orbitalvelocity
4. Sync any missing codestyles

## Phase 4: Verify Integrity

1. Confirm all project-specific content preserved
2. Verify matrix still loads correctly
3. Test a sample task workflow

## Dispatch Strategy

| Subtask | Dispatch | Reason |
|---------|----------|--------|
| Create backup | CLI | Quick, one command |
| Inventory project-specific | Manual (you) | Needs careful review |
| Update READMEs | CLI (parallel) | Simple file updates |
| Verify integrity | Manual (you) | Needs judgment |

## Success Criteria

- [ ] Backup exists at `~/Projects/pylabpraxis/.agent-backup-*.tar.gz`
- [ ] All project-specific content preserved
- [ ] Subdirectory READMEs updated to new format
- [ ] `.agent/README.md` updated
- [ ] New templates available
- [ ] No broken links or references

## Rollback

If something goes wrong:

```bash
cd ~/Projects/pylabpraxis
rm -rf .agent/
tar -xzf .agent-backup-*.tar.gz
```

---

## Execution Log

_Record execution steps here as they happen_
