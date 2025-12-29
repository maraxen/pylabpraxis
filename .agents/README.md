# .agents/ Directory

Agent documentation and coordination for PyLabPraxis development.

---

## 🚀 Quick Start

1. **[NEXT_STEPS.md](./NEXT_STEPS.md)** – Roadmap and active phases
2. **[CONDUCTOR.md](./CONDUCTOR.md)** – Development framework rules
3. **[GEMINI.md](/GEMINI.md)** – Project conventions (root)

---

## 📁 Directory Structure

```
.agents/
├── skills/               # Claude Skills format
│   ├── jules-remote/     # Jules usage guide
│   └── agentic-workflow.md
│
├── prompts/              # Agent onboarding prompts
│   ├── dispatcher.md     # Jules task dispatcher
│   └── context-transfer.md
│
├── status/               # Living status docs
│   ├── backend.md        # Test coverage, priorities
│   └── frontend.md       # Phase status, features
│
├── tasks/                # Active task tracking
│   └── {date}_{task}.md
│
├── archive/              # Historical docs
│
├── NEXT_STEPS.md         # Condensed roadmap
├── CONDUCTOR.md          # Framework rules
├── TECHNICAL_DEBT.md     # Known issues
├── FRONTEND_UI_GUIDE.md  # UI/UX specifications
└── agent_tasks.jsonl     # Machine-readable tasks
```

---

## 📋 Key References

| Document | Purpose |
|----------|---------|
| [status/backend.md](./status/backend.md) | Backend coverage gaps, commands |
| [status/frontend.md](./status/frontend.md) | Frontend phase status |
| [skills/jules-remote/](./skills/jules-remote/SKILL.md) | Jules CLI usage |
| [prompts/dispatcher.md](./prompts/dispatcher.md) | Task dispatch guide |
| [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md) | Known issues |

---

## 🛠️ Quick Commands

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

## 📦 Archive

Historical docs in [`archive/`](./archive/):

- Completed session logs
- Resolved issues
- Deprecated plans

---

*Maintained by: Development Team*
