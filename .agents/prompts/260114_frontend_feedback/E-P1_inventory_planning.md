# Agent Prompt: Inventory/Asset Selector UX Design

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260114_frontend_feedback](./README.md)
**Difficulty:** 🟡 Medium
**Type:** 🔵 Planning
**Dependencies:** None
**Backlog Reference:** [GROUP_E_playground_init.md](./GROUP_E_playground_init.md)

---

## 1. The Task

Plan the unification and improvement of the "Inventory Add" (Playground) and "Protocol Asset Selection" components.

**User Feedback:**

> "categories in the playground inventory adder are not good for machines or resources. this component should be united with what we use to select for the protocols, but with different logic. not sure if this is actually the case. we should think carefully and plan out the best ux here."

**Goal:** Produce a UX design document and implementation plan for a unified asset selector component.

## 2. Technical Implementation Strategy

This is a **Planning Task**. You must investigate the codebase and produce a design document.

### Phase 1: Audit Current Implementations

1. **Inventory Dialog:** `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts`
   - Document current category structure
   - Identify pain points mentioned in feedback

2. **Protocol Asset Selector:** Locate and audit the component used for protocol asset selection
   - Likely in `src/app/features/protocols/` (e.g., `ProtocolPlanner` or `ProtocolBuilder`)
   - Document its category/selection approach

### Phase 2: Design Unified Component

Design a "Unified Asset Selector" component supporting:

| Mode | Context | Behavior |
|:-----|:--------|:---------|
| Protocol Definition | Abstract Definitions | Select machine/resource *types* |
| Playground Inventory | Concrete Instances | Select + configure backend for simulation |

### Phase 3: UX Plan

Define how "different logic" will be handled:

- Protocol mode: Simple type selection
- Playground mode: Type selection + simulation backend configuration

## 3. Context & References

**Primary Files to Investigate:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts` | Current inventory adder |
| `praxis/web-client/src/app/features/protocols/` | Protocol asset selector location (find exact file) |

**Reference Files:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts` | Machine selection patterns |
| `praxis/web-client/src/app/features/assets/components/resource-dialog.component.ts` | Resource selection patterns |

## 4. Constraints & Conventions

- **This is a PLANNING task:** Do not implement code, only design
- **Output:** Write design document to `.agents/artifacts/`
- **Scope:** Document must be detailed enough to spawn implementation prompts

## 5. Verification Plan

**Definition of Done:**

1. Audit document comparing both components created
2. UX design for Unified Asset Selector documented
3. Mode-switching behavior clearly defined
4. Implementation prompts (E-03+) specs identified

**Deliverables:**

Create file: `.agents/artifacts/inventory_ux_design.md`

**Document Structure:**

```markdown
# Unified Asset Selector UX Design

## Audit Summary
### Inventory Dialog (Playground)
- [Findings]

### Protocol Asset Selector
- [Findings]

## Unified Design
### Component Architecture
- [Design]

### Mode: Protocol Definition
- [Behavior]

### Mode: Playground Inventory
- [Behavior]

## Implementation Plan
- [Phases and prompts to generate]
```

---

## On Completion

- [ ] Create design document in `.agents/artifacts/`
- [ ] Generate E-03+ implementation prompt specs
- [ ] Mark this prompt complete in batch README
- [ ] Set status in this document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `GROUP_E_playground_init.md` - Parent initiative
