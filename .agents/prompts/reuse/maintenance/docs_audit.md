# Maintenance Prompt: Documentation Audit

**Purpose:** Review documentation completeness and accuracy  
**Frequency:** Quarterly  

---

## Prompt

```markdown
Examine .agents/README.md for development context.

## Task

Audit documentation for completeness, accuracy, and freshness.

## Phase 1: Triage

1. **List Documentation Files**:

   ```bash
   find . -name "*.md" -not -path "./.git/*" -not -path "./node_modules/*" | head -n 50
   ```

1. **Check for Outdated Docs**:

   ```bash
   find . -name "*.md" -mtime +90 -not -path "./.git/*" | head -n 20
   ```

## Phase 2: Categorize and Strategize

1. **Review Key Documentation**:

   | Document | Check |
   |:---------|:------|
   | `README.md` | Setup instructions current? |
   | `GEMINI.md` | Project guidelines accurate? |
   | `.agents/README.md` | Agent workflow current? |
   | API docs | Endpoints documented? |

2. **Identify Issues**:

   | Issue | Priority |
   |:------|:---------|
   | Missing setup instructions | High |
   | Outdated API references | High |
   | Broken links | Medium |
   | Incomplete sections | Medium |
   | Stale dates/references | Low |

3. **Document Strategy** before making changes.

4. **Get User Input**: ⏸️ PAUSE for approval.

## Phase 3: Apply Fixes

1. **Update Outdated Sections**.
2. **Fix Broken Links**.
3. **Add Missing Documentation**.
4. **Update Timestamps**.

## Phase 4: Verify and Document

1. **Verify Links**: Check internal links work.
2. **Update Health Audits**.

## References

- [README.md](../../../../README.md)
- [GEMINI.md](../../../../GEMINI.md)

```

---

## Customization

This prompt is pre-configured for Praxis. No placeholders needed.
