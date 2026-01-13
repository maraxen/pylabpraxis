# Technical Debt

This document tracks known issues, temporary patches, and required follow-up work for the Praxis project.

## Models & Database

- [ ] **SQLModel/PostgreSQL Verification**: Unified `PraxisBase` and Alembic metadata integration have only been verified against SQLite. Full verification against a live PostgreSQL instance is required when infrastructure is available. <!-- id: 101 -->

- [ ] **SQLModel Polymorphic Inheritance Limitation**: SQLModel cannot handle joined table inheritance when parent classes have `dict` fields with `sa_column=Column(JsonVariant)`. The `sa_column` config is not inherited, causing `ValueError: <class 'dict'> has no matching SQLAlchemy type`. Current workaround uses hybrid pattern (SQLAlchemy ORM for tables + SQLModel for schemas). **Review periodically** as SQLModel evolves - this may be fixed in future versions. See: `praxis/backend/models/domain/` for schema classes, `praxis/backend/models/orm/` for ORM tables. <!-- id: 102 -->

## Tests

- [ ] Review REPL tests in `tests/core/test_repl_session.py` and migrate them to a frontend/integration test suite; these tests require PyLabRobot runtime and interactive imports and are skipped in backend CI.<!-- id: 201 -->
  - Reason: REPL depends on environment and GUI/interactive backends that belong to integration or frontend testing.
  - Owner: TBD
  - Priority: low
  - Notes: Consider creating a small Docker-based integration job that installs `pylabrobot` and runs these tests in an environment that can import hardware simulation backends.
