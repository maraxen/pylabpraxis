# Agent Prompt: Well Selector Performance

Examine `.agents/README.md` for development context.

**Status:** 🟢 Done  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Medium  
**Dependencies:** None  
**Backlog Reference:** [audit_notes_260114.md](../../artifacts/audit_notes_260114.md) Section F.3

---

## 1. The Task

Improve well selector performance for 384-well plates. Click+drag operations are laggy.

**Current State:** 96-well plates work fine, 384-well plates are slow on click+drag.

## 2. Technical Implementation Strategy

### Step 1: Profile Current Performance

- Use Chrome DevTools Performance panel
- Record click+drag on 384-well plate
- Identify bottlenecks (rendering, event handlers, state updates)

### Step 2: Likely Optimizations

1. **Debounce selection updates**: Don't update state on every mouse move
2. **Use CSS instead of ngStyle**: Avoid inline style bindings
3. **Virtualize if needed**: Only render visible wells (unlikely needed)
4. **OnPush change detection**: Ensure component uses OnPush
5. **Reduce DOM nodes**: Simplify well elements

### Step 3: Common Fixes

```typescript
// Instead of updating on every mousemove
onMouseMove(well: Well) {
  if (this.isDragging) {
    this.pendingWells.add(well);
  }
}

onMouseUp() {
  // Batch update at end of drag
  this.selectedWells.update(wells => [...wells, ...this.pendingWells]);
  this.pendingWells.clear();
}
```

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `shared/components/well-selector/` or similar | Main component |
| Well plate rendering component | Cell rendering |

## 4. Constraints & Conventions

- **Frontend Path**: `praxis/web-client`
- **Testing**: Profile before and after

## 5. Verification Plan

**Definition of Done:**

1. Click+drag on 384-well plate is smooth
2. No visible lag during selection
3. Selection still works correctly

**Manual Verification:**

1. Navigate to Run Protocol > Well Selection step
2. Load a 384-well plate
3. Click and drag to select 96 wells
4. Verify smooth interaction

---

## On Completion

- [x] Document before/after metrics
- [x] Commit changes
- [x] Mark this prompt complete

---

## References

- `.agents/artifacts/audit_notes_260114.md` - Source requirements
