# Reusable Prompt: Technical Debt Migration

Examine .agent/README.md for development context.

**Purpose:** Review technical debt and migrate items to formal tracking (backlog + development matrix)  
**Use when:** TECHNICAL_DEBT.md has accumulated items, periodic debt review sessions

---

## Prompt

```
Examine .agent/README.md for development context.

## Task

Review technical debt and migrate items to the formal tracking system (DEVELOPMENT_MATRIX.md, backlog/, ROADMAP.md).

## Instructions

1. **Review Technical Debt**:
   - [TECHNICAL_DEBT.md](.agent/TECHNICAL_DEBT.md) - Current debt items

2. **Cross-Reference Existing Tracking**:
   - [DEVELOPMENT_MATRIX.md](.agent/DEVELOPMENT_MATRIX.md) - Check for already-tracked items
   - [backlog/](.agent/backlog/) - Identify existing coverage

3. **Analyze Each Item**: For each debt item, determine:
   - Is it already tracked? (skip if yes)
   - Priority: High | Medium | Low
   - Difficulty: 🔴 Complex | 🟡 Intricate | 🟢 Easy Win
   - Area: Backend | Frontend | REPL | Hardware | Docs
   - Should it be split into multiple items? (e.g., per-repo)

4. **Create Backlog Items**: For each new item:
   - Create backlog file using [backlog_item.md](.agent/templates/backlog_item.md) template
   - Include Goal, Phases with checkboxes, Notes, References

5. **Update Tracking Documents**:
   - Add rows to DEVELOPMENT_MATRIX.md Active Items
   - Update ROADMAP.md if item affects quarterly milestones
   - Clean up TECHNICAL_DEBT.md (keep as minimal template or note migration)

6. **Ask for clarification and specification** on:
   - Priority assignments for ambiguous items
   - Whether to split broad items into per-repo tasks
   - Roadmap inclusion for infrastructure items
   - Archive strategy for TECHNICAL_DEBT.md after migration
   - Consolidation of overlapping items (separate vs merged)

## Output

Provide:
- Summary of items analyzed (tracked vs new)
- List of new backlog items created
- Document updates made
```

---

## Customization

No placeholders required. Run as-is for standard debt review.

---

## Example Usage

```
Examine .agent/README.md for development context.

## Task

Review technical debt and migrate items to the formal tracking system (DEVELOPMENT_MATRIX.md, backlog/, ROADMAP.md).

[... full prompt as above ...]
```
