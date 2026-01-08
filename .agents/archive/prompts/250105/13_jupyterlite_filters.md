# Prompt 13: JupyterLite Asset Menu Search & Filters (COMPLETED)

**Status**: ✅ Completed
**Date**: 2026-01-05

Add search bar and filter chips to JupyterLite asset sidebar.

## Context

The REPL has an asset/inventory sidebar. Add search and filtering using the **same filtering logic and components as the Asset Management page**.

## Tasks

1. Add search bar at top of asset sidebar (same as Asset Management)

2. Integrate `FilterChipComponent` (from chip_filter_standardization work)

3. **Use the same filtering logic and capability as the Asset Management page**:
   - Same filter chips
   - Same filter service/logic
   - Same result count behavior

4. When filter changes, update visible assets in sidebar

5. Handle empty state:
   - Show "No resources in inventory. Add resources from the Assets page"
   - Include clickable link to `/app/assets`

6. Test in browser mode with JupyterLite

## Files to Modify

- `praxis/web-client/src/app/features/repl/components/jupyterlite-repl/`
- `praxis/web-client/src/app/features/repl/components/asset-sidebar/` (or equivalent)

## Reference

- `.agents/backlog/repl_jupyterlite.md` (Phase 4)
- `.agents/backlog/chip_filter_standardization.md`
