# Frontend Development Plan - Gemini CLI

**Date**: 2025-12-15
**Branch**: `angular_refactor`
**Target**: Angular 21.0.3 frontend with comprehensive unit tests
**Priority**: HIGH - Frontend is 75% MVP ready, needs testing + feature completion

---

## 🎯 Mission Overview

Complete the Angular frontend to production-ready state by:
1. **Unit Test Suite** - Expand from ~5% to 60%+ coverage
2. **Missing Features** - Asset definitions, protocol details, dynamic parameters
3. **UX Improvements** - Responsive design, loading states, error handling

**Current Status**: Core features working, authentication complete, but minimal testing and missing detail views.

---

## 📋 Phase 1: Unit Test Suite (HIGH PRIORITY)

**Goal**: Achieve 60% test coverage for MVP production readiness
**Current**: ~5% coverage (only basic app tests exist)
**Tech Stack**: Vitest 4.0.8 for unit tests

### Commands Reference
```bash
cd praxis/web-client
npm test                    # Run unit tests
npm test -- --coverage      # Run with coverage report
npm test -- --ui            # Run with Vitest UI
```

---

### Task 1.1: Core Infrastructure Tests 🔧

**Priority**: CRITICAL (blocks deployment)
**Estimated Effort**: 3-4 hours

#### A. AppStore Tests (`src/app/core/store/app.store.spec.ts`)

**File**: Already exists but needs expansion
**Current**: 32 tests passing
**Target**: Comprehensive state management coverage

**Test Cases to Add/Verify**:

```typescript
describe('AppStore - Extended Coverage', () => {
  // Authentication state
  ✓ Should initialize with null user and token
  ✓ Should update user state on login
  ✓ Should clear state on logout
  ✓ Should persist token to localStorage
  ✓ Should restore token from localStorage on init

  // Token management
  ✓ Should handle missing token gracefully
  ✓ Should handle malformed token
  ✓ Should clear invalid tokens

  // Computed signals
  ✓ isAuthenticated should derive from token presence
  ✓ Should emit when authentication state changes

  // Edge cases
  ✓ Should handle concurrent login/logout
  ✓ Should cleanup on multiple logout calls
});
```

**Files to modify**:
- `praxis/web-client/src/app/core/store/app.store.spec.ts`

---

#### B. AuthGuard Tests (`src/app/core/guards/auth.guard.spec.ts`)

**File**: Already exists
**Current**: 13 tests passing
**Target**: Complete route protection coverage

**Test Cases to Add/Verify**:

```typescript
describe('AuthGuard - Route Protection', () => {
  // Basic protection
  ✓ Should allow access when authenticated
  ✓ Should redirect to /login when not authenticated
  ✓ Should preserve intended route after login

  // Edge cases
  ✓ Should handle missing token
  ✓ Should handle expired token (if applicable)
  ✓ Should work with lazy-loaded routes
  ✓ Should handle navigation cancellation

  // Router integration
  ✓ Should set correct redirect URL
  ✓ Should clear redirect after successful navigation
});
```

**Files to modify**:
- `praxis/web-client/src/app/core/guards/auth.guard.spec.ts`

---

#### C. AuthInterceptor Tests (`src/app/core/http/auth.interceptor.spec.ts`)

**File**: Already exists
**Current**: 20 tests passing
**Target**: Complete HTTP interceptor coverage

**Test Cases to Add/Verify**:

```typescript
describe('AuthInterceptor - Token Injection', () => {
  // Token injection
  ✓ Should add Bearer token to requests when authenticated
  ✓ Should not add token when not authenticated
  ✓ Should handle requests without token gracefully

  // Header management
  ✓ Should preserve existing headers
  ✓ Should override Authorization if present
  ✓ Should handle multiple concurrent requests

  // Error handling
  ✓ Should handle 401 responses
  ✓ Should handle 403 responses
  ✓ Should not modify error responses

  // Edge cases
  ✓ Should work with FormData requests
  ✓ Should work with Blob responses
});
```

