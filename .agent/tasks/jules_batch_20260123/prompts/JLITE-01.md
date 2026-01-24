# JLITE-01: Audit simulate-ghpages.sh Directory Structure

## Context

**Script**: `scripts/simulate-ghpages.sh`
**Simulation Dir**: `/tmp/ghpages-sim/`
**Goal**: Investigate why all static assets return 404 in simulation

## Background

The GitHub Pages simulation environment has a P1 blocker where all JupyterLite static assets return 404. This prevents proper E2E testing of the deployed environment.

## Requirements

### Phase 1: Analyze Script

1. Read `scripts/simulate-ghpages.sh`
2. Document the directory structure it creates
3. Identify how assets are copied
4. Note any depth/path handling issues

### Phase 2: Verify Directory Structure

1. Run the simulation: `./scripts/simulate-ghpages.sh`
2. Inspect `/tmp/ghpages-sim/` structure
3. Compare expected vs actual paths
4. Check for:
   - Missing files
   - Incorrect nesting (double `/praxis/praxis/`)
   - Permission issues

### Phase 3: Check serve Configuration

1. Review `serve.json` for rewrites
2. Verify rewrites handle nested paths
3. Check if JupyterLite assets are covered

### Phase 4: Propose Fix

If issues found:

1. Document the root cause
2. Propose minimal fix to script
3. Test fix locally

## Output

Create `jlite-ghpages-audit.md`:

```markdown
# JupyterLite GH-Pages Simulation Audit

## Directory Structure Analysis
Expected:
/tmp/ghpages-sim/
└── praxis/
    ├── assets/
    │   └── jupyterlite/
    └── ...

Actual: [what was found]

## Issues Found
1. [Issue description]
   Root cause: [explanation]
   Fix: [proposed solution]

## serve.json Analysis
[Findings about rewrite rules]

## Recommended Fixes
[Ordered list of changes]
```

## Acceptance Criteria

- [ ] Root cause of 404s identified
- [ ] Directory structure documented
- [ ] Fix proposed (or confirmation it's working)
