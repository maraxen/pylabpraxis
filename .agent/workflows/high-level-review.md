---
description: Process for conducting a High Level Review and dispatching Agent Prompts via .agent/prompts
---

# High Level Review Workflow

Trigger this workflow when the user requests a "high level review", "project audit", "status check", or asks "what's next?".

## 1. Context Discovery

Establish the project context by reading the following sources in order:

1. **Project Root**: Read `.agent/README.md` (Primary Source of Truth).
2. **Strategic Context**:
    * Read `.agent/DEVELOPMENT_MATRIX.md` (Active Development Tracking).
    * Read `.agent/ROADMAP.md` (Long Horizon Goals).
    * *Note: Treat these files as high-signal but verify their currency against the actual codebase.*
3. **Tactical Context**: Read `implementation_plan.md` (if active) and `TODO.md`.
4. **Codebase**: Briefly scan for high-priority `FIXME` or `TODO` tags in recently modified files.

## 2. Issue Triage (R.I.C.E. Analysis)

Identify issues and categorize them into the sequential workflow pipeline. Use **R.I.C.E.** (Reach, Impact, Confidence, Effort) to prioritize.

### 🔍 Type I: Inspection (Low Confidence)

* **Goal**: Validate vagueness, reproduce bugs, or audit logs.
* **Output**: A report in `references/` that feeds into a Planning prompt.
* **Skills**: `systematic-debugging`, `web-design-guidelines`.

### 🧠 Type P: Planning (Medium Confidence)

* **Goal**: Take an Inspection report or feature request and design the solution.
* **Output**: A "Spec" or "Plan" in `references/` that guides Execution prompts.
* **Skills**: `senior-architect`, `pylabpraxis-planning`, `writing-plans`.

### 🛠️ Type E: Execution (High Confidence)

* **Goal**: Implement a clear plan.
* **Output**: Code changes via Atomic Commits.
* **Skills**: `senior-fullstack`, `test-driven-development`, `atomic-git-commit`.

## 3. Prompt Generation (The Dispatcher)

**Do not just list tasks.** You must generate **Agent Prompt Files** and a **Reference Directory** using the `dev-prompt-management` skill.

### Structure Setup

1. **Create Batch Folder**: `.agent/prompts/{YYYYMMDD}_{short_desc}/`.
2. **Create References Folder**: `.agent/prompts/{YYYYMMDD}_{short_desc}/references/`.
    * *Usage*: Store findings from Inspection here to be read by Planning prompts. Store Specs from Planning here to be read by Execution prompts.
3. **Create Batch README**: Add a `README.md` in the batch folder summarizing the R.I.C.E. scores.

### Prompt Construction & Naming

Generate markdown files based on `.agent/template/agent_prompt.md`. Adhere to this naming convention and chaining logic:

#### 1. Inspection Prompts (`{ID}_I_{desc}.md`)

* **Context**: Reads project root.
* **Instruction**: "Investigate X. Write your findings to `references/{ID}_findings.md`. Do NOT fix code yet."

#### 2. Planning Prompts (`{ID}_P_{desc}.md`)

* **Context**: Reads `references/{ID}_findings.md` (if coming from Inspection).
* **Instruction**: "Design the solution for X. Write the implementation plan to `references/{ID}_spec.md`."

#### 3. Execution Prompts (`{ID}_E_{desc}.md`)

* **Context**: Reads `references/{ID}_spec.md`.
* **Instruction**: "Implement the spec using **Atomic Commits** via `atomic-git-commit`."
  * **Strict Atomic Commits**: One commit per logical change (e.g., "Refactor utility" vs "Implement Feature").
  * **TDD**: Require **Test-Driven Development** (write test -> fail -> fix).

## 4. Output to User

Present a summary table of the generated prompt chain for dispatch approval:

| ID | Prompt File | Type | Source/Ref | R.I.C.E |
|----|-------------|------|------------|---------|
| 1  | `01_I_inspect_auth.md` | **I**nspect | `> references/01_findings.md` | 8.5 |
| 2  | `02_P_plan_auth_fix.md`| **P**lan | `< references/01_findings.md` | N/A |
| 3  | `03_E_impl_auth_fix.md`| **E**xecute | `< references/02_spec.md` | 9.0 |

**Next Step:**
"I have generated the prompt batch in `.agent/prompts/...`. Shall I execute the first link in the chain?"