**Files to modify**:
- `praxis/web-client/src/app/core/http/auth.interceptor.spec.ts`

---

### Task 1.2: Service Layer Tests 🔧

**Priority**: HIGH (core business logic)
**Estimated Effort**: 4-5 hours

#### A. AuthService Tests (`src/app/features/auth/services/auth.service.spec.ts`)

**File**: Needs creation
**Target**: Complete authentication service coverage

**Test Cases**:

```typescript
describe('AuthService', () => {
  // Login flow
  ✓ Should call POST /api/v1/auth/login with credentials
  ✓ Should store token in AppStore on success
  ✓ Should return user data on successful login
  ✓ Should handle invalid credentials (401)
  ✓ Should handle network errors

  // Logout flow
  ✓ Should call POST /api/v1/auth/logout
  ✓ Should clear AppStore state
  ✓ Should redirect to login page
  ✓ Should handle logout errors gracefully

  // Token management
  ✓ Should get current user from /api/v1/auth/me
  ✓ Should handle token expiration
  ✓ Should refresh token (if implemented)
});
```

**Files to create**:
- `praxis/web-client/src/app/features/auth/services/auth.service.spec.ts`

**Reference implementation**:
- `praxis/web-client/src/app/features/auth/services/auth.service.ts`

---

#### B. AssetService Tests (`src/app/features/assets/services/asset.service.spec.ts`)

**File**: Already exists
**Current**: 15 tests passing
**Target**: Complete CRUD coverage

**Test Cases to Add/Verify**:

```typescript
describe('AssetService', () => {
  // Machines
  ✓ getMachines() should fetch all machines
  ✓ createMachine() should POST machine data
  ✓ deleteMachine() should DELETE by ID
  ✓ Should handle machine creation errors

  // Resources
  ✓ getResources() should fetch all resources
  ✓ createResource() should POST resource data
  ✓ deleteResource() should DELETE by ID
  ✓ Should handle resource creation errors

  // Definitions
  ✓ getMachineDefinitions() should call /discovery/machines
  ✓ getResourceDefinitions() should call /discovery/resources
  ✓ Should cache definitions

  // Error handling
  ✓ Should handle 404 for missing assets
  ✓ Should handle validation errors (422)
  ✓ Should retry on network failure
});
```

**Files to modify**:
- `praxis/web-client/src/app/features/assets/services/asset.service.spec.ts`

---

#### C. ProtocolService Tests (`src/app/features/protocols/services/protocol.service.spec.ts`)

**File**: Already exists
**Current**: 27 tests passing
**Target**: Complete protocol management coverage

**Test Cases to Add/Verify**:

```typescript
describe('ProtocolService', () => {
  // Protocol retrieval
  ✓ getProtocols() should fetch all protocols
  ✓ getProtocolById() should fetch single protocol
  ✓ Should handle protocol not found

  // File upload
  ✓ uploadProtocol() should POST FormData
  ✓ Should handle file validation errors
  ✓ Should track upload progress
  ✓ Should handle large file uploads

  // Protocol metadata
  ✓ Should parse protocol parameters
  ✓ Should validate parameter types
  ✓ Should handle missing metadata

  // Caching
  ✓ Should cache protocol list
  ✓ Should invalidate cache on upload
  ✓ Should refresh stale data
});
```

**Files to modify**:
- `praxis/web-client/src/app/features/protocols/services/protocol.service.spec.ts`

---

#### D. ExecutionService Tests (`src/app/features/run-protocol/services/execution.service.spec.ts`)

**File**: Already exists
**Current**: 26 tests (14 have timing issues)
**Target**: Fix timing issues, add WebSocket coverage

**Test Cases to Add/Fix**:

