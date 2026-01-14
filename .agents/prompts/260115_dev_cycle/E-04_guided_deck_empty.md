# Agent Prompt: Guided Deck Setup Empty Start

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Medium  
**Dependencies:** None  
**Backlog Reference:** [audit_notes_260114.md](../../artifacts/audit_notes_260114.md) Section F.5

---

## 1. The Task

Modify guided deck setup to start EMPTY, with only machine-specific defaults (e.g., OT-2 trash). Pull deck state from database.

**Current State:** Deck may show pre-populated items.

**Desired State:** Deck starts empty except for immutable machine defaults. Users add labware matching protocol requirements.

## 2. Technical Implementation Strategy

### Step 1: Understand Current State Source

Trace where deck state comes from:

- Is it from `machine.plr_state`?
- From `machine.plr_definition`?
- Hardcoded defaults?

### Step 2: Define "Empty" State

For each machine type, define what "empty" means:

- OT-2: Trash in slot 12 only
- Hamilton STAR: No labware, deck rails visible
- Generic: Completely empty

### Step 3: Modify Deck Initialization

```typescript
initializeDeck(machine: Machine) {
  // Get deck layout from definition (structure, not contents)
  const deckLayout = machine.plr_definition?.deck || this.getDefaultLayout(machine);
  
  // Get machine-specific defaults
  const defaults = this.getMachineDefaults(machine);
  
  // Start with only defaults
  this.deckState.set({
    layout: deckLayout,
    resources: defaults // e.g., [{ slot: 12, resource: 'Trash' }] for OT-2
  });
}
```

### Step 4: Database Integration

Ensure deck state can be persisted to and loaded from database.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `features/run-protocol/components/guided-setup/` | Deck initialization |
| `shared/components/deck-view/` | Deck rendering |

## 4. Constraints & Conventions

- **Frontend Path**: `praxis/web-client`
- **Backend**: No changes unless DB schema update needed

## 5. Verification Plan

**Definition of Done:**

1. Deck starts empty (plus machine defaults)
2. Users can add labware
3. State persists correctly

**Manual Verification:**

1. Start Run Protocol flow
2. Select a protocol and machine
3. Reach Deck Setup step
4. Verify deck is empty except defaults
5. Add a plate, verify it appears

---

## On Completion

- [ ] Commit changes
- [ ] Mark this prompt complete

---

## References

- `.agents/artifacts/audit_notes_260114.md` - Source requirements
