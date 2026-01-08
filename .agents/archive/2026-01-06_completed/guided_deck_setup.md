# Enhanced Guided Deck Setup - Implementation Plan

**Priority**: P2 (High)
**Difficulty**: XL (Extra Large - 3+ days)
**Owner**: Full Stack
**Created**: 2026-01-01
**Status**: Completed ✅ (2026-01-01)

---

## Executive Summary

The Enhanced Guided Deck Setup feature provides an interactive step-by-step wizard that guides users through physical deck configuration before protocol execution. This replaces the current abstract placement model with a concrete, slot-based system that mirrors real laboratory workflows.

**Key Deliverables**:

1. Semantic deck model with Rails → Carriers → Slots hierarchy
2. Slot-based resource placement (replacing absolute X/Y coordinates)
3. Interactive step-by-step wizard UX
4. Carrier inference engine for protocol requirements
5. Z-axis ordering heuristics for placement sequence

---

## Current State Analysis

### Existing Implementation

| Component | File | Status |
|-----------|------|--------|
| `DeckViewComponent` | `shared/components/deck-view/deck-view.component.ts` | ⚠️ Partial - uses absolute X/Y |
| `DeckGeneratorService` | `features/run-protocol/services/deck-generator.service.ts` | ⚠️ Hardcoded Hamilton STAR |
| `PlrResource` model | `core/models/plr.models.ts` | ✅ Flexible but lacks slots |
| `DeckLayout` model | `features/run-protocol/models/deck-layout.models.ts` | ✅ Has `DeckSlot` interface |

### Current Gaps

1. **Rails**: `getRails()` uses `$index * 22.5mm` approximation instead of hardware-spec positions
2. **Carriers**: Styled with CSS but not modeled as physical mounting bars with slots
3. **Slots**: No distinct slot entities - labware uses absolute coordinates
4. **Placement**: Resources placed by X/Y offset, not into named slots
5. **Inference**: No automatic carrier calculation based on protocol requirements

---

## Architecture Design

### Phase 1: Semantic Deck Model (L - 1-2 days)

#### 1.1 Enhanced Type Definitions

Create new interfaces in `deck-layout.models.ts`:

```typescript
// Rail definition from hardware specs
export interface DeckRail {
  index: number;           // 0-29 for Hamilton STAR 30-rail
  xPosition: number;       // mm from deck origin
  width: number;           // Rail width in mm (22.5mm standard)
  compatibleCarrierTypes: string[];  // Carrier FQNs that fit
}

// Carrier with explicit slots
export interface DeckCarrier {
  id: string;              // Unique identifier
  fqn: string;             // PLR FQN (e.g., "pylabrobot.resources.ml_star.plt_car_l5ac")
  name: string;            // Display name
  type: CarrierType;       // 'plate' | 'tip' | 'trough' | 'tube' | 'mfx'
  railPosition: number;    // Starting rail index
  railSpan: number;        // Number of rails occupied (1-3 typically)
  slots: CarrierSlot[];    // Ordered slots on carrier
  dimensions: {
    width: number;         // mm
    height: number;        // mm  
    depth: number;         // mm
  };
}

// Individual slot on a carrier
export interface CarrierSlot {
  id: string;                    // e.g., "plt_car_l5ac_slot_1"
  index: number;                 // 0-based position on carrier
  name: string;                  // Display name (e.g., "Position 1")
  compatibleResourceTypes: string[];  // PLR resource FQNs/categories
  occupied: boolean;
  resource?: PlrResource | null;
  position: {
    x: number;                   // Relative to carrier origin
    y: number;
    z: number;
  };
  dimensions: {
    width: number;
    height: number;
  };
}

// Complete deck configuration
export interface DeckConfiguration {
  deckType: string;              // PLR deck FQN
  deckName: string;              // Display name
  rails: DeckRail[];             // Hardware-defined rails
  carriers: DeckCarrier[];       // Placed carriers
  dimensions: {
    width: number;               // mm
    height: number;
    depth: number;
  };
  numRails: number;
}
```

#### 1.2 Deck Definition Catalog Integration

Leverage existing PLR deck definitions from `praxis.db`:

```typescript
// DeckCatalogService - fetch deck specs from SqliteService/API
interface DeckDefinitionSpec {
  fqn: string;
  name: string;
  manufacturer: string;
  numRails: number;
  railSpacing: number;           // mm between rail centers
  railPositions?: number[];      // Exact X positions if available
  compatibleCarriers: string[];  // Carrier FQNs
  dimensions: { width: number; height: number; depth: number };
}
```

