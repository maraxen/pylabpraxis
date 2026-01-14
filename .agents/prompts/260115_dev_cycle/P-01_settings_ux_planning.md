# Agent Prompt: Settings UX Planning

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P3  
**Batch:** [260115](README.md)  
**Difficulty:** Medium  
**Dependencies:** None  
**Backlog Reference:** [audit_notes_260114.md](../../artifacts/audit_notes_260114.md) Section H.2

---

## 1. The Task

Conduct in-depth planning for a Settings UX overhaul. This is a design task, not implementation.

**User Goal:** Settings page needs overhaul - determine what settings would be valuable and the best way to present them (search bar, tabs, additional settings).

**Deliverable:** A design artifact (`settings_ux_design.md`) proposing the new Settings architecture.

## 2. Planning Strategy

### Step 1: Current State Audit

Review `settings.component.ts`:

- What settings currently exist?
- How are they organized?
- What's the current visual layout?

### Step 2: Settings Inventory

Categorize potential settings:

| Category | Settings | Currently Exists? |
|:---------|:---------|:------------------|
| Appearance | Theme (light/dark/system) | ✅ |
| Appearance | Density (compact/normal) | ❓ |
| Simulation | Default backend | ❓ |
| Simulation | Infinite consumables | ✅ |
| Hardware | Auto-discover on startup | ❓ |
| Hardware | USB device permissions | ❓ |
| Data | Clear run history | ❓ |
| Data | Export preferences | ❓ |
| Notifications | Enable/disable | ❓ |
| Tutorial | Reset/restart | ✅ |

### Step 3: UX Pattern Research

Consider:

- **Tabs vs. Sections**: When is each appropriate?
- **Search**: Should settings be searchable?
- **Danger Zone**: How to handle destructive actions?
- **Sync Indicator**: Show if settings are local vs. synced?

### Step 4: Wireframe Concepts

Propose 2-3 layout options:

1. Vertical tabs with section content
2. Single scrolling page with section headers
3. Search-first with categorized results

## 3. Output Artifact

Create `.agents/artifacts/settings_ux_design.md` with:

```markdown
# Settings UX Design

## Current State
[Screenshot or description of current settings]

## Proposed Settings Inventory
[Full list organized by category]

## UX Recommendations

### Layout Choice
[Tabs vs. Sections with rationale]

### Search
[Should we implement? Complexity vs. value]

### Danger Zone
[Pattern for destructive actions]

## Wireframes
[Text-based wireframes or images]

## Implementation Phases
[Suggested rollout]
```

## 4. Constraints & Conventions

- **No Code**: This is design only
- **Reference**: Look at VS Code, Figma settings for inspiration
- **Screenshots**: Capture current state for comparison

## 5. Verification Plan

**Definition of Done:**

1. `settings_ux_design.md` artifact created
2. At least 10 potential settings identified
3. Layout recommendation with rationale
4. User review requested

---

## On Completion

- [x] Create `.agents/artifacts/settings_ux_design.md`
- [x] Update this prompt status to 🟢 Completed
- [x] Request user review via `notify_user`

---

## References

- `src/app/features/settings/` - Current implementation
- `.agents/artifacts/audit_notes_260114.md` - Source requirements
