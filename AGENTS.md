# AGENTS.md

> Agent routing document. Read this first.

---

## 🎭 Agent Mode Selection

**Default Mode**: Unless another mode is specified, assume you are in **Evolving-Orchestrator** mode.
Read `.agent/agents/evolving-orchestrator.md` for your system prompt.

To use a different mode, the user will say:

- `@mode_name` (e.g., `@fixer`, `@explorer`)
- "Acting as [mode_name]"
- Reference a specific agent file

### @Mention Convention

**When you see `@mode_name` in a prompt, immediately load `.agent/agents/{mode_name}.md` and adopt that agent's system prompt.**

Examples:

- `@fixer` → Load `.agent/agents/fixer.md`
- `@oracle` → Load `.agent/agents/oracle.md`
- `@recon` → Load `.agent/agents/recon.md`

### Available Modes

| Mode | Trigger | File | Description |
|------|---------|------|-------------|
| **evolving-orchestrator** | (default) | `.agent/agents/evolving-orchestrator.md` | Multi-agent coordinator |
| explorer | `@explorer` | `.agent/agents/explorer.md` | Codebase search |
| librarian | `@librarian` | `.agent/agents/librarian.md` | Documentation |
| oracle | `@oracle` | `.agent/agents/oracle.md` | Architecture |
| designer | `@designer` | `.agent/agents/designer.md` | UI/UX |
| fixer | `@fixer` | `.agent/agents/fixer.md` | Implementation |
| flash | `@flash` | `.agent/agents/flash.md` | Fast execution |
| general | `@general` | `.agent/agents/general.md` | Multi-step |
| investigator | `@investigator` | `.agent/agents/investigator.md` | Investigation |
| recon | `@recon` | `.agent/agents/recon.md` | Reconnaissance |
| deep-researcher | `@deep-researcher` | `.agent/agents/deep-researcher.md` | Research |
| multimodal-looker | `@multimodal-looker` | `.agent/agents/multimodal-looker.md` | Visual |
| summarize | `@summarize` | `.agent/agents/summarize.md` | Summarization |

---

## 🔄 "What's Next?" Protocol

When the user asks "What's next?" or similar:

### Step 0: Connect via MCP

```
workspace_handshake(project_root="/Users/mar/Projects/pylabpraxis")
prep_orchestrator()
```

This returns active tasks, open debt, recent dispatches, and available workflows.

### Step 1: Query the Matrix

Use `prep_orchestrator()` output, or fall back to grep:

```bash
grep "| TODO |" .agent/DEVELOPMENT_MATRIX.md
```

Sort by priority (P1 > P2 > P3 > P4).

### Step 2: Present Top Options

Show top 3 candidates with:

- ID, Priority, Difficulty
- Description
- Required Skills, Research, Workflows

### Step 3: On Selection - Load Full Context

For selected task ID (e.g., `a1b2c3`):

1. **Task Dir**: Read `.agent/tasks/a1b2c3_*/README.md` if exists
2. **Skills**: Load each skill from Skills column
   - Read `.agent/skills/{skill}/SKILL.md` for each
3. **Research**: Load docs from Research column
   - Read `.agent/research/{doc}` for each
4. **Workflows**: Load workflow from Workflows column
   - Read `.agent/workflows/{workflow}.md` for each
5. **Agent Mode**: Load agent prompt from Mode column
   - Read `.agent/agents/{mode}.md`

### Step 4: Format Dispatch Prompt

Include in the dispatch:

```
## Context
- Matrix ID: {id}
- Skills: {list with key points from each}
- Research: {summaries}
- Workflow: {steps}

## Task
{description from matrix}

## Success Criteria
{from task README if exists}
```

### Step 5: Update Matrix

```bash
# Set status
sed -i '' 's/| {id} | TODO/| {id} | IN_PROGRESS/' .agent/DEVELOPMENT_MATRIX.md
# Add agent
sed -i '' 's/| {id} \(.*\)| - |/| {id} \1| @{agent} |/' .agent/DEVELOPMENT_MATRIX.md
```

---

## 🚀 Quick Start

1. **Check matrix**: Review `.agent/DEVELOPMENT_MATRIX.md` for priorities
2. **Read agent prompt**: Load your mode from `.agent/agents/`
3. **Find task context**: Check `.agent/tasks/{id}_*/` for active work
4. **Load skills**: Read skills listed in matrix
5. **Follow workflows**: Apply workflows from matrix

---

## 📁 Directory Structure

```
.agent/
├── README.md              # Coordination hub
├── DEVELOPMENT_MATRIX.md  # SINGLE SOURCE OF TRUTH
├── ROADMAP.md             # Milestones (refs matrix IDs)
├── TECHNICAL_DEBT.md      # Known issues
├── NOTES.md               # Lessons learned
├── agents/                # Agent mode prompts
├── tasks/                 # Active work ({id}_name/)
├── skills/                # Skill definitions
├── workflows/             # Process definitions
├── research/              # Research documents
├── templates/             # Document templates
├── backlog/               # Long-term items
├── archive/               # Completed work
└── ...
```

