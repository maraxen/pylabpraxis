# Archive: SQLModel + OpenAPI Codegen Unification

**Completion Date**: 2026-01-12
**Initiative**: Backend/Frontend Unification Refactor

## Summary

Successfully migrated foundational entities and services from a fragmented SQLAlchemy/Pydantic/Manual-TS structure to a unified SQLModel-based domain with automated TypeScript client generation. This initiative significantly reduced boilerplate and introduced systemic type safety across the stack.

## Achievements

### 1. Foundation Infrastructure

- Established `PraxisBase(SQLModel)` as the unified base for all domain models.
- Integrated SQLModel metadata into `alembic/env.py`.
- Implemented `JsonVariant` for robust JSON field handling across inheritance.

### 2. Core Model Migration

- Migrated `Asset` polymorphic base to SQLModel domain (`praxis/backend/models/domain/asset.py`).
- Consolidated `orm/` and `pydantic_internals/` logic for the base asset layer.

### 3. API & Service Layer

- Refactored `create_crud_router` factory to support SQLModel schemas.
- Updated `PraxisClient` generation to include all domain-driven endpoints.

### 4. Frontend Integration

- Setup `openapi-typescript-codegen` pipeline in `praxis/web-client`.
- Migrated core Angular services (`asset.service.ts`, `protocol.service.ts`) to use the generated API client.
- Updated signal stores and components to consume auto-generated TypeScript interfaces.

## Lessons Learned

- **Inheritance Quirks**: Discovered that SQLModel/SQLAlchemy Joined Table Inheritance (JTI) is fragile with complex JSON fields, leading to a pivot toward Table-Per-Class (Abstract Base) inheritance for sub-assets.
- **Client Generation**: Automated client generation is a major productivity multiplier but requires careful schema naming in FastAPI to ensure readable TS interfaces.

## Related Backlog

- [sqlmodel_codegen_refactor.md](../backlog/sqlmodel_codegen_refactor.md) (Remaining Phases: 2.2-4.2, 7)
