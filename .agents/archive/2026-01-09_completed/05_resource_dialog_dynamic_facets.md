# Agent Prompt: 05_resource_dialog_dynamic_facets

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260109](./README.md)  
**Backlog:** [ui_consistency.md](../../backlog/ui_consistency.md)  

---

## Task

Replace hardcoded "More filters" facets in the Resource dialog with dynamically derived facets from resource type definitions.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [ui_consistency.md](../../backlog/ui_consistency.md) | Work item tracking (Phase 5) |
| `praxis/web-client/src/app/features/assets/dialogs/add-resource-dialog/` | Resource dialog |
| `praxis/web-client/src/app/core/services/sqlite.service.ts` | Type definitions access |

---

## Implementation

1. **Identify Hardcoded Facets**:
   - Locate static filter options in resource dialog
   - Document current hardcoded values

2. **Dynamic Derivation**:
   - Query resource type definitions for metadata
   - Extract filterable properties (category, manufacturer, etc.)
   - Build facet options from available metadata values

3. **UI Integration**:
   - Update filter chip dropdown to use dynamic options
   - Ensure selected filters persist across dialog reopens

4. **Sync Mechanism**:
   - Keep filter dropdown in sync with available resource metadata
   - Handle new resources adding new facet values

---

## Expected Outcome

- Filter facets auto-populate from resource type definitions
- New resource types automatically add their metadata to filters
- No manual updates needed when new resource types are added

---

## Project Conventions

- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
