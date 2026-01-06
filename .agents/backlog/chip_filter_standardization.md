# Chip-Based Filter Standardization

**Priority**: P2 (High)
**Owner**: Frontend
**Created**: 2026-01-05
**Status**: In Progress
**Last Updated**: 2026-01-05

---

## Overview

Standardize all dropdown/filter controls across the application to use a unified **chip-based UI pattern**. Chips should be:

- Clickable to reveal selection menus
- Highlighted when active (filter applied)
- Disabled with shake animation + message when selecting would yield no results
- Consistent across all filter surfaces (Assets, REPL, Execution Monitor, etc.)

---

## Design Specification

### Chip States

| State | Appearance | Behavior |
|-------|------------|----------|
| **Inactive** | Outlined, muted color | Click reveals dropdown menu |
| **Active** | Filled/highlighted | Shows selected value, click reveals menu |
| **Disabled** | Grayed out, dashed border | Click triggers shake animation + tooltip message |

### Interaction Pattern

```
┌──────────────────────────────────────────────────────────┐
│ [Status ▾] [Brand ▾] [Count ▾] [Type ▾] [Volume ▾]      │  ← Sort controls separate
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ Sort: [Name ▾] [▲ Asc / ▼ Desc]                         │
└──────────────────────────────────────────────────────────┘
```

### Disabled Chip Behavior

When a chip selection would render no results:

1. Chip appears grayed out with dashed border
2. On click/tap: subtle horizontal shake animation (~200ms)
3. Tooltip/snackbar: "No results match this filter combination"
4. Chip remains clickable but selection menu shows "(0 results)" next to disabled options

---

## Resource Filter Chips

For the Resource Inventory, implement the following filter chips:

| Chip | Source | Notes |
|------|--------|-------|
| **Status** | `asset.status` | Active, Maintenance, Discarded |
| **Brand** | `definition.vendor` | Extracted from PLR metadata |
| **Count** | `definition.items_x * items_y` | e.g., 96, 384, 24 (for plates) |
| **Type** | `definition.plr_category` | Consumable, Container, etc. |
| **Volume** | Computed | Per-item for plates/tips, total for troughs |

### Volume Computation Logic

```typescript
function getDisplayVolume(resource: Resource): string {
  const def = resource.definition;
  
  if (def.is_itemized) {
    // For plates, tip racks: show per-item volume
    const perItem = def.max_volume / (def.items_x * def.items_y);
    return formatVolume(perItem) + '/well';
  } else {
    // For troughs, tubes: show total volume
    return formatVolume(def.max_volume);
  }
}
```

---

## Machine Registry Filter Chips

| Chip | Source | Notes |
|------|--------|-------|
| **Category** | `definition.machine_category` | LiquidHandler, PlateReader, etc. |
| **Simulated** | `instance.backend_type` | Show "Sim" chip for simulation backends |
| **Status** | `instance.status` | Connected, Disconnected, Error |
| **Backend** | `definition.compatible_backends` | STAR, OT2, Chatterbox, etc. |

---

## Variant Alignment Detection

### Problem

For resources like plate carriers, there are many variants sharing a common base:

- `PLT_CAR_L5_A00`
- `PLT_CAR_L5_HHS`
- `PLT_CAR_L5_MD`

Chips already handle filtering (Brand, Count, Type, Volume). The goal is to **subtly indicate** when variants are aligned (share a common base pattern) without cluttering the UI.

### Solution: Subtle Tooltip Indicator

When resources share a common base pattern, show a subtle visual indicator:

```
┌─────────────────────────────────────────────────────────────────┐
│ PLT_CAR_L5_A00                                    [●] 3 variants│
└─────────────────────────────────────────────────────────────────┘
```

Hovering on the `[●] 3 variants` indicator shows tooltip:

```
Related variants:
• PLT_CAR_L5_HHS
• PLT_CAR_L5_MD
• PLT_CAR_L5_AC
```

### Algorithm

```typescript
function detectAlignedVariants(names: string[]): Map<string, string[]> {
  const variantGroups = new Map<string, string[]>();
  
  for (const name of names) {
    const parts = name.split('_');
    
    // Try progressively shorter prefixes
    for (let i = parts.length - 1; i >= 2; i--) {
      const prefix = parts.slice(0, i).join('_');
      
      // Find other names with same prefix
      const siblings = names.filter(n => 
        n !== name && n.startsWith(prefix + '_')
      );
      
      if (siblings.length > 0) {
        variantGroups.set(name, siblings);
        break;
      }
    }
  }
  
  return variantGroups;
}
```

### Display Behavior

- **Full name always visible**: Show complete name (e.g., `PLT_CAR_L5_A00`)
- **Variant indicator**: Small dot/badge if item has aligned variants
- **Tooltip on hover**: Lists related variants
- **Asset detail view**: Show full variant list prominently

---

## Implementation Tasks

### Phase 1: Core Filter Chip Component

- [ ] Create `FilterChipComponent` with states (inactive, active, disabled)
- [ ] Implement shake animation for disabled clicks
- [ ] Implement tooltip/snackbar for disabled message
- [ ] Add menu integration (mat-menu or custom dropdown)
- [ ] Unit tests for all states

### Phase 2: Result Count Logic

- [ ] Create `FilterResultService` to pre-compute option availability
- [ ] Integrate with data sources (SqliteService, AssetService)
- [ ] Implement "(0 results)" disabled state
- [ ] Unit tests for result count computation

### Phase 3: Resource Inventory Integration

- [ ] Replace current `ResourceFiltersComponent` with chip-based version
- [ ] Implement all 5 resource filter chips
- [ ] Implement volume computation logic
- [ ] Implement unique name parsing
- [ ] Integration tests

### Phase 4: Machine Registry Integration

- [x] Update `MachineDefinitionAccordionComponent` filters
- [x] Add "Simulated" chip indicator
- [x] Integration tests (Manual verification complete)

### Phase 5: Execution Monitor Integration

- [x] Update `RunFiltersComponent` to use chip pattern (Existing implementation verified)
- [x] Ensure consistency with other surfaces
- [x] Integration tests (Manual verification complete)

### Phase 6: REPL/JupyterLite Asset Menu

- [x] Add filter chips to asset sidebar in JupyterLite
- [x] Share filter component with Asset Management (Used styling/logic patterns)
- [x] Integration tests (Manual verification complete)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `shared/components/filter-chip/` | Create | New chip component |
| `shared/services/filter-result.service.ts` | Create | Result count computation |
| `features/assets/components/resource-filters/` | Modify | Use new chip component |
| `features/assets/components/machine-filters/` | Modify | Use new chip component |
| `features/execution-monitor/components/run-filters/` | Modify | Use new chip component |
| `features/repl/components/asset-sidebar/` | Modify | Add chip filters |

---

## Success Criteria

1. [ ] All filter surfaces use consistent chip UI
2. [ ] Chips show (0 results) and disable when appropriate
3. [ ] Shake animation triggers on disabled chip click
4. [ ] Volume displays correctly (per-item vs total)
5. [ ] Unique name parsing reduces visual clutter
6. [ ] Sort controls are visually separated from filters
7. [ ] Works in browser mode with SqliteService

---

## Related Documents

- [ui_visual_tweaks.md](./ui_visual_tweaks.md) - General UI polish
- [asset_management.md](./asset_management.md) - Asset views
- [execution_monitor.md](./execution_monitor.md) - Run history filters