```typescript
describe('ExecutionService', () => {
  // Protocol execution
  ✓ startRun() should POST to /api/v1/runs
  ✓ stopRun() should POST to /api/v1/runs/:id/stop
  ✓ Should handle execution errors

  // WebSocket connection (FIX TIMING ISSUES)
  ✓ Should connect to WebSocket on startRun
  ✓ Should receive status updates
  ✓ Should receive log messages
  ✓ Should handle connection errors
  ✓ Should reconnect on disconnect
  ✓ Should cleanup on component destroy

  // State management
  ✓ Should track execution status (PREPARING/RUNNING/COMPLETED)
  ✓ Should accumulate logs
  ✓ Should update progress

  // Error handling
  ✓ Should handle protocol not found
  ✓ Should handle failed execution
  ✓ Should handle cancelled execution

  // Mock WebSocket properly to avoid timing issues
  ✓ Use fake timers (vi.useFakeTimers())
  ✓ Mock WebSocket constructor
  ✓ Advance timers instead of using real delays
});
```

**Files to modify**:
- `praxis/web-client/src/app/features/run-protocol/services/execution.service.spec.ts`

**Key Fix**: Use Vitest fake timers to eliminate timing issues:
```typescript
import { vi } from 'vitest';

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});
```

---

### Task 1.3: Component Tests (Optional - Lower Priority)

**Priority**: MEDIUM (nice-to-have for MVP)

If time permits, add tests for key components:
- Login component
- Protocol upload dialog
- Machine/Resource dialogs
- Run protocol component

**Note**: Component tests are less critical than service/infrastructure tests. Focus on Phase 1 Tasks 1.1 and 1.2 first.

---

## 📋 Phase 2: Missing Features (MEDIUM PRIORITY)

### Task 2.1: Asset Definitions Tab 🔨

**Priority**: HIGH (visible gap in UI)
**Estimated Effort**: 2-3 hours

**Current State**: Line 126 in `asset-list.component.ts` shows "Definitions listing coming soon"

**Backend Endpoints Available**:
- `GET /api/v1/discovery/machines` - Machine type definitions
- `GET /api/v1/discovery/resources` - Resource type definitions

**Implementation Steps**:

1. **Create DefinitionsListComponent**:
```typescript
// praxis/web-client/src/app/features/assets/components/definitions-list.component.ts
@Component({
  selector: 'app-definitions-list',
  template: `
    <mat-tab-group>
      <mat-tab label="Machine Types">
        <app-machine-definitions-list />
      </mat-tab>
      <mat-tab label="Resource Types">
        <app-resource-definitions-list />
      </mat-tab>
    </mat-tab-group>
  `
})
```

2. **Add to AssetService**:
```typescript
// Already has methods, just wire them up
getMachineDefinitions(): Observable<MachineDefinition[]>
getResourceDefinitions(): Observable<ResourceDefinition[]>
```

3. **Update AssetListComponent**:
```typescript
// Line 126 - replace placeholder with:
<app-definitions-list />
```

**Files to modify**:
- `praxis/web-client/src/app/features/assets/components/asset-list.component.ts`
- Create: `praxis/web-client/src/app/features/assets/components/definitions-list.component.ts`
- Create: `praxis/web-client/src/app/features/assets/components/machine-definitions-list.component.ts`
- Create: `praxis/web-client/src/app/features/assets/components/resource-definitions-list.component.ts`

**UI Design**:
- Display definitions in Material table
- Show: name, type, parameters, constraints
- Read-only view (no create/delete needed)

---

### Task 2.2: Protocol Details View 🔨

**Priority**: HIGH (critical for usability)
**Estimated Effort**: 3-4 hours

**Current State**: Line 122 in `protocol-list.component.ts` just logs to console

**Implementation Steps**:

