# Deep Introspection: Browser Mode Schema & Data Integrity

**Objective**: Resolve persistent `500 Internal Server Error` and data integrity issues in Browser Mode (`npm run start:browser`) without using browser automation tools.

**Context**: The application uses `sql.js` and `IndexedDB` to mock a backend. There is a disconnect between the SQL schema (`schema.sql`), the Typescript service (`SqliteService.ts`), and the mock data (`plr-definitions.ts`, `protocol-runs.ts`).

## Task

You are an expert Systems Architect. Perform a deep static analysis of the codebase to identify the root cause of the schema/code divergence.

### 1. Analyze Schema vs. Implementation

* Compare `src/assets/db/schema.sql` (The Source of Truth) against `src/app/core/services/sqlite.service.ts`.
* Identify **EVERY** mismatch:
  * Table names
  * Column names (e.g., `tags` vs `tags_json`, `start_time` vs `started_at`)
  * Data types
  * Nullability/Constraints (Are we inserting NULLs into NOT NULL columns?)

### 2. Analyze Mock Data Validity

* Inspect `src/assets/browser-data/` files.
* Verify if the mock data objects actually match the `schema.sql` structure.
* Determine why the user perceives "too few definitions" (Check if we are missing a large catalog file that should be imported).

### 3. Analyze Backend Parity (If accessible)

* Look at `praxis/backend` (e.g., `machine_type_definition.py`, SQLAlchemy models) to see what the "Real" schema is.
* Determine if `schema.sql` itself is outdated compared to the Python backend.

### 4. Deliverables

* **Root Cause Analysis**: Why specifically is the 500 error happening? (Likely an unhandled SQLite error during `SELECT` or `INSERT`).
* **Action Plan**: A valid, non-patchy plan to align the Mock Service with the Real Schema.
* **Code Corrections**: You may propose edits, but ensure they are systemic fixes, not one-off patches.

**Constraints:**

* **NO BROWSER AUTOMATION**. Use `grep`, `read_file`, and code analysis tools only.
* Assume `tryLoadPrebuiltDb` is intentionally disabled to force fresh generation.
* Prioritize correctness over backwards compatibility.
