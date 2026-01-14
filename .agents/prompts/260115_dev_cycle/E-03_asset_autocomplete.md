# Agent Prompt: Asset Autocomplete Redesign

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Medium  
**Dependencies:** P-03  
**Input Artifact:** `protocol_execution_ux_plan.md`

---

## 1. The Task

Redesign the Asset Autocomplete / Guided Setup flow in `run-protocol` to fix persistence issues and improve usability.

**Goal:** Asset selections must persist when navigating back/forth in the stepper, and the selection UI should be cleaner.

## 2. Implementation Steps

Refer to "Proposed Changes" Section 2 in `protocol_execution_ux_plan.md`.

### Step 1: GuidedSetup Component

- Add `@Input() initialSelections` to `GuidedSetupComponent`.
- Refactor `autoSelect` to respect existing/initial selections.

### Step 2: Parent Integration

- Update `RunProtocolComponent` to maintain the `configuredAssets` state map.
- Pass this state into `app-guided-setup`.

### Step 3: Interaction Polish

- Ensure dropdowns don't flicker.
- Ensure mapping state is clearly "Set" vs "Pending".

## 3. Constraints

- **Persistence**: Critical requirement. Navigating `Step 4 -> Step 3 -> Step 4` must show the previously selected assets.

## 4. Verification Plan

- [ ] Select an asset in Guided Setup (Step 4).
- [ ] Navigate back to Parameters (Step 2).
- [ ] Navigate forward to Guided Setup.
- [ ] Verify the asset is still selected.

---

## On Completion

- [ ] Update this prompt status to 🟢 Completed.
