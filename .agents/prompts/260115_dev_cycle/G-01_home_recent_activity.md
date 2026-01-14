# Agent Prompt: Home Recent Activity Mock Data

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P3  
**Batch:** [260115](README.md)  
**Difficulty:** Easy  
**Dependencies:** None  
**Backlog Reference:** [audit_notes_260114.md](../../artifacts/audit_notes_260114.md) Section H.1

---

## 1. The Task

Update the Home page "Recent Activity" section to use realistic mock data based on bundled example protocols. Add ability to clear fake runs.

**Current State:** Hardcoded mock data like "Serial Dilution Run #42".

**Desired State:** Mock data referencing actual bundled protocols (e.g., "Simple Transfer", "Selective Transfer").

## 2. Technical Implementation Strategy

#### [MODIFY] `praxis/web-client/src/app/features/home/home.component.ts`

Update `loadRuns()` method:

- Reference protocol names that exist in the system
- Use realistic timestamps
- Add "Clear Demo Runs" button

Template changes:

```html
@if (recentRuns().length > 0) {
  <!-- existing runs -->
  <button mat-stroked-button (click)="clearDemoRuns()" class="mt-2">
    Clear Demo Runs
  </button>
}
```

Component changes:

```typescript
clearDemoRuns() {
  this.recentRuns.set([]);
  // Optionally persist to localStorage
  localStorage.setItem('praxis_demo_runs_cleared', 'true');
}

private loadRuns() {
  if (localStorage.getItem('praxis_demo_runs_cleared') === 'true') {
    this.recentRuns.set([]);
    return;
  }
  // Load realistic mock data
  this.recentRuns.set([
    { name: 'Simple Transfer Demo', protocolName: 'Simple Transfer', ... },
    { name: 'Selective Transfer Test', protocolName: 'Selective Transfer', ... },
  ]);
}
```

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `features/home/home.component.ts` | Update mock data, add clear button |

**Reference Files:**

| Path | Description |
|:-----|:------------|
| `assets/browser-data/protocols.ts` | Bundled protocol names |

## 4. Constraints & Conventions

- **Frontend Path**: `praxis/web-client`
- **Persistence**: Use localStorage for "cleared" state

## 5. Verification Plan

**Definition of Done:**

1. [x] Recent activity shows realistic protocol names
2. [x] "Clear Demo Runs" button works
3. [x] Cleared state persists across page refresh

**Manual Verification:**

1. Navigate to Home page
2. Verify protocol names match bundled protocols
3. Click "Clear Demo Runs"
4. Refresh page, verify runs stay cleared

---

## On Completion

- [x] Commit changes
- [x] Mark this prompt complete

---

## References

- `.agents/artifacts/audit_notes_260114.md` - Source requirements
