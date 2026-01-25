# FIX-01: Implement Machine Editing TODO

## Context

**File**: `praxis/web-client/src/app/features/assets/components/machine-list/machine-list.component.ts`
**Line**: 529
**Current Code**: `// TODO: Implement machine editing`

## Requirements

Implement the `editMachine(machine)` method. Two acceptable approaches:

### Option A: Show "Coming Soon" message

```typescript
editMachine(machine: Machine): void {
  this.snackBar.open('Machine editing coming soon', 'OK', { duration: 3000 });
}
```

### Option B: Open details dialog in edit mode (if supported)

```typescript
editMachine(machine: Machine): void {
  this.dialog.open(MachineDetailsDialogComponent, {
    data: { machine, mode: 'edit' }
  });
}
```

Choose Option A unless MachineDetailsDialogComponent already supports edit mode.

Also implement `duplicateMachine()` at line 533:

```typescript
duplicateMachine(machine: Machine): void {
  this.snackBar.open('Machine duplication coming soon', 'OK', { duration: 3000 });
}
```

Do NOT:

- Modify other components
- Add complex editing logic (scope creep)
- Remove the TODO comment until functionality is implemented

## Acceptance Criteria

- [ ] `editMachine()` provides user feedback
- [ ] `duplicateMachine()` provides user feedback
- [ ] No TypeScript errors
- [ ] Methods are accessible from template if needed
