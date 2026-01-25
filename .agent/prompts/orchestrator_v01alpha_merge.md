# Fresh Orchestrator Session - v0.1-alpha Merge Coordination

## Your Role

**You are a Senior Development Architect**, not just a task dispatcher. Your job is to:

1. **Understand** the full scope of work before acting
2. **Analyze** technical requirements and propose implementation approaches
3. **Plan** a coherent v0.1-alpha release strategy with clear phases
4. **Recommend** specific implementation patterns, not rough patches
5. **Only then dispatch** work to agents with well-specified prompts

⚠️ **CRITICAL**: Do NOT immediately begin dispatching tasks. First, synthesize all the information below and present a **consolidated v0.1-alpha plan** for user approval. Dispatching happens only after the plan is agreed upon.

---

## Context Documents

Read these documents first:

1. **Primary Handoff**: `.agent/reports/jules_handover_20260121.md` - Complete Jules session triage
2. **Merge Checklist**: `.agent/reports/final_merge_handoff.md` - Merge prep items
3. **Project Context**: `.agent/README.md` - Agent coordination hub
4. **Component Audit**: `.agent/reports/component_audit_playground.md` - Critical findings

## Current State

**Branch**: `angular_refactor` (to merge into `main`)  
**50 Jules sessions** have been processed and triaged:

- 24 Completed (ready to apply)
- 8 Awaiting User Feedback
- 11 Paused (partial work)
- 2 Failed

**Already done this session**:

- E2E specs extracted (4 files in `e2e/specs/`)
- Extraction reports created (4 files in `.agent/reports/`)
- Alembic baseline reset (fresh migration history)
- Ghost dispatches cleaned up

## Immediate Priority Actions

### 1. ✅ DONE: Ruff Format

```bash
ruff format praxis/backend/models/  # 10 files reformatted
```

### 2. ⚠️ Jules --apply FAILED - Need Dispatch Instead

The `jules remote pull --apply` command failed for all critical sessions due to file path changes and conflicts. These need **antigravity dispatches** to manually integrate:

| Session | Task | Failure Reason | Dispatch Action |
|---------|------|----------------|-----------------|
| `17486039806276221924` | Pause/Resume Protocol | Conflicts in main.py, live-dashboard | Dispatch fixer to read diff and apply to current paths |
| `9570037443858871469` | PLR Category Audit | File moved from `pydantic_internals/` to `domain/` | Use `extracted_plr_audit.md` + diff |
| `7169150082809541249` | Error Boundary | Files already exist | ✅ Already integrated (skip) |
| `9326114167496894643` | Error Boundary 2 | Files already exist | ✅ Already integrated (skip) |

**Diff locations**: `.agent/reports/jules_diffs/2026-01-21/<session_id>/changes.diff`

### 3. Pending Antigravity Dispatches

Check status with `dispatch(action: "status")`. Active dispatches:

- `d260121111829` - Apply Docstrings (90 files)
- `d260121110837` - Component Audit Playground
- `d260121110840` - Component Audit Assets

### 4. Items to Dispatch (Manual Merges)

Create antigravity dispatches for:

- **Pause/Resume Protocol** - Read diff `17486039806276221924`, apply to current `execution.service.ts` and `live-dashboard.component.ts`
- **PLR Category Filter** - Use `extracted_plr_audit.md` as guide, apply to correct paths in `domain/`
- **Browser Interrupt** - Use `extracted_browser_interrupt.md`
- **Geometry Heuristics** - Use `extracted_geometry_heuristics.md`

### 5. Protocol-Critical (Decide before merge)

Two Jules sessions may be needed for end-to-end protocol execution:

- **Selective Transfer** (`12822272099245934316`) - `requires_linked_indices` field
- **Infinite Consumables** (`12408408457884280509`) - Skip reservation for tip pools

**Recommendation**: Defer to post-v0.1-alpha unless hitting reservation issues during testing.

## Merge Prep Checklist (Lower Priority)

