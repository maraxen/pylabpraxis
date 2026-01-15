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

```text
.agent/
├── README.md                  # This file
├── DEVELOPMENT_MATRIX.md      # Central tracking table (priority, difficulty, status)
├── ROADMAP.md                 # High-level milestones
├── TECHNICAL_DEBT.md          # Issues and temporary patches
├── NOTES.md                   # Lessons learned, gotchas
├── status.json                # Browser subagent coordination
├── tasks/                     # Unified Task Units (Unified I-P-E-T)
│   └── YYMMDD/                # Dated task batches
│       └── [task_name]/       # Isolated task directory
│           ├── README.md      # Unified Task Prompt & Status
│           ├── tracking/      # Incremental progress logs
│           └── artifacts/     # Generated designs/discovery docs
├── backlog/                   # Detailed work items (legacy/persistent)
├── codestyles/                # Language-specific code style guides
├── templates/                 # Document templates
│   ├── unified_task.md        # Unified I-P-E-T task template
│   └── ...
├── references/                # External references and best practices
├── skills/                    # Agent skill definitions
└── archive/                   # Completed work
```

---

## 📋 Development Tracking

### DEVELOPMENT_MATRIX.md

Central table with **Priority** and **Difficulty** for all items.

**Difficulty levels** (for agent dispatch):

- 🔴 **Complex**: Requires careful planning, likely debugging
- 🟡 **Intricate**: Many parts, but well-specified tasks
- 🟢 **Easy Win**: Straightforward, minimal ambiguity

**Agents must update this matrix** when completing work or changing status.

---

## 💻 Agent Workflow

### Before Work

1. Review `DEVELOPMENT_MATRIX.md` for priorities.
2. Select or create a task in `tasks/YYMMDD/[task_name]/`.
3. Review `README.md` in the task directory for unified context.

### During Work

- Follow [codestyles/](codestyles/) for language conventions.
- **Unified I-P-E-T**: Follow the Inspect -> Plan -> Execute -> Test flow within the task document.
- **State Management**: Update the `README.md` status and tracking elements frequently so work can resume seamlessly.
- **Frontend Styling**: Always use theme variables (CSS variables).
- **Frontend Testing**: Run tests using `npx vitest [target] --run` within `praxis/web-client`.
- Use `uv run` for all Python commands.
- Wrap long commands with `timeout`.

---

## 🤖 Jules Skill

Use the **Jules** skill (`.agent/skills/jules-remote/`) to dispatch atomic coding tasks to Google's autonomous coding agent.

### When to Use

- **Atomic Tasks**: Unit tests, single components, bug fixes with reproduction steps.
- **New Files**: Creating services or components from scratch.

### Quick Workflow

1. **Dispatch**: `jules new --session "Task Title" "Detailed Description..."`
2. **List**: `jules remote list --session`
3. **Review**: `jules remote pull --session <ID>` (downloads patch for review)
4. **Apply**: `jules remote pull --session <ID> --apply`

See [.agent/skills/jules-remote/SKILL.md](skills/jules-remote/SKILL.md) for full documentation and templates.

---

## 📝 Unified Task System

### Layout

Tasks are housed in `.agent/tasks/YYMMDD/[task_name]/`.

Each task directory contains:

- **README.md**: The primary command center. Contains the I-P-E-T phases, Current Status, and Definition of Done.
- **tracking/**: Files for logging incremental data (e.g., large grep results, temporary thought blocks).
- **artifacts/**: Persistent outputs like design specs, audit reports, or generated diagrams.

### Phase Gates

1. **Inspect (I)**: Gather information. No code edits.
2. **Plan (P)**: Draft implementation strategy. Get verification.
3. **Execute (E)**: Apply changes.
4. **Test (T)**: Verify and document results.

Mark phases as complete in the `README.md` before proceeding.
Summary: This structure ensures that even if an agent session is interrupted, the next agent has a clear state of mind and knows exactly where to pick up.

### Maintenance Prompts

For regular health audits, use the prompts in `prompts/reuse/maintenance/`:

- **Per-audit**: linting, type_checking, test_coverage, docstring_audit, todo_audit
- **Quarterly**: ci_review, docs_audit, dependency_audit, security_audit, dead_code_cleanup, dry_audit
- **As needed**: performance_audit

See [prompts/reuse/maintenance/README.md](prompts/reuse/maintenance/README.md) for usage.

---

## 📚 References System

The `references/` directory maintains external documentation and best practices:

- `testing/` - Testing strategies, pytest/Vitest patterns
- `backend/` - FastAPI, SQLAlchemy, PyLabRobot patterns
- `frontend/` - Angular, RxJS, browser mode patterns
- `architecture/` - System design decisions

Use [templates/reference_document.md](templates/reference_document.md) to add new references.

---

## 📦 Archive System

The `.agent/archive/` directory is used to store completed work and keep the main workspace clean.

- **Automated Archiving**: Use the prompt in `.agent/archive/UPDATE_ARCHIVE.md` to consolidate completed prompts, summaries, and artifacts into `archive.tar.gz`.
- **Manifest**: Check `.agent/archive/COMPRESSED_ARCHIVE.md` to see what is currently stored in the archive without unpacking it.

---

## ⚡ Quick Commands

```bash
# Start services
make db-test
PRAXIS_DB_DSN="..." uv run uvicorn main:app --reload --port 8000
cd praxis/web-client && npm start

# Run tests
uv run pytest                                # Backend
cd praxis/web-client && npx vitest [target] --run # Frontend

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
