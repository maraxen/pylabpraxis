# Agent Prompt: Deck View Logic & Constraints

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed (Tentative - Awaiting improved Workcell view)  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** High  
**Dependencies:** None  
**Input Artifact:** `deck_view_ux_design.md`

---

## 1. The Task

Implement the foundational logic upgrades for the Deck View, specifically the database-backed state and constraint system.

**Goal:** Move deck state source-of-truth to the database and implement valid layout constraints.

## 2. Implementation Steps

Follow "Component Architecture" and "Phase Plan" in `deck_view_ux_design.md`.

### Step 1: Database Schema

- Create `deck_states` table (machine_id, json_state).
- Create API endpoints for GET/PUT deck state.
- make sure these are bypassed in browser mode to instead act with the localStorage indexeddb sqlite service

### Step 2: DeckConstraintService

- Implement `DeckConstraintService`:
  - `validateDrop(resource, slot, currentDeck)` -> `{ valid: boolean, reason?: string }`
  - Implement basic constraints: Slot Type Compatibility (Carrier on Rail), Collision (placeholder).

### Step 3: Visualizer Integration

- Update `DeckViewComponent` to accept `[constraints]` input.
- Show visual feedback (Green/Red glow) during drag based on `validateDrop`.
- Persist state changes to the new API instead of `localStorage`.

### Step 4: Empty Deck Logic

- Ensure new machines start with an Empty deck (except fixed trash/hardware), ensuring `GuidedSetup` drives the population.

## 3. Constraints

- **Scope**: Focus on the Logic and Persistence phase first. "Ghost" workflow can be a follow-up if complexity is too high.
- **State**: Must reference `sqlite.service.ts`.

## 4. Verification Plan

- [x] Database stores deck state.
- [x] Initial load fetches from DB.
- [x] Moving a resource persists to DB.
- [x] Invalid drops are visually indicated (Red).
- [x] Valid drops are visually indicated (Green).

---

## On Completion

- [x] Update `deck_view_ux_design.md` with implementation details.
- [x] Update this prompt status to 🟢 Completed.

## 5. Manual Validation Steps

1. **Verify Database Table**:
   - Open browser devtools.
   - Inspect IndexedDB `praxis_db` -> `sqlite` -> `db_dump`.
   - Use a tool like SQLite Viewer or `SqliteService` console logs to verify `deck_states` table exists.
2. **Persistence Test**:
   - Move a resource (e.g., a Plate) to a new slot on the deck.
   - Refresh the page.
   - **Expected**: Resource remains in the new slot (verified via `getDeckState` call on load).
3. **Constraint Validation**:
   - Drag a **Carrier** onto a **Rail**.
   - **Expected**: Visual feedback indicator (Green highlight).
   - Drag a **Plate** directly onto a **Rail** (if restricted).
   - **Expected**: Visual feedback indicator (Red highlight).
4. **Empty Deck Initialization**:
   - Create a new machine without a predefined deck in `plr-definitions.ts`.
   - **Expected**: Machine starts with an empty deck (except for fixed hardware like Trash).
