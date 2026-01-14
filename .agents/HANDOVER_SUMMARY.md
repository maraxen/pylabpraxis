# Handover Summary: Workcell & Inventory Implementation Phase

**Date:** 2026-01-14
**Status:** Transitioning to Implementation Execution

## Context

We have just completed a massive cleanup and normalization phase (Archived Batch 260114). The codebase is now in a consistent state with unified models (SQLModel) and standardized frontend controls (`ViewControlsComponent`). All major blockers from the previous alpha audit have been resolved or planned.

## Active Planning Artifacts

These are the files you should use to guide the next steps. They are located in `.agents/artifacts/`:

1. **[Workcell UX Redesign](.agents/artifacts/workcell_ux_redesign.md)**:
   - **Goal**: Implement a hierarchical Workcell Explorer and rich machine cards.
   - **Status**: Design approved, implementation pending.
   - **Key Files**: `visualizer.component.ts`, `deck-view.component.ts`.

2. **[Unified Asset Selector Design](.agents/artifacts/inventory_ux_design.md)**:
   - **Goal**: Bridge the gap between Playground inventory adding and Protocol guided setup.
   - **Status**: Design approved, infrastructure implementation pending.
   - **Key Files**: `inventory-dialog.component.ts`, `guided-setup.component.ts`.

3. **[Simulation Architecture Plan](.agents/artifacts/simulation_architecture_plan.md)**:
   - **Goal**: Formalize the separation between frontend "FrontendType" and backend "SimulationDriver".

## Priority Backlog (Next Up)

1. **The WebSerial "NameError" Bug**: (P1) Top priority. `WebSerial` is not being correctly injected into the Pyodide `builtins` context in some browser environments. See `web_serial_shim.py` and the initialization logic in the REPL feature.
2. **Workcell Hierarchical Explorer (F-01)**: Implement the sidebar tree and machine status badges as per the redesign artifact.
3. **Hardware Discovery & Persistence**: Audit and implement reliable WebUSB/WebSerial device enumeration.

## Key Technical Patterns

- **Frontend State**: We use Signals extensively for UI state.
- **Data Access**: Use `SqliteService` (for browser mode persistent mocks) and standard Angular HTTP for production.
- **Component Styling**: Always use theme tokens. Avoid hardcoded hex codes.

## Archived Reference

If you need to revisit the rationale for recent changes, see `.agents/archive/archive.tar.gz`. Specifically, look at `summaries/pylabpraxis_batch_260114.md` for a mapping of all recently completed tasks.

---
*Good luck. The foundation is solid—time to build the high-level dashboard.*

## Inspection Findings (260115)

**Playground Inspection (I-02)**:

- **WebSerial/Shim**: Root cause identified. `getOptimizedBootstrap()` is unused; shims are never injected. Requires async refactor of URL builder.
- **Kernel Load**: Blank screen rooted in initialization race. Requires adopting "Restart Kernel" pattern (async load after view init).
- **Theme Sync**: Initial theme parameter ignored due to race or early default signal value.
