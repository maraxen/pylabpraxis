# Praxis Agent Coordination

Central coordination hub for AI agents working on Praxis development.

---

## 🚀 Quick Start

1. **Check status**: Review [status.json](status.json) for browser subagent availability
2. **Check priorities**: Review [DEVELOPMENT_MATRIX.md](DEVELOPMENT_MATRIX.md) for current work
3. **Read guidelines**: See [codestyles/](codestyles/) for language-specific conventions
4. **Find tasks**: See [backlog/](backlog/) for detailed work items

---

## 📁 Directory Structure

```
.agents/
├── README.md                  # This file
├── DEVELOPMENT_MATRIX.md      # Central tracking table (priority, difficulty, status)
├── ROADMAP.md                 # High-level milestones
├── TECHNICAL_DEBT.md          # Issues and temporary patches
├── NOTES.md                   # Lessons learned, gotchas
├── status.json                # Browser subagent coordination
├── backlog/                   # Detailed plans per development item
├── codestyles/                # Language-specific code style guides
│   ├── python.md
│   ├── typescript.md
│   ├── javascript.md
│   ├── html-css.md
│   └── general.md
├── prompts/                   # Agent prompts
│   ├── reuse/                 # Reusable prompt templates
│   └── YYMMDD/                # Dated prompt batches
├── templates/                 # Document templates
│   ├── agent_prompt.md        # Detailed agent dispatch
│   ├── backlog_item.md        # Work item tracking
│   ├── prompt_batch.md        # Dated batch README
│   └── reusable_prompt.md     # Parameterized prompts
├── reference/                 # Product specs and guides
│   └── hardware_matrix.md     # PLR hardware communication protocols (VID/PID)
├── skills/                    # Agent skill definitions
└── archive/                   # Completed work
```

---

## 📋 Development Tracking

### DEVELOPMENT_MATRIX.md

Central table with **Priority** and **Difficulty** for all items:

| Priority | Difficulty | Item | Status |
|:---------|:-----------|:-----|:-------|
| P2 | 🔴 Complex | Example Item | 🟡 In Progress |

**Difficulty levels** (for agent dispatch):

- 🔴 **Complex**: Requires careful planning, likely debugging
- 🟡 **Intricate**: Many parts, but well-specified tasks
- 🟢 **Easy Win**: Straightforward, minimal ambiguity

**Agents must update this matrix** when completing work or changing status.

### ROADMAP.md

High-level milestones. Update at major milestone completions.

### NOTES.md

Captures lessons learned, specialized knowledge, and "gotchas" discovered during development. Periodically distill patterns into [codestyles/](codestyles/).

---

## 💻 Agent Workflow

### Before Work

1. Check `status.json` - mark browser_subagent as in-use if needed
2. Review `DEVELOPMENT_MATRIX.md` for priorities
3. Review relevant `backlog/` item for context

### During Work

- Follow [codestyles/](codestyles/) for language conventions
- Use `uv run` for all Python commands
- Wrap long commands with `timeout`

### After Work

1. Update `DEVELOPMENT_MATRIX.md` with progress
2. Update `status.json` - release browser_subagent if held
3. Update backlog item with notes/completions

---

## 📝 Prompts System

### Reusable Prompts

Store reusable prompt templates in `prompts/reuse/`:

- Fill placeholders like `{FILE}`, `{COMPONENT}`
- Use for common recurring tasks

### Dated Prompt Batches

Staged execution of prompt sets in `prompts/YYMMDD/`:

- Each folder has a `README.md` listing prompts with status (use [templates/prompt_batch.md](templates/prompt_batch.md))
- Individual prompts should follow the [templates/agent_prompt.md](templates/agent_prompt.md) structure
- Mark prompts complete as they're executed
- When all complete, mark README status as "✅ All Complete"
- Archive-ready folders can be moved to `archive/`

---

## ⚡ Quick Commands

```bash
# Start services
make db-test
PRAXIS_DB_DSN="..." uv run uvicorn main:app --reload --port 8000
cd praxis/web-client && npm start

# Run tests
uv run pytest                    # Backend
cd praxis/web-client && npm test # Frontend

# Linting
uv run ruff check praxis/backend --fix
uv run pyright praxis/backend

# Sync definitions
curl -X POST http://localhost:8000/api/v1/discovery/sync-all
```

---

## 📚 See Also

- [GEMINI.md](../GEMINI.md) - Agent memory and project guidelines
- [README.md](../README.md) - Project overview