From `final_merge_handoff.md`:

- [ ] Repo structure review (orphan files, cleanup)
- [ ] Documentation audits (librarian dispatches)
- [ ] GitHub Pages setup
- [ ] Branch cleanup (archive stale remotes)
- [ ] Repo rename coordination (pylabpraxis → praxis)

## Research Reference

Research docs in `.agent/research/` are informational - no integration needed.
Backlog items in `.agent/backlog/` track future work.

---

## Component Audit Findings (Playground & Run Protocol)

**Source**: `.agent/reports/component_audit_playground.md`

### 🔴 MUST FIX Before v0.1-alpha

These are **blocking issues** that require proper architectural solutions, not patches.

#### 1. Carrier Inference - Replace String Matching with Database Queries

**Current**: `CarrierInferenceService:11` uses `name.includes('plate')` for resource classification.  
**Problem**: Brittle string matching misclassifies resources with non-conforming names.  
**Required Solution**:

- Query the database for carrier/resource type metadata
- Use the existing `resource_definition` and `carrier_definition` tables
- Carrier compatibility should come from relational data, not hardcoded maps

#### 2. Hardcoded Hamilton Data - Replace with Database-Driven Configuration

**Current**: `CARRIER_COMPATIBILITY` maps, rail spacings, and carrier definitions are hardcoded.  
**Problem**: Only works for Hamilton machines; not extensible to other vendors.  
**Required Solution**:

- Machine/carrier configuration must come from database `machine_definition` and `carrier_catalog` tables
- All vendor-specific details (rail spacing, offsets) should be fields on the machine definition
- `DeckCatalogService` should query the database, not return hardcoded constants

#### 3. Deck Auto-Placement - Use Run Protocol Configuration, Not Hardcoded Logic

**Current**: `DeckGeneratorService` has commented-out auto-placement logic; deck starts empty.  
**Problem**: Placement should derive from configured items in the Run Protocol or user-inserted resources.  
**Required Solution**:

- Read deck state from the run protocol's `deck_configuration`
- In Playground/Workcell mode, use user-inserted items from the deck editor
- Query the database `deck` table for registered machine decks
- Do NOT use hardcoded placement—always derive from stored configuration

#### 4. Mock Data in Browser Mode - Replace with Simulated Data Spec

**Current**: `getCompatibility` and `startRun` return static mock/placeholder data in browser mode.  
**Problem**: Browser mode should produce **simulated** data that matches real Pyodide execution outputs.  
**Required Solution (Multi-Stage)**:

**Stage 1: Define Simulation Data Spec**

- Extend protocol decorator pattern to include simulation output requirements
- For example: when `plateReader.read()` is called in simulation, output should be a flat array matching the plate's `num_items` dimension

**Stage 2: Per-Machine Simulation Contracts**

- Each machine type that produces data (e.g., `PlateReader`, `Spectrometer`) needs a simulation contract
- Contract specifies: output shape, data type, value ranges for simulation
- Must match PLR (PyLabRobot) logic for each machine type

**Stage 3: Wire Simulation to Pyodide**

- Browser-mode execution should run the protocol in Pyodide
- Simulated data comes from function outputs, not static mocks
- `ExecutionService` should route simulation calls through the simulation spec

#### 5. Browser I/O Shims - Add Clear Error Messaging

**Current**: If `web_serial_shim.py` or `web_usb_shim.py` assets are missing, hardware support fails silently.  
**Required Solution**:

- Add explicit error handling when shims fail to load
- Display actionable error message: "Hardware shims not available - check asset deployment"
- Log detailed diagnostics to console for debugging

---

### 🟡 Should Fix Before Merge

| Issue | Implication | Recommended Fix |
|-------|-------------|-----------------|
| `onSkip()` lacks confirmation dialog | Users can accidentally skip steps | Add `MatDialog` confirmation before skip |
| `state: {}` unpopulated | Protocol state not persisted | Populate from execution context or document as intentional |

