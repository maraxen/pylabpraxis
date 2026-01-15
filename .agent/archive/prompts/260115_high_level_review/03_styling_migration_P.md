# Agent Prompt: Styling Migration Planning


**Status:** 🟢 Completed
**Priority:** P3
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Medium
**Dependencies:** `references/styling_audit_report.md`
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Create a detailed `implementation_plan.md` to migrate the frontend codebase from hardcoded styling values to Theme CSS Variables and Tailwind utility classes.
**Input**: `references/styling_audit_report.md` (Generated in Inspection phase).
**Goal**: Define the exact steps to refactor colors and spacing without breaking the UI.

## 2. Technical Implementation Strategy

**(To be developed during Planning)**

The plan should cover:

1. **Global Variables**: Updating `src/styles.scss` with missing semantic tokens found in the audit.
2. **Search & Replace Strategy**: How to safely replace `#ED7A9B` with `var(--primary-color)` across 24+ files.
3. **Component Refactoring**: A step-by-step approach for high-offender files (`unified-shell.component.ts`, etc.).
4. **Linting**: Adding rules to prevent regression.

## 3. Context & References

**Relevant Skills**:

- `frontend-design`
- `code-maintenance`

**Primary Files**:

| Path | Description |
|:-----|:------------|
| `references/styling_audit_report.md` | Audit findings |
| `praxis/web-client/src/styles.scss` | Theme definition |
| `praxis/web-client/src/app` | Source code |

## 4. Constraints & Conventions

- **Do Not Execute**: PLANNING only (Type P).
- **Output**: `implementation_plan.md` (verified by user).
- **Styling**: Use Tailwind (`p-4`, `text-primary`) where possible, falling back to CSS variables (`var(--primary-color)`) for custom properties.

## 5. Verification Plan

**Definition of Done**:

1. `implementation_plan.md` is created and approved by the user.
2. Prompt `03_styling_migration_E.md` is created/queued.

---

## On Completion

- [x] Create `03_styling_migration_E.md` (Type E)
- [x] Mark this prompt complete in batch README
