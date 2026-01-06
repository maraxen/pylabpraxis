# Browser Mode Default Assets & Demo Mode Elimination

**Priority**: P2 (High)
**Owner**: Frontend/Backend
**Created**: 2026-01-05
**Status**: Planning

---

## Overview

Eliminate the separate "Demo Mode" toggle and instead make **Browser Mode the default experience** with sensible defaults:

1. **1 instance of every resource type** from the PLR catalog
2. **1 instance of every machine type** with simulation backend
3. **Infinite consumables** (tips, plates auto-replenish)
4. **Simulated-only indicator** on machines

This removes the need to maintain separate demo data seeding, toggles, and exit dialogs.

---

## Rationale

### Current State

- Demo Mode is a separate toggle in Settings and Welcome dialog
- Requires manual seeding of "mock" data
- Users must decide upfront whether to use demo or not
- Two code paths to maintain

### Target State

- Browser Mode IS the demo experience
- No toggle needed - simulation is the default
- Real hardware integration is the exception (production mode)
- Single code path, simpler maintenance

---

## Default Asset Population

### Resources: 1 of Each Type

On first browser mode load (or database reset):

```typescript
async function seedDefaultResources(): Promise<void> {
  const definitions = await resourceDefinitionService.getAll();
  
  for (const def of definitions) {
    const instance: Resource = {
      id: generateId(),
      definition_id: def.id,
      name: def.name,  // Use definition name
      status: 'active',
      fqn: def.fqn,
      asset_type: 'resource',
      // ... other fields
    };
    await resourceRepository.create(instance);
  }
}
```

### Machines: 1 Instance of Each Type with Simulation Backend

On first browser mode load:

```typescript
async function seedDefaultMachines(): Promise<void> {
  const definitions = await machineDefinitionService.getAll();
  
  for (const def of definitions) {
    // Find simulation-compatible backend
    const simBackend = def.compatible_backends?.find(b => 
      b.includes('Simulator') || b.includes('Chatterbox')
    ) || 'SimulatorBackend';
    
    const instance: Machine = {
      id: generateId(),
      definition_id: def.id,
      name: `${def.name} (Sim)`,
      status: 'active',
      backend_type: simBackend,
      is_simulated: true,  // NEW FIELD
      fqn: def.fqn,
      asset_type: 'machine',
      // ... other fields
    };
    await machineRepository.create(instance);
  }
}
```

### Machine Adding UX Fix

**Current Problem**: The "Add Machine" dialog only shows backends, not frontend types.

**Target Flow**:

1. User selects **frontend type** (e.g., "Liquid Handler", "Plate Reader")
2. System shows **compatible backends** (e.g., "Hamilton STAR", "Opentrons OT-2", "Simulator")
3. User selects backend
4. If backend has configurable capabilities (e.g., 96-head, iSwap), show capability form
5. Machine instance is created

```
┌─────────────────────────────────────────────────────────────────┐
│  Add Machine                                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: Select Machine Type                                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🔘 Liquid Handler                                           ││
│  │ ○  Plate Reader                                             ││
│  │ ○  Heater Shaker                                            ││
│  │ ○  Centrifuge                                               ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Step 2: Select Backend                                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ○  Hamilton STAR                                            ││
│  │ ○  Opentrons OT-2                                           ││
│  │ 🔘 Simulator (default for browser mode)                      ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Step 3: Configure Capabilities (if applicable)                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ☑ 96-Channel Head                                           ││
│  │ ☑ iSwap (Plate Gripper)                                     ││
│  │ ☐ CO-RE Gripper                                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### "Simulated" Indicator Chip

Machines with simulation backends should display a visual indicator:

```html
<mat-chip color="accent" class="sim-chip">
  <mat-icon>computer</mat-icon>
  Simulated
</mat-chip>
```

This appears in:

- Machine list cards
- Machine selection step in Run Protocol
- Deck setup wizard
- REPL asset menu

---

## Infinite Consumables

### Consumable Types

- **Tips**: TipRack, TipCarrier contents
- **Plates**: Well plates used as disposables
- **Other**: Filter tips, seals, lids

### Default Behavior: Infinite (Auto-Replenish)

By default in browser/simulation mode, consumables auto-replenish:

```typescript
class ConsumableTracker {
  infiniteConsumables: boolean = true;  // Default ON in browser mode
  
