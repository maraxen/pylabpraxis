# FIX-02: Implement Resource Editing TODO

## Context

**File**: `praxis/web-client/src/app/features/assets/components/resource-list/resource-list.component.ts`
**Lines**: 249, 253
**Current Code**:

- Line 249: `// TODO: Implement resource editing`
- Line 253: `// TODO: Implement resource duplication`

## Requirements

Implement placeholder methods with user feedback:

```typescript
editResource(resource: Resource): void {
  this.snackBar.open('Resource editing coming soon', 'OK', { duration: 3000 });
}

duplicateResource(resource: Resource): void {
  this.snackBar.open('Resource duplication coming soon', 'OK', { duration: 3000 });
}
```

Ensure MatSnackBar is imported and injected if not already:

```typescript
import { MatSnackBar } from '@angular/material/snack-bar';

private snackBar = inject(MatSnackBar);
```

Do NOT:

- Implement full editing functionality
- Modify other components
- Change resource data structures

## Acceptance Criteria

- [ ] `editResource()` shows snackbar
- [ ] `duplicateResource()` shows snackbar
- [ ] No TypeScript errors
- [ ] No console errors when methods are called
