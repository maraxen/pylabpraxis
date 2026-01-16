# Task: Frontend Type Safety Audit

**ID**: TD-401
**Status**: 🔵 In Progress
**Priority**: P2
**Difficulty**: Medium

---

## 📋 Phase 1: Inspection (I)

**Objective**: Audit all `as any` and `: any` usage in web client.

- [ ] `grep -r "as any" praxis/web-client/src/`
- [ ] `grep -r ": any" praxis/web-client/src/`
- [ ] Categorize by service/component
- [ ] Identify which are temporary patches vs intentional

**Findings**:
> [To be captured during inspection]

---

## 📐 Phase 2: Planning (P)

**Objective**: Define proper types for each `any` usage.

- [ ] Map each `any` to its expected type from `schema.ts`
- [ ] Identify missing interface definitions
- [ ] Plan type import restructuring

**Implementation Plan**:

1. Create missing interface definitions
2. Replace `any` with proper types (prioritize services)
3. Update component props/state types
4. Enable stricter TypeScript checks

**Definition of Done**:

1. Zero `as any` in service files
2. Minimal, documented `any` in components (edge cases only)
3. `npm run build` passes with no type errors

---

## 🛠️ Phase 3: Execution (E)

**Objective**: Replace `any` with proper types.

- [ ] Update `simulation-results.service.ts`
- [ ] Update other affected services
- [ ] Update component types
- [ ] Add missing interfaces to `schema.ts` or dedicated files

**Work Log**:

- [Pending]

---

## 🧪 Phase 4: Testing & Verification (T)

**Objective**: Verify type safety improvements.

- [ ] `npm run build` - No type errors
- [ ] `npm test` - All tests pass
- [ ] Manual verification of affected features

**Results**:
> [To be captured]

---

## 📚 Tracking & Context

- **Matrix Reference**: [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- **Technical Debt ID**: 401
- **Files**:
  - `praxis/web-client/src/app/core/services/` - Services with `any`
  - `praxis/web-client/src/app/core/models/` - Type definitions
