# Agent Prompt: ViewControls Adoption Audit

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Easy  
**Dependencies:** None
**Backlog Reference:** [audit_notes_260114.md](../../artifacts/audit_notes_260114.md) Section C

---

## 1. The Task

Audit the following pages to document their current filter/search implementations and determine what's needed to adopt `ViewControlsComponent`:

1. Protocol Library (`protocol-library.component.ts`)
2. Execution Monitor (`execution-monitor.component.ts` or similar)
3. Data Visualization (`data-visualization.component.ts`)

**Goal:** For each page, document existing filters and produce a spec for ViewControls integration.

## 2. Technical Inspection Strategy

### Step 1: Locate Components

```bash
cd praxis/web-client/src/app/features
find . -name "*protocol-library*" -o -name "*execution*" -o -name "*monitor*" -o -name "*data-viz*" -o -name "*visualization*"
```

### Step 2: Analyze Each Component

For each component, document:

| Aspect | Details |
|:-------|:--------|
| File path | Full path to component |
| Current search | How is search implemented? (mat-input, custom) |
| Current filters | What filters exist? (dropdowns, chips) |
| Current grouping | Any group-by functionality? |
| Current sorting | Sort options available? |
| Data source | What service/observable provides data? |
| ViewTypes needed | Card, List, Table - which make sense? |

### Step 3: Define ViewControls Config

For each page, propose:

```typescript
const viewControlsConfig: ViewControlsConfig = {
  viewTypes: ['card', 'list', 'table'],
  filters: [
    { key: 'status', label: 'Status', options: [...], pinned: true },
    // ...
  ],
  groupByOptions: [...],
  sortOptions: [...],
  storageKey: 'unique-key'
}
```

## 3. Output

Update the batch README or create a summary in this prompt's completion notes listing:

1. Files to modify
2. Existing patterns to replace
3. Proposed ViewControls configurations

## 4. Constraints & Conventions

- **Frontend Path**: `praxis/web-client`
- **Pattern Reference**: `definitions-list.component.ts` - already uses ViewControls

## 5. Verification Plan

**Definition of Done:**

1. All three components located and analyzed
2. ViewControlsConfig proposed for each
3. Migration complexity rated (Easy/Medium/Hard)

---

## On Completion

- [ ] Document findings in completion notes
- [ ] Update this prompt status to 🟢 Completed

---

## References

- `src/app/shared/components/view-controls/` - ViewControls implementation
- `src/app/features/assets/components/definitions-list/` - Reference adoption
