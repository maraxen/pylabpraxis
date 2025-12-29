# Planning Prompt: Pluggable Storage Layer Implementation

Use this prompt to onboard a fresh planning model (e.g., Claude, Gemini, GPT) to review and plan the implementation of the pluggable storage layer.

---

## Prompt

```
You are a senior software architect reviewing a task plan for PyLabPraxis, a laboratory automation platform. Your goal is to:

1. **Review** the task document for completeness, risks, and feasibility
2. **Refine** the implementation plan with specific action items
3. **Create** a phased execution plan with clear milestones
4. **Identify** any architectural concerns or alternative approaches

## Context

PyLabPraxis is a FastAPI + Angular application for controlling laboratory robots. It currently requires PostgreSQL for data persistence and Redis for pub/sub and task queuing. We want to enable a GitHub Pages demo that runs entirely in the browser.

### The Proposal

Rather than creating a "mock mode" fork, we're implementing a **pluggable storage layer** using the Repository Pattern. This allows:
- Production: PostgreSQL + Redis (unchanged)
- Demo/Test: SQLite in-memory + in-process pub/sub
- Future: Edge deployments, other databases

## Required Reading

Before planning, read these documents in order:

1. **Task Document**: `.agents/tasks/2025-12-29_pluggable_storage_demo.md`
   - Contains the full implementation plan, architecture diagrams, and testing strategy

2. **Project Conventions**: `GEMINI.md` (root directory)
   - Architecture overview, coding standards, service layer patterns

3. **Current Database Setup**: `praxis/backend/utils/db.py`
   - Current SQLAlchemy configuration

4. **Redis Usage**: `praxis/backend/api/websockets.py`
   - How Redis is currently used for WebSocket pub/sub

5. **Celery Configuration**: `praxis/backend/core/celery.py`
   - Current task queue setup

6. **Main Application**: `main.py`
   - Application lifespan and service initialization

## Deliverables

After reviewing, provide:

### 1. Architecture Review
- Is the proposed Protocol-based abstraction correct?
- Are there simpler alternatives?
- What edge cases might we miss?

### 2. Refined Implementation Plan
Break down each phase into specific, actionable steps:

```

Phase 1: Storage Abstractions
├── Step 1.1.1: Create protocols.py with KeyValueStore, PubSub, TaskQueue
├── Step 1.1.2: Create memory_adapter.py with InMemoryKeyValueStore
├── Step 1.1.3: Create redis_adapter.py wrapping existing Redis usage
├── Step 1.2.1: Update main.py to use StorageFactory
└── ...

```

### 3. Risk Analysis
For each identified risk:
- Likelihood (Low/Medium/High)
- Impact (Low/Medium/High)
- Specific mitigation steps

### 4. Testing Matrix
Map each component to its test requirements:

| Component | Unit Test | Integration Test | E2E Test |
|-----------|-----------|-----------------|----------|
| InMemoryKeyValueStore | ✓ | ✓ | |
| ... | ... | ... | ... |

### 5. Milestone Timeline
Propose a phased rollout with checkpoints:

- **Milestone 1**: Storage abstractions complete, tests pass with memory backend
- **Milestone 2**: SQLite compatibility verified
- **Milestone 3**: Frontend demo mode working locally
- **Milestone 4**: GitHub Pages deployment live

### 6. Open Questions
List any decisions that need user input before proceeding.

## Constraints

- **No breaking changes** to production setup
- **Python 3.12+**, async/await throughout
- **SQLAlchemy 2.0** patterns (use `Mapped[]`, `mapped_column`)
- Follow existing code style (see GEMINI.md)
- Tests must pass with both memory and PostgreSQL backends

## Output Format

Structure your response as:

1. **Executive Summary** (2-3 sentences)
2. **Architecture Review** (with diagrams if helpful)
3. **Detailed Implementation Plan** (numbered steps)
4. **Risk Matrix** (table format)
5. **Testing Matrix** (table format)
6. **Timeline** (milestone format)
7. **Open Questions** (numbered list)
8. **Recommended First Action** (what to do right now)
```

---

## Files to Provide to the Model

When using this prompt, ensure the model has access to:

1. `.agents/tasks/2025-12-29_pluggable_storage_demo.md` (the task document)
2. `GEMINI.md` (project conventions)
3. `praxis/backend/utils/db.py` (database config)
4. `praxis/backend/api/websockets.py` (Redis usage)
5. `praxis/backend/core/celery.py` (task queue)
6. `main.py` (application lifespan)

---

## Usage

### With Claude Code

```
Review the pluggable storage task and create a detailed implementation plan.
Read: .agents/tasks/2025-12-29_pluggable_storage_demo.md
```

### With Gemini/ChatGPT

Copy the prompt above and attach the relevant files.

### With Jules

```bash
jules remote new --session "Plan pluggable storage implementation" --description "$(cat .agents/prompts/pluggable-storage-planning.md)"
```
