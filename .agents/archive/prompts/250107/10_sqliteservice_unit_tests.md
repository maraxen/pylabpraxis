# Prompt: SqliteService Unit Tests

**Priority**: P2 (High)
**Backlog**: [quality_assurance.md](../../backlog/quality_assurance.md)

## Context

The `SqliteService` is the backbone of "Browser Mode", providing a local SQLite database powered by `sql.js` (and potentially `wa-sqlite`). While basic initialization tests exist, the core data manipulation and persistence logic remains untested.

## Objective

Expand the unit test suite in `praxis/web-client/src/app/core/services/sqlite.service.spec.ts` to provide comprehensive coverage.

## Tasks

### 1. Mocking Enhancements

- Refine the `sql.js` mocks to support realistic behavior for `exec`, `run`, and `prepare`.
- Implement a mock for IndexedDB to verify that the database IS actually persisted locally.

### 2. Core CRUD Execution

- **`query()`**: Verify that SELECT statements return expected data structures.
- **`run()`**: Verify that INSERT/UPDATE/DELETE statements correctly modify the database state.
- **Transactions**: Ensure that multi-statement queries are handled correctly.

### 3. Lifecycle & Initialization

- Test the "Import Database" flow: verify a `.db` file can be loaded and replaces the current in-memory state.
- Test the "Export Database" flow: verify it returns a valid `Uint8Array`.
- Test recovery from a corrupted or missing database.

### 4. Persistence Verification

- Verify that `saveToLocalStorage()` (or IndexedDB logic) is called after every write operation.
- Ensure the service correctly loads the persisted data on the next initialization.

## Requirements

- Use **Vitest** and Angular **TestBed**.
- Aim for >90% code coverage within `sqlite.service.ts`.
- Do not rely on a real browser environment; use mocks for WASM and DOM APIs.

## Verification

- Run `npm test` in `praxis/web-client`.
- Check the coverage report for `sqlite.service.ts`.
- All tests must pass with no flaky behavior.
