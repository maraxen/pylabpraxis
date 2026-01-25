# FIX-04: Guard method.args Undefined

## Context

**File**: `praxis/web-client/src/app/features/playground/components/direct-control/direct-control.component.ts`
**Priority**: P1 (crash fix)
**Problem**: Component crashes when `method.args` is undefined

## Requirements

Add defensive guards in two locations:

### Location 1: Line 88 (buildForm method)

**Current**:

```typescript
buildForm(method: MethodInfo) {
  const group: any = {};
  method.args.forEach(arg => {
```

**Fixed**:

```typescript
buildForm(method: MethodInfo) {
  const group: any = {};
  (method.args || []).forEach(arg => {
```

### Location 2: Line 108 (similar pattern)

Apply the same guard:

```typescript
(method.args || []).forEach(arg => {
```

Search for any other usages of `method.args` in the file and apply the same pattern.

Do NOT:

- Change the component's public API
- Modify method signatures
- Add new dependencies

## Acceptance Criteria

- [ ] `method.args` is guarded against undefined in all usages
- [ ] No crashes when method has no args
- [ ] TypeScript compilation succeeds
- [ ] Existing functionality preserved
