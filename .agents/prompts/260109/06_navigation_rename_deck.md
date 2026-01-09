# Agent Prompt: 06_navigation_rename_deck

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [ui_consistency.md](../../backlog/ui_consistency.md)  

---

## Task

Rename sidebar navigation item "Deck" to "Workcell" and audit all navigation labels for clarity and consistency.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [ui_consistency.md](../../backlog/ui_consistency.md) | Work item tracking (Phase 2) |
| `praxis/web-client/src/app/layout/unified-shell.component.ts` | Sidebar navigation |
| `praxis/web-client/src/app/app.routes.ts` | Route definitions |

---

## Implementation

1. **Rename "Deck" to "Workcell"**:
   - Update label in `unified-shell.component.ts`
   - Update route path if applicable (e.g., `/app/deck` → `/app/workcell`)
   - Add route redirect for backwards compatibility

2. **Navigation Audit**:
   - Review all sidebar items for clarity
   - Ensure consistent naming convention (noun vs verb, singular vs plural)
   - Document any ambiguous labels

3. **Testing**:
   - Verify navigation works after rename
   - Check all internal links pointing to old route

---

## Expected Outcome

- "Deck" renamed to "Workcell" in sidebar
- Route works with new and old paths (redirect)
- Navigation labels are clear and consistent

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