1. **Create ProtocolDetailComponent**:
```typescript
// praxis/web-client/src/app/features/protocols/components/protocol-detail.component.ts
@Component({
  selector: 'app-protocol-detail',
  template: `
    <mat-card>
      <mat-card-header>
        <mat-card-title>{{ protocol().name }}</mat-card-title>
        <mat-card-subtitle>v{{ protocol().version }}</mat-card-subtitle>
      </mat-card-header>

      <mat-card-content>
        <section>
          <h3>Metadata</h3>
          <!-- Show author, created_at, description, etc -->
        </section>

        <section>
          <h3>Parameters</h3>
          <mat-list>
            @for (param of protocol().parameters; track param.name) {
              <mat-list-item>
                <span>{{ param.name }}</span>
                <span>{{ param.type }}</span>
                <span>{{ param.required ? 'Required' : 'Optional' }}</span>
              </mat-list-item>
            }
          </mat-list>
        </section>

        <section>
          <h3>Asset Requirements</h3>
          <!-- List required machines/resources -->
        </section>

        <section>
          <h3>Actions</h3>
          <button mat-raised-button (click)="runProtocol()">Run</button>
          <button mat-raised-button color="warn" (click)="deleteProtocol()">Delete</button>
        </section>
      </mat-card-content>
    </mat-card>
  `
})
```

2. **Add Route**:
```typescript
// praxis/web-client/src/app/app.routes.ts
{
  path: 'protocols/:id',
  component: ProtocolDetailComponent,
  canActivate: [authGuard]
}
```

3. **Update ProtocolListComponent**:
```typescript
// Line 122 - replace console.log with:
viewDetails(protocol: Protocol): void {
  this.router.navigate(['/protocols', protocol.accession_id]);
}
```

**Files to create**:
- `praxis/web-client/src/app/features/protocols/components/protocol-detail.component.ts`

**Files to modify**:
- `praxis/web-client/src/app/features/protocols/components/protocol-list.component.ts`
- `praxis/web-client/src/app/app.routes.ts`

---

### Task 2.3: Dynamic Protocol Parameters 🔨

**Priority**: HIGH (hardcoded parameters are a hack)
**Estimated Effort**: 3-4 hours

**Current State**: Line 76 in `run-protocol.component.ts` has hardcoded parameters

**Implementation Steps**:

1. **Fetch Protocol Parameter Schema**:
```typescript
// When protocol is selected
onProtocolSelect(protocolId: string): void {
  this.protocolService.getProtocolById(protocolId).subscribe(protocol => {
    this.selectedProtocol.set(protocol);
    this.buildParameterForm(protocol.parameters);
  });
}
```

2. **Dynamic Form Builder**:
```typescript
buildParameterForm(parameters: ProtocolParameter[]): void {
  const group: any = {};

  for (const param of parameters) {
    const validators = param.required ? [Validators.required] : [];

    // Add type-specific validators
    if (param.type === 'number') {
      validators.push(Validators.pattern(/^\d+$/));
    }
    if (param.min !== undefined) {
      validators.push(Validators.min(param.min));
    }
    if (param.max !== undefined) {
      validators.push(Validators.max(param.max));
    }

    group[param.name] = new FormControl(param.default, validators);
  }

  this.parametersForm = new FormGroup(group);
}
```

3. **Dynamic Template**:
```typescript
@for (param of selectedProtocol().parameters; track param.name) {
  <mat-form-field>
    <mat-label>{{ param.name }}</mat-label>

    @switch (param.type) {
      @case ('string') {
        <input matInput [formControlName]="param.name" />
      }
      @case ('number') {
        <input matInput type="number" [formControlName]="param.name" />
      }
      @case ('boolean') {
        <mat-checkbox [formControlName]="param.name">{{ param.name }}</mat-checkbox>
      }
      @case ('enum') {
        <mat-select [formControlName]="param.name">
          @for (option of param.options; track option) {
            <mat-option [value]="option">{{ option }}</mat-option>
          }
        </mat-select>
      }
    }

    <mat-hint>{{ param.description }}</mat-hint>
    <mat-error>{{ param.name }} is required</mat-error>
  </mat-form-field>
}
```