  onTipDepletion(tipRack: TipRack): void {
    if (this.infiniteConsumables) {
      // Instantly replenish
      tipRack.tips = tipRack.tips.map(tip => ({ ...tip, has_tip: true }));
      this.notify('Tip rack auto-replenished (simulation mode)');
    }
  }
}
```

### Settings Toggle

Users can disable infinite consumables in Settings:

```
┌─────────────────────────────────────────────────────────────────┐
│  Simulation Settings                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ☑ Infinite Consumables (auto-replenish tips, plates)           │
│    When enabled, tips and plates automatically refill.           │
│    Disable to simulate realistic consumable depletion.           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Tutorial Integration

The guided tutorial should include a step that:

1. Points to the Settings panel
2. Explains the "Infinite Consumables" toggle
3. Notes: "For realistic simulations, you can turn this off to track actual consumable usage"

### UI Indicators

When infinite consumables is ON:

- Show "∞" symbol next to consumable counts in inventory
- Tip racks show "∞" instead of "96/96 tips"
- Notifications when auto-replenishment occurs (subtle toast)

---

## Demo Mode Removal Checklist

### Files to Remove/Modify

| File | Action | Notes |
|------|--------|-------|
| `services/demo.interceptor.ts` | Remove | No longer needed |
| `components/welcome-dialog/` | Modify | Remove demo toggle |
| `components/settings/` | Modify | Remove demo toggle |
| `services/onboarding.service.ts` | Modify | Remove demo state |
| `services/sqlite.service.ts` | Modify | Use default seeding |
| `store/app.store.ts` | Modify | Remove demoMode signal |

### Components to Update

- `WelcomeDialogComponent` - Remove demo mode toggle, keep tutorial start
- `SettingsComponent` - Remove demo mode toggle, keep "Reset to Defaults" button
- `ExitDemoDialogComponent` - Remove entirely (no longer applicable)

### Services to Update

- `ModeService` - Remove `isDemoMode()`, browser mode implies simulation
- `OnboardingService` - Remove demo mode state tracking
- `SqliteService` - `seedMockData()` → `seedDefaultAssets()`

---

## Reset to Defaults

Instead of "Exit Demo Mode", provide a "Reset to Defaults" option:

```typescript
async function resetToDefaults(): Promise<void> {
  // Clear all user-created assets
  await assetRepository.clearAll();
  
  // Re-seed defaults
  await seedDefaultResources();
  await seedDefaultMachines();
  
  // Show confirmation
  snackbar.show('Inventory reset to defaults');
}
```

This appears in Settings as a destructive action with confirmation dialog.

---

## Implementation Tasks

### Phase 1: Add Simulation Indicator

- [ ] Add `is_simulated` field to Machine model
- [x] Create "Simulated" chip component
- [x] Display chip in machine cards, selection step, deck setup
- [x] Unit tests

### Phase 2: Default Asset Seeding

- [ ] Refactor `seedMockData()` to `seedDefaultAssets()`
- [ ] Implement 1-of-each-type logic for resources
- [ ] Implement 1-of-each-type with sim backend for machines
- [ ] Integration tests

### Phase 3: Infinite Consumables

- [ ] Implement auto-replenish logic for tips
- [ ] Add logging/notification for replenishment events
- [ ] Skip depletion validation in browser mode
- [ ] Unit tests

### Phase 4: Demo Mode Removal

- [ ] Remove `DemoInterceptor`
- [ ] Update `WelcomeDialogComponent`
- [ ] Update `SettingsComponent`
- [ ] Remove `ExitDemoDialogComponent`
- [ ] Update `ModeService` and `OnboardingService`
- [ ] Regression tests

### Phase 5: Reset to Defaults

- [ ] Implement `resetToDefaults()` function
- [ ] Add confirmation dialog
- [ ] Add to Settings component
- [ ] E2E test

---

## Migration Notes

### Existing Users

Users with existing browser mode databases:

- On next load, if database is empty → seed defaults
- If database has data → leave as-is
- "Reset to Defaults" always available in Settings

### Tutorial Updates

Tutorial should:

- Mention that all resources/machines are simulated
- Explain that real hardware requires production mode
- Skip demo mode references

---

## Success Criteria

1. [ ] Browser mode starts with populated inventory (no empty state for new users)
2. [ ] All seeded machines show "Simulated" indicator
3. [ ] Consumables auto-replenish with notification
4. [ ] No demo mode toggle anywhere in UI
5. [ ] "Reset to Defaults" works correctly
6. [ ] Tutorial updated to reflect changes

---

## Related Documents

- [tutorial_demo_mode.md](./tutorial_demo_mode.md) - Original demo mode implementation
- [browser_mode_issues.md](./browser_mode_issues.md) - Browser mode fixes
- [modes_and_deployment.md](./modes_and_deployment.md) - Mode architecture
