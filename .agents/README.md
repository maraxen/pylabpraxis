# .agents/ Directory - Agent Documentation Hub

**Purpose**: Development documentation for agents working on PyLabPraxis  
**Last Updated**: 2025-12-23

---

## 🚀 Quick Start

New to this project? Read these in order:

1. **[HANDOFF.md](./HANDOFF.md)** - Latest handoff notes and current state
2. **[NEXT_STEPS.md](./NEXT_STEPS.md)** - Roadmap with Track A/B references
3. **[CONDUCTOR.md](./CONDUCTOR.md)** - Conductor framework rules
4. **[GEMINI.md](/GEMINI.md)** - Project conventions (root directory)

---

## 📋 Active Implementation Plans

| Document | Purpose |
|----------|---------|
| [TRACK_A_PLAN.md](./TRACK_A_PLAN.md) | **E2E Protocol Execution** - Run `simple_transfer.py` |
| [TRACK_B_PLAN.md](./TRACK_B_PLAN.md) | **UI/UX Polish** - Backend filtering, property separation |
| [PROMPT_TRACK_A.md](./PROMPT_TRACK_A.md) | Agent prompt to start Track A |
| [PROMPT_TRACK_B.md](./PROMPT_TRACK_B.md) | Agent prompt to start Track B |

---

## 📚 Reference Documentation

### Status Tracking

| Document | Purpose |
|----------|---------|
| [BACKEND_STATUS.md](./BACKEND_STATUS.md) | Backend tasks, coverage gaps, commands |
| [FRONTEND_STATUS.md](./FRONTEND_STATUS.md) | Frontend status (concise) |
| [FRONTEND_DEV.md](./FRONTEND_DEV.md) | Frontend development phases |

### Guides & Protocols

| Document | Purpose |
|----------|---------|
| [FRONTEND_UI_GUIDE.md](./FRONTEND_UI_GUIDE.md) | UI/UX style guide, Material 3 |
| [AGENTIC_WORKFLOW.md](./AGENTIC_WORKFLOW.md) | Jules collaboration protocol |
| [CONTEXT_TRANSFER.md](./CONTEXT_TRANSFER.md) | Agent handoff protocol |

### State Files

| File | Purpose |
|------|---------|
| [agent_tasks.jsonl](./agent_tasks.jsonl) | Machine-readable task tracking |

---

## 📦 Archive

Historical documentation preserved in [`archive/`](./archive/):

- Completed planning docs (Angular roadmap, Gemini frontend plan)
- Resolved issues (production bugs, refactoring strategy)
- Completed coordination (Jules handoff, frontend coordination)

---

## 🛠️ Quick Commands

```bash
# Start services
make db-test
PRAXIS_DB_DSN="..." uv run uvicorn main:app --reload --port 8000
cd praxis/web-client && npm start

# Sync definitions
curl -X POST http://localhost:8000/api/v1/discovery/sync-all

# Run tests
uv run pytest                    # Backend
cd praxis/web-client && npm test # Frontend
```

---

**Maintained By**: Development Team