**Files to modify**:
- `praxis/web-client/src/app/features/run-protocol/components/run-protocol.component.ts`

**Parameter Types to Support**:
- `string` - Text input
- `number` - Number input with min/max
- `boolean` - Checkbox
- `enum` - Dropdown select
- `array` - Could use chips or multi-select (future)

---

## 📋 Phase 3: UX Improvements (LOWER PRIORITY)

### Task 3.1: Responsive Design Fix 🔧

**File**: `src/app/layout/main-layout.component.ts`
**Issue**: Line 118 - `isHandset = signal(false)` is hardcoded

**Fix**:
```typescript
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';

constructor(private breakpointObserver: BreakpointObserver) {
  this.breakpointObserver
    .observe([Breakpoints.Handset])
    .subscribe(result => {
      this.isHandset.set(result.matches);
    });
}
```

---

### Task 3.2: Loading States 🔧

**Files**: All list components
**Issue**: No loading spinners while fetching data

**Implementation**:
```typescript
// Add loading signal
isLoading = signal(false);

// In fetch methods
loadData(): void {
  this.isLoading.set(true);
  this.service.getData().subscribe({
    next: (data) => {
      this.data.set(data);
      this.isLoading.set(false);
    },
    error: () => {
      this.isLoading.set(false);
    }
  });
}

// In template
@if (isLoading()) {
  <mat-spinner />
} @else {
  <!-- Data content -->
}
```

**Files to modify**:
- `praxis/web-client/src/app/features/assets/components/asset-list.component.ts`
- `praxis/web-client/src/app/features/protocols/components/protocol-list.component.ts`

---

### Task 3.3: JSON Error Handling 🔧

**Files**:
- `src/app/features/assets/components/machine-dialog.component.ts`
- `src/app/features/assets/components/resource-dialog.component.ts`

**Issue**: JSON parsing errors only logged to console

**Fix**:
```typescript
import { MatSnackBar } from '@angular/material/snack-bar';

constructor(private snackBar: MatSnackBar) {}

onJsonInput(event: Event): void {
  try {
    const json = JSON.parse(value);
    this.form.patchValue({ config: json });
  } catch (e) {
    this.snackBar.open('Invalid JSON: ' + e.message, 'Close', {
      duration: 5000,
      panelClass: 'error-snack'
    });
    // Optionally highlight the field
    this.form.get('config')?.setErrors({ invalidJson: true });
  }
}
```

---

## 📊 Success Criteria

### Phase 1 Complete When:
- ✅ Unit test coverage ≥ 60%
- ✅ All core services have comprehensive tests
- ✅ All infrastructure (guards, interceptors, store) tested
- ✅ ExecutionService timing issues resolved
- ✅ `npm test` passes with no failures

### Phase 2 Complete When:
- ✅ Asset definitions tab shows machine/resource types
- ✅ Protocol detail view accessible via route
- ✅ Protocol parameters generated dynamically from schema
- ✅ No hardcoded parameters in run-protocol component

### Phase 3 Complete When:
- ✅ Responsive design works on mobile/tablet
- ✅ All list components show loading spinners
- ✅ JSON errors shown to user (not just console)

---

## 🛠️ Development Environment Setup

```bash
# Navigate to frontend
cd praxis/web-client

# Install dependencies (if needed)
npm install

# Run dev server
npm start
# App available at http://localhost:4200

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch

# Build for production
npm run build

# Lint code
npm run lint
```

---

## 📝 File Structure Reference