#### 1.3 Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `models/deck-layout.models.ts` | **Extend** | Add Rail, Carrier, Slot interfaces |
| `services/deck-catalog.service.ts` | **Create** | Fetch deck/carrier specs from backend/SqliteService |
| `models/plr.models.ts` | **Extend** | Add optional `slot_id` to PlrResource |

---

### Phase 2: Slot-Based Rendering (L - 1-2 days)

#### 2.1 Update DeckViewComponent

Replace absolute positioning with slot-aware rendering:

```typescript
// Current: absolute positioning
<div class="resource" [style.left.px]="scaleX(res.location.x)">

// Target: slot-based positioning  
<div class="carrier" *ngFor="let carrier of carriers()">
  <div class="slot" 
       *ngFor="let slot of carrier.slots"
       [class.empty]="!slot.occupied"
       [class.compatible]="isSlotCompatible(slot, draggedResource)"
       [class.occupied]="slot.occupied">
    @if (slot.resource) {
      <div class="slot-resource">{{ slot.resource.name }}</div>
    } @else {
      <div class="empty-slot">{{ slot.name }}</div>
    }
  </div>
</div>
```

#### 2.2 Rails Rendering from Deck Spec

```typescript
// DeckViewComponent
private deckConfig = signal<DeckConfiguration | null>(null);

getRails(): DeckRail[] {
  const config = this.deckConfig();
  if (!config) return [];
  
  // Use hardware-spec positions, not approximation
  return config.rails;
}

// Template
<div class="rail" 
     *ngFor="let rail of getRails()"
     [style.left.px]="scaleX(rail.xPosition)"
     [style.width.px]="scaleX(rail.width)">
  <span class="rail-label">{{ rail.index }}</span>
</div>
```

#### 2.3 Carrier Slot Visualization

```scss
// deck-view.component.scss additions
.carrier {
  position: absolute;
  background: var(--plr-carrier-bg);
  border: 2px solid var(--plr-carrier-border);
  border-radius: 4px;
  
  .slot {
    position: relative;
    border: 1px dashed var(--plr-slot-border);
    margin: 4px;
    min-height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &.empty {
      background: var(--plr-slot-empty-bg);
      opacity: 0.6;
      
      &::after {
        content: 'Empty';
        color: var(--sys-text-secondary);
        font-size: 0.75rem;
      }
    }
    
    &.occupied {
      border-style: solid;
      border-color: var(--plr-slot-occupied-border);
    }
    
    &.compatible {
      border-color: var(--sys-success);
      background: rgba(var(--sys-success-rgb), 0.1);
    }
    
    &.incompatible {
      border-color: var(--sys-error);
      opacity: 0.5;
    }
  }
}
```

#### 2.4 Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `deck-view.component.ts` | **Major Refactor** | Slot-based rendering |
| `deck-view.component.scss` | **Extend** | Slot/carrier styles |
| `deck-generator.service.ts` | **Refactor** | Generate `DeckConfiguration` |

---

### Phase 3: Carrier Inference Engine (L - 1-2 days)

#### 3.1 Protocol Requirements Analysis

