# .agents/ Directory - Development Documentation

This directory contains development documentation for agents working on the PyLabPraxis project.

**Last Updated**: 2025-12-21

---

## 📁 Active Documents

### NEXT_STEPS.md ⭐ NEW
**Purpose**: **Roadmap**: Lessons learned and prioritized next steps for development.
**Updated**: 2025-12-21
**Contents**:
- API endpoint fixes and lessons learned
- PLR discovery issues (generic vs concrete classes)
- Simulation mode implementation plan
- Asset management PLR autofill
- Deck visualizer integration
- Example protocol library

**Use When**: Planning next development work, understanding current blockers.

---

### FRONTEND_DEV.md
**Purpose**: **Master Plan**: The active roadmap for Angular frontend development.
**Updated**: 2025-12-16
**Contents**:
- Implementation checklist for Phase 2 (Features) & Phase 3 (Polish)
- Formly integration plan
- Status Bar implementation plan
- E2E testing strategy

**Use When**: Planning active frontend development tasks.

---

### FRONTEND_COORDINATION.md
**Purpose**: **Live Sync**: Real-time task claiming and file locking for multi-agent work.
**Updated**: Real-time
**Contents**:
- Currently active agents and their tasks
- File locks to prevent conflicts
- Task assignment board
- Communication log

**Use When**: Starting work, claiming tasks, checking for conflicts.

---

### FRONTEND_UI_GUIDE.md
**Purpose**: **Style Guide**: UI/UX specifications, component choices, and type mapping.
**Updated**: 2025-12-16
**Contents**:
- Core architectural decisions (MatTable, Formly, SVG)
- Type mapping (Python -> Formly/Material)
- Color palette and typography
- Component usage guidelines

**Use When**: Implementing new UI components to ensure consistency.

---

### BACKEND_STATUS.md
**Purpose**: Current state of backend development and remaining tasks
**Updated**: 2025-12-11
**Contents**:
- ✅ Major accomplishments (refactoring, bug fixes, test optimization)
- Tier 1-3 task organization by complexity
- Coverage gap analysis
- Quick reference commands

**Use When**: Planning backend work, checking task status

---

### FRONTEND_STATUS.md
**Purpose**: Current state of Angular frontend development and remaining tasks
**Updated**: 2025-12-16
**Version**: v0.2.0-beta
**Contents**:
- Technology stack (Angular 21, Material 3, NgRx Signals)
- Feature completeness matrix
- API integration status
- Project structure reference

**Use When**: High-level progress tracking.

---

### ANGULAR_FRONTEND_ROADMAP.md
**Purpose**: Angular migration roadmap and architecture decisions
**Status**: Reference document
**Contents**:
- Tech stack decisions
- Feature module specifications
- Development phases timeline
- API integration points

**Use When**: Understanding frontend architecture decisions

---

### AGENTIC_WORKFLOW.md
**Purpose**: Protocol for collaboration between Advanced Coding Agents and Jules
**Status**: Current
**Contents**:
- Agent roles and responsibilities
- Task dispatching patterns
- Status monitoring commands
- Workflow lifecycle

**Use When**: Coordinating multi-agent workflows, dispatching tasks to Jules

---

### CONTEXT_TRANSFER.md
**Purpose**: Protocol for context handoffs between agents
**Status**: Current (if exists)
**Use When**: Starting new work session, handing off to another agent

---

### agent_tasks.jsonl
**Purpose**: Machine-readable task tracking
**Format**: JSONL (one JSON object per line)
**Fields**: id, tier, title, status, assignee, files, dependencies, created, updated
**Use When**: Programmatic task management, status queries

---

## 📦 Archive

### archive/PRODUCTION_BUGS_RESOLVED_20251208.md
**Original**: PRODUCTION_BUGS.md
**Archived**: 2025-12-11
**Reason**: All 3 production bugs have been resolved
**Contents**:
- Bug 1: Missing `fqn` field (HIGH) - ✅ RESOLVED
- Bug 2: Field name mismatch (MEDIUM) - ✅ RESOLVED
- Bug 3: `json.load()` vs `json.loads()` (LOW) - ✅ RESOLVED

---

### archive/REFACTORING_STRATEGY_COMPLETED_20251209.md
**Original**: REFACTORING_STRATEGY.md
**Archived**: 2025-12-11
**Reason**: All major module refactoring completed (Dec 9, 2025)
**Contents**:
- workcell_runtime: 1274 lines → 7+ file submodule ✅
- orchestrator: 963 lines → 5+ file submodule ✅
- asset_manager: 919 lines → 5+ file submodule ✅
- decorators: 735 lines → 4+ file submodule ✅

