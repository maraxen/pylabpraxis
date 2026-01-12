# Technical Debt

This document tracks known issues, temporary patches, and required follow-up work for the Praxis project.

## Models & Database

- [ ] **SQLModel/PostgreSQL Verification**: Unified `PraxisBase` and Alembic metadata integration have only been verified against SQLite. Full verification against a live PostgreSQL instance is required when infrastructure is available. <!-- id: 101 -->

- [ ] **SQLModel Polymorphic Inheritance Limitation**: SQLModel cannot handle joined table inheritance when parent classes have `dict` fields with `sa_column=Column(JsonVariant)`. The `sa_column` config is not inherited, causing `ValueError: <class 'dict'> has no matching SQLAlchemy type`. Current workaround uses hybrid pattern (SQLAlchemy ORM for tables + SQLModel for schemas). **Review periodically** as SQLModel evolves - this may be fixed in future versions. See: `praxis/backend/models/domain/` for schema classes, `praxis/backend/models/orm/` for ORM tables. <!-- id: 102 -->
