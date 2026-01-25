# AUDIT-09: Replace Mock Methods with Real Introspection

## Problem

Direct Control uses hardcoded mock methods instead of real machine capabilities. Feature is non-functional.

## Target Files

- `praxis/web-client/src/app/features/playground/components/direct-control/direct-control.component.ts`
- `praxis/web-client/src/app/features/playground/components/direct-control/direct-control.component.html`

## Requirements

### 1. Replace Mock Data Source

Remove `getMockMethodsForCategory()` and replace with real introspection.

In `direct-control.component.ts`:

```typescript
// Remove this mock function entirely:
// private getMockMethodsForCategory(category: string): MethodInfo[] { ... }

// Replace with real data source:
private loadMethods() {
  if (!this.machine()) return;
  
  // Get methods from machine definition
  const machineType = this.machine()?.machine_type;
  if (machineType) {
    this.methods.set(this.getMethodsFromMachineType(machineType));
  }
}

private getMethodsFromMachineType(type: string): MethodInfo[] {
  // Look up methods from machine definition service
  const definition = this.machineDefinitionService.getDefinition(type);
  return definition?.methods ?? [];
}
```

### 2. Add Response/Error Handling

The component currently "fires and forgets". Add feedback:

```typescript
// Add state signals
commandResult = signal<any>(null);
commandError = signal<string | null>(null);
isExecuting = signal(false);

// Update runCommand method
runCommand() {
  if (!this.form.valid) return;
  
  this.isExecuting.set(true);
  this.commandError.set(null);
  this.commandResult.set(null);
  
  const command = {
    machineName: this.machine()?.name,
    methodName: this.selectedMethod()?.name,
    args: this.form.value
  };
  
  this.executeCommand.emit(command);
  
  // Listen for result (parent should call back)
  // Or use a service that returns Observable
}

// Add method for parent to call with result
handleCommandResult(result: any) {
  this.isExecuting.set(false);
  this.commandResult.set(result);
}

handleCommandError(error: string) {
  this.isExecuting.set(false);
  this.commandError.set(error);
}
```

### 3. Update Template with Feedback UI

In `direct-control.component.html`:

```html
<!-- Loading state -->
<mat-progress-bar *ngIf="isExecuting()" mode="indeterminate"></mat-progress-bar>

<!-- Result display -->
<div class="command-result" *ngIf="commandResult()">
  <mat-icon color="primary">check_circle</mat-icon>
  <pre>{{ commandResult() | json }}</pre>
</div>

<!-- Error display -->
<div class="command-error" *ngIf="commandError()">
  <mat-icon color="warn">error</mat-icon>
  <span>{{ commandError() }}</span>
</div>
```

### 4. Improve Parameter Type Support

Update `getArgType()` to handle complex types:

```typescript
getArgType(type: string): 'number' | 'boolean' | 'text' | 'list' | 'select' {
  if (type.includes('int') || type.includes('float')) return 'number';
  if (type.includes('bool')) return 'boolean';
  if (type.startsWith('list[')) return 'list';
  if (type.startsWith('Literal[') || type.includes('enum')) return 'select';
  return 'text';
}
```

## Reference

See `docs/audits/AUDIT-09-direct-control.md` for full gap analysis.

## Verification

```bash
npm run test --prefix praxis/web-client
npx playwright test e2e/specs/playground-direct-control.spec.ts
```
