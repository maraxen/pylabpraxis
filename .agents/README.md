# .agents/ Directory

Agent documentation and coordination for Praxis development.

---

## Quick Start

1. **[ROADMAP.md](./ROADMAP.md)** - Current priorities and status
2. **[backlog/](./backlog/)** - Detailed task tracking by area
3. **[reference/](./reference/)** - Product specs and guides

---

## Directory Structure

```
.agents/
├── ROADMAP.md              # Master roadmap and priorities
├── TECHNICAL_DEBT.md       # Known technical issues
├── backlog/
│   ├── ui-ux.md            # UI/UX features and polish
│   ├── backend.md          # Backend and infrastructure
│   ├── cleanup.md          # Codebase standards, rename
│   └── docs.md             # Documentation priorities
├── reference/
│   ├── product.md          # Product vision
│   ├── product-guidelines.md
│   ├── tech-stack.md       # Technology choices
│   ├── workflow.md         # Development workflow
│   └── ui-guide.md         # UI/UX specifications
├── skills/                 # Agent skill definitions
├── prompts/                # Agent onboarding prompts
├── status/                 # Living status docs (legacy)
└── archive/                # Historical docs
    └── conductor-tracks/   # Archived development tracks
```

---

## Backlog Areas

| File | Focus |
|------|-------|
| [backlog/ui-ux.md](./backlog/ui-ux.md) | Visual polish, interactions, data viz |
| [backlog/backend.md](./backlog/backend.md) | APIs, services, PLR integration |
| [backlog/cleanup.md](./backlog/cleanup.md) | Naming, standards, pre-merge |
| [backlog/docs.md](./backlog/docs.md) | Documentation, demos, guides |

---

## Quick Commands

```bash
# Start services
make db-test
PRAXIS_DB_DSN="..." uv run uvicorn main:app --reload --port 8000
cd praxis/web-client && npm start

# Run tests
uv run pytest                    # Backend
cd praxis/web-client && npm test # Frontend

# Sync definitions
curl -X POST http://localhost:8000/api/v1/discovery/sync-all
```

---

## Agent Guidelines

When working on tasks:

1. Check [ROADMAP.md](./ROADMAP.md) for current priorities
2. Find detailed tasks in [backlog/](./backlog/)
3. Reference [reference/workflow.md](./reference/workflow.md) for dev process
4. Update task status as you work
5. Use "Praxis" (not "PyLabPraxis") in all new content
6. Use "machines" (not "instruments") consistently

---

*Maintained by: Development Team*
