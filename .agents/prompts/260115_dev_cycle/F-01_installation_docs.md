# Agent Prompt: Installation Docs Split

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P3  
**Batch:** [260115](README.md)  
**Difficulty:** Low  
**Dependencies:** I-05  
**Input Artifact:** `docs_audit_findings.md`

---

## 1. The Task

Create dedicated installation documentation for Browser Mode, Production Mode, and Lite Mode.

**Issue (Audit G.1):** Missing production/browser distinction; paths not found.

## 2. Implementation Steps

### Step 1: Create Files

- `docs/installation-browser.md`: "Zero setup, just visit URL".
- `docs/installation-production.md`: Docker compose setup, Postgres, API.
- `docs/installation-lite.md`: Local dev with SQLite + Python (no Postgres).

### Step 2: Link

- Update `docs/index.md` or sidebar to link these new pages.

## 3. Constraints

- **Content**: Use existing `README.md` content as source, just split it up.

## 4. Verification Plan

- [x] 3 new files exist.
- [x] Links in sidebar work.

---

## On Completion

- [x] Update this prompt status to 🟢 Completed.
