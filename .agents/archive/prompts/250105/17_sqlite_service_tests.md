# Prompt 17: Unit Tests - SqliteService

Create comprehensive unit tests for SqliteService browser database operations.

## Tasks

1. Create test file for SqliteService

2. Test initialization:
   - Database loads correctly
   - Tables exist with expected schema
   - Seed data works (or loads bundled data)

3. Test CRUD operations for each repository:
   - ResourceRepository: create, get, getAll, update, delete
   - MachineRepository: create, get, getAll, update, delete
   - ProtocolDefinitionRepository: getAll

4. Test multi-table insertion (assets + resources/machines tables)

5. Test query filtering and pagination

6. Test IndexedDB persistence:
   - Save to IndexedDB
   - Load from IndexedDB
   - Data survives simulated reload

7. Mock sql.js for unit testing

## Files to Create

- `praxis/web-client/src/app/core/services/sqlite.service.spec.ts`

## Reference

- `.agents/backlog/code_quality_plan.md`
