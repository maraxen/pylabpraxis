# Agent Prompt: Documentation Audit

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P3  
**Batch:** [260115](README.md)  
**Difficulty:** Easy  
**Dependencies:** None  
**Backlog Reference:** [audit_notes_260114.md](../../artifacts/audit_notes_260114.md) Section G

---

## 1. The Task

Audit the documentation for missing content and rendering issues.

**User-Reported Issues:**

- `api-production` paths not found
- Production mode info missing from docs
- Diagrams not rendering (possibly related to browser/production mode tabs)
- Missing: Lite mode docs (SQLite + no-setup KV store)

**Goal:** Catalog missing docs and identify rendering issues.

## 2. Technical Inspection Strategy

### Step 1: Inventory Docs Structure

```bash
cd /Users/mar/Projects/pylabpraxis/docs
find . -name "*.md" | head -50
```

### Step 2: Identify Mode-Specific Docs

Check for existence of:

- `installation-browser.md` or similar
- `installation-production.md` or similar
- `installation-lite.md` or similar

### Step 3: Verify Mermaid Rendering

1. Navigate to docs viewer in browser
2. Find a page with Mermaid diagrams
3. Check if diagrams render
4. Note any errors in console

### Step 4: Check Mode Tabs

If docs have "Browser Mode" / "Production Mode" tabs:

- Do links work for both?
- Is content present for both?

## 3. Output Artifact

Create `.agents/artifacts/docs_audit_findings.md` with:

```markdown
# Documentation Audit Findings

## Missing Documents

| Document | Purpose | Priority |
|:---------|:--------|:---------|
| installation-browser.md | Browser mode setup | High |
| installation-production.md | Full stack setup | High |
| installation-lite.md | SQLite mode setup | Medium |

## Mode Coverage Gaps

[Pages that mention production but have no production docs]

## Mermaid Rendering Issues

[Description of issue, console errors if any]

## Recommended Fixes

1. [Fix 1]
2. [Fix 2]
```

## 4. Constraints & Conventions

- **Docs Path**: `/docs`
- **Frontend Docs Viewer**: Check routing in web client

## 5. Verification Plan

**Definition of Done:**

1. Missing docs catalogued
2. Mermaid rendering status documented
3. Mode tab functionality checked

---

## On Completion

- [ ] Create `.agents/artifacts/docs_audit_findings.md`
- [ ] Update this prompt status to 🟢 Completed

---

## References

- `.agents/artifacts/audit_notes_260114.md` - Source requirements
