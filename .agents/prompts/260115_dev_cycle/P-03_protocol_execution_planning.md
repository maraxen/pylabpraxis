# Agent Prompt: Protocol Execution UX Planning

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Medium  
**Dependencies:** None  
**Backlog Reference:** [audit_notes_260114.md](../../artifacts/audit_notes_260114.md) Section F

---

## 1. The Task

Plan improvements to the Protocol Execution UX across the Run Protocol flow.

**Issues to Address:**

- Well arguments showing in Parameters AND Well Selection (should be Well Selection only)
- Selective transfer index size hints needed
- Asset autocomplete is clunky, selections don't persist
- Protocol description formatting (tabs for Description, Assets, Parameters?)

**Deliverable:** Updates to existing protocol execution artifacts or a new focused design document.

## 2. Planning Strategy

### Step 1: Current Flow Analysis

Document the current Run Protocol stepper:

1. Select Protocol
2. Configure Parameters
3. Select Machine
4. Map Assets
5. Deck Setup
6. Review & Run

For each step, note:

- What information is shown
- What inputs are required
- Current pain points

### Step 2: Well Arguments Solution

Analyze how well selection parameters work:

- Where are they defined in protocol decorator?
- How are they currently exposed in Parameters step?
- How should they instead appear in Well Selection step?

### Step 3: Index Linking Design

For selective transfers:

- How to detect linked indices (protocol decorator vs. simulation)
- Live counter UX: "Source: 4 wells | Destination: 4 wells"
- Validation error at step end: "Source and destination must have same well count"

### Step 4: Asset Autocomplete Redesign

Current problems:

- Selections don't persist
- Interaction is clunky

Design improvements:

- Clearer selection state
- Better dropdown behavior
- Persist selections across step navigation

### Step 5: Protocol Summary Formatting

Consider:

- Tabs: Description | Required Assets | Parameters
- Or: Collapsible sections
- Show well arguments in summary preview

## 3. Output

Update or reference the existing run protocol artifacts:

- `run-protocol.component.ts`
- `guided-setup.component.ts`

Create a focused section in audit notes or standalone planning doc.

## 4. Constraints & Conventions

- **Frontend Path**: `praxis/web-client/src/app/features/run-protocol/`
- **Reference**: Current stepper implementation

## 5. Verification Plan

**Definition of Done:**

1. Current flow fully documented
2. Well arguments solution specified
3. Index linking UX designed
4. Asset autocomplete improvements proposed
5. Protocol summary format decided

---

## On Completion

- [x] Document findings/designs
- [x] Update this prompt status to 🟢 Completed

---

## References

- `src/app/features/run-protocol/` - Current implementation
- `.agents/artifacts/audit_notes_260114.md` - Source requirements