---

## 🛠️ Skills Integration

Skills are referenced in the DEVELOPMENT_MATRIX.md Skills column.

When dispatching or working on a task:

1. Parse the Skills column (comma-separated)
2. Load each `.agent/skills/{skill}/SKILL.md`
3. Include relevant guidance in dispatch prompt
4. Follow skill instructions during execution

Common skills: `tdd`, `debugging`, `ui-ux-pro-max`, `senior-architect`, etc.

---

## 📊 Dev Matrix Skill

For programmatic matrix interaction, use the `dev-matrix` skill:

- Add tasks with proper ID generation
- Update status via grep/sed
- Query next items
- Link tasks to directories

See `.agent/skills/dev-matrix/SKILL.md`

---

## 🎛️ Orchestration Skill

For multi-agent coordination patterns, use the `orchestration` skill:

- CLI-compatible vs interactive-only agents
- Model selection (flash vs pro) by task type
- Parallel vs sequential dispatch patterns
- Cross-agent handoff protocols

See `global_skills/orchestration/SKILL.md`

---

## 🔌 MCP Infrastructure

**Unified MCP Server**: `agent-infra`

### Session Start Protocol

**Always call `workspace_handshake` at session start:**

Using MCP: `workspace_handshake(project_root="/Users/mar/Projects/pylabpraxis")`

This connects your session to the correct project database.

### Available Tools

| Tool | Purpose |
|------|---------|
| `workspace_handshake` | Connect to project (required first) |
| `prep_orchestrator` | Get full orchestration context |
| `task_list` / `task_create` / `task_update` | Manage development tasks |
| `dispatch` / `dispatch_status` | Track agent dispatches |
| `prompt_list` / `prompt_invoke` | Load and invoke reusable prompts |
| `skill_list` / `skill_load` | Load skill documentation |
| `debt_add` / `debt_list` | Track technical debt |
| `report_recon` / `report_research` | Store findings |
| `backup_create` / `export_markdown` | Data management |

### 🔄 Pull-Based Task Queue

We have implemented a pull-based work queue where agents can claim pending dispatches instead of being pushed work. This enables:

- Rate-limited execution
- Model-specific task routing
- Self-service task pickup

#### `claim_dispatch`

- **Purpose**: Claim a pending dispatch from the queue.
- **Input**: `{ target_prefix: "antigravity", model: "claude-sonnet-4" }`
- **Output**: Returns dispatch with prompt and optional system prompt.
- **Behavior**: Atomically marks dispatch as "running" to prevent double-claiming.

#### `complete_dispatch`

- **Purpose**: Mark a claimed dispatch as completed or failed.
- **Input**: `{ dispatch_id: "d123", status: "completed", result: "Summary" }`

#### Target Format Convention

| Target | Description |
|--------|-------------|
| `antigravity` | Any Claude Code agent |
| `antigravity:claude-sonnet-4` | Claude Sonnet 4 |
| `antigravity:gemini-3-pro-high` | Gemini Pro high context |
| `antigravity:gemini-3-flash` | Gemini Flash |
| `cli:gemini-3-pro-preview` | External Gemini CLI |
| `jules` | Jules remote agent |

#### Example Session Loop

```javascript
// 1. Claim task
const task = await claim_dispatch({ target_prefix: "antigravity" });
if (task) {
  // 2. Do work
  const result = await doWork(task.prompt);
  // 3. Complete
  await complete_dispatch({ dispatch_id: task.dispatch_id, status: "completed", result });
}
```

### ⚡ Push Mode Permissions

When using `dispatch_type="push"`, you should specify explicit permissions instead of relying on a blanket `--yolo` mode whenever possible. This follows the principle of least privilege.

```javascript
dispatch({
  target: "cli:gemini-3-pro-preview",
  dispatch_type: "push",
  execute: true,
  // Specify only the tools needed for this task
  permissions: ["write_file", "read_file", "run_shell_command"],
  mode: "fixer",
  prompt: "..."
});
```

The system will automatically configure the CLI session with these permissions, ensuring the agent has exactly what it needs to complete the task safely.

### Migration Note

Database location: [.agent/agent.db](cci:7://file:///Users/mar/Projects/pylabpraxis/.agent/agent.db:0:0-0:0)

To re-run migration:

```bash
/Users/mar/Projects/orbitalvelocity/agent-infra-mcp/target/release/agent-infra-mcp \
  --agent-root .agent migrate
```

---

## 💻 Gemini CLI Headless Skill

For scripting and automation via Gemini CLI:

- Model selection: `--model gemini-2.5-flash` vs `gemini-2.5-pro`
- Environment variables: `GEMINI_MODEL_FAST`, `GEMINI_MODEL_DEEP`
- Handling model accession updates
- Integration with dev matrix

See `global_skills/gemini-cli-headless/SKILL.md`

---

*This document is the entry point. Always start here.*