**Historical Reference**: Useful for understanding refactoring patterns if extending to other modules

---

### archive/FRONTEND_DEV_FLUTTER_DEPRECATED.md
**Original**: FRONTEND_DEV.md
**Archived**: 2025-12-11
**Reason**: Frontend migrated from Flutter to Angular v21
**Note**: Historical reference only - do not use for current development

---

## 🎯 Quick Start for New Agents

1. **Read first**:
   - `FRONTEND_DEV.md` - Active frontend plan
   - `FRONTEND_COORDINATION.md` - Check for active agents/locks
   - `BACKEND_STATUS.md` - Backend tasks and state
   - `AGENTIC_WORKFLOW.md` - Collaboration protocol

2. **Check tasks**:
   - **Frontend**: Check `FRONTEND_COORDINATION.md` and `FRONTEND_DEV.md`
   - **Backend**: Look at `BACKEND_STATUS.md` for T1-T3 tasks
   - Check `agent_tasks.jsonl` for claimed tasks

3. **Claim a task**:
   - **Frontend**: Update `FRONTEND_COORDINATION.md` with your status and lock files
   - **Backend**: Update `agent_tasks.jsonl` with your assignee name

4. **Implementation**:
   - **Frontend**: Follow `FRONTEND_UI_GUIDE.md` for consistent UI/UX

5. **After completion**:
   - **Frontend**: Release lock in `FRONTEND_COORDINATION.md`, update `FRONTEND_STATUS.md`
   - **Backend**: Update `agent_tasks.jsonl` status to "DONE"
   - Append entry to `/agent_history.jsonl` (root)
   - **Backend**: Run `uv run ruff check . --fix` on modified files
   - **Frontend**: Run `npm run lint` in `praxis/web-client/`

---

## 📊 Current Project Status (Dec 16, 2025)

### Backend Status ⚙️
**Major Accomplishments**:
- ✅ Core module refactoring (all 4 modules)
- ✅ Production bugs fixed (all 3)
- ✅ Test suite performance optimization

**Current Priorities**:
1. **Fix test collection** (T2.5) - CRITICAL
2. **Mark slow tests** (T1.5)
3. **Service test coverage** (T2.3, T3.4)

**Coverage**: ~45-55% (target: 80%)

---

### Frontend Status 🖥️
**Current State**: v0.2.0-beta (~75% MVP ready)

**Working Features**:
- ✅ Core navigation & layout
- ✅ Asset management (machines, resources)
- ✅ Protocol library & upload
- ✅ Protocol execution with live dashboard
- ✅ Settings & theming
- ✅ Unit Tests (Core, Auth, Execution, Assets, Protocols)

**Critical Gaps**:
1. **Asset Definitions tab** (Phase 2.2)
2. **Protocol details view** (Phase 2.3)
3. **Dynamic Parameters Form** (Phase 2.3 - Formly)
4. **Visualizer** (Phase 3) - Not started

**Test Coverage**: ~25% (target: 60% for MVP)

---

## 🛠️ Useful Commands

### Backend Commands
```bash
# Run tests (optimized)
make test-parallel-fast

# Find slow tests
make test-durations

# Type check
uv run ty check praxis/

# Lint
uv run ruff check . --fix
```

### Frontend Commands
```bash
# Navigate to frontend
cd praxis/web-client

# Start dev server
npm start

# Run unit tests (Vitest)
npm test

# Run E2E tests (Playwright)
npm run e2e

# Build production
npm run build

# Lint
npm run lint
```

### Status Commands
```bash
# View backend tasks
cat .agents/BACKEND_STATUS.md

# View frontend coordination
cat .agents/FRONTEND_COORDINATION.md

# View claimed tasks
cat .agents/agent_tasks.jsonl | jq
```

---

## 📚 Related Documentation

- **Testing Guide**: `docs/TESTING.md` (comprehensive 628-line guide)
- **Backend Architecture**: `docs/architecture.md`
- **Frontend Roadmap**: `.agents/ANGULAR_FRONTEND_ROADMAP.md`
- **Project Root**: `AGENTS.md`, `GEMINI.md`

---

**Maintained By**: Development Team
**Questions**: Check `BACKEND_STATUS.md` or ask in team chat