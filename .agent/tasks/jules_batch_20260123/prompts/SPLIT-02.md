# SPLIT-02: Decompose playground.component.ts

## Context

**File**: `src/app/features/playground/playground.component.ts`
**Current Size**: 1,324 lines
**Goal**: Split into modular components and services

## Architecture Analysis

The playground component likely contains:

1. **JupyterLite/REPL Integration**: Iframe management, messaging
2. **Code Editor**: Monaco or similar integration
3. **Output Display**: Results, visualizations
4. **Toolbar/Controls**: Run, clear, settings

## Requirements

### Phase 1: Extract Services

1. **PlaygroundEditorService**: Editor state, syntax highlighting config
2. **PlaygroundKernelService**: Kernel communication, Pyodide messaging (if not already extracted)
3. Keep component as orchestration layer

### Phase 2: Extract Components

1. `playground-toolbar.component.ts` - Action buttons, settings
2. `playground-output.component.ts` - Results display area
3. `playground-sidebar.component.ts` - File browser, history (if exists)

### Phase 3: Verification

1. `npm run build` must pass
2. `npm test` must pass
3. JupyterLite integration must still work
4. Manual test: Open playground, run Python code, verify output

## Acceptance Criteria

- [ ] Main component under 300 lines
- [ ] Services extracted for complex logic
- [ ] Child components for distinct UI areas
- [ ] `npm run build` passes
- [ ] Commit: `refactor(playground): decompose into modular components`

## Anti-Requirements

- Do NOT break JupyterLite/Pyodide integration
- Do NOT change the visual appearance
- Do NOT modify the REPL bootstrap logic
