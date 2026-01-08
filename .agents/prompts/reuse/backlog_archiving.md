# Reusable Prompt: Backlog Archiving

Examine .agents/README.md for development context.

**Purpose:** Consolidate completed work, archive backlog items, and clean up development matrix  
**Use when:** End of sprint, quarterly cleanup, or when backlog has accumulated completed items

---

## Prompt

```
Examine .agents/README.md for development context.

## Task

Review completed work, archive backlog items, and clean up the development matrix.

## Instructions

1. **Review Current State**:
   - [DEVELOPMENT_MATRIX.md](.agents/DEVELOPMENT_MATRIX.md) - Identify ✅ Complete or 🟡 In Progress items that are finished
   - [backlog/](.agents/backlog/) - Review item statuses

2. **Identify Items for Archiving**: Collect items that:
   - Are marked ✅ Complete in the matrix
   - Have all checkboxes completed in their backlog file
   - Have been verified and validated

3. **Archive Process**: For each completed item:
   - Move backlog file from `backlog/` to `archive/`
   - Update any internal links in the archived file
   - Move row from "Active Items" to "Completed Items" in DEVELOPMENT_MATRIX.md
   - Add completion date

4. **Consolidate Related Items**: If multiple completed items belong to the same initiative:
   - Create a consolidated archive document summarizing the work
   - Reference individual archived items
   - Update ROADMAP.md to mark milestone as complete if applicable

5. **Update Ongoing Maintenance**: For health audits and recurring items:
   - Update "Last Review" dates in the matrix
   - Reset checkboxes for next review cycle if needed

6. **Ask for clarification and specification** on:
   - Items with ambiguous completion status
   - Whether partial completions should be archived or kept active
   - Consolidation groupings for related items
   - Whether to create summary docs for major milestones

## Output

Provide:
- List of items archived
- Updates to DEVELOPMENT_MATRIX.md (moved to Completed)
- Updates to ROADMAP.md (milestones marked complete)
- Any consolidation documents created
```

---

## Customization

No placeholders required. Run as-is for standard archive review.

---

## Example Usage

```
Examine .agents/README.md for development context.

## Task

Review completed work, archive backlog items, and clean up the development matrix.

[... full prompt as above ...]
```
