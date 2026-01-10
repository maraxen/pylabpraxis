# Agent Prompt: Fix Asset Filtering for PLR Classes

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260109](./README.md)
**Backlog Reference:** [asset_management.md](../../backlog/asset_management.md#p1-asset-filtering)

---

## 1. The Task

The asset management view (`AssetsComponent`) includes a filtering mechanism, but the "PLR Class" filter (e.g., filtering for `TipRack` or `Plate`) is currently non-functional or incorrect.

The `AssetSearchService` appears to be a stub or is missing the specific logic to filter `Asset` objects based on their underlying `ResourceDefinition`'s PLR class. This prevents users from quickly finding specific types of labware in large inventories.

**Goal:** Implement robust client-side (or backend-supported) filtering in `AssetSearchService` to correctly handle the "PLR Class" filter criteria.

## 2. Technical Implementation Strategy

*(Architectural guidance for implementing asset filtering logic)*

**Analysis:**

The `AssetFiltersComponent` likely captures user input but the connection to `AssetSearchService` or the filtering logic within the service is defective. "PLR Class" typically refers to the `class_name` or `type` field in the `ResourceDefinition` associated with an `Asset`.

**Frontend Components:**

1. **`AssetSearchService` (`praxis/web-client/.../services/asset-search.service.ts`)**:
   - Implement/Verify the `filterAssets(assets: Asset[], criteria: AssetFilterCriteria)` method.
   - Ensure it specifically checks `asset.definition.plr_type` (or the equivalent property mapping to the PyLabRobot class name).
   - Handle partial matches or exact matches as appropriate for the UI (likely exact match if it's a dropdown, or fuzzy if text).

2. **`AssetFiltersComponent` (`praxis/web-client/.../components/asset-filters/asset-filters.component.ts`)**:
   - Ensure the component emits the correct filter structure that `AssetSearchService` expects.
   - Verify the "PLR Class" input field is bound to the correct model property.

**Data Flow:**

1. User selects a PLR Class (e.g., "Corning 96 Well Plate") in `AssetFiltersComponent`.
2. Component emits `filterChange` event.
3. `AssetsComponent` receives the event and calls `AssetSearchService.filterAssets()`.
4. Service iterates through the cached/loaded assets and returns the subset matching the PLR class.
5. `AssetsComponent` updates the `ResourceListComponent` with the filtered list.

**Sharp Bits:**

- Ensure case-insensitivity if using text search.
- Check if the backend `ResourceDefinition` model uses `class_name`, `name`, or `plr_type`. You may need to inspect `praxis/web-client/src/app/core/models/plr.models.ts` or `asset.models.ts` to find the exact field name.
- Verify that the filter criteria structure aligns between frontend and backend (if using backend filtering).

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/services/asset-search.service.ts` | The core filtering logic implementation. |
| `praxis/web-client/src/app/features/assets/components/asset-filters/asset-filters.component.ts` | The UI component for filter inputs. |
| `praxis/web-client/src/app/features/assets/services/asset-search.service.spec.ts` | Unit tests for the filtering logic. |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/models/asset.models.ts` | Asset and ResourceDefinition interfaces. |
| `praxis/web-client/src/app/features/assets/assets.component.ts` | The container component orchestrating data flow. |
| `praxis/backend/api/resources.py` | Reference for how resources are structured on the backend. |

## 4. Constraints & Conventions

- **Commands**: Use `npm run test` or `npx nx test web-client` for frontend tests.
- **Frontend Path**: `praxis/web-client`
- **State**: If creating new state management for filters, prefer Angular Signals.
- **Type Safety**: Ensure strict typing for the Filter Criteria interface.

## 5. Verification Plan

**Definition of Done:**

1. **Unit Tests**: The `AssetSearchService` has comprehensive tests verifying:
   - Filtering by PLR Class returns correct matches.
   - Filtering handles empty/null criteria gracefully.
   - Filtering handles case sensitivity correctly (if applicable).

2. **Execution**:
   ```bash
   cd praxis/web-client
   npx nx test web-client --testFile=asset-search.service.spec.ts
   ```

3. **Manual Check**: The Asset Dashboard UI updates the list when the filter is applied.

---

## On Completion

- [ ] Commit changes with descriptive message: `fix(assets): implement correct PLR class filtering`
- [ ] Update `backlog/asset_management.md` status
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` if applicable
- [ ] Mark this prompt complete in batch README and set the status to 🟢 Completed

---

## References

- `.agents/README.md` - Development context and agent workflow
- `backlog/asset_management.md` - Full asset management issue tracking
- `DEVELOPMENT_MATRIX.md` - Current work priorities
