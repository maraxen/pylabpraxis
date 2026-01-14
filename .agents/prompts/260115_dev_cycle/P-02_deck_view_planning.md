# Agent Prompt: Deck View UX Planning

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Hard  
**Dependencies:** None  
**Backlog Reference:** [audit_notes_260114.md](../../artifacts/audit_notes_260114.md) Section J

---

## 1. The Task

Plan a comprehensive Deck View UX optimization and overhaul. This is **separate** from the Workcell UX Redesign.

**Scope:**

- Deck visualization improvements
- Deck state from database (empty start + machine defaults)
- Deck placement constraint specifications
- Guided deck setup improvements

**Deliverable:** A design artifact (`deck_view_ux_design.md`).

## 2. Planning Strategy

### Step 1: Current State Analysis

Review existing deck components:

| Component | Location | Purpose |
|:----------|:---------|:--------|
| `DeckViewComponent` | `shared/components/deck-view/` | Main deck visualization |
| `GuidedSetupComponent` | `features/run-protocol/` | Protocol deck setup |
| `VisualizerComponent` | `features/visualizer/` | Workcell deck display |

### Step 2: User Pain Points

From audit notes:

- Deck should start EMPTY (except machine defaults)
- Deck state should come from database
- Need support for deck placement constraints
- Guided setup needs improvement

### Step 3: Constraint System Design

Design how constraints work:

- **Source**: Protocol decorator (`@praxis.deck_constraints(...)`) or simulation inference
- **Types**: Slot restrictions, incompatible placements, required positions
- **UI**: Visual indicators for valid/invalid placements
- **Validation**: When to check (continuous vs. step end)

### Step 4: State Flow Design

```
Database State → Frontend Deck Model → Visualization
                       ↓
              User modifications
                       ↓
              Runtime validation
```

## 3. Output Artifact

Create `.agents/artifacts/deck_view_ux_design.md` with:

```markdown
# Deck View UX Design

## Current State Analysis
[Description of existing components]

## Design Goals
1. Empty deck start
2. Database-driven state
3. Constraint system
4. Improved guided setup

## Constraint System

### Constraint Sources
- Protocol decorator
- Simulation inference
- Machine definition

### Constraint Types
[Enumeration with examples]

### UI Representation
[How constraints are shown visually]

## State Management
[How deck state flows from DB to UI]

## Guided Setup Improvements
[Specific UX enhancements]

## Component Architecture
[New/modified components]

## Implementation Phases
[Phased rollout plan]
```

## 4. Constraints & Conventions

- **No Code**: Design only
- **Separate from Workcell**: Don't conflate with hierarchical explorer

## 5. Verification Plan

**Definition of Done:**

1. `deck_view_ux_design.md` artifact created
2. Constraint system fully specified
3. State flow documented
4. User review requested

---

## On Completion

- [x] Create `.agents/artifacts/deck_view_ux_design.md`
- [x] Update this prompt status to 🟢 Completed
- [ ] Request user review

---

## References

- `src/app/shared/components/deck-view/` - Current deck component
- `.agents/artifacts/workcell_ux_redesign.md` - Related but separate
- `.agents/artifacts/audit_notes_260114.md` - Source requirements
