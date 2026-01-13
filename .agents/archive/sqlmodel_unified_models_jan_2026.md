# Archive: SQLModel Unified Models & Refactor (Jan 2026)

**Date Completed**: 2026-01-13
**Initiative**: [SQLModel + OpenAPI Codegen Unification Refactor](../archive/backlog/sqlmodel_codegen_refactor.md)
**Primary Goal**: Consolidate multiple sources of truth into a single unified SQLModel domain model system.

---

## Accomplishments

### 1. Model Unification

- Successfully migrated all models from a hybrid (SQLAlchemy ORM + Pydantic) system to unified **SQLModel** domain models.
- Removed the `praxis/backend/models/orm/` directory entirely.
- Established `praxis/backend/models/domain/` as the single source of truth for both database tables and API schemas.

### 2. Architectural Pivot: Table-Per-Class

- Pivoted from Joined Table Inheritance (JTI) to **Table-Per-Class** (Abstract Base) inheritance for the `Asset` hierarchy.
- `Asset` is now an abstract base (`table=False`).
- `Machine` and `Resource` are concrete tables (`table=True`).
- Resolved SQLModel's limitations with JSON field inheritance by using `sa_type=JsonVariant`.

### 3. Data Integrity: Soft Foreign Keys

- Implemented **Soft Foreign Keys** for relationships between `AssetReservation` and concrete assets.
- Removed physical SQL constraints on `asset_accession_id` while maintaining indexed UUID7 columns for global uniqueness.
- Configured complex SQLModel `Relationship` definitions with `primaryjoin` to support this pattern.

### 4. Relationship Completeness

- Conducted a comprehensive audit of all 15 domain models.
- Added missing `Relationship()` navigation fields across all models, enabling full ORM navigation (e.g., `protocol.source_repository`).
- Fixed 92+ test failures that were previously blocked by relationship issues.

### 5. Frontend Integration

- Regenerated the TypeScript OpenAPI client based on the unified SQLModel schemas.
- Migrated Angular services in `web-client` to use the generated client.
- Verified the end-to-end pipeline from SQLModel -> OpenAPI -> TypeScript.

---

## Verification Results

- **Backend Tests**: 305 tests in `tests/models/test_domain/` passing 100%.
- **Test Collection**: 2,105+ tests collecting cleanly across the entire suite.
- **Frontend Build**: `npm run build` passing in `web-client`.
- **API Status**: OpenAPI documentation verified as rendering correctly.

---

## Reference Documents

- [Original Backlog Item](../archive/backlog/sqlmodel_codegen_refactor.md)
- [Audit Report](../archive/prompts/260112_2/AUDIT_REPORT.md)
- [Prompt Batch 260112_2](../archive/prompts/260112_2/README.md)

---

**Merged into Main**: 2026-01-13
**Author**: Antigravity
