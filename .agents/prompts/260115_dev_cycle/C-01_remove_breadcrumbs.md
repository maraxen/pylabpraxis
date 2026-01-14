# Agent Prompt: Remove Breadcrumbs

Examine `.agents/README.md` for development context.

**Status:** 🔵 Complete
**Priority:** P2
**Batch:** [260115](README.md)
**Difficulty:** Easy
**Dependencies:** None
**Backlog Reference:** [audit_notes_260114.md](../../artifacts/audit_notes_260114.md) Section D

---

## 1. The Task

Remove the breadcrumb bar from the unified shell. It currently serves no purpose.

**User Decision:** Remove entirely, document decision.

## 2. Technical Implementation Strategy

#### [MODIFY] `praxis/web-client/src/app/layout/unified-shell.component.ts`

Remove:

- Import of `BreadcrumbComponent`
- `<app-breadcrumb>` from template
- `.breadcrumb-bar` styles
- `BreadcrumbComponent` from imports array

#### [DELETE or DEPRECATE] `praxis/web-client/src/app/core/components/breadcrumb/`

Mark as deprecated or delete entirely.

#### [DELETE or DEPRECATE] `praxis/web-client/src/app/core/services/breadcrumb.service.ts`

Mark as deprecated or delete entirely.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `layout/unified-shell.component.ts` | Remove breadcrumb usage |
| `core/components/breadcrumb/` | Delete or deprecate |
| `core/services/breadcrumb.service.ts` | Delete or deprecate |

## 4. Constraints & Conventions

- **Document Decision**: Add note to `.agents/NOTES.md` explaining why breadcrumbs were removed
- **Frontend Path**: `praxis/web-client`

## 5. Verification Plan

**Definition of Done:**

1. Breadcrumb bar no longer visible in UI
2. No console errors
3. Build passes:

```bash
cd praxis/web-client
npm run build
```

---

## On Completion

- [x] Add note to `.agents/NOTES.md`
- [x] Commit changes
- [x] Mark this prompt complete

---

## References

- `.agents/artifacts/audit_notes_260114.md` - Source decision
