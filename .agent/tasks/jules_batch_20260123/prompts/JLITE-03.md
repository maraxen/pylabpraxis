# JLITE-03: Fix Pyodide Kernel Auto-Initialization

## Context

**Issue**: Pyodide kernel doesn't auto-start; user must manually select
**Severity**: P2 (UX friction)
**Goal**: Make the Python/Pyodide kernel start automatically

## Background

When users navigate to `/app/playground`, the JupyterLite REPL should:

1. Load automatically
2. Initialize the Pyodide kernel
3. Run bootstrap code (micropip, praxis module)
4. Be ready for user input

Currently, users must manually select the kernel.

## Requirements

### Phase 1: Investigate Configuration

1. Read `src/assets/jupyterlite/repl/jupyter-lite.json`
2. Look for kernel configuration options
3. Check for `defaultKernel` or similar settings
4. Review JupyterLite documentation for auto-start

### Phase 2: Check Bootstrap Flow

1. Read `playground.component.ts`
2. Find kernel initialization code
3. Check `getOptimizedBootstrap()` function
4. Trace how `code` parameter is passed to REPL

### Phase 3: Implement Fix

Possible solutions:

1. **Config-based**: Add kernel setting to `jupyter-lite.json`
2. **URL-based**: Ensure `?kernel=python` is passed
3. **Code-based**: Trigger kernel selection programmatically

### Phase 4: Test

1. Build and run
2. Navigate to playground
3. Verify:
   - Kernel starts automatically
   - Bootstrap code runs
   - "praxis:ready" signal fires

## Key Files

- `src/assets/jupyterlite/repl/jupyter-lite.json`
- `src/app/features/playground/playground.component.ts`
- `getOptimizedBootstrap()` function

## Acceptance Criteria

- [ ] Kernel auto-starts on page load
- [ ] Bootstrap code executes
- [ ] No manual kernel selection required
- [ ] Commit: `fix(jupyterlite): auto-initialize Pyodide kernel`
