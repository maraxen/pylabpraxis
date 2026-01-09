# Agent Prompt: 29_protocol_detail_dialog

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260109](./README.md)
**Backlog:** [ux_issues_260109.md](../../backlog/ux_issues_260109.md)

---

## Task

Replace protocol detail page navigation with an inline dialog. Clicking a protocol should open a details dialog instead of navigating to a separate page.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [protocol-library.component.ts](../../../praxis/web-client/src/app/features/protocols/components/protocol-library/protocol-library.component.ts) | Protocol list with click handler |
| [protocol-detail.component.ts](../../../praxis/web-client/src/app/features/protocols/components/protocol-detail/protocol-detail.component.ts) | Current detail page |
| [protocol.routes.ts](../../../praxis/web-client/src/app/features/protocols/protocol.routes.ts) | Route configuration |

---

## Current Behavior

```typescript
// protocol-library.component.ts (line 200)
this.router.navigate(['/protocols', protocol.accession_id]);
```

Clicking a protocol navigates to `/protocols/:id` which renders `ProtocolDetailComponent` as a full page.

---

## Required Changes

### 1. Create Protocol Detail Dialog Component

Create `protocol-detail-dialog.component.ts`:

```typescript
@Component({
  selector: 'app-protocol-detail-dialog',
  standalone: true,
  imports: [MatDialogModule, CommonModule, ...],
  template: `...`
})
export class ProtocolDetailDialogComponent {
  protocol = input.required<ProtocolDefinition>();

  constructor(public dialogRef: MatDialogRef<ProtocolDetailDialogComponent>) {}
}
```

**Dialog Content** (from existing `protocol-detail.component.ts`):
- Protocol name and description
- Asset requirements list
- Parameter definitions list
- Simulation status/warnings
- "Run Protocol" button

### 2. Update Protocol Library Click Handler

```typescript
// Before
onProtocolClick(protocol: ProtocolDefinition) {
  this.router.navigate(['/protocols', protocol.accession_id]);
}

// After
onProtocolClick(protocol: ProtocolDefinition) {
  this.dialog.open(ProtocolDetailDialogComponent, {
    data: { protocol },
    width: '700px',
    maxHeight: '80vh'
  });
}
```

### 3. Remove Info Button

The "i" info icon button that currently navigates to the detail page should be removed from protocol cards/list items.

### 4. Dialog Actions

The dialog should include:
- **Close** button
- **Run Protocol** button → Navigates to `/run-protocol?id=<accession_id>`

### 5. Consider Route Deprecation

The `/protocols/:id` route can be deprecated but kept for backward compatibility (direct URL access).

---

## Design Guidelines

- Dialog width: 700px (or 80vw max)
- Use existing card styling from protocol detail page
- Include Material Dialog actions bar
- Support both light and dark themes

---

## On Completion

- [ ] Protocol detail dialog component created
- [ ] Protocol library opens dialog on click
- [ ] Info button removed from protocol cards
- [ ] "Run Protocol" button navigates correctly
- [ ] Update backlog status
- [ ] Mark this prompt complete in batch README

---

## References

- [ux_issues_260109.md](../../backlog/ux_issues_260109.md) - Section 3
- [ui_consistency.md](../../backlog/ui_consistency.md) - Dialog patterns
