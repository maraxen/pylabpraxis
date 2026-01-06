# Prompt 11: Machine & Execution Monitor Filter Chips (COMPLETED)

**Status**: ✅ Completed
**Date**: 2026-01-05

Integrate chip-based filters into Machine Registry and Execution Monitor.

## Tasks

1. Machine Registry chips:
   - Category: LiquidHandler, PlateReader, HeaterShaker, etc.
   - Simulated: filter by is_simulated flag
   - Status: Connected, Disconnected, Error
   - Backend: STAR, OT2, Chatterbox, Simulator

2. Execution Monitor chips:
   - Status: Running, Completed, Failed, Cancelled
   - Protocol: multi-select from available protocols
   - (Date range can remain as separate control)

3. Make Execution Monitor filters actually filter the run list (currently broken)

4. Ensure consistent styling across all filter surfaces

## Files to Modify

- `praxis/web-client/src/app/features/assets/components/machine-accordion/`
- `praxis/web-client/src/app/features/execution-monitor/components/run-filters/`

## Reference

- `.agents/backlog/chip_filter_standardization.md` (Phase 4, 5)
- `.agents/backlog/browser_mode_issues.md` (issue #7)
