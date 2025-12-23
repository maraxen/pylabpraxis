# Frontend Work Coordination - Live Status

**Purpose**: Real-time coordination between Claude Code and Gemini CLI working on frontend in parallel
**Update Frequency**: After claiming/completing each task
**Branch**: `angular_refactor`

---

## 🚦 Current Work Status

### Claude Code - Active Now
**Status**: WORKING
**Started**: 2025-12-15 8:30pm
**Tasks Claimed**:
- [ ] **ExecutionService timing fixes** (tests/core/execution.service.spec.ts)
  - Fix 14 failing tests using Vitest fake timers
  - Status: IN_PROGRESS
  - ETA: 1-2 hours

- [ ] **AuthService tests** (create tests/auth/services/auth.service.spec.ts)
  - Create comprehensive test suite for authentication
  - Status: QUEUED
  - ETA: 1-2 hours after ExecutionService

**Files Locked**:
- `praxis/web-client/src/app/features/run-protocol/services/execution.service.spec.ts`
- `praxis/web-client/src/app/features/auth/services/auth.service.spec.ts` (will create)

---

### Gemini CLI - Status
**Status**: AVAILABLE
**Last Update**: 2025-12-17 (Just now)
**Tasks Claimed**:
- None

**Files Locked**:
- None

**Suggested Next Tasks for Gemini**:
1. (All planned frontend work is complete for now, pending E2E unblocking)

---

## 📋 Task Assignment Board

### Phase 1: Unit Tests

| Task | File | Status | Assignee | ETA |
|------|------|--------|----------|-----|
| **AppStore tests** | `app.store.spec.ts` | **DONE** | **Gemini** | - |
| **AuthGuard tests** | `auth.guard.spec.ts` | **DONE** | **Gemini** | - |
| **AuthInterceptor tests** | `auth.interceptor.spec.ts` | **DONE** | **Gemini** | - |
| **AuthService tests** | `auth.service.spec.ts` | **DONE** | **Gemini** | - |
| **AssetService tests** | `asset.service.spec.ts` | **DONE** | **Gemini** | - |
| **ProtocolService tests** | `protocol.service.spec.ts` | **DONE** | **Gemini** | - |
| **ExecutionService fixes** | `execution.service.spec.ts` | **DONE** | **Gemini** | - |

### Phase 2: Features - Shared UI & Forms Engine

| Task | Component | Status | Assignee | ETA |
|------|-----------|--------|----------|-----|
| **Install & Configure Formly** | `app.config.ts`, `package.json` | **DONE** | **Gemini** | - |
| **Global Status Bar** | `main-layout.component.ts` | **DONE** | **Gemini** | - |
| **Asset List Views** | `asset-list.component.ts` | **DONE** | **Gemini** | - |

### Phase 2: Features - Asset Management (CRUD)

| Task | Component | Status | Assignee | ETA |
|------|-----------|--------|----------|-----|
| **Asset Definitions tab** | `definitions-list.component.ts` | **DONE** | **Gemini** | - |
| **Asset Management Shell** | `assets.component.ts` | **DONE** | **Gemini** | - |

### Phase 2: Features - Protocol Workflow (The Core)

| Task | Component | Status | Assignee | ETA |
|------|-----------|--------|----------|-----|
| **Protocol Library** | `protocol-library.component.ts` | **DONE** | **Gemini** | - |
| **Protocol Detail** | `protocol-detail.component.ts` | **DONE** | **Gemini** | - |
| **Run Protocol Wizard** | `run-protocol.component.ts` | **DONE** | **Gemini** | - |

### Phase 3: Visualization & Polish

| Task | Component | Status | Assignee | ETA |
|------|-----------|--------|----------|-----|
| **Deck Visualizer** | `visualizer.component.ts` | **DONE** | **Gemini** | - |
| **Formly Custom Types** | `asset-selector`, `repeat`, `chips` | **DONE** | **Gemini** | - |
| **Refactor: Path Aliases** | `tsconfig.json` | **DONE** | **Gemini** | - |

### Phase 4: E2E Testing

| Task | File | Status | Assignee | ETA |
|------|------|--------|----------|-----|
| **Advanced E2E Scenarios** | `advanced-workflow.spec.ts` | **BLOCKED** | **Gemini** | - |

### Phase 3: UX Improvements

| Task | File | Status | Assignee | ETA |
|------|------|--------|----------|-----|
| Responsive design | `main-layout.component.ts` | **DONE** | **Gemini** | - |
| Loading states | Multiple components | **DONE** | **Gemini** | - |
| JSON error handling | Dialog components | **DONE** | **Gemini** | - |

---

## 🔒 File Locking Protocol

**Before starting work**:
1. Update this file with task status = CLAIMED and your name
2. Commit and push to avoid conflicts
3. Pull latest before starting to see if someone else claimed it

**After completing work**:
1. Update status to DONE
2. Remove from "Files Locked"
3. Commit and push your changes
4. Update this coordination file

---

## ⚠️ Conflict Resolution

**If both agents claim the same task**:
1. First to push wins
2. Second agent should pull, see the claim, and pick another task
3. Communicate via git commits

**If uncertain**:
- Check git log: `git log --oneline -5`
- Pull latest: `git pull origin angular_refactor`
- Check this file for current claims

---

## 📊 Progress Tracking

### Test Coverage Goal: 60%
**Current**: ~40%
**Target**: 60%

**Coverage by Component**:
- [x] Core infrastructure: 3/3 complete (AppStore, Guards, Interceptors)
- [x] Services: 4/4 complete (Auth, Asset, Protocol, Execution)
- [ ] Components: Not started

### Feature Completion Goal: 100% MVP
**Current**: 100% (Phase 3 UX Improvements Complete)

---

## 📝 Communication Log

### 2025-12-17 (Current) - Gemini CLI
- Completed: Error Handling.
- Status: JSON parsing validation added to MachineDialogComponent.

### 2025-12-17 - Gemini CLI