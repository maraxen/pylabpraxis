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
workspace_handshake(project_root="/Users/mar/Projects/praxis")
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

Using MCP: `workspace_handshake(project_root="/Users/mar/Projects/praxis")`

This connects your session to the correct project database.

### Available Tools

| Tool | Purpose |
|------|---------|
| `workspace_handshake` | Connect to project (required first) |
| `prep_orchestrator` | Get full orchestration context |
| `task(action: "list")` / `task(action: "create")` / `task(action: "update")` | Manage development tasks |
| `dispatch` / `dispatch(action: "status")` | Track agent dispatches |
| `prompt(action: "list")` / `prompt(action: "invoke")` | Load and invoke reusable prompts |
| `skill(action: "list")` / `skill(action: "load")` | Load skill documentation |
| `debt(action: "add")` / `debt(action: "list")` | Track technical debt |
| `report(action: "recon")` / `report(action: "research")` | Store findings |
| `config(action: "backup")` / `config(action: "export")` | Data management |

### 🔄 Pull-Based Task Queue

We have implemented a pull-based work queue where agents can claim pending dispatches instead of being pushed work. This enables:

- Rate-limited execution
- Model-specific task routing
- Self-service task pickup

#### `dispatch(action: "claim")`

- **Purpose**: Claim a pending dispatch from the queue.
- **Input**: `{ target_prefix: "antigravity", model: "claude-sonnet-4" }`
- **Output**: Returns dispatch with prompt and optional system prompt.
- **Behavior**: Atomically marks dispatch as "running" to prevent double-claiming.

#### `dispatch(action: "complete")`

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
const task = await dispatch(action: "claim")({ target_prefix: "antigravity" });
if (task) {
  // 2. Do work
  const result = await doWork(task.prompt);
  // 3. Complete
  await dispatch(action: "complete")({ dispatch_id: task.dispatch_id, status: "completed", result });
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

### ⚠️ Manual Execution Required (Temporary)

**The `execute=true` flag in MCP dispatches currently does NOT spawn CLI processes.** It only records the dispatch and shows the command that would be run.

**Workaround**: After dispatch, manually run the command:

```bash
timeout 300 gemini --model gemini-3-flash-preview -p "YOUR_PROMPT_HERE" 2>&1 | tee .agent/reports/dispatch_ID.log
```

Or have the orchestrator run the command directly via `run_command`.

*This is tracked as technical debt - see `debt(action: "list")()` for status.*

### Migration Note

Database location: [.agent/agent.db](cci:7://file:///Users/mar/Projects/praxis/.agent/agent.db:0:0-0:0)

To re-run migration:

```bash
/Users/mar/Projects/orbitalvelocity/agent-infra-mcp/target/release/agent-infra-mcp \
  --agent-root .agent migrate
```

---

## 📦 Tasks vs Dispatches

**Understanding the Hierarchy**:

- **Tasks** (`tasks` table) are the **Project Backlog** items (Matrix IDs). They represent *what* needs to be done. They persist until the job is `DONE`.
- **Dispatches** (`dispatches` table) are the **Active Sessions** created to *work* on those tasks. A single Task may require multiple Dispatches (e.g., one for research, one for coding, one for review).

**Guidance**:

- **Create a Task** when you have a distinct unit of work tracked in the Matrix (e.g., "Refactor Auth").
- **Fire a Dispatch** when you need an agent to *execute* a step of that work (e.g., "Analyze Auth Code", "Implement Login").
- **Always link them**: `dispatch(..., task_id: "task_123")`.

### 🔗 Automatic Task Context Injection

**When you provide a `task_id` in a dispatch, the system automatically:**

1. **Fetches the task** from the database
2. **Inherits the task's mode** if not explicitly provided in the dispatch
3. **Injects a Task Context block** into the full prompt:

```markdown
# Task Context (ID: abc123)

Title: Fix auth bug
Description: Resolve the login timeout issue affecting production users...
Status: IN_PROGRESS
Priority: P1
```

**The final prompt structure sent to the agent:**

```
[System Prompt]       ← from .agent/agents/{mode}.md
---
[Task Context]        ← auto-injected from task_id
---
[Instructions]        ← your prompt
```

This means you don't need to manually include task details in your dispatch prompt—just provide the `task_id` and the system handles context coupling automatically.

## 🚀 Batch Dispatching

The `dispatch` tool now supports batch operations for parallel execution.

```json
{
  "dispatches": [
    { "target": "antigravity", "prompt": "Research API", "task_id": "t1" },
    { "target": "antigravity", "prompt": "Scaffold DB", "task_id": "t2" }
  ],
  "metadata": { "batch_id": "b1" }
}
```

For **CLI Push** dispatches (`execute: true`), this generates a parallel execution script:

```bash
( gemini ... & )
( gemini ... & )
wait
```

**Track batch status:**

```javascript
dispatch(action: "status")({ batch_id: "b1" })
```

## 📦 Batch Task Creation

You can create multiple tasks in a single request, useful for project scaffolding:

```json
{
  "tasks": [
    { "description": "Setup DB", "priority": "P1" },
    { "description": "Create API", "priority": "P2" }
  ],
  "metadata": { "batch_id": "setup-v1" }
}
```

---

## 💻 Gemini CLI Dispatch

### ⚠️ CRITICAL: Model Selection

**ALWAYS use `cli` target (auto model selection) unless explicitly instructed otherwise.**

```
✅ CORRECT: target: "cli"
❌ WRONG:   target: "cli:gemini-2.5-flash"  (deprecated)
❌ WRONG:   target: "cli:gemini-3-pro"      (use auto instead)
```

The `cli` target automatically selects the best available model. Specifying models manually risks using deprecated or unavailable versions.

### Dispatch Targets

| Target | Model | Use Case |
|--------|-------|----------|
| `cli` | Auto (recommended) | All CLI dispatches |
| `jules` | N/A | Remote Jules agent tasks |
| `antigravity` | Claude | Complex, interactive tasks |

### CLI Dispatch Example

```javascript
mcp_orbitalvelocity_dispatch({
  target: "cli",           // NOT "cli:gemini-2.5-flash"
  mode: "fixer",
  dispatch_type: "push",
  execute: true,
  permissions: ["read_file", "write_file"],
  prompt: "Your task here..."
})
```

### Gemini CLI Headless Skill

For advanced scripting and automation:

- Environment variables: `GEMINI_MODEL_FAST`, `GEMINI_MODEL_DEEP`
- Handling model updates
- Integration with dev matrix

See `global_skills/gemini-cli-headless/SKILL.md`

---

*This document is the entry point. Always start here.*
