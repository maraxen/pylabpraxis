# Agent Prompt: 05_pre_merge_finalization

Examine `.agents/README.md` for development context.

**Status:** ✅ Completed  
**Batch:** [260108](./README.md)  
**Backlog:** [cleanup_finalization.md](../../backlog/cleanup_finalization.md)  
**Priority:** P3

---

## Task

Finalize documentation, archive completed work, and clean up workspace before merge.

---

## Implementation Steps

### 1. Archive Snapshot

Rotate completed prompts and backlogs to archive:

```bash
# Create dated archive folder
mkdir -p ".agents/archive/2026-01-08_completed"

# Archive completed prompt batches (if all prompts complete)
# mv ".agents/prompts/250105" ".agents/archive/2026-01-08_completed/"
# mv ".agents/prompts/250106" ".agents/archive/2026-01-08_completed/"
```

### 2. Workspace Audit

Check for and remove temporary/debug files:

```bash
# Find potential temp files
find . -name "*.bak" -o -name "*.tmp" -o -name ".DS_Store" | head -20

# Check for debug console.log statements (frontend)
grep -r "console.log" praxis/web-client/src --include="*.ts" | grep -v ".spec.ts" | head -10

# Check for debugging print statements (backend)
grep -r "print(" praxis/backend --include="*.py" | head -10
```

### 3. Success Metrics Verification

Review and document completion status for major features:

| Feature | Expected | Verified |
|---------|----------|----------|
| Simulation UI Integration | Phase 8 complete | [x] |
| Browser Mode Defaults | All items archived | [x] |
| Chip Filter Standardization | Core complete | [x] |
| JupyterLite REPL | Core complete | [x] |
| Error Handling & State Resolution | Complete | [x] |

### 4. Update Contributor Docs

Update `CONTRIBUTING.md` with agent workflow documentation:

```markdown
## Agentic Development Workflow

This project uses the `.agents/` directory for AI-assisted development:

- **DEVELOPMENT_MATRIX.md**: Central priority/status tracking
- **backlog/**: Detailed work item specifications  
- **prompts/**: Agent dispatch prompts organized by date
- **codestyles/**: Language-specific conventions

See `.agents/README.md` for full documentation.
```

### 5. Final Documentation Updates

- [x] Verify all `DEVELOPMENT_MATRIX.md` items reflect current status
- [x] Verify `ROADMAP.md` milestones are accurate
- [x] Ensure all technical debt items in `TECHNICAL_DEBT.md` are current

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [cleanup_finalization.md](../../backlog/cleanup_finalization.md) | Backlog tracking |
| [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md) | Priority matrix |
| [ROADMAP.md](../../ROADMAP.md) | Milestone tracking |
| [CONTRIBUTING.md](file:///Users/mar/Projects/pylabpraxis/CONTRIBUTING.md) | Contributor guide |
| [archive/](../../archive/) | Completed work archive |

---

## Project Conventions

- **Commands**: Use `uv run` for Python
- Archive format: `archive/YYYY-MM-DD_description/`

---

## On Completion

- [x] Create summary of archived items
- [x] Update [cleanup_finalization.md](../../backlog/cleanup_finalization.md) - mark Pre-Merge Finalization complete
- [x] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [x] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
- [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md) - Known issues
