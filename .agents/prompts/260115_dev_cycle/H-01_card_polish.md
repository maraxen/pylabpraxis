# Agent Prompt: Card Visual Polish

Examine `.agents/README.md` for development context.

**Status:** ✅ Completed  
**Priority:** P3  
**Batch:** [260115](README.md)  
**Difficulty:** Medium  
**Dependencies:** I-04  
**Input Artifact:** `card_audit_findings.md`

---

## 1. The Task

Implement the design system recommendations to fix card overlaps and hierarchy issues.

**Issues (Audit I):** Corner chips overlapping content, text overlap, rigid sizing.

## 2. Implementation Steps

### Step 1: Global Card Styles

- Define a "Minimum Card" structure in SCSS.
- Ensure text truncation (`text-overflow: ellipsis`) is applied to titles/descriptions.

### Step 2: Chip Placement

- Move corner status chips to a dedicated "Header" row or ensure they have `z-index` and background/padding that prevents ugly overlaps.
- Or use `flex-wrap` to push content down if chip is present.

### Step 3: Responsive Checks

- Apply fixes to: `MachineListComponent`, `ResourceAccordion`.

## 3. Constraints

- **Visuals**: "Premium" feel. avoid clutter.

## 4. Verification Plan

- [x] Resizing window to 300px doesn't break card layout.
- [x] Long titles truncate properly.
- [x] Chips don't obscure text.

---

## On Completion

- [x] Update this prompt status to 🟢 Completed.
