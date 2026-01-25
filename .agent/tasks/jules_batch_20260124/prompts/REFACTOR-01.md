# REFACTOR-01: Add User-Friendly Error Toasts to Asset Wizard

## Context

**File**: `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.ts`
**Issue**: Raw database errors shown in console instead of user-friendly messages

## Requirements

Add error handling with MatSnackBar:

### 1. Inject MatSnackBar (if not already)

```typescript
import { MatSnackBar } from '@angular/material/snack-bar';

private snackBar = inject(MatSnackBar);
```

### 2. Wrap createAsset() with try-catch

```typescript
async createAsset(): Promise<void> {
  try {
    // existing creation logic...
    
    this.snackBar.open('Asset created successfully', 'OK', { duration: 3000 });
  } catch (error: any) {
    const msg = error?.message || String(error);
    
    if (msg.includes('UNIQUE constraint')) {
      this.snackBar.open(
        'An asset with this name already exists. Please use a different name.',
        'OK',
        { duration: 5000 }
      );
    } else {
      this.snackBar.open(
        'Failed to create asset. Please try again.',
        'OK',
        { duration: 5000 }
      );
      console.error('Asset creation error:', error);
    }
  }
}
```

Do NOT:

- Change the wizard flow or steps
- Modify validation logic
- Add complex error recovery

## Acceptance Criteria

- [ ] UNIQUE constraint errors show friendly message
- [ ] Generic errors show generic message
- [ ] Success shows confirmation
- [ ] No TypeScript errors
- [ ] Wizard still functions correctly