```typescript
// CarrierInferenceService
@Injectable({ providedIn: 'root' })
export class CarrierInferenceService {
  
  /**
   * Analyze protocol requirements and calculate minimum carriers needed.
   */
  inferRequiredCarriers(
    protocol: ProtocolDefinition,
    availableCarriers: DeckCarrier[]
  ): CarrierRequirement[] {
    const requirements: CarrierRequirement[] = [];
    
    // Group assets by type
    const assetsByType = this.groupAssetsByType(protocol.assets);
    
    // For each type, calculate minimum carriers
    for (const [type, assets] of Object.entries(assetsByType)) {
      const compatibleCarriers = availableCarriers.filter(
        c => this.isCarrierCompatible(c, type)
      );
      
      if (compatibleCarriers.length === 0) {
        throw new Error(`No compatible carriers for ${type}`);
      }
      
      // Calculate minimum carriers needed
      const slotsNeeded = assets.length;
      const bestCarrier = this.findOptimalCarrier(compatibleCarriers, slotsNeeded);
      const carriersNeeded = Math.ceil(slotsNeeded / bestCarrier.slots.length);
      
      requirements.push({
        resourceType: type,
        count: carriersNeeded,
        carrierFqn: bestCarrier.fqn,
        slotsNeeded,
        slotsAvailable: bestCarrier.slots.length * carriersNeeded
      });
    }
    
    return requirements;
  }
  
  /**
   * Auto-assign resources to optimal slots on carriers.
   */
  assignResourcesToSlots(
    resources: PlrResource[],
    carriers: DeckCarrier[]
  ): SlotAssignment[] {
    const assignments: SlotAssignment[] = [];
    const slotPool = carriers.flatMap(c => c.slots.filter(s => !s.occupied));
    
    for (const resource of resources) {
      const compatibleSlots = slotPool.filter(
        s => this.isSlotCompatibleWithResource(s, resource)
      );
      
      if (compatibleSlots.length === 0) {
        throw new Error(`No compatible slot for ${resource.name}`);
      }
      
      // Use first available compatible slot
      const slot = compatibleSlots[0];
      slot.occupied = true;
      slot.resource = resource;
      
      assignments.push({
        resource,
        slot,
        carrier: carriers.find(c => c.slots.includes(slot))!
      });
    }
    
    return assignments;
  }
}
```

#### 3.2 Slot Compatibility Matrix

```typescript
// Compatibility rules based on PLR resource/carrier types
const SLOT_COMPATIBILITY: Record<string, string[]> = {
  'PlateCarrier': ['Plate', 'Lid', 'PlateAdapter'],
  'TipCarrier': ['TipRack', 'NestedTipRack'],
  'TroughCarrier': ['Trough', 'Reservoir'],
  'TubeCarrier': ['TubeRack', 'Tube'],
  'MFXCarrier': ['Plate', 'TipRack', 'Trough'],  // Multi-function
};
```

#### 3.3 Files to Create

| File | Action | Description |
|------|--------|-------------|
| `services/carrier-inference.service.ts` | **Create** | Carrier calculation logic |
| `models/carrier-inference.models.ts` | **Create** | Inference result types |

---

### Phase 4: Guided Setup Wizard (XL - 2-3 days)

#### 4.1 Wizard Component Structure

```
guided-deck-setup/
├── guided-deck-setup.component.ts       # Main wizard container
├── guided-deck-setup.component.html
├── guided-deck-setup.component.scss
├── steps/
│   ├── carrier-placement-step.component.ts    # "Slide carriers into rails"
│   ├── resource-placement-step.component.ts   # "Place X into slot Y"
│   ├── verification-step.component.ts         # "Confirm configuration"
│   └── step-indicator.component.ts            # Progress indicator
├── models/
│   └── wizard-state.models.ts
└── services/
    └── wizard-state.service.ts
```

#### 4.2 Wizard Flow

```
┌────────────────────────────────────────────────────────────┐
│                    GUIDED DECK SETUP                       │
├────────────────────────────────────────────────────────────┤
│  Step 1: Carrier Placement                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  "Slide the following carriers into the deck:"      │  │
│  │                                                      │  │
│  │  ☐ Plate Carrier (PLT_CAR_L5AC) → Rail 5           │  │
│  │  ☐ Tip Carrier (TIP_CAR_480) → Rail 15             │  │
│  │  ☐ Trough Carrier (RGT_CAR_3R) → Rail 25           │  │
│  │                                                      │  │
│  │  [Deck Visualization with highlighted rails]        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                           [Next →]         │
├────────────────────────────────────────────────────────────┤
│  Step 2: Resource Placement (iterative)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  "Place the following resources:"                   │  │
│  │                                                      │  │
│  │  1. sample_plate → Plate Carrier, Slot 1           │  │
│  │  2. tip_rack_1 → Tip Carrier, Slot 1               │  │
│  │  3. reservoir → Trough Carrier, Slot 1             │  │
│  │                                                      │  │
│  │  [Deck visualization with slot highlighting]        │  │
│  └──────────────────────────────────────────────────────┘  │
│                               [← Back]  [Skip]  [Next →]   │
├────────────────────────────────────────────────────────────┤
│  Step 3: Verification                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  "Review your deck configuration"                   │  │
│  │                                                      │  │
│  │  [Full deck visualization with all placements]      │  │
│  │                                                      │  │
│  │  ⚠️ Are you sure the physical deck matches this    │  │
│  │     configuration?                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                               [← Back]  [Confirm ✓]        │
└────────────────────────────────────────────────────────────┘
```

