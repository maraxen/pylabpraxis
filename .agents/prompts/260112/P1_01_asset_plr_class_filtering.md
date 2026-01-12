# Agent Prompt: Asset PLR Class Filtering

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260112](./README.md)
**Backlog Reference:** [protocol_workflow.md](../../backlog/protocol_workflow.md)

---

## 1. The Task

Fix the asset filtering system so that protocol execution's autofill and asset selection only shows resources compatible with the required PyLabRobot class. Currently, when a protocol requires a specific PLR class (e.g., `Plate`, `TipRack`), the asset selector may show incompatible resources.

**User Value:** Users can quickly select the correct labware for their protocols without manually filtering through incompatible options.

---

## 2. Technical Implementation Strategy

### Problem Analysis

The `GuidedSetupComponent` uses multiple matching strategies:
1. Exact FQN match
2. FQN class name match
3. Type hint string match
4. Category matching via `required_plr_category`

The issue is that `required_plr_category` is not reliably populated from the backend, and the fallback FQN inference logic in `getResourceCategory()` (lines 462-495) is incomplete.

### Frontend Components

1. **Enhance `GuidedSetupComponent`** (`praxis/web-client/src/app/features/run-protocol/components/guided-setup/guided-setup.component.ts`)
   - Improve `matchesByCategory()` to handle PLR class hierarchy
   - Add proper inheritance-aware matching (e.g., `TipRack` should match `ItemizedResource`)

2. **Enhance `AssetSelectorComponent`** (`praxis/web-client/src/app/shared/formly-types/asset-selector.component.ts`)
   - Apply consistent filtering logic with GuidedSetup
   - Ensure `plrTypeFilter` prop is properly used

### Backend/Services

1. **Protocol Definition Enrichment** - Ensure `required_plr_category` is populated when protocol assets are analyzed
   - Check `praxis/backend/utils/plr_static_analysis/` for how asset requirements are extracted
   - Verify FQN and category information is preserved through to the API response

### Data Flow

1. Protocol definition is loaded with asset requirements
2. Each requirement has `fqn`, `type_hint_str`, and optionally `required_plr_category`
3. `getCompatibleResources()` filters inventory against requirement
4. Autofill selects best match from filtered list

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/run-protocol/components/guided-setup/guided-setup.component.ts` | Main asset matching logic |
| `praxis/web-client/src/app/shared/formly-types/asset-selector.component.ts` | Formly-based asset selector |
| `praxis/web-client/src/app/core/db/plr-category.ts` | PLR category enum definitions |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/backend/utils/plr_static_analysis/models.py` | Backend PLR analysis models |
| `praxis/web-client/src/app/features/protocols/models/protocol.models.ts` | Protocol/AssetRequirement types |
| `praxis/web-client/src/app/features/assets/models/asset.models.ts` | Resource model with plr_definition |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python, `npm` for Angular.
- **Backend Path**: `praxis/backend`
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use Tailwind utility classes where possible.
- **State**: Prefer Signals for new Angular components.
- **Linting**: Run `uv run ruff check .` before committing.

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors:
   ```bash
   cd praxis/web-client && npm run build
   ```

2. Manual testing scenarios:
   - Create a protocol requiring a `Plate` resource
   - Verify only Plate-type resources appear in the autofill dropdown
   - Create a protocol requiring a `TipRack`
   - Verify tip racks appear but plates do not

3. Existing tests pass:
   ```bash
   cd praxis/web-client && npm test -- --include="**/guided-setup*"
   ```

---

## On Completion

- [ ] Commit changes with descriptive message referencing the backlog item
- [ ] Update backlog item status in `protocol_workflow.md`
- [ ] Update DEVELOPMENT_MATRIX.md - mark "Asset Filtering" as completed
- [ ] Release browser_subagent in status.json if used
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `TECHNICAL_DEBT.md` - Known issues