```
praxis/web-client/src/app/
├── core/
│   ├── store/
│   │   └── app.store.spec.ts          # Task 1.1A - Expand
│   ├── guards/
│   │   └── auth.guard.spec.ts         # Task 1.1B - Expand
│   └── http/
│       └── auth.interceptor.spec.ts   # Task 1.1C - Expand
├── features/
│   ├── auth/
│   │   └── services/
│   │       └── auth.service.spec.ts   # Task 1.2A - Create
│   ├── assets/
│   │   ├── services/
│   │   │   └── asset.service.spec.ts  # Task 1.2B - Expand
│   │   └── components/
│   │       ├── definitions-list.component.ts    # Task 2.1 - Create
│   │       ├── machine-definitions-list.component.ts
│   │       └── resource-definitions-list.component.ts
│   ├── protocols/
│   │   ├── services/
│   │   │   └── protocol.service.spec.ts   # Task 1.2C - Expand
│   │   └── components/
│   │       └── protocol-detail.component.ts   # Task 2.2 - Create
│   └── run-protocol/
│       ├── services/
│       │   └── execution.service.spec.ts  # Task 1.2D - Fix timing
│       └── components/
│           └── run-protocol.component.ts  # Task 2.3 - Dynamic params
└── layout/
    └── main-layout.component.ts        # Task 3.1 - Responsive fix
```

---

## 🚀 Execution Strategy

### Recommended Order:

1. **Start with Task 1.1** (Core Infrastructure Tests)
   - These are foundational and critical
   - Should take 3-4 hours
   - Immediate impact on production readiness

2. **Move to Task 1.2** (Service Layer Tests)
   - Build on infrastructure tests
   - Should take 4-5 hours
   - Gets you to 60% coverage goal

3. **Implement Task 2.1** (Asset Definitions)
   - Visible feature completion
   - Should take 2-3 hours
   - Quick win for UX

4. **Implement Task 2.2** (Protocol Details)
   - Another visible feature
   - Should take 3-4 hours
   - Completes protocol workflow

5. **Implement Task 2.3** (Dynamic Parameters)
   - Remove hardcoded hack
   - Should take 3-4 hours
   - Completes run-protocol feature

6. **Phase 3 if time permits** (UX Improvements)
   - Nice-to-have polish
   - Can be done incrementally

### Total Estimated Time: 15-20 hours
- Phase 1: 7-9 hours
- Phase 2: 8-11 hours
- Phase 3: Optional, 2-4 hours

---

## 📞 Support & Context

### Reference Documents:
- `.agents/FRONTEND_STATUS.md` - Current state and tasks
- `.agents/ACTIVE_DEVELOPMENT.md` - Recent session history
- `praxis/web-client/DEV_SETUP.md` - Environment setup
- `praxis/web-client/README.md` - Project overview

### API Endpoints (for reference):
All documented in `FRONTEND_STATUS.md` "API Integration Status" section

### Tech Stack:
- Framework: Angular 21.0.3 (standalone components)
- UI: Angular Material 21.0.2
- State: NgRx Signals 20.1.0
- Testing: Vitest 4.0.8
- E2E: Playwright 1.57.0

### Design Patterns:
- Standalone components (no NgModules)
- Signal-based state management
- Lazy-loaded routes
- Reactive forms
- Feature-first structure

---

## ✅ Handoff Checklist

Before marking work complete:
- [ ] All tests pass (`npm test`)
- [ ] Coverage report generated (`npm test -- --coverage`)
- [ ] Coverage ≥ 60% achieved
- [ ] No console errors in dev server
- [ ] Build succeeds (`npm run build`)
- [ ] Lint passes (`npm run lint`)
- [ ] Update `FRONTEND_STATUS.md` with completed tasks
- [ ] Commit changes with descriptive message
- [ ] Push to `angular_refactor` branch

---

## 🎯 Success Metrics

**Before** (Current State):
- Unit test coverage: ~5%
- Missing features: 3 major gaps
- UX issues: 4 known problems

**After** (Target State):
- Unit test coverage: ≥ 60%
- Missing features: 0 (all implemented)
- UX issues: All resolved
- Production-ready frontend ✅

---

Good luck, Gemini! The codebase is well-structured and ready for these enhancements. 🚀
