# Prompt Batch: 260110 — SQLModel + OpenAPI Codegen Unification

**Status:** 🟡 In Progress
**Created:** 2026-01-10
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)

---

## Overview

This batch implements a phased migration from 4 sources of truth (SQLAlchemy ORM + Pydantic + TypeScript interfaces + manual services) to 1.5 sources of truth using **SQLModel** for unified backend models and **OpenAPI Generator** for auto-generated frontend code.

**Goals:**
- Eliminate duplicate model definitions (ORM vs Pydantic)
- Automatic TypeScript type generation from backend
- Improved type safety across the full stack
- Simplified maintenance and reduced drift

---

## Dependency Graph

```
Phase 1: Foundation (Parallelizable)
├── P2_01_sqlmodel_foundation_setup ─────┐
└── P2_02_openapi_codegen_pipeline ──────┼─┐
                                         │ │
Phase 2: Core Entities                   │ │
├── P2_03_migrate_asset_base ◄───────────┘ │  (Requires P2_01)
│   ├── P2_04_migrate_machine ◄────────────┤  (Requires P2_03)
│   ├── P2_05_migrate_resource ◄───────────┤  (Can parallel with P2_04)
│   └── P2_06_migrate_deck ◄───────────────┘  (Requires P2_03)
│
Phase 3: Protocol & Scheduling
├── P2_07_migrate_protocol_run ◄───────────── (Requires Phase 2)
├── P2_08_migrate_schedule ◄───────────────── (Can parallel with P2_07)
└── P2_09_migrate_protocol_source ◄────────── (Can parallel with P2_07)
│
Phase 4: Data & Supporting
├── P2_10_migrate_data_outputs ◄───────────── (Requires Phase 2+3.1)
└── P2_11_migrate_workcell_user ◄──────────── (Can parallel with P2_10)
│
Phase 5: Infrastructure
├── P2_12_update_crud_services ◄───────────── (Requires Phase 2-4)
└── P2_13_update_test_fixtures ◄───────────── (Can parallel with P2_12)
│
Phase 6: Frontend
├── P2_14_generate_typescript_client ◄─────── (Requires Phase 5)
└── P2_15_migrate_angular_services ◄───────── (Requires P2_14)
│
Phase 7: Cleanup
├── P2_16_cleanup_legacy_files ◄───────────── (Requires Phase 6)
└── P2_17_final_validation ◄───────────────── (Final step)
```

---

## Prompts

