# AGENTS.md

> This project is managed by the **Orbital Velocity Orchestrator** at `~/Projects`.

---

## Orchestration Model

**Subagents receive fully-assembled prompts.** The orchestrator:

1. Selects the agent mode (fixer, recon, designer, etc.)
2. Loads the system prompt from `~/Projects/.agent/agents/{mode}.md`
3. Appends relevant skills from `~/Projects/.agent/skills/`
4. Adds the task-specific prompt
5. Dispatches the complete prompt to this session

**You do NOT need to load modes or skills yourself.** Your instructions are already complete.

---

## MCP Tools (Subagent Scope)

| Tool | Actions | Purpose |
|:-----|:--------|:--------|
| `dispatch` | status, complete | Report progress, mark done |
| `message` | respond, list | Respond to orchestrator |
| `staging` | add | Quick ideas for later |
| `debt` | add | Log technical debt found |
| `artifact` | submit | Submit findings/reports |

**Heartbeat requirement:** Call `dispatch(action: "status")` every 2-3 minutes on long tasks.

**Completion pattern:**

```javascript
mcp_orbitalvelocity_dispatch(action: "complete", payload: {
  dispatch_id: "<your_dispatch_id>",  
  status: "completed",
  result: "Summary of what was accomplished"
})
```

---

## Project: praxis

| Action | Command |
|:-------|:--------|
| Dev Server | `npm start` |
| Build | `npm run build` |
| Tests | `npm test` |
| E2E Tests | `npx playwright test` |
| Lint | `npm run lint` |

### Tech Stack

- **Frontend**: Angular 19 (standalone components)
- **Language**: TypeScript (strict mode)
- **Styling**: CSS Variables + Material Design
- **Build**: Angular CLI / esbuild
- **Testing**: Jest (unit), Playwright (E2E)
- **Persistence**: SQLite Wasm + OPFS

### Structure

```text
src/
├── app/
│   ├── components/     # UI components
│   ├── services/       # Angular services
│   ├── pages/          # Route pages
│   └── models/         # TypeScript interfaces
├── assets/             # Static assets
└── environments/       # Environment configs

e2e/                    # Playwright E2E tests
```
