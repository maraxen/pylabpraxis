# Spatial View UX Recommendation

## Executive Summary

The "Spatial View" currently functions as an aggregated **"All Assets" Grid View**, displaying both machines and resources as cards. Its name is misleading as it does not provide a topological or map-based interface (e.g., deck layout), which users likely expect from the term "Spatial".

**Recommendation:** Rename to **"Asset Gallery"** (or "All Assets") and position it as the high-level visual directory. In the long term, consider consolidating all tabs into a single "Asset Explorer" with unified view controls (List/Grid toggle) and high-level type filters.

## Current State Analysis

### Spatial View Features

* **Data Scope:** Aggregates **Machines AND Resources** in a single view.
* **Visualization:** Grid of "Asset Cards" showing icon, status, and location.
* **UX Metaphor:** Visual browsing / Card catalog.
* **Unique Capabilities:**
  * Single view to see relationship between Machines and Resources (via Location filter).
  * Visual emphasis on "What is where" (via Location metadata on cards).

### Comparison with Other Tabs

| Feature | Spatial View | Machines Tab | Resources Tab |
|:---|:---|:---|:---|
| **Data** | Mixed (All Assets) | Machines Only | Resources Only |
| **View Type** | Grid (Cards) | List / Table | Accordion / List |
| **Filtering** | Shared (Category, Status, Location) | **Specialized** (Backend, Simulated Mode) | **Specialized** (Brand, Discarded) |
| **Primary Use** | Browsing, Location lookup | Hardware Management, Debugging | Inventory Management |

## Options Evaluated

### Option A: Keep as Separate Tab (Renamed)

Keep the functionality exactly as is but rename it to match its mental model.

* **Pros:** Low effort, preserves the "All Assets" utility.
* **Cons:** Still adds to tab clutter; doesn't solve the long-term UI fragmentation.
* **Names:** "Asset Gallery", "Overview Grid", "All Assets".

### Option B: Merge as View Mode (Unified)

Deprecate the separate tab. Add a "View Mode" (List vs. Grid) toggle to a unified "Assets" view.

* **Pros:** Cleanest UX, follows standard patterns (e.g., Google Drive, Finder). Reduces code duplication.
* **Cons:** High effort (Requires `A-01` unified view controls implementation first). Complex filtering logic (combining Machine/Resource specific filters).
* **Risk:** "Machines" and "Resources" audiences might be distinct (DevOps vs Lab Tech), so merging might clutter the UI for specific personas.

### Option C: Deprecate

Remove the tab entirely.

* **Pros:** Simplifies navigation.
* **Cons:** Loss of functionality—users lose the ability to see Machines and Resources side-by-side or filter everything by "Location" in one go.

## Recommendation

**Short Term (Immediate): Option A (Rename)**
Rename the tab to **"Gallery"** or **"All Assets"** to clarify intent. "Spatial" should be reserved for actual physical layouts (e.g., Deck View).

**Long Term (Planned): Option B (Merge)**
As part of the **View Controls Standardization (Group A)** initiative:

1. Create a unified `AssetExplorerComponent`.
2. Implement `ViewControls` to toggle between **List (Table)** and **Grid (Cards)**.
3. Use "Machines" and "Resources" as top-level filters (or tabs) within that explorer.
4. Once the unified view exists, deprecate the standalone "Spatial View" component code.

## Implementation Path

*This aligns with `A-01_shared_view_controls`.*

1. **Immediate Action:** Update `AssetsComponent` tab label from "Spatial View" to "Gallery".
2. **Phase 2 (Group A):** Build `ViewControlsComponent` with toggle support.
3. **Phase 3:** Refactor `SpatialViewComponent` logic into the shared `MachineListComponent` / `ResourceListComponent` to support Grid Mode rendering.

## Risks & Mitigations

* **Risk:** Users looking for the "Map" might be disappointed.
  * *Mitigation:* Ensure the upcoming "Workcell" or "Deck" features are clearly labeled as the spatial/map tools.
* **Risk:** Performance on "All Assets" if registry grows large.
  * *Mitigation:* The current implementation supports pagination/virtualization concepts (or should). Grid views are heavier than lists; ensure `trackBy` and `OnPush` are strictly used (already present).
