# Plan: Workflow Velocity (UX Polish)

## Phase 1: Minimal Implementation (Demo Ready)
*   [ ] Task: Implement Command Palette (`Cmd+K`).
    *   [ ] Subtask: Install/Create a dialog component for the palette.
    *   [ ] Subtask: Create a centralized `CommandRegistryService` to register actions and navigation paths.
    *   [ ] Subtask: Wire `Cmd+K` global listener to open the palette.
*   [ ] Task: Implement Safe Navigation Shortcuts.
    *   [ ] Subtask: Implement `KeyboardService` that handles `Cmd/Ctrl` modifiers and checks `document.activeElement` to ignore inputs.
    *   [ ] Subtask: Register `Cmd+P`, `Cmd+R`, `Cmd+M` handlers.
*   [ ] Task: Conductor - User Manual Verification 'Workflow Velocity Minimal' (Protocol in workflow.md)

## Phase 2: Full Implementation
*   [ ] Task: Implement Context Menus.
*   [ ] Task: Implement Advanced/Hold Shortcuts.
*   [ ] Task: Conductor - User Manual Verification 'Workflow Velocity Full' (Protocol in workflow.md)
