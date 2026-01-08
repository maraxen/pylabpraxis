# Agent Prompt: [NN]_[prompt_name]

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started | 🟡 In Progress | ✅ Complete  
**Batch:** [YYMMDD](../YYMMDD/README.md)  
**Backlog:** [backlog_item.md](../../backlog/backlog_item.md)  

---

## Task

[Clear, specific description of what the agent should accomplish]

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [backlog_item.md](../../backlog/backlog_item.md) | Work item tracking |
| [file.py](file:///path/to/file.py) | Implementation target |

---

## Project Conventions

- **Commands**: Use `uv run` for all Python commands
- **Backend Tests**: `uv run pytest tests/ -v`
- **Frontend Tests**: `cd praxis/web-client && npm test`
- **Linting**: `uv run ruff check praxis/backend --fix`
- **Type Check**: `uv run pyright praxis/backend`

See [codestyles/](../../codestyles/) for language-specific guidelines.

---

## On Completion

- [ ] Update backlog item status
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md) if applicable
- [ ] Release browser_subagent in [status.json](../../status.json) if used
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
- [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md) - Known issues
