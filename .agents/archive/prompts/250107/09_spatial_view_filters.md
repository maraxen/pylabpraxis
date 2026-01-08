# Prompt: Spatial View (Asset Filters)

**Priority**: P3 (Medium)
**Backlog**: [asset_management.md](../../backlog/asset_management.md)

## Context

The Spatial View provides a 3D or schematic overview of assets. As the number of assets grows, users need a way to filter and sort this view to find specific resources or machines.

## Objective

Implement the `AssetFiltersComponent` and integrate it into the Spatial View.

## Tasks

### 1. `AssetFiltersComponent` Implementation

- Create a new component at `praxis/web-client/src/app/features/assets/components/asset-filters/`.
- Use the standard `FilterChipComponent` for consistency with other filter bars.
- Add a text search input for Name/FQN.

### 2. Filtering Logic

- Implement filters for:
  - **Status**: (e.g., Available, Busy, Error, Maintenance).
  - **Category**: (e.g., Liquid Handler, Plate Reader, Tip Rack).
  - **Workcell**: Filter assets belonging to specific high-level groupings.
  - **Machine**: Filter resources associated with a specific machine.

### 3. Sorting Logic

- Implement sorting by:
  - **Machine Location**: Logical naming or physical coordinates.
  - **Status**: Group by availability.
  - **Name/Date**: Standard alphabetical or chronological sorting.

### 4. UI/UX Data Model Update

- Add a `location_label` physical location text field to the machine/resource editing dialogs.
- Ensure this label is searchable and filterable.

## Requirements

- Ensure the filter bar is responsive and collapses on smaller screens.
- Use Angular Signals for state management of active filters.
- Maintain visual parity with the Resource Inventory filter bar.

## Verification

- Filter by "Available" and verify only available assets are shown.
- Sort by "Name" and verify the list order.
- Search for a specific `location_label` and verify the result.
