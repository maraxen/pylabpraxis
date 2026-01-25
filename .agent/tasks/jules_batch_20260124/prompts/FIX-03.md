# FIX-03: Add Deck Confirmation Dialog

## Context

**File**: `praxis/web-client/src/app/features/run-protocol/components/deck-setup-wizard/deck-setup-wizard.component.ts`
**Line**: 337
**Current Code**: `// TODO: Add confirmation dialog`

## Requirements

Add a confirmation dialog before destructive deck operations. Find the method containing the TODO and wrap the destructive action:

```typescript
import { MatDialog } from '@angular/material/dialog';

// Inject if not already
private dialog = inject(MatDialog);

// Before destructive action
const dialogRef = this.dialog.open(ConfirmDialogComponent, {
  data: {
    title: 'Confirm Action',
    message: 'Are you sure you want to proceed? This action cannot be undone.',
    confirmText: 'Confirm',
    cancelText: 'Cancel'
  }
});

dialogRef.afterClosed().subscribe(confirmed => {
  if (confirmed) {
    // Proceed with destructive action
  }
});
```

If `ConfirmDialogComponent` doesn't exist, use a simple `window.confirm()`:

```typescript
if (confirm('Are you sure you want to proceed? This action cannot be undone.')) {
  // Proceed with destructive action
}
```

Do NOT:

- Create new dialog components (out of scope)
- Modify unrelated deck logic
- Change the deck data structures

## Acceptance Criteria

- [ ] Destructive action requires user confirmation
- [ ] User can cancel the action
- [ ] No TypeScript errors
- [ ] TODO comment replaced with implementation
