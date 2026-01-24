# SPLIT-01: Decompose run-protocol.component.ts

## Context

**File**: `src/app/features/run-protocol/run-protocol.component.ts`
**Current Size**: 1,477 lines
**Goal**: Split into modular components and extracted services

## Architecture Analysis

Before splitting, identify:

1. **UI Sections**: Header, sidebar, main content areas
2. **State Management**: What state is managed locally vs in services
3. **Event Handlers**: Group by functionality (setup, execution, monitoring)
4. **Child Components**: What can become standalone components

## Requirements

### Phase 1: Extract Services

1. Identify business logic that can move to dedicated services
2. Create new service files in `services/` folder
3. Move complex computations, API calls, state transformations
4. Keep component focused on presentation and orchestration

### Phase 2: Extract Components

1. Break UI into logical child components:
   - `run-protocol-header.component.ts` (if distinct header section exists)
   - `run-protocol-sidebar.component.ts` (if sidebar exists)
   - Other logical UI groupings
2. Use `@Input()` and `@Output()` for parent-child communication
3. Maintain existing CSS/styling

### Phase 3: Verification

1. Run `npm run build` - must compile
2. Run `npm test` - existing tests must pass
3. Manual verification that UI looks identical
4. Update any imports in files that reference this component

## Acceptance Criteria

- [ ] Main component under 300 lines
- [ ] Each extracted component/service is focused and cohesive
- [ ] All imports updated throughout codebase
- [ ] `npm run build` passes
- [ ] `npm test` passes
- [ ] Commit: `refactor(run-protocol): decompose monolithic component into modules`

## Anti-Requirements

- Do NOT change functionality or behavior
- Do NOT modify CSS unless necessary for extraction
- Do NOT introduce new dependencies
