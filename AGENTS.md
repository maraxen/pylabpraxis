# AGENTS.md

> Agent entry point for the Pylabpraxis codebase.

---

## 🚀 Quick Start

1. **Read context**: Start with [.agent/README.md](.agent/README.md)
2. **Check priorities**: Review [.agent/DEVELOPMENT_MATRIX.md](.agent/DEVELOPMENT_MATRIX.md)
3. **Find your task**: Check [.agent/tasks/](.agent/tasks/) for active work
4. **Follow conventions**: See [.agent/codestyles/](.agent/codestyles/)

---

## ⚡ Performance Rules

- **Playwright Tests**: ALWAYS use a timeout with targeted test commands to prevent stalling (e.g., `timeout 60s npx playwright test [spec]`).

---

## ⚠️ Orchestration Principle

**Orchestration agents must orchestrate tasks, not execute them directly.**

When using multi-agent workflows:
- Orchestrators should delegate work to specialist agents
- Do not perform implementation work yourself when a specialist exists
- Use @explorer, @librarian, or reconnaissance agents for codebase exploration
- Check `.agent/ORCHESTRATION.md` for lessons learned and delegation patterns
- Your role is to coordinate, verify, and integrate results

---

## 📁 Directory Structure

```
.agent/
├── README.md              # Coordination hub documentation
├── DEVELOPMENT_MATRIX.md  # Priority/difficulty tracking
├── ROADMAP.md             # Strategic milestones
├── TECHNICAL_DEBT.md      # Known issues and patches
├── NOTES.md               # Lessons learned and gotchas
├── ORCHESTRATION.md       # Orchestration lessons and delegation patterns
├── tasks/                 # Active work units (Unified I-P-E-T)
├── backlog/               # Long-term work item specs
├── skills/                # 23 reusable skill definitions
├── templates/             # Document templates (10 total)
├── workflows/             # Process definitions
├── pipelines/             # Specialized multi-stage pipelines
├── references/            # Technical resources
├── codestyles/            # Language conventions
├── prompts/               # Dispatch prompts
└── archive/               # Completed work
```

---

## 🛠️ Skills Catalog

| Skill | Trigger | Description |
|-------|---------|-------------|
| `agentic-workflow` | Multi-agent coordination | Strategic/Tactical agent protocol |
| `jules-remote` | `jules new`, `jules remote` | Dispatch to Jules tactical agent |
| `senior-architect` | System design | Architecture diagrams, tech decisions |
| `senior-fullstack` | Full implementation | React, Next.js, Node.js, GraphQL |
| `systematic-debugging` | Bug investigation | Root cause analysis methodology |
| `test-driven-development` | Feature work | Red-green-refactor workflow |
| `test-fixing` | Failing tests | Smart error grouping and fixes |
| `playwright-skill` | Browser automation | E2E testing, screenshots |
| `webapp-testing` | Frontend testing | Local app verification |
| `frontend-design` | UI creation | High-quality interfaces |
| `ui-ux-pro-max` | Design intelligence | 50 styles, 21 palettes |
| `theme-factory` | Styling artifacts | 10 preset themes |
| `web-design-guidelines` | UI review | Accessibility, best practices |
| `writing-plans` | Planning | Multi-step task planning |
| `verification-before-completion` | Pre-commit | Evidence before assertions |
| `atomic-git-commit` | Committing | Logical commit grouping |
| `git-pushing` | Push changes | Conventional commits |
| `using-git-worktrees` | Feature isolation | Worktree management |
| `code-maintenance` | Health checks | Linting, audits, cleanup |
| `prompt-engineering` | Prompt optimization | Debugging agent behavior |
| `pylabpraxis-planning` | Project planning | Backlog, matrix updates |
| `loki-mode` | Autonomous startup | Multi-agent orchestration |
| `backend-dev-guidelines` | Backend work | Express, Prisma patterns |

---

## 📋 Workflows

| Workflow | Command | Purpose |
|----------|---------|---------|
| [high-level-review](.agent/workflows/high-level-review.md) | `/high-level-review` | R.I.C.E. triage and prompt chain generation |
| [frontend-polish](.agent/workflows/frontend-polish.md) | - | Capture → Analyze → Fix → Validate pipeline |

---

## 📝 Templates Index

| Template | Use Case |
|----------|----------|
| `unified_task.md` | I-P-E-T task tracking |
| `agent_prompt.md` | Single implementation task |
| `plan.md` | Implementation plans |
| `research.md` | Research/discovery |
| `investigation.md` | Debugging/root cause |
| `handoff.md` | Session handoff notes |
| `backlog_item.md` | Long-term work items |
| `reference_document.md` | External references |
| `reusable_prompt.md` | Common prompts |
| `prompt_batch.md` | Grouped prompts |

---

## 🤖 Subagent Roles

| Role | Specialty | When to Use |
|------|-----------|-------------|
| **Explorer** | Codebase navigation | Finding files, understanding structure |
| **Librarian** | Documentation | Reference management, knowledge capture |
| **Oracle** | Architecture | Design decisions, planning, trade-offs |
| **Designer** | UI/UX | Visual polish, frontend implementation |
| **Fixer** | Bug resolution | Debugging, test repair, hotfixes |

---

## 📚 Key Documents

- [DEVELOPMENT_MATRIX.md](.agent/DEVELOPMENT_MATRIX.md) - Current priorities (P1-P4)
- [.agent/ORCHESTRATION.md](.agent/ORCHESTRATION.md) - Orchestration learning log & strategies
- [ROADMAP.md](.agent/ROADMAP.md) - Strategic milestones
- [TECHNICAL_DEBT.md](.agent/TECHNICAL_DEBT.md) - Known issues
- [NOTES.md](.agent/NOTES.md) - Gotchas and lessons learned
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

---

## ⚡ Quick Commands

```bash
# Backend
uv run pytest                              # Run tests
uv run ruff check praxis/backend --fix     # Lint

# Frontend
cd praxis/web-client
npm run build                              # Build
npm run start:browser                      # Dev server
npx vitest [target] --run                  # Tests
```
