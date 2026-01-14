# Agent Prompt: Card Visual Audit

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P3  
**Batch:** [260115](README.md)  
**Difficulty:** Medium  
**Dependencies:** None  
**Backlog Reference:** [audit_notes_260114.md](../../artifacts/audit_notes_260114.md) Section I

---

## 1. The Task

Conduct a visual audit of card components across the application to identify layout, overlap, and hierarchy issues.

**User-Reported Issues:**

- Cards in inventory management have overlap issues
- Corner chips and text overlap without collision detection
- No flex adjustment of font size for constrained spaces
- Need to define "minimum card" that expands with available space

**Goal:** Document all card variants, their issues, and propose a consistent card design system.

## 2. Technical Inspection Strategy

### Step 1: Locate Card Components

```bash
cd praxis/web-client/src/app
find . -name "*card*" -type f -name "*.ts"
grep -rn "mat-card" --include="*.html" --include="*.ts" | head -50
```

### Step 2: Catalog Card Variants

Create a table of all card usages:

| Component | Card Type | Content | Known Issues |
|:----------|:----------|:--------|:-------------|
| MachineListComponent | Machine card | Name, status, type | TBD |
| ResourceAccordion | Resource card | Name, category, properties | TBD |
| ProtocolLibrary | Protocol card | Name, description, tags | TBD |
| HomeComponent | Stats card | Icon, count, label | TBD |

### Step 3: Visual Inspection via Browser Agent

For each card type:

1. Navigate to the page containing the card
2. Capture screenshot at full width
3. Resize to narrow width (300px), capture screenshot
4. Note any text truncation, overlap, or layout breaks

### Step 4: Responsive Breakpoint Analysis

Document how cards behave at:

- Desktop (1280px+)
- Tablet (768px-1279px)  
- Mobile (<768px)

## 3. Output Artifact

Create `.agents/artifacts/card_audit_findings.md` with:

```markdown
# Card Visual Audit Findings

## Card Inventory
[Table of all card usages]

## Issue Catalog

### MachineListComponent Cards
- **Screenshots:** [links]
- **Full-width issues:** [description]
- **Narrow-width issues:** [description]
- **Proposed fixes:** [solutions]

[Repeat for each card type]

## Design System Recommendations

### Minimum Card Definition
[What content must always be visible]

### Progressive Enhancement
[What content appears as space increases]

### Responsive Breakpoints
[Consistent behavior at each breakpoint]

### Shared Styles
[CSS utilities to create]
```

## 4. Constraints & Conventions

- **Screenshots**: Save to `.agents/tmp/cards/`
- **Styling**: Reference theme tokens from `styles.scss`

## 5. Verification Plan

**Definition of Done:**

1. All card usages catalogued
2. Screenshots captured for at least 4 card types
3. Responsive issues documented
4. Design system recommendations provided

---

## On Completion

- [ ] Create `.agents/artifacts/card_audit_findings.md`
- [ ] Update this prompt status to 🟢 Completed

---

## References

- `.agents/artifacts/audit_notes_260114.md` - Source requirements