| # | Prompt | Phase | Status | Depends On | Parallelizable |
|---|--------|-------|--------|------------|----------------|
| 01 | [P2_01_sqlmodel_foundation_setup.md](./P2_01_sqlmodel_foundation_setup.md) | 1.1 | 🟢 Not Started | None | ✅ Yes (with 02) |
| 02 | [P2_02_openapi_codegen_pipeline.md](./P2_02_openapi_codegen_pipeline.md) | 1.2 | 🟢 Not Started | None | ✅ Yes (with 01) |
| 03 | [P2_03_migrate_asset_base.md](./P2_03_migrate_asset_base.md) | 2.1 | 🟢 Not Started | 01 | ❌ Sequential |
| 04 | [P2_04_migrate_machine.md](./P2_04_migrate_machine.md) | 2.2 | 🟢 Not Started | 03 | ⚠️ After 03 |
| 05 | [P2_05_migrate_resource.md](./P2_05_migrate_resource.md) | 2.3 | 🟢 Not Started | 03 | ⚠️ Parallel with 04 |
| 06 | [P2_06_migrate_deck.md](./P2_06_migrate_deck.md) | 2.4 | 🟢 Not Started | 03 | ⚠️ After 03 |
| 07 | [P2_07_migrate_protocol_run.md](./P2_07_migrate_protocol_run.md) | 3.1 | 🟢 Not Started | Phase 2 | ⚠️ After Phase 2 |
| 08 | [P2_08_migrate_schedule.md](./P2_08_migrate_schedule.md) | 3.2 | 🟢 Not Started | Phase 2 | ⚠️ Parallel with 07 |
| 09 | [P2_09_migrate_protocol_source.md](./P2_09_migrate_protocol_source.md) | 3.3 | 🟢 Not Started | Phase 2 | ⚠️ Parallel with 07 |
| 10 | [P2_10_migrate_data_outputs.md](./P2_10_migrate_data_outputs.md) | 4.1 | 🟢 Not Started | Phase 2, 3.1 | ⚠️ After 07 |
| 11 | [P2_11_migrate_workcell_user.md](./P2_11_migrate_workcell_user.md) | 4.2 | 🟢 Not Started | Phase 2 | ⚠️ Parallel with 10 |
| 12 | [P2_12_update_crud_services.md](./P2_12_update_crud_services.md) | 5.1 | 🟢 Not Started | Phase 2-4 | ❌ Sequential |
| 13 | [P2_13_update_test_fixtures.md](./P2_13_update_test_fixtures.md) | 5.2 | 🟢 Not Started | Phase 2-4 | ⚠️ Parallel with 12 |
| 14 | [P2_14_generate_typescript_client.md](./P2_14_generate_typescript_client.md) | 6.1 | 🟢 Not Started | Phase 5 | ❌ Sequential |
| 15 | [P2_15_migrate_angular_services.md](./P2_15_migrate_angular_services.md) | 6.2 | 🟢 Not Started | 14 | ❌ Sequential |
| 16 | [P2_16_cleanup_legacy_files.md](./P2_16_cleanup_legacy_files.md) | 7.1 | 🟢 Not Started | Phase 6 | ❌ Sequential |
| 17 | [P2_17_final_validation.md](./P2_17_final_validation.md) | 7.2 | 🟢 Not Started | 16 | ❌ Final |

---

## Execution Order (Optimal)

### Parallel Group 1 (Can start immediately)
- `P2_01_sqlmodel_foundation_setup.md`
- `P2_02_openapi_codegen_pipeline.md`

### Sequential: Asset Base
- `P2_03_migrate_asset_base.md` (after 01)

### Parallel Group 2 (After 03)
- `P2_04_migrate_machine.md`
- `P2_05_migrate_resource.md`
- `P2_06_migrate_deck.md`

### Parallel Group 3 (After Phase 2)
- `P2_07_migrate_protocol_run.md`
- `P2_08_migrate_schedule.md`
- `P2_09_migrate_protocol_source.md`

### Parallel Group 4 (After 07)
- `P2_10_migrate_data_outputs.md`
- `P2_11_migrate_workcell_user.md`

### Parallel Group 5 (After Phase 4)
- `P2_12_update_crud_services.md`
- `P2_13_update_test_fixtures.md`

### Sequential: Frontend (After Phase 5)
- `P2_14_generate_typescript_client.md`
- `P2_15_migrate_angular_services.md`

### Sequential: Cleanup (After Phase 6)
- `P2_16_cleanup_legacy_files.md`
- `P2_17_final_validation.md`

---

## Key Technical Decisions

1. **SQLModel for unified models**: Combines SQLAlchemy ORM + Pydantic in single classes
2. **`openapi-typescript-codegen`**: Generates TypeScript client from OpenAPI schema
3. **Incremental migration**: Legacy files kept until all imports updated
4. **Single-table inheritance preserved**: Asset polymorphism maintained

---

## Verification Commands

```bash
# Quick smoke test after any prompt
uv run pytest tests/ -x -q

# Full test suite
uv run pytest tests/ -v --cov=praxis

# OpenAPI pipeline
uv run python scripts/generate_openapi.py
cd praxis/web-client && npm run generate-api && npm run build
```

---

## Completion Checklist

- [ ] All 17 prompts executed
- [ ] `DEVELOPMENT_MATRIX.md` updated
- [ ] `sqlmodel_codegen_refactor.md` backlog item closed
- [ ] Tests passing with ≥ original coverage
- [ ] Documentation updated

---

> **Archive Note:** When all items above are complete, update Status to "✅ All Complete" and this folder can be moved to `archive/`.
