# Agent Prompt: Well Arguments Cleanup

Examine `.agents/README.md` for development context.

**Status:** 🟢 Done  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Medium  
**Dependencies:** None  
**Backlog Reference:** [audit_notes_260114.md](../../artifacts/audit_notes_260114.md) Section F.1

---

## 1. The Task

Remove well selection arguments from the Parameters step in Run Protocol flow. Well arguments should ONLY appear in the Well Selection step. Show them in the protocol summary screen.

**Current State:** Well selection (e.g., `source_wells`, `dest_wells`) appears in BOTH Parameters step AND Well Selection step.

**Desired State:** Well selection ONLY in Well Selection step. Protocol summary shows well selections for review.

## 2. Technical Implementation Strategy

#### Step 1: Identify Well Parameters

Find parameters that are well-selection type:

- Type hints like `list[str]` for wells
- PLR annotations for well selection
- Names containing `wells`, `indices`

#### Step 2: Filter from Parameters Step

Modify parameter rendering logic to exclude well-type parameters:

```typescript
// In parameters step component
get displayableParameters() {
  return this.parameters.filter(p => !this.isWellParameter(p));
}

isWellParameter(param: ProtocolParameter): boolean {
  return param.type === 'wells' || 
         param.name.includes('wells') || 
         param.name.includes('indices');
}
```

#### Step 3: Show in Protocol Summary

After protocol selection, show a summary that includes:

- Description
- Required Assets
- Well Parameters (read-only preview)

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `features/run-protocol/run-protocol.component.ts` | Main stepper |
| `features/run-protocol/components/parameter-step/` | Filter well params |
| Protocol summary component (may need to create) | Show well params |

## 4. Constraints & Conventions

- **Frontend Path**: `praxis/web-client/src/app/features/run-protocol/`
- **Preserve Data**: Ensure well values are still collected, just not in Parameters step

## 5. Verification Plan

**Definition of Done:**

1. Well parameters don't appear in Parameters step
2. Well parameters appear in Well Selection step (unchanged)
3. Protocol summary shows well selections
4. Build passes

**Manual Verification:**

1. Start Run Protocol flow
2. Select "Selective Transfer" protocol
3. In Parameters step, verify no well-related inputs
4. In Well Selection step, verify well inputs present
5. In Review step, verify well selections shown

---

## On Completion

- [x] Commit changes
- [x] Mark this prompt complete

---

## References

- `.agents/artifacts/audit_notes_260114.md` - Source requirements
