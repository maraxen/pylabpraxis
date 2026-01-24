# E2E-AUDIT-01: Audit E2E Test Coverage Gaps

## Context

**E2E Directory**: `praxis/web-client/e2e/specs/`
**App Routes**: `src/app/app.routes.ts`
**Goal**: Identify which routes/features lack E2E test coverage

## Application Routes (from app.routes.ts)

```
/                     - Splash page
/login, /register, /forgot-password - Auth pages
/app/home             - Home dashboard
/app/assets/*         - Asset management
/app/protocols/*      - Protocol library
/app/run/*            - Run protocol
/app/monitor, /app/monitor/:id - Execution monitor
/app/workcell/*       - Workcell dashboard
/app/data/*           - Data visualization
/app/settings/*       - Settings
/app/playground       - JupyterLite REPL
/docs/*               - Documentation
```

## Requirements

### Phase 1: Inventory Existing Coverage

1. List all spec files in `e2e/specs/`
2. For each spec, identify which routes/features it covers
3. Create a coverage matrix

### Phase 2: Identify Gaps

1. Compare routes vs existing tests
2. Note partially covered features
3. Prioritize by criticality:
   - P1: Core user journeys (asset creation, protocol run)
   - P2: Secondary features (settings, data viz)
   - P3: Edge cases

### Phase 3: Report

Create `coverage-audit.md` in the task directory with:

1. Coverage matrix table
2. Gap analysis
3. Prioritized list of tests to create

## Output Format

```markdown
# E2E Coverage Audit

## Coverage Matrix
| Route | Existing Tests | Coverage Level |
|-------|---------------|----------------|
| /app/assets | 02-asset-management.spec.ts | ✅ Full |
| /app/monitor/:id | None | ❌ Missing |

## Gaps (Prioritized)
1. **P1**: /app/monitor/:id - Run detail view has no coverage
2. **P2**: /app/workcell - Limited coverage
...
```

## Acceptance Criteria

- [ ] Complete inventory of existing tests
- [ ] Coverage matrix per route
- [ ] Prioritized gap list for future work
- [ ] Output saved to task artifacts

## Notes

- Focus on route coverage, not component-level unit tests
- Consider OPFS migration impact on existing tests
