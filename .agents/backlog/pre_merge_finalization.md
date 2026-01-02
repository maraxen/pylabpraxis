# Pre-Merge Finalization & Cleanup

**Status**: Pending
**Priority**: P1 (Critical before merge)
**Goal**: Prepare the codebase and documentation for merging into `main`, ensuring a clean slate for future development and establishing robust agentic workflows.

## 1. Documentation & Planning Archival

- [ ] **Create Archive Snapshot**:
  - Create `.agents/archive/v0.1-mvp-complete/`.
  - Move current `ROADMAP.md` and `DEVELOPMENT_MATRIX.md` to this archive.
  - Copy current `.agents/backlog/` to `.agents/archive/v0.1-mvp-complete/backlog/` (snapshot).
- [ ] **Establish Long-Term Docs**:
  - Create fresh `.agents/ROADMAP.md` focused on Post-MVP/Long-Term goals.
  - Create fresh `.agents/DEVELOPMENT_MATRIX.md` populating it with existing P3/P4 items from the old matrix (e.g., Device Profiles, DES Scheduling).
  - Update live `.agents/backlog/*.md` files: Remove completed (✅) items, keeping only active/future tasks.

## 2. Contributing Guide Enhancement

- [ ] **Update `CONTRIBUTING.md`**:
  - Add "Agentic Development Workflow" section.
  - **Transparency**: Explain expectation for agents to read/update `.agents/` docs for context.
  - **Commit Expectations**: Mention pre-commit hooks, `make lint`, `make typecheck`.
  - **Workflow**: How to pick a task from the Matrix, create a plan, update the Matrix, and implement.

## 3. Codebase Cleanup

- [ ] **Configuration Merger**:
  - Move `ty.toml` content into `pyproject.toml` under `[tool.ty]`.
  - Delete `ty.toml`.
  - Delete `ty_baseline.txt`, `ty_errors*.txt`.
- [ ] **File Reorganization**:
  - Move `locustfile.py` -> `tests/performance/locustfile.py`.
  - Move root scripts (`debug_*.py`, `verify_queue.py`) -> `scripts/`.
  - Move stray root markdown prompts -> `.agents/archive/prompts/`.

## 4. Reusable Agent Prompts (New Feature)

Create a suite of reusable markdown prompts in `.agents/prompts/planning/` to help agents autonomously select and plan work.

- [ ] **Design Prompts**:
  - **Goal**: Review `DEVELOPMENT_MATRIX.md`, `ROADMAP.md`, and `backlog/*.md` to select appropriate items.
  - **Variants**:
        1. `simple_task_selection.md`: For small bugs, cleanup, UI polish (S/M difficulty).
        2. `medium_feature_planning.md`: For new features requiring implementation plans (M/L difficulty).
        3. `complex_architecture_review.md`: For major refactors or system-wide changes (L/XL difficulty).
- [ ] **Prompt Requirements**:
  - **Interactive**: Must instruct the agent to ask the User for clarification and targeted feedback before finalizing the plan.
  - **Context-Aware**: Instructions to read the definition of "Done" and existing architectural constraints.
  - **Evolution**: Include a "Meta-Correction" section where the agent (or user) can record what went wrong with the prompt usage to improve it for next time.
