# Agent Prompt: Mermaid Rendering Fix

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Priority:** P3  
**Batch:** [260115](README.md)  
**Difficulty:** Low  
**Dependencies:** I-05  
**Input Artifact:** `docs_audit_findings.md`

---

## 1. The Task

Fix Mermaid diagram rendering in the Documentation Viewer.

**Issue (Audit G.2):** Diagrams not rendering, possibly due to tab switching or timing.

## 2. Implementation Steps

### Step 1: Diagnostics

- Check if `mermaid.init()` is called after route navigation.

### Step 2: Fix

- Add `AfterViewInit` hook or Router event listener in `DocsViewerComponent` to re-trigger Mermaid processing on content load.

## 3. Constraints

- **Lib**: Using standard mermaid js.

## 4. Verification Plan

- [ ] Open a doc page with mermaid -> Diagram renders.
- [ ] Navigate to another page -> Diagram renders.

---

## On Completion

- [ ] Update this prompt status to 🟢 Completed.
