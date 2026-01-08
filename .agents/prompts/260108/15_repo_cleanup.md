# Agent Prompt: 15_repo_cleanup

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260108](./README.md)  
**Backlog:** [cleanup_finalization.md](../../backlog/cleanup_finalization.md)  
**Priority:** P3

---

## Task

Remove temporary files, debug scripts, and development artifacts from the repository root. Organize remaining utility files.

---

## Files to Address

### Remove

| File | Reason |
|------|--------|
| `.pymon` | pytest-monitor cache (should be gitignored) |
| `debug_*.py` | Temporary debug scripts |
| `verify_queue.py` | One-off verification script |
| `locustfile.py` | Load testing (move to `tests/` or remove) |
| `agents_backup.tar.gz` | Backup file (should not be in repo) |

### Organize

| File | Action |
|------|--------|
| Utility scripts in root | Move to `scripts/` if valuable |
| Test fixtures in wrong locations | Move to `tests/fixtures/` |

---

## Implementation Steps

### 1. Audit Repository Root

```bash
ls -la | grep -v '^d' | head -30  # List files in root
find . -maxdepth 1 -name "debug_*" -o -name "test_*" -o -name "*.pyc"
```

### 2. Remove Unnecessary Files

```bash
rm -f .pymon
rm -f debug_*.py
rm -f verify_queue.py
rm -f agents_backup.tar.gz
# Move or remove locustfile.py based on value
```

### 3. Update .gitignore

Ensure these patterns are in `.gitignore`:

```gitignore
.pymon
debug_*.py
*.tar.gz
```

### 4. Verify Clean State

```bash
git status
git diff --stat
```

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [cleanup_finalization.md](../../backlog/cleanup_finalization.md) | Backlog tracking |
| [.gitignore](file:///Users/mar/Projects/pylabpraxis/.gitignore) | Git ignore patterns |

---

## Project Conventions

- **Commands**: Use `uv run` for Python commands
- Keep repository root clean - scripts go in `scripts/`

See [codestyles/general.md](../../codestyles/general.md) for conventions.

---

## On Completion

- [ ] Commit changes with message: `chore: clean up repository root (remove debug files, update .gitignore)`
- [ ] Update [cleanup_finalization.md](../../backlog/cleanup_finalization.md) - mark Repo Cleanup complete
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
