---
name: agentic-workflow
description: Use this skill when coordinating between strategic AI agents (Claude, Gemini) and tactical agents (Jules). Defines roles, dispatch protocols, and context injection best practices.
---

# Agentic Workflow Protocol

This document defines the collaboration protocol between the **Advanced Coding Agent** (Strategic Agent, e.g., Gemini 3 Thinking, Claude Opus, GPT-5 Codex) and **Jules** (Tactical Agent) to maximize development velocity.

---

## 1. Agent Roles

### 🧠 Advanced Coding Agent (Strategic Architect)

* **Examples**: Gemini 3 Thinking, Claude Opus, GPT-5 Codex.
* **Scope**: System architecture, complex refactoring, multi-file feature implementation, planning, and high-level decision making.
* **Responsibility**:
  * Analyzing large-scale problems.
  * Designing implementation plans.
  * Writing critical/skeleton code.
  * Dispatching tactical tasks to Jules.
  * Finalizing and verifying work.

### ⚡ Jules (Tactical Engineer)

* **Scope**: Targeted implementation, linting fixes, test writing, boilerplate generation, and isolated bug fixes.
* **Responsibility**:
  * Executing clear, scoped directives.
  * Fixing specific linter errors (Ruff/Pyright).
  * Writing unit tests for defined interfaces.
  * Running migrations or repetitive refactors.

---

## 2. Dispatching Tasks to Jules

When the Advanced Coding Agent identifies independent or lower-context subtasks, they should be dispatched to Jules via the CLI.

### Command Structure

Use `jules new` with a strictly structured prompt:

```bash
jules new "<ACTION> <SCOPE>. <CONTEXT>. <CONSTRAINT>."
```

* **ACTION**: verb (Fix, Create, Refactor).
* **SCOPE**: Specific files or error codes.
* **CONTEXT**: Necessary background (e.g., "Use the new AtomicSystem class").
* **CONSTRAINT**: What NOT to do (e.g., "Do not change the public API").

### Examples

**Simple Linting Fix:**

```bash
jules new "Fix Ruff F401 (unused imports) in praxis/backend/core. Do not remove imports marked with # noqa."
```

**Boilerplate Generation:**

```bash
jules new "Create CRUD endpoints for DeckOrm in praxis/backend/api/decks.py keying off the pattern in users.py. Use crud_router_factory."
```

**Isolated Logic:**

```bash
jules new "Implement the 'calculate_center_of_mass' function in praxis/backend/geometry/metrics.py. Input is a numpy array of coordinates. Add type hints."
```

---

## 3. Status Monitoring & Management

Monitor and manage Jules sessions using the following commands:

### Check Active Sessions

List all running or completed sessions:

```bash
jules remote list --session
```

### View Session Logs

See the detailed output and thoughts of a specific session:

```bash
jules remote log <SESSION_ID>
```

*Tip: user `jules remote log --latest` for the most recent session.*

### Show Session Details

Get high-level status and metadata:

```bash
jules remote show <SESSION_ID>
```

---

## 4. Context Injection

Jules does not share the Advanced Coding Agent's full context window. You must explicitly inject necessary context.

* **Reference Files**: Mention key files explicitly in the prompt.
* **Patterns**: briefly explain the pattern to follow (e.g., "Follow the repository pattern in `users.py`").
* **Do Not Assume**: Jules does not know about previous conversation history.

---

## 5. Workflow Lifecycle

1. **Advanced Coding Agent** plans the feature.
2. **Advanced Coding Agent** identifies 3 subtasks suitable for **Jules**.
3. **Advanced Coding Agent** or User runs `jules new` commands.
4. User monitors status via `jules remote list --session`.
5. **Jules** completes tasks and opens PRs/pushes changes.
6. **Advanced Coding Agent** pulls changes, reviews, and integrates.
