# Prompt 1: Protocol Warnings in Selection UI (COMPLETED)

**Status**: ✅ Completed
**Date**: 2026-01-05

Show failure mode warnings on protocols in the Run Protocol selection step.

## Context

Backend simulation caches failure_modes_json for each protocol. Surface these in the UI.

## Tasks

1. Create `SimulationResultsService` to fetch simulation data from protocol definitions
2. Create `ProtocolWarningBadgeComponent`:
   - Shows count badge (e.g., "⚠️ 2 issues") if failure modes exist
   - On click/hover, expands to show failure mode details
3. Integrate badge into protocol list in Run Protocol wizard (step 1)
4. Show "✅ Ready" badge for protocols with no failure modes
5. Handle case where simulation hasn't run yet (show "Not analyzed" state)
6. In browser mode, check for cached simulation results in SQLite

## Files to Create

- `praxis/web-client/src/app/core/services/simulation-results.service.ts`
- `praxis/web-client/src/app/shared/components/protocol-warning-badge/`

## Files to Modify

- `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts`
- `praxis/web-client/src/app/features/run-protocol/components/protocol-card/`

## Reference

- `.agents/backlog/simulation_ui_integration.md` (Phase 8.2)
