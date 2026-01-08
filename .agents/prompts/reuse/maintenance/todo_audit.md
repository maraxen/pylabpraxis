# Maintenance Prompt: TODO Audit

**Purpose:** Migrate TODOs to technical debt tracking  
**Frequency:** Per health audit  

---

## Prompt

```markdown
Examine .agents/README.md for development context.

## Task

Find all TODO/FIXME comments in the codebase, migrate actionable items to TECHNICAL_DEBT.md.

## Phase 1: Triage

1. **Find All TODOs**:

   **Backend**:
   ```bash
   grep -rn "TODO\|FIXME\|XXX\|HACK" praxis/backend --include="*.py" > todos_backend.log 2>&1
   ```

   **Frontend**:

   ```bash
   grep -rn "TODO\|FIXME\|XXX\|HACK" praxis/web-client/src --include="*.ts" --include="*.html" > todos_frontend.log 2>&1
   ```

1. **Count**:

   ```bash
   wc -l todos_backend.log todos_frontend.log
   ```

2. **Prioritize**: Start with the layer with fewer items.

## Phase 2: Categorize and Strategize

1. **Review**:

   ```bash
   cat todos_backend.log | head -n 50
   ```

2. **Categorize**:

   | Category | Action |
   |:---------|:-------|
   | **Actionable TODO** | Migrate to TECHNICAL_DEBT.md |
   | **Stale/completed** | Remove the comment |
   | **Already tracked** | Remove or add reference |
   | **Still needed marker** | Keep with cleanup |

3. **Document Strategy** before applying fixes.

4. **Get User Input**: ⏸️ PAUSE for approval.

## Phase 3: Apply Fixes

1. **Migrate to TECHNICAL_DEBT.md**:

   Add entries in this format:

   ```markdown
   ### [Brief description]
   
   **File**: `path/to/file.py:123`
   **Priority**: High/Medium/Low
   **Description**: [What needs to be done]
   ```

2. **Clean Up Comments**:
   - Remove completed/stale TODOs
   - Update remaining with ticket/issue reference

## Phase 4: Verify and Document

1. **Re-count**:

   ```bash
   grep -rn "TODO\|FIXME" praxis/backend --include="*.py" | wc -l
   ```

2. **Update Health Audits**.

## References

- [TECHNICAL_DEBT.md](../../../TECHNICAL_DEBT.md)

```

---

## Customization

This prompt is pre-configured for Praxis. No placeholders needed.