#### 4.3 Step Components

**CarrierPlacementStepComponent**:

```typescript
@Component({
  selector: 'app-carrier-placement-step',
  template: `
    <div class="step-content">
      <h3>Step 1: Place Carriers on Deck</h3>
      <p class="instruction">Slide the following carriers into the indicated rails:</p>
      
      <div class="carrier-list">
        @for (req of carrierRequirements(); track req.carrierFqn) {
          <div class="carrier-item" [class.completed]="req.placed">
            <mat-checkbox [(ngModel)]="req.placed">
              <span class="carrier-name">{{ req.displayName }}</span>
              <span class="carrier-location">→ Rail {{ req.railPosition }}</span>
            </mat-checkbox>
          </div>
        }
      </div>
      
      <app-deck-view 
        [resource]="deckResource()" 
        [highlightRails]="pendingRails()"
        [showCarrierGhosts]="true">
      </app-deck-view>
    </div>
  `
})
export class CarrierPlacementStepComponent {
  carrierRequirements = input.required<CarrierRequirement[]>();
  deckResource = input.required<PlrResource>();
  
  pendingRails = computed(() => 
    this.carrierRequirements()
      .filter(r => !r.placed)
      .map(r => r.railPosition)
  );
  
  allPlaced = computed(() => 
    this.carrierRequirements().every(r => r.placed)
  );
}
```

**ResourcePlacementStepComponent**:

```typescript
@Component({
  selector: 'app-resource-placement-step',
  template: `
    <div class="step-content">
      <h3>Step 2: Place Resources in Slots</h3>
      
      @for (assignment of assignments(); track assignment.resource.name; let i = $index) {
        <div class="placement-instruction" 
             [class.current]="i === currentIndex()"
             [class.completed]="assignment.placed">
          <span class="index">{{ i + 1 }}.</span>
          <span class="resource-name">{{ assignment.resource.name }}</span>
          <mat-icon>arrow_forward</mat-icon>
          <span class="slot-location">
            {{ assignment.carrier.name }}, {{ assignment.slot.name }}
          </span>
          @if (assignment.placed) {
            <mat-icon class="check">check_circle</mat-icon>
          }
        </div>
      }
      
      <app-deck-view 
        [resource]="deckResource()"
        [highlightSlot]="currentSlot()"
        [highlightResource]="currentResource()">
      </app-deck-view>
      
      <div class="z-order-hint" *ngIf="showZOrderHint()">
        <mat-icon>info</mat-icon>
        <span>Place items in this order for optimal access (lowest first)</span>
      </div>
    </div>
  `
})
export class ResourcePlacementStepComponent {
  assignments = input.required<SlotAssignment[]>();
  
  currentIndex = signal(0);
  
  currentSlot = computed(() => 
    this.assignments()[this.currentIndex()]?.slot
  );
}
```

#### 4.4 Z-Axis Ordering Heuristic

```typescript
/**
 * Sort resources by Z-axis for optimal placement order.
 * Lower Z resources should be placed first (they're at the bottom).
 */
sortByZAxis(assignments: SlotAssignment[]): SlotAssignment[] {
  return [...assignments].sort((a, b) => {
    // Get Z position from resource or slot
    const zA = a.resource.location?.z ?? a.slot.position.z;
    const zB = b.resource.location?.z ?? b.slot.position.z;
    
    // Lower Z first (bottom of stack)
    return zA - zB;
  });
}

/**
 * For complex protocols, detect stacking and provide order hints.
 */
detectStackingOrder(assignments: SlotAssignment[]): StackingHint[] {
  const hints: StackingHint[] = [];
  
  // Group by slot
  const bySlot = this.groupBySlot(assignments);
  
  for (const [slotId, items] of Object.entries(bySlot)) {
    if (items.length > 1) {
      // Multiple items in same slot = stacking
      const sorted = this.sortByZAxis(items);
      hints.push({
        slotId,
        order: sorted.map(a => a.resource.name),
        reason: 'Stacked resources - place bottom first'
      });
    }
  }
  
  return hints;
}
```

#### 4.5 Skip Confirmation

