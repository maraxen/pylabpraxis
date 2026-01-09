# Agent Prompt: Fix Registry UI Issues

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Difficulty:** Medium
**Batch:** [260109](./README.md)
**Backlog Reference:** [asset_management.md](../../backlog/asset_management.md#p2-registry-ui-issues)

---

## 1. The Task

The Registry UI in asset management has several issues:
1. Add Machine button incorrectly links to Add Resource
2. Add Resource shows error "definitions are precinct in browser mode" (likely typo for "present")
3. The overall registry interface needs improvement for better UX

**Goal:** Fix navigation issues and improve error messaging in the Registry UI for browser mode.

**User Value:** Users can browse and understand available machine and resource definitions.

---

## 2. Technical Implementation Strategy

**Issue Analysis:**

The Registry (definitions list) shows available machine and resource types that can be instantiated. In browser mode, definitions come from bundled data rather than a backend.

**Problems to Fix:**

1. **Navigation Bug**: Add Machine → Add Resource linking issue
2. **Error Message**: "precinct" should be "present" or better messaging
3. **Browser Mode UX**: Clarify that registry is read-only in browser mode

**Frontend Components:**

1. Fix button click handlers in `DefinitionsListComponent` or parent
2. Update error message in resource definitions view
3. Add informational banner for browser mode limitations

**Data Flow:**

1. User clicks "Add Machine" → should navigate to machine dialog
2. User clicks "Add Resource" → should navigate to resource dialog or show info

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/definitions-list/definitions-list.component.ts` | Registry list component |
| `praxis/web-client/src/app/features/assets/assets.component.ts` | Parent component with navigation logic |
| `praxis/web-client/src/app/features/assets/components/asset-dashboard/asset-dashboard.component.ts` | Dashboard with registry links |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts` | Machine creation dialog |
| `praxis/web-client/src/app/features/assets/components/resource-dialog.component.ts` | Resource creation dialog |
| `praxis/web-client/src/app/core/services/mode.service.ts` | Mode detection service |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular tasks
- **Frontend Path**: `praxis/web-client`
- **State**: Use Angular Signals
- **Mode Detection**: Use `ModeService.isBrowserMode()`

**Investigation Steps:**

```bash
# Find "precinct" typo
grep -r "precinct" praxis/web-client/src/

# Find add machine/resource handlers
grep -r "addMachine\|addResource" praxis/web-client/src/app/features/assets/
```

**Fix Navigation:**

In the component handling add buttons:

```typescript
// Ensure correct navigation
addMachine() {
  // Should open machine dialog, not resource
  this.dialog.open(MachineDialogComponent, { ... });
}

addResource() {
  // Should open resource dialog
  this.dialog.open(ResourceDialogComponent, { ... });
}
```

**Fix Error Message:**

```typescript
// Before
'definitions are precinct in browser mode'

// After
'Resource definitions are loaded from bundled data in browser mode. Connect to a backend to add custom definitions.'
```

**Add Browser Mode Banner:**

```html
@if (isBrowserMode()) {
  <div class="browser-mode-banner">
    <mat-icon>info</mat-icon>
    <span>
      Registry is read-only in browser mode.
      Definitions are loaded from bundled PyLabRobot data.
    </span>
  </div>
}
```

---

## 5. Verification Plan

**Definition of Done:**

1. "Add Machine" button opens machine dialog
2. "Add Resource" button opens resource dialog
3. No "precinct" typo in error messages
4. Browser mode shows informational banner about read-only registry
5. Users understand registry limitations in browser mode

**Verification Commands:**

```bash
cd praxis/web-client
npm run build

# Verify no typos
grep -r "precinct" dist/
```

**Manual Verification:**
1. Navigate to Assets > Registry tab
2. Try Add Machine button - verify correct dialog opens
3. Try Add Resource button - verify correct dialog opens
4. Check for clear browser mode messaging
5. Verify no confusing error messages

---

## On Completion

- [ ] Commit changes with message: `fix(assets): fix registry UI navigation and messaging`
- [ ] Update backlog item status in `backlog/asset_management.md`
- [ ] Update `DEVELOPMENT_MATRIX.md` if applicable
- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed

---

## References

- `.agents/README.md` - Development context and agent workflow
- `backlog/asset_management.md` - Full asset management issue tracking
