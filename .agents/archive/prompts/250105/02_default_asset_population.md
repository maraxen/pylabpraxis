# Prompt 2: Default Asset Population

Implement default asset population for browser mode (replacing demo mode seeding).

## Context

Browser mode should start with 1 instance of every resource and every machine. This replaces the demo mode approach.

## Tasks

1. Refactor `SqliteService.seedMockData()` to `seedDefaultAssets()`:
   - Query all ResourceDefinitions from prebuilt DB, create 1 Resource instance for each
   - Query all MachineDefinitions from prebuilt DB, create 1 Machine instance for each

2. For machines:
   - Set `is_simulated: true`
   - Find simulation-compatible backend:
     - If definition has "Simulator" or "Chatterbox" in compatible_backends, use it
     - **Otherwise, patch out the IO layer** (any machine can run in simulation by stubbing IO)
   - Name with "(Sim)" suffix

3. Only seed if assets table has no user-created instances (not definitions)

4. Preserve user data on subsequent loads (don't overwrite)

5. Add "Reset to Defaults" button in Settings with confirmation dialog

## Files to Modify

- `praxis/web-client/src/app/core/services/sqlite.service.ts`
- `praxis/web-client/src/app/features/settings/settings.component.ts`
- `praxis/web-client/src/app/shared/models/machine.ts`

## Reference

- `.agents/backlog/browser_mode_defaults.md`
