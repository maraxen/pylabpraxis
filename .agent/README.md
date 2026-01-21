# Agent Coordination Hub

Central coordination hub for AI agents working on this project.

---

## 🚀 Quick Start

1. **Check status**: Review [DEVELOPMENT_MATRIX.md](DEVELOPMENT_MATRIX.md) for current work and priorities.
2. **Read guidelines**: See [codestyles/](codestyles/) for language-specific conventions.
3. **Select Agent Mode**: See [../AGENTS.md](../AGENTS.md) to choose the right agent for the job.
4. **Find tasks**: Check [tasks/](tasks/) for active work (linked via Matrix ID).

---

## 📁 Directory Structure

```text
.agent/
├── README.md                  # This file
├── DEVELOPMENT_MATRIX.md      # SINGLE SOURCE OF TRUTH (Priority, Status, Assignments)
├── ROADMAP.md                 # High-level milestones (references Matrix IDs)
├── TECHNICAL_DEBT.md          # Issues and temporary patches
├── NOTES.md                   # Lessons learned, gotchas
├── tasks/                     # Unified Task Units ({id}_task_name/)
│   └── {id}_{name}/           # Isolated task directory
│       ├── README.md          # Unified Task Prompt & Status
│       ├── tracking/          # Incremental progress logs
│       └── artifacts/         # Generated designs/discovery docs
├── backlog/                   # Long-term work items (legacy/persistent)
├── codestyles/                # Language-specific code style guides
├── templates/                 # Document templates (Use these!)
├── references/                # External references and best practices
├── skills/                    # Agent skill definitions (Synced from global_skills)
├── agents/                    # System prompts for different agent modes
└── archive/                   # Completed work
```

---

## 📋 Development Matrix (Source of Truth)

**DEVELOPMENT_MATRIX.md** is the canonical tracking table.

- **ID**: Unique 6-character identifier (e.g., `a1b2c3`).
- **Status**: `TODO`, `IN_PROGRESS`, `BLOCKED`, `REVIEW`, `DONE`.
- **Mode/Skills**: Specifies which agent mode and skills to use.

**Updates**:

- Agents must update the matrix when changing task status.
- Use `grep`/`sed` tools or the `dev-matrix` skill for updates.

---

## 💻 Agent Workflow

### Before Work

1. **Matrix Check**: `grep "| TODO | P1 |" .agent/DEVELOPMENT_MATRIX.md`.
2. **Context**: Load the task ID context from `.agent/tasks/{id}_*/`.
3. **Dispatch**: Use the mode and skills specified in the matrix.

### During Work

- **Task Directory**: Work within `.agent/tasks/{id}_{name}/`.
- **I-P-E-T**: Follow Inspect -> Plan -> Execute -> Test.
- **Status**: Keep the task `README.md` updated.
- **Sync**: Update `DEVELOPMENT_MATRIX.md` on significant state changes.

---

## 📝 Unified Task System

Tasks are housed in `.agent/tasks/{id}_{name}/`.

- **Linkage**: The directory name starts with the Matrix ID.
- **Structure**:
  - `README.md`: Command center.
  - `tracking/`: Logs.
  - `artifacts/`: Outputs.

---

## 📦 Archive System

Completed work moves to `.agent/archive/` to keep the workspace clean.
Use the `archive` scripts or prompts when tasks are typically > 30 days done.

---

## ⚡ Quick Commands (Placeholder)

```bash
# Add project-specific commands here
# e.g., run tests, build, lint
```
