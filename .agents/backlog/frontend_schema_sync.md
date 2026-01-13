# Backlog Item: Frontend Schema Synchronization (Post-SQLModel)

**Status:** 🟢 Planned
**Difficulty:** 🟡 Intricate
**Area:** Frontend
**Created:** 2026-01-13
**Relates To:** [Model Unification (SQLModel)](../archive/backlog/sqlmodel_codegen_refactor.md)

---

## Goal

After the backend migration to SQLModel unified domain models, the frontend Angular application now has ~29 TypeScript compilation errors and ~17 warnings. This work brings the frontend schema types, API client, and component code into alignment with the regenerated schema and OpenAPI spec.

---

## Error Analysis Summary

### Root Causes

1. **Missing Schema Exports** - The new `schema.ts` uses table-based naming (e.g., `MachineDefinition`) but repositories still import legacy catalog names (`MachineDefinitionCatalog`, `ResourceDefinitionCatalog`, `Asset`)
2. **Property Name Changes** - JSONB fields now use `_json` suffix consistently (e.g., `inferred_requirements` → `inferred_requirements_json`)
3. **Missing API Model Properties** - `ProtocolRunRead` is missing `protocol_name`, `top_level_protocol_definition_accession_id`, `protocol_definition_accession_id`, `started_at`, `completed_at` that components expect
4. **Missing API Service Module** - `ReplService` not generated or path incorrect
5. **Missing User Model** - `UserResponse` import path no longer valid
6. **Type Compatibility Issues** - `Record<string, unknown>` now used for accession_id fields instead of `string`, causing strict type mismatches
7. **Unused Imports** - Angular components have stale imports (RouterLink, StateDisplayComponent, MachineCardComponent, etc.)
8. **Sass Deprecations** - `@import` rules deprecated in favor of `@use`

---

## Phases

### Phase 1: Schema Type Alignment

Update `schema.ts` or add aliases to bridge naming gaps.

- [ ] Add `Asset` interface to schema.ts (or confirm inheritance from Machine/Resource/Deck)
- [ ] Add type aliases: `MachineDefinitionCatalog = MachineDefinition`, `ResourceDefinitionCatalog = ResourceDefinition`
- [ ] Update `repositories.ts` imports to use correct type names
- [ ] Audit all `Record<string, unknown>` fields that should be `string` (accession_id types)

### Phase 2: API Client Regeneration Audit

Verify OpenAPI client generation captured all endpoints and models.

- [ ] Confirm `ReplService` exists in `api-generated/services/` or regenerate
- [ ] Confirm `UserResponse` or equivalent exists in `api-generated/models/`
- [ ] Check if `FunctionProtocolDefinitionResponse` is generated (or renamed)
- [ ] Verify `ProtocolRunRead` includes all fields used by components

### Phase 3: Service Layer Updates

Update services to use new type names and property paths.

- [ ] `playground-runtime.service.ts`: Fix ReplService import, type `msg` properly
- [x] `simulation-results.service.ts`: Update property access (`inferred_requirements_json`, `failure_modes_json`, `simulation_result_json`)
- [ ] `auth.service.ts`: Fix UserResponse import path
- [ ] `asset.service.ts`: Fix ResourceDefinitionCatalog import
- [ ] `protocol.service.ts`: Fix FunctionProtocolDefinitionResponse import

### Phase 4: Component Updates

Update components to align with new schema property names.

- [ ] `data-visualization.component.ts`: Update ProtocolRunRead property access
  - `protocol_name` → determine new field or derived value
  - `started_at` → `start_time`
  - `completed_at` → `end_time`
  - Handle nullable Date arguments properly
- [ ] `run-protocol.component.ts`: Fix `MachineCompatibility[]` type mapping
- [ ] `hardware-discovery-dialog`: Fix property access on empty object type

### Phase 5: Cleanup Unused Imports (Warnings)

Remove or fix unused component imports in Angular files.

- [ ] `AssetDashboardComponent`: Remove unused RouterLink import
- [ ] `ForgotPasswordComponent`: Remove unused RouterLink import
- [ ] `LoginComponent`: Remove unused RouterLink import
- [ ] `RegisterComponent`: Remove unused RouterLink import
- [ ] `RunDetailComponent`: Remove unused StateDisplayComponent import
- [ ] `HomeComponent`: Remove unused MachineCardComponent import
- [ ] `WellSelectorComponent`: Remove unused Grid/GridRow/GridCell/NgClass imports
- [ ] `GuidedSetupComponent`: Remove unnecessary optional chain

### Phase 6: Sass Migration (Warnings)

Migrate from deprecated `@import` to `@use` syntax.

- [ ] Update `src/styles.scss` to use `@use` instead of `@import`
- [ ] Update any component-level SCSS files using `@import`

### Phase 7: Verification

- [ ] Run `npm run build` - expect 0 errors, 0 warnings
- [ ] Run `npm test` - ensure no test regressions
- [ ] Manually test key flows: protocol library, data visualization, hardware discovery

---

## Notes

### Key Type Mappings

| Old Name                     | New Name                   | Notes                                |
|------------------------------|----------------------------|--------------------------------------|
| `MachineDefinitionCatalog` | `MachineDefinition` | Table rename |
| `ResourceDefinitionCatalog` | `ResourceDefinition` | Table rename |
| `DeckDefinitionCatalog` | `DeckDefinitionCatalog` | Unchanged (catalog table) |
| `Asset` | N/A | Base class for Machine, Resource, Deck (JTI) |
| `inferred_requirements` | `inferred_requirements_json` | JSONB suffix convention |
| `simulation_result` | `simulation_result_json` | JSONB suffix convention |
| `started_at` | `start_time` | ProtocolRun field rename |
| `completed_at` | `end_time` | ProtocolRun field rename |

### Affected Files

```text
src/app/core/db/repositories.ts
src/app/core/db/schema.ts
src/app/core/services/playground-runtime.service.ts
src/app/core/services/simulation-results.service.ts
src/app/features/assets/services/asset.service.ts
src/app/features/auth/services/auth.service.ts
src/app/features/data/data-visualization.component.ts
src/app/features/protocols/services/protocol.service.ts
src/app/features/run-protocol/run-protocol.component.ts
src/app/shared/components/hardware-discovery-dialog/...
src/styles.scss
```

### Regeneration Commands

```bash
# Regenerate browser schema
uv run scripts/generate_browser_schema.py

# Regenerate OpenAPI client
cd praxis/web-client && npm run generate-api

# Build to verify
npm run build
```

---

## References

- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md)
- [SQLModel Migration Archive](../archive/backlog/sqlmodel_codegen_refactor.md)
- [schema.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/db/schema.ts)
- [repositories.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/db/repositories.ts)
