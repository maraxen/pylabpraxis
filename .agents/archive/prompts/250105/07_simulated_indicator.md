# Prompt 7: Simulated Machine Indicator & Infinite Consumables

Add "Simulated" chip indicator to machines and implement infinite consumables.

## Tasks

1. Create "Simulated" chip component:
   - Small accent-colored chip with computer icon
   - Display on machine cards, selection step, deck setup

2. Add to `MachineCardComponent` and `MachineSelectionStepComponent`

3. Implement infinite consumables:
   - Add `infiniteConsumables` setting to AppStore (default: true in browser mode)
   - When tip depletion occurs and setting is ON, auto-replenish
   - Show "∞" symbol next to consumable counts when enabled
   - Show subtle toast notification on auto-replenish

4. Add Settings toggle: "Infinite Consumables (auto-replenish tips, plates)"
   - Include help text explaining the behavior
   - Note in tutorial that this can be disabled for realistic simulations

5. Update tutorial to mention this setting

## Files to Modify

- `praxis/web-client/src/app/shared/components/machine-card/`
- `praxis/web-client/src/app/features/run-protocol/components/machine-selection/`
- `praxis/web-client/src/app/features/settings/settings.component.ts`
- `praxis/web-client/src/app/store/app.store.ts`

## Reference

- `.agents/backlog/browser_mode_defaults.md`
