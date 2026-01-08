# Prompt 6: Time Travel Debugging

Implement "Time Travel" debugging in the Execution Monitor run detail view.

## Context

State history is recorded during execution. Allow users to scrub through and inspect state at any operation.

## Tasks

1. Create `StateInspectorComponent`:
   - Timeline scrubber showing operation sequence
   - Prev/Next navigation buttons
   - Current operation display

2. Create state comparison view showing "State Before" and "State After" for selected operation

3. Create `StateHistoryTimelineComponent`:
   - Sparkline-style visualization of state changes over time
   - Show tips loaded, well volumes, etc. as mini-charts

4. Add "State Inspector" tab to run detail view

5. Handle browser mode: load state history from SqliteService

## Files to Create

- `praxis/web-client/src/app/features/execution-monitor/components/state-inspector/`
- `praxis/web-client/src/app/features/execution-monitor/components/state-history-timeline/`

## Files to Modify

- `praxis/web-client/src/app/features/execution-monitor/components/run-detail/`

## Reference

- `.agents/backlog/simulation_ui_integration.md` (Phase 8.5, 8.6)
