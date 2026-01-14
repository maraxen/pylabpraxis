# Agent Prompt: Settings System Overhaul

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Priority:** P3  
**Batch:** [260115](README.md)  
**Difficulty:** High  
**Dependencies:** None  
**Input Artifact:** `settings_ux_design.md`

---

## 1. The Task

Implement the comprehensive Settings UX overhaul as defined in the design artifact.

**Goal:** Transform the current single-scrolling settings page into a scalable, categorized Sidebar layout.

## 2. Implementation Steps

Follow the "Implementation Phases" in `settings_ux_design.md`.

### Step 1: Structure & Migration

- Create `SettingsShellComponent` with Vertical Tab layout (Sidenav or split view).
- Migrate existing settings from `settings.component.ts` into focused sub-components:
  - `GeneralSettingsComponent`
  - `SimulationSettingsComponent`
  - `HardwareSettingsComponent`
  - `DataSettingsComponent`
  - `AboutSettingsComponent`

### Step 2: New Features

- **Density Toggle**: Implement CSS class/variable toggle on `<body>` or root.
- **Search**: Add client-side search to the sidebar.
- **Danger Zone**: Style "Factory Reset" and "Clear Data" actions appropriately.

### Step 3: Cleanup

- Remove the old `settings.component.ts` logic.
- Ensure all routes point to the new shell.

## 3. Constraints

- **Design**: Strictly follow `settings_ux_design.md`.
- **Styling**: Use `mat-list-item` or similar for density-friendly rows.
- **State**: Use `AppStore` for persisting preferences (Theme, Density, etc).

## 4. Verification Plan

- [ ] Vertical navigation works and handles mobile/desktop.
- [ ] All existing settings (Theme, Export, Tutorial) are preserved and working.
- [ ] Search correctly filters the visible settings.
- [ ] "Danger Zone" items have distinct styling/confirmations.
- [ ] Density toggle visibly affects the UI (at least the settings page itself).

---

## On Completion

- [ ] Update `settings_ux_design.md` with any deviations.
- [ ] Update this prompt status to 🟢 Completed.
