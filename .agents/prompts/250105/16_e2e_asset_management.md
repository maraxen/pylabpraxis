# Prompt 16: E2E Test Suite - Asset Management

Create comprehensive E2E tests for asset management operations.

## Tasks

1. Create Playwright test file: `tests/e2e/asset-management.spec.ts`

2. Test Resource CRUD:
   - Add resource from definition
   - View resource in inventory
   - Edit resource properties
   - Delete resource
   - Verify persistence after page reload

3. Test Machine CRUD:
   - Add machine (frontend type → backend → capabilities)
   - View machine in inventory
   - Edit machine properties
   - Delete machine
   - Verify persistence after page reload

4. Test filter functionality:
   - Apply status filter
   - Apply category filter
   - Combine filters
   - Verify result counts

5. Run in browser mode (no backend)

## Files to Create

- `tests/e2e/asset-management.spec.ts`

## Reference

- `.agents/backlog/code_quality_plan.md`
