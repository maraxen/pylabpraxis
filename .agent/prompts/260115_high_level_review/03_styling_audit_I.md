# Agent Prompt: Styling Audit


**Status:** ✅ Completed
**Priority:** P3
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Easy
**Dependencies:** None
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Audit the frontend codebase for hardcoded styling values and plan a migration to Theme CSS Variables.
**Problem**: Multiple components use hardcoded hex codes (`#1a1a2e`, `#4caf50`, etc.) instead of `var(--sys-surface)`, `var(--sys-primary)`.
**Input**: User reports "Every styling review that needs to be done".

## 2. Technical Implementation Strategy

**Inspection Phase**:

1. Run `grep` or `ripgrep` for hex codes (`#[0-9a-fA-F]{3,6}`) in `src/app`.
2. Identify non-standard spacing/sizing (hardcoded `px` values that should be standard spacing units).

**Output Generation**:

- Create `references/styling_audit_report.md` detailing:
  - List of files with high offensiveness (many hardcoded values).
  - Distribution of hex colors to identify common palettes that need variables.

## 3. Context & References

**Relevant Skills**:

- `web-design-guidelines` (Validate against design system)
- `frontend-design` (Aesthetic consistency)

**Primary Files to Inspect**:

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app` | Source root |
| `praxis/web-client/src/styles.scss` | Global Theme Vars |

## 4. Constraints & Conventions

- **Do Not Implement**: INSPECTION only (Type I).
- **Output**: `references/styling_audit_report.md`.

## 5. Verification Plan

**Definition of Done**:

1. `references/styling_audit_report.md` created.
2. Prompt `03_styling_migration_P.md` Queued.

---

## On Completion

- [x] Create `03_styling_migration_P.md` (Type P)
- [x] Mark this prompt complete in batch README and set status to ✅ Completed
