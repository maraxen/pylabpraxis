# Settings UX Design

**Status:** Draft
**Date:** 2026-01-14
**Author:** Antigravity

## Current State

The current settings page is a single scrolling view containing `mat-card` elements for each section.

**Current Sections:**

1. **Appearance**: Theme toggle (Light/System/Dark)
2. **Features**: Maintenance Tracking, Infinite Consumables
3. **Onboarding**: Tutorial controls
4. **Remote Hardware Access**: Instructional text + ngrok expansion
5. **About**: Version info
6. **Data Management**: Export/Import, Reset Inventory

**Pain Points:**

- **Navigation**: Scrolling becomes inefficient as settings grow.
- **Organization**: "Data Management" and "Remote Hardware" are mixed with simple toggles.
- **Scalability**: No clear place for new categories like "Simulation specific" or "Network".
- **Visuals**: Review notes indicate "Card Visual Polish" is needed (overlap issues).

## Proposed Settings Inventory

We propose organizing settings into 5 logical categories.

### 1. General & Appearance

* **Theme**: Light / Dark / System (Existing)
- **Density**: Compact / Normal (New - *High value for complex lab interfaces*)
- **Language/Region**: (Placeholder for future)

### 2. Simulation

* **Simulation Mode**: Global Enable/Disable (New in UI, exists in Store)
- **Default Backend**: Selection for new machines (New - per Arch plan)
- **Infinite Consumables**: Auto-replenish tips/plates (Existing)
- **Speed**: Simulation speed multiplier (Potential future)

### 3. Hardware & Connections

* **Remote Agent**: Connection status & token configuration (Refined "Remote Hardware Access")
- **Discovery**: Auto-discover local devices on startup (New toggle)
- **Browser Permissions**: Status of WebSerial / WebUSB permissions (New - *Critical for browser mode*)

### 4. Data & Storage

* **Run History**: Clear "Recent Activity" mock data (New)
- **Backup**: Export / Import Database (Existing)
- **Factory Reset**: Reset all assets to defaults (Existing)
  - *UX Note*: Move to bottom / "Danger Zone" styling.

### 5. About & Help

* **Tutorial**: Reset/Restart Onboarding (Existing)
- **Version Info**: App Version, Frameworks (Existing)
- **Documentation Link**: External link to docs (New)

## UX Recommendations

### Layout Choice: Vertical Tabs (Sidebar)

**Recommendation**: **Vertical Tabs** (Left-side navigation).

**Rationale**:

- **Scalability**: Accommodates 5-10 categories significantly better than horizontal tabs or single scroll.
- **Pattern Match**: Matches VS Code, GitHub, and other complex developer/technical tools.
- **Mobile Friendly**: Sidebar can collapse to a drawer (Hamburger menu) easily.

**Concept:**

```
+----------------+---------------------------------------------------+
|  SETTINGS      |  General                                          |
|                |                                                   |
|  General       |  Appearance                                       |
|  Simulation    |  [ Theme Toggle ]                                 |
|  Hardware      |  [ Density Toggle ]                               |
|  Data          |                                                   |
|  About         |  ------------------------------------------------ |
|                |                                                   |
|                |  Localization                                     |
|                |  ...                                              |
+----------------+---------------------------------------------------+
```

### Search

**Recommendation**: **Implement textual search** at the top of the Settings Sidebar.

- **Value**: High. Users often assume "Reset" is in General vs Data. Search bridges this gap.
- **Implementation**: Client-side filter of the settings tree.

### Danger Zone

**Recommendation**: Use a distinct "Danger Zone" pattern for destructive actions.

- **Location**: Bottom of the specific section (e.g., Data) OR a dedicated "Danger Zone" category if many exist.
- **Styling**: Red border, usage of `mat-error` colors, explicit confirmation dialogs (already implemented for Reset).

## Implementation Phases

### Phase 1: Structure & Migration

- Create `SettingsShellComponent` with Vertical Tab layout (Sidenav or Split View).
- Migrate existing cards into separate components (`AppearanceSettings`, `DataSettings`, etc.).
- Default route redirects to 'General'.

### Phase 2: Visual Polish & Search

- Implement Search bar filtering.
- Standardize "Setting Item" component (Label, Description, Control).
- Remove `mat-card` wrappers in favor of cleaner Section Headers + List Items for checking settings density.

### Phase 3: New Features

- Add "Density" toggle (requires global CSS variable hook).
- Add "Clear Run History" (requires `AppStore` update).
- Add "Browser Permissions" status checks.
