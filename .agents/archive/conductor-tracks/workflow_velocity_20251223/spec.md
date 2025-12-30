# Specification: Workflow Velocity (UX Polish)

## 1. Overview
This track aims to make PyLabPraxis feel like a professional "power tool" for lab scientists. It focuses on reducing friction through keyboard shortcuts, quick actions, and responsive UI feedback.

## 2. Goals
*   **Keyboard Efficiency:** Enable navigation and common actions without taking hands off the keyboard.
*   **Discoverability:** A Command Palette to make features easy to find.
*   **Contextual Actions:** Right-click menus for faster interaction with specific elements.

## 3. Minimal Implementation (Demo Ready)
*   **Command Palette:** A modal triggered by `Cmd+K` (or `Ctrl+K`) that searches and navigates to:
    *   Specific Protocols
    *   Asset Library
    *   Settings
    *   (Future) Specific actions like "New Run".
*   **Safe Shortcuts:** Global, modifier-based shortcuts to prevent accidental activation during typing.
    *   `Cmd+P`: Go to Protocols.
    *   `Cmd+R`: Go to Resources.
    *   `Cmd+M`: Go to Machines.
*   **Status Banners:** High-visibility, distinct banners for critical system states ("E-Stop", "Door Open").

## 4. Full Implementation (Post-Demo)
*   **Context Menus:** Right-click menus on assets/protocols/steps.
*   **Advanced Hotkeys:** "Safe" hotkeys for critical actions (e.g., `Hold Shift + Esc` to Stop).
*   **Micro-interactions:** Refined animations and feedback for all interactive elements.

## 5. Constraints
*   **Safety:** **NO** single-key shortcuts for dangerous actions (Pause/Stop). All critical actions require modifiers or confirmation.
*   **Scoping:** Keyboard listeners must respect input focus (don't trigger nav when typing in a text box).
