# Tutorial & Demo Mode Toggle

**Priority:** P2  
**Status:** Complete  
**Created:** 2026-01-05

## Summary

Implement first-time user onboarding with guided tutorial and runtime demo mode toggle.

## User Story

As a first-time user, I want to be guided through the application features so that I can quickly understand how to use Praxis effectively.

As a user, I want to toggle demo mode on/off at runtime so that I can switch between sample data exploration and real work.

## Features

### First-Time Welcome Popup

- Appears on first visit (no `localStorage` flag)
- Contains "Demo Mode (Recommended)" toggle switch
- "Start Tutorial" and "Skip" buttons

### Guided Tutorial (Shepherd.js)

- 11-step tour of key features
- Highlights:
  - Dashboard, Assets, Machines, Resources
  - Protocols, Run, REPL, Data Visualization
  - History, System Status, Theme Toggle
- Can be exited early

### Exit Demo Mode Dialog

- Appears after tutorial completes (if demo mode was ON)
- Options: "Exit Demo Mode" or "Keep Demo Mode"
- "Exit" clears sample data, switches to empty browser mode

### Settings Integration

- "Restart Tutorial" button
- "Demo Mode" toggle switch
- Persistent via `localStorage`

## Technical Notes

- New service: `OnboardingService` manages state
- `ModeService.detectMode()` updated to check runtime toggle
- Third-party dependency: `shepherd.js` (~35KB)

## Acceptance Criteria

- [x] First visit shows welcome dialog
- [x] Demo mode toggle seeds/clears sample data
- [x] Tutorial completes all 11 steps OR exits cleanly
- [x] Tutorial correctly highlights REPL, Data, Theme, and Status
- [x] Exit-demo dialog appears post-tutorial (if applicable)
- [x] Returning users skip welcome dialog
- [x] Settings contains restart/toggle options