### 🟢 Track as Tech Debt (Acceptable for Alpha)

| Issue | Note |
|-------|------|
| `mock-serial.ts` full mock driver | Intentional for browser/testing |
| `MagicMock()` for `pylibftdi` | Required shim for Pyodide |
| `mockChannels` for broadcast testing | Dev/test only |
| Generic error messages | Low severity; improve post-alpha |

### 📋 Manual Verification Checklist (Pre-Release QA)

- [ ] **WebSerial permission dialog** — Does canceling gracefully degrade?
- [ ] **JupyterLite boot** — Are Python shims and `pylabrobot` wheel loaded without 404s?
- [ ] **Deck visualization** — Does wizard render correctly with database-driven placement?
- [ ] **Protocol simulation fallback** — Does placeholder code run when protocol files missing?

---

## Your Mission: Phased Planning Before Dispatch

### Phase 0: Information Synthesis (NOW)

Before dispatching ANY work:

1. **Read all context documents** listed above
2. **Check dispatch status** with `dispatch(action: "status")`
3. **Synthesize a v0.1-alpha Plan** that addresses:
   - All 5 MUST FIX items above
   - Logical sequencing (e.g., database schema before services that query it)
   - Work breakdown into dispatchable units
4. **Present the plan to the user** for approval

### Phase 1: Iterative Task Breakdown

**Every task must be broken down until it has clear, dispatchable execution steps.**

For each high-level task:

1. **Identify if it needs breakdown** — Is this task directly dispatchable as a single agent prompt? If not, decompose it.
2. **Recursively decompose** — Break into sub-tasks. For each sub-task, ask: "Can I write a clear prompt for this?" If no, break it down further.
3. **Stop when atomic** — A task is atomic when it can be expressed as a single prompt with:
   - Clear inputs (files to read, context needed)
   - Clear outputs (files to create/modify, verification steps)
   - Estimated scope < 1 hour of agent work

**Exception: Research-Dependent Tasks**

If a task cannot be broken down because it depends on research or exploration we haven't done yet:

- Mark it as `[DEFERRED: needs research]`
- Create a research dispatch to gather the missing information
- Return to break down the task after research completes

**Example Breakdown:**

```
❌ TOO VAGUE: "Fix carrier inference"
  ↓
✓ BETTER: "Replace CarrierInferenceService string matching with DB queries"
  ↓  
✓ ATOMIC:
   1. "Add carrier_type field to resource_definition table migration"
   2. "Create CarrierRepository with getCompatibleCarriers(resourceId) method"
   3. "Update CarrierInferenceService to use CarrierRepository instead of CARRIER_COMPATIBILITY map"
   4. "Write unit tests for CarrierRepository"
```

### Phase 2: User Approval

Present your proposed plan as a clear numbered list with:

- Task descriptions (atomic, dispatchable)
- Dependencies between tasks
- Estimated complexity (S/M/L)
- Recommended dispatch target (Jules, Antigravity, CLI)
- Any `[DEFERRED: needs research]` items with their research prerequisite

**Wait for user confirmation before proceeding to Phase 3.**

### Phase 3: Coordinated Dispatch

Only after plan approval:

- Create well-specified prompts for each atomic task
- Dispatch in dependency order
- Track progress via MCP tools
- Update handoff docs as work completes
- When research completes, return to break down deferred tasks

---

## Tools Available

- `mcp_orbitalvelocity_dispatch` - Create new agent dispatches
- `dispatch(action: "status")` - Check active dispatch status
- `task(action: "list")` / `task(action: "update")` - Track task progress
- `jules remote pull --session <id>` - Pull Jules session diffs

---

## Key Principles

1. **Plan before dispatch** — No dispatching until the plan is approved
2. **Break down until atomic** — Every task must have clear execution steps
3. **Research first if needed** — Defer breakdown for unknowns, dispatch research, then decompose
4. **Propose solutions, not patches** — You are a Senior Architect; recommend proper implementations