```typescript
// VerificationStepComponent
async onSkip(): Promise<boolean> {
  const result = await this.dialog.open(ConfirmDialogComponent, {
    data: {
      title: 'Skip Deck Setup?',
      message: 'Are you sure the physical deck is properly configured? ' +
               'Incorrect setup may cause protocol execution errors.',
      confirmText: 'Yes, Skip Setup',
      cancelText: 'Go Back'
    }
  }).afterClosed().toPromise();
  
  return result === true;
}
```

#### 4.6 Files to Create

| File | Action | Description |
|------|--------|-------------|
| `features/run-protocol/components/guided-deck-setup/` | **Create** | New component directory |
| `guided-deck-setup.component.ts` | **Create** | Main wizard |
| `steps/carrier-placement-step.component.ts` | **Create** | Carrier placement |
| `steps/resource-placement-step.component.ts` | **Create** | Resource placement |
| `steps/verification-step.component.ts` | **Create** | Final confirmation |
| `services/wizard-state.service.ts` | **Create** | Wizard state management |

---

### Phase 5: Integration (M - 4-8 hours)

#### 5.1 Run Protocol Flow Integration

Insert Guided Deck Setup as a new step in the protocol execution wizard:

```
Current Flow:
1. Select Protocol → 2. Configure Parameters → 3. Select Assets → 4. Review & Run

New Flow:
1. Select Protocol → 2. Configure Parameters → 3. Select Assets → 
   4. Deck Setup (NEW) → 5. Review & Run
```

#### 5.2 State Persistence

```typescript
// Persist deck configuration to LocalStorage for page refresh recovery
@Injectable({ providedIn: 'root' })
export class DeckSetupStateService {
  private readonly STORAGE_KEY = 'praxis_deck_setup_state';
  
  saveState(protocolId: string, config: DeckConfiguration): void {
    const state = {
      protocolId,
      config,
      timestamp: Date.now()
    };
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(state));
  }
  
  loadState(protocolId: string): DeckConfiguration | null {
    const raw = localStorage.getItem(this.STORAGE_KEY);
    if (!raw) return null;
    
    const state = JSON.parse(raw);
    
    // Only restore if same protocol and not stale (< 24h)
    if (state.protocolId !== protocolId) return null;
    if (Date.now() - state.timestamp > 24 * 60 * 60 * 1000) return null;
    
    return state.config;
  }
}
```

#### 5.3 Files to Modify

| File | Action | Description |
|------|--------|-------------|
| `run-protocol.component.ts` | **Modify** | Add Deck Setup step |
| `run-protocol.component.html` | **Modify** | Add step to stepper |

---

## Implementation Order

| Phase | Effort | Priority | Dependencies | Target |
|-------|--------|----------|--------------|--------|
| 1. Semantic Deck Model | L | Immediate | None | Week 1 |
| 2. Slot-Based Rendering | L | Immediate | Phase 1 | Week 1-2 |
| 3. Carrier Inference | L | Short-term | Phase 1 | Week 2 |
| 4. Guided Setup Wizard | XL | Short-term | Phases 1-3 | Week 2-3 |
| 5. Integration | M | Short-term | Phase 4 | Week 3 |

**Total Estimated Effort**: XL (5-8 days)

---

## Success Criteria

1. [x] Rails render at hardware-spec X positions (using `DeckCatalogService`)
2. [x] Carriers show distinct slots with empty/occupied states
3. [x] Resources snap into slots, not absolute X/Y positions
4. [x] Carrier inference correctly calculates minimum carriers for protocol
5. [x] Wizard guides user through carrier → resource placement flow
6. [x] Z-axis ordering provides correct placement sequence for stacked items
7. [x] Skip confirmation prevents accidental bypassing
8. [x] State persists across page refresh (LocalStorage)

---

## Related Documents

- [deck_view.md](./deck_view.md) - Parent backlog (to be merged)
- [asset_management.md](./asset_management.md) - Deck Setup debugging context
- [protocol_execution.md](./protocol_execution.md) - Wizard state persistence

---

## Testing Strategy

### Unit Tests

- `CarrierInferenceService.inferRequiredCarriers()` - various protocol configurations
- `CarrierInferenceService.assignResourcesToSlots()` - slot compatibility
- Z-axis sorting algorithm

### E2E Tests

- Complete wizard flow from protocol selection to deck verification
- Skip confirmation dialog
- State restoration after page refresh

---

*This plan was completed on 2026-01-01 with 43 passing unit tests.*
