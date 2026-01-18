import { Component, ChangeDetectionStrategy, Input, computed, signal, inject, output, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DragDropModule, CdkDragDrop, CdkDrag, CdkDropList } from '@angular/cdk/drag-drop';
import { PlrResource, PlrState, PlrResourceDetails } from '@core/models/plr.models';
import { DeckCatalogService } from '@features/run-protocol/services/deck-catalog.service';
import { DeckConstraintService, ValidationResult } from '@features/run-protocol/services/deck-constraint.service';
import { DeckRail, DeckSlotSpec } from '@features/run-protocol/models/deck-layout.models';


/** Tooltip position state */
interface TooltipState {
  visible: boolean;
  x: number;
  y: number;
  resource: PlrResource | null;
  parent: PlrResource | null;
  index?: number;
}

@Component({
  selector: 'app-deck-view',
  standalone: true,
  imports: [CommonModule, DragDropModule],
  template: `
    <div class="deck-container" [style.width.px]="containerWidth()" [style.height.px]="containerHeight()">
      <!-- Background Rails (rail-based decks like Hamilton) -->
      @if (resource()?.num_rails) {
        <div class="rails-container absolute inset-0 pointer-events-none">
          @for (rail of getRails(); track rail.index) {
            <div class="rail-line"
              [style.left.px]="scaleLeft(rail.xPosition)"
            [attr.data-rail-index]="rail.index"></div>
          }
        </div>
      }
      <!-- Slot boundaries (slot-based decks like OT-2) -->
      @if (isSlotBasedDeck()) {
        <div class="slots-container absolute inset-0 pointer-events-none">
          @for (slot of getSlots(); track slot.slotNumber) {
            <div class="slot-boundary"
              [style.left.px]="scaleLeft(slot.position.x)"
              [style.bottom.px]="scaleBottom(slot.position.y)"
              [style.width.px]="scaleDim(slot.dimensions.width)"
              [style.height.px]="scaleDim(slot.dimensions.height)"
              [class.slot-trash]="slot.slotType === 'trash'"
              [class.slot-module]="slot.slotType === 'module'"
              [attr.data-slot-number]="slot.slotNumber">
              <span class="slot-label">{{ slot.label }}</span>
            </div>
          }
        </div>
      }
    
      <!-- Render the root resource and its children recursively -->
      <ng-container *ngTemplateOutlet="resourceTpl; context: { $implicit: resource(), parent: null, index: -1 }"></ng-container>
    
      <!-- Hover Tooltip -->
      @if (tooltip().visible && tooltip().resource) {
        <div class="resource-tooltip"
          [style.left.px]="tooltip().x + 12"
          [style.top.px]="tooltip().y + 12">
          <div class="tooltip-header">{{ tooltip().resource!.name }}</div>
          <div class="tooltip-type">{{ tooltip().resource!.type }}</div>
          <div class="tooltip-dims">{{ tooltip().resource!.size_x | number:'1.1-1' }} × {{ tooltip().resource!.size_y | number:'1.1-1' }} mm</div>
          @if (hasLiquid(tooltip().resource!, tooltip().parent, tooltip().index)) {
            <div class="tooltip-volume">Volume: {{ getVolume(tooltip().resource!, tooltip().parent, tooltip().index) | number:'1.0-1' }} µL</div>
          }
          @if (hasTip(tooltip().resource!, tooltip().parent, tooltip().index)) {
            <div class="tooltip-tip">Tip: Present</div>
          }
        </div>
      }
    </div>
    
    <ng-template #resourceTpl let-res let-parent="parent" let-index="index">
      <div class="resource-node"
        [title]="res.name"
        cdkDropList
        [cdkDropListDisabled]="!isGhost(res)"
        (cdkDropListDropped)="onDrop($event)"
        (mouseenter)="onResourceHover($event, res, parent, index)"
        (mouseleave)="onResourceLeave()"
        (click)="onResourceClick($event, res, parent, index)"
        [attr.data-type]="res.type"
        [style.left.px]="scaleLeft(res.location.x)"
        [style.bottom.px]="scaleBottom(res.location.y)"
        [style.width.px]="scaleDim(res.size_x)"
        [style.height.px]="scaleDim(res.size_y)"
        [class.is-root]="res === resource()"
        [class.is-ghost]="isGhost(res)"
        [class.is-well]="isWellOrSpot(res.type)"
        [class.type-plate]="isPlateType(res.type)"
        [class.type-tiprack]="isTipRackType(res.type)"
        [class.type-trough]="isTroughType(res.type)"
        [class.type-carrier]="isCarrierType(res.type)"
        [class.type-trash]="res.type === 'Trash'"
        [class.type-lid]="isLidType(res.type)"
        [class.type-petridish]="isPetriDishType(res.type)"
        [class.type-tube]="isTubeType(res.type)"
        [class.type-adapter]="isPlateAdapterType(res.type)"
        [class.has-liquid]="hasLiquid(res, parent, index)"
        [class.has-tip]="isWellOrSpot(res.type) && hasTip(res, parent, index)"
        [class.empty]="isWellOrSpot(res.type) && isEmpty(res, parent, index)"
        [class.is-selected]="selectedResource() === res"
        [style.background]="hasLiquid(res, parent, index) ? getLiquidStyle(res, parent, index) : getCustomColor(res)"
        [style.background-color]="!hasLiquid(res, parent, index) ? getCustomColor(res) : null">
    
        <!-- Label for significant resources -->
        @if (shouldShowLabel(res)) {
          <div class="resource-label">
            {{ res.name }}
          </div>
        }
    
        <!-- Recursively render children -->
        @for (child of res.children; track child.name; let i = $index) {
          <ng-container *ngTemplateOutlet="resourceTpl; context: { $implicit: child, parent: res, index: i }"></ng-container>
        }
      </div>
    </ng-template>
    `,
  styles: [`
    /* =========================================
       PLR-Style Deck Visualizer Theme
       Matches PyLabRobot's visualizer aesthetic
       ========================================= */

    :host {
      display: block;
      overflow: auto;
      /* PLR-style dark background */
      background: var(--plr-bg, var(--mat-sys-surface-container-low));
      padding: 20px;
    }

    /* Light theme overrides */
    :host-context(.light-theme) {
      --plr-bg: #e8eef4;
      --plr-deck-bg: #f8fafc;
      --plr-deck-border: #94a3b8;
      --plr-rail: rgba(0, 0, 0, 0.08);
      --plr-label: #475569;
      --plr-hover-glow: rgba(237, 122, 155, 0.4);
    }

    /* Dark theme (default) */
    :host {
      --plr-bg: var(--mat-sys-surface-container-low);
      --plr-deck-bg: var(--mat-sys-surface-container, #2d2d44);
      --plr-deck-border: var(--mat-sys-outline-variant, rgba(255,255,255,0.1));
      --plr-rail: rgba(255, 255, 255, 0.06);
      --plr-label: rgba(255, 255, 255, 0.7);
      --plr-hover-glow: rgba(237, 122, 155, 0.5);
    }

    .deck-container {
      position: relative;
      background: var(--plr-deck-bg);
      border: 2px solid var(--plr-deck-border);
      border-radius: 4px;
      box-shadow:
        0 4px 20px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
      transform-origin: top left;
    }

    .resource-node {
      position: absolute;
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
      box-sizing: border-box;
      transition: all 0.15s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      border-radius: 2px;
    }

    .resource-node:hover:not(.is-root):not(.is-well) {
      z-index: 10;
      box-shadow:
        0 0 0 2px var(--plr-hover-glow),
        0 4px 12px rgba(0, 0, 0, 0.3);
      transform: translateY(-1px);
      cursor: pointer;
    }

    .resource-node.is-selected {
      z-index: 15;
      box-shadow:
        0 0 0 3px var(--sys-primary, #6366f1),
        0 4px 16px rgba(99, 102, 241, 0.4);
    }

    /* Tooltip styles */
    .resource-tooltip {
      position: fixed;
      z-index: 1000;
      background: var(--sys-surface-container-highest, #1e1e2e);
      border: 1px solid var(--sys-outline-variant, #444);
      border-radius: 8px;
      padding: 8px 12px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
      pointer-events: none;
      max-width: 200px;
    }

    .tooltip-header {
      font-weight: 600;
      font-size: 12px;
      color: var(--sys-on-surface, #fff);
      margin-bottom: 2px;
    }

    .tooltip-type {
      font-size: 10px;
      color: var(--sys-on-surface-variant, #aaa);
      margin-bottom: 4px;
    }

    .tooltip-dims,
    .tooltip-volume,
    .tooltip-tip {
      font-size: 10px;
      color: var(--sys-on-surface-variant, #ccc);
    }

    .tooltip-volume {
      color: var(--sys-tertiary, #60a5fa);
    }

    .tooltip-tip {
      color: var(--sys-secondary, #fbbf24);
    }

    .is-root {
      position: relative;
      left: 0 !important;
      top: 0 !important;
      border: none;
      background: transparent;
      border-radius: 0;
    }

    .resource-label {
      font-size: 11px;
      font-weight: 500;
      color: var(--plr-label);
      pointer-events: none;
      text-align: center;
      padding: 2px 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
      text-shadow: none;
      background: rgba(0, 0, 0, 0.4);
      border-radius: 2px;
      letter-spacing: 0.3px;
    }

    /* Rails - PLR style vertical guides */
    .rails-container {
      z-index: 0;
    }

    .rail-line {
      position: absolute;
      top: 30px;
      bottom: 30px;
      width: 3px;
    }

    /* Slots - grid-style positioning for OT-2 style decks */
    .slots-container {
      z-index: 0;
    }

    .slot-boundary {
      position: absolute;
      border: 2px dashed var(--plr-slot-border, rgba(255, 255, 255, 0.25));
      border-radius: 4px;
      background: var(--plr-slot-bg, rgba(255, 255, 255, 0.03));
      box-sizing: border-box;
      display: flex;
      align-items: flex-start;
      justify-content: flex-start;
      padding: 4px;
    }

    .slot-boundary.slot-trash {
      border-color: var(--plr-slot-trash, rgba(239, 68, 68, 0.4));
      background: var(--plr-slot-trash-bg, rgba(239, 68, 68, 0.08));
    }

    .slot-boundary.slot-module {
      border-color: var(--plr-slot-module, rgba(147, 51, 234, 0.4));
      background: var(--plr-slot-module-bg, rgba(147, 51, 234, 0.08));
    }

    .slot-label {
      font-size: 10px;
      font-weight: 600;
      color: var(--plr-slot-label, rgba(255, 255, 255, 0.6));
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.4);
      letter-spacing: 0.5px;
    }

    /* Light theme slot overrides */
    :host-context(.light-theme) .slot-boundary {
      border-color: rgba(0, 0, 0, 0.15);
      background: rgba(0, 0, 0, 0.02);
    }

    :host-context(.light-theme) .slot-boundary.slot-trash {
      border-color: rgba(239, 68, 68, 0.5);
      background: rgba(239, 68, 68, 0.05);
    }

    :host-context(.light-theme) .slot-label {
      color: rgba(0, 0, 0, 0.5);
      text-shadow: 0 1px 2px rgba(255, 255, 255, 0.4);
    }

    /* Ghost/placeholder styling */
    .is-ghost {
      border: 2px dashed rgba(255, 255, 255, 0.2) !important;
      background-color: rgba(255, 255, 255, 0.02) !important;
    }

    /* Well styling - PLR uses circles for round wells */
    .is-well {
      border-radius: 50%;
      border: 1px solid rgba(255, 255, 255, 0.2);
      box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
    }

    /* Resource type-specific colors (PLR palette) */
    .resource-node[data-type='Plate'],
    .resource-node.type-plate {
      background: linear-gradient(135deg, #4a90d9 0%, #357abd 100%);
      border-color: #2563eb;
    }

    .resource-node[data-type='TipRack'],
    .resource-node.type-tiprack {
      background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
      border-color: #c2410c;
    }

    .resource-node[data-type='Trough'],
    .resource-node[data-type='Reservoir'],
    .resource-node.type-trough {
      background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
      border-color: #15803d;
    }

    .resource-node[data-type='Carrier'],
    .resource-node.type-carrier {
      background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
      border-color: #374151;
    }

    .resource-node[data-type='Trash'],
    .resource-node.type-trash {
      background: linear-gradient(135deg, #71717a 0%, #52525b 100%);
      border-color: #3f3f46;
    }

    /* Lid - translucent overlay style */
    .resource-node[data-type='Lid'],
    .resource-node.type-lid {
      background: linear-gradient(135deg, rgba(148, 163, 184, 0.6) 0%, rgba(100, 116, 139, 0.6) 100%);
      border-color: #64748b;
      border-style: dashed;
    }

    /* Petri dish - circular, amber/culture color */
    .resource-node[data-type='PetriDish'],
    .resource-node.type-petridish {
      background: linear-gradient(135deg, #fcd34d 0%, #f59e0b 100%);
      border-color: #d97706;
      border-radius: 50%;
    }

    /* Tube and TubeRack - purple/violet */
    .resource-node[data-type='Tube'],
    .resource-node[data-type='TubeRack'],
    .resource-node.type-tube {
      background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
      border-color: #7c3aed;
    }

    /* Plate adapter - subtle gray with pattern */
    .resource-node[data-type='PlateAdapter'],
    .resource-node.type-adapter {
      background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
      border-color: #4b5563;
      border-style: dotted;
    }

    /* Well states */
    .is-well.has-liquid {
      background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
    }

    .is-well.has-tip {
      background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
    }

    .is-well.empty {
      background: rgba(255, 255, 255, 0.05);
    }

    /* Light theme resource colors */
    :host-context(.light-theme) .resource-node[data-type='Plate'],
    :host-context(.light-theme) .resource-node.type-plate {
      background: linear-gradient(135deg, #93c5fd 0%, #60a5fa 100%);
      border-color: #3b82f6;
    }

    :host-context(.light-theme) .resource-node[data-type='TipRack'],
    :host-context(.light-theme) .resource-node.type-tiprack {
      background: linear-gradient(135deg, #fdba74 0%, #fb923c 100%);
      border-color: #f97316;
    }

    :host-context(.light-theme) .resource-node[data-type='Trough'],
    :host-context(.light-theme) .resource-node[data-type='Reservoir'],
    :host-context(.light-theme) .resource-node.type-trough {
      background: linear-gradient(135deg, #86efac 0%, #4ade80 100%);
      border-color: #22c55e;
    }

    :host-context(.light-theme) .resource-node[data-type='Lid'],
    :host-context(.light-theme) .resource-node.type-lid {
      background: linear-gradient(135deg, rgba(203, 213, 225, 0.7) 0%, rgba(148, 163, 184, 0.7) 100%);
      border-color: #94a3b8;
    }

    :host-context(.light-theme) .resource-node[data-type='PetriDish'],
    :host-context(.light-theme) .resource-node.type-petridish {
      background: linear-gradient(135deg, #fde68a 0%, #fcd34d 100%);
      border-color: #f59e0b;
    }

    :host-context(.light-theme) .resource-node[data-type='Tube'],
    :host-context(.light-theme) .resource-node[data-type='TubeRack'],
    :host-context(.light-theme) .resource-node.type-tube {
      background: linear-gradient(135deg, #c4b5fd 0%, #a78bfa 100%);
      border-color: #8b5cf6;
    }

    :host-context(.light-theme) .resource-node[data-type='PlateAdapter'],
    :host-context(.light-theme) .resource-node.type-adapter {
      background: linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%);
      border-color: #6b7280;
    }

    :host-context(.light-theme) .resource-label {
      text-shadow: none;
      color: #1e293b;
      background: rgba(255, 255, 255, 0.6);
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeckViewComponent {
  /* Services */
  private deckCatalog = inject(DeckCatalogService);

  /* Inputs */
  resource = signal<PlrResource | null>(null);
  state = signal<PlrState | null>(null);

  @Input({ alias: 'resource', required: true }) set _resource(val: PlrResource | null) {
    this.resource.set(val);
  }

  @Input({ alias: 'state' }) set _state(val: PlrState | null) {
    this.state.set(val);
  }

  itemDropped = output<CdkDragDrop<any>>();
  resourceSelected = output<PlrResourceDetails>();

  /* Tooltip State */
  tooltip = signal<TooltipState>({ visible: false, x: 0, y: 0, resource: null, parent: null });
  selectedResource = signal<PlrResource | null>(null);

  onDrop(event: CdkDragDrop<any>) {
    this.itemDropped.emit(event);
  }

  onResourceHover(event: MouseEvent, res: PlrResource, parent: PlrResource | null, index: number = -1) {
    if (res === this.resource()) return; // Don't show tooltip for root
    this.tooltip.set({
      visible: true,
      x: event.clientX,
      y: event.clientY,
      resource: res,
      parent,
      index
    });
  }

  onResourceLeave() {
    this.tooltip.set({ visible: false, x: 0, y: 0, resource: null, parent: null, index: undefined });
  }

  @HostListener('mousemove', ['$event'])
  onMouseMove(event: MouseEvent) {
    if (this.tooltip().visible) {
      this.tooltip.update(t => ({ ...t, x: event.clientX, y: event.clientY }));
    }
  }

  onResourceClick(event: MouseEvent, res: PlrResource, parent: PlrResource | null, index: number = -1) {
    if (res === this.resource()) return; // Don't select root
    event.stopPropagation();
    this.selectedResource.set(res);

    const details: PlrResourceDetails = {
      name: res.name,
      type: res.type,
      location: res.location,
      dimensions: { x: res.size_x, y: res.size_y, z: res.size_z },
      volume: this.getVolume(res, parent, index),
      maxVolume: res.max_volume,
      hasTip: this.hasTip(res, parent, index),
      parentName: parent?.name,
      slotId: res.slot_id
    };
    this.resourceSelected.emit(details);
  }

  /* Configuration */
  readonly pixelsPerMm = 0.5;

  private constraintService = inject(DeckConstraintService);

  // Track drag state for visual feedback
  activeDropTarget = signal<{ id: string | number, valid: boolean, reason?: string } | null>(null);

  onDragEnter(event: any, target: DeckSlotSpec | DeckRail) {
    // This requires access to the item being dragged. 
    // CDK DragDrop doesn't easily expose the data during 'enter' without some setup.
    // For now, we assume the dragged item is exposed via a service or signal if needed,
    // OR we rely on the specific drag item context if available.

    // Simplification: We'll do validation on 'start' or track it via CDK predicate if possible.
    // But since `cdkDropListEnterPredicate` takes `(drag: CdkDrag, drop: CdkDropList)`, we can use that.
  }

  /**
   * Predicate to determine if an item can be dropped on a Rail.
   * Can be bound to [cdkDropListEnterPredicate].
   */
  railEnterPredicate = (drag: CdkDrag<PlrResource>, drop: CdkDropList) => {
    // Retrieve rail info from drop list data or attributes
    // This is tricky because predicates are often static or need closure scope.
    // We'll trust the visual feedback and 'onDrop' validation for now, 
    // OR implement a more complex tracking system.
    return true;
  };

  /**
   * Check validity for styling purposes during rendering (if static).
   * For dynamic drag feedback, we'll need to hook into CDK events.
   */

  validateDropPreview(resource: PlrResource, target: DeckSlotSpec | DeckRail): ValidationResult {
    return this.constraintService.validateDrop(resource, target, this.resource()!);
  }

  containerWidth = computed(() => {
    const res = this.resource();
    return res ? res.size_x * this.pixelsPerMm : 0;
  });

  containerHeight = computed(() => {
    const res = this.resource();
    return res ? res.size_y * this.pixelsPerMm : 0;
  });

  scaleDim(val: number): number {
    return val * this.pixelsPerMm;
  }

  /**
   * PLR uses a Cartesian coordinate system (origin at bottom-left).
   * Web uses top-left. To map correctly without complex transforms,
   * we position children using 'bottom' and 'left'.
   */
  scaleBottom(y: number): number {
    return y * this.pixelsPerMm;
  }

  scaleLeft(x: number): number {
    return x * this.pixelsPerMm;
  }

  /**
   * Returns custom color only if explicitly set on resource.
   * Otherwise returns null to let CSS classes handle theming.
   */
  getCustomColor(res: PlrResource): string | null {
    if (res.color && !this.isStandardType(res.type)) {
      return res.color;
    }
    return null;
  }

  /* Type Checks */
  isStandardType(type: string): boolean {
    const standardTypes = [
      'Plate', 'Microplate', 'WellPlate',
      'TipRack', 'TipCarrier', 'TipSpot',
      'Trough', 'Reservoir',
      'Carrier', 'MFXCarrier', 'PLTCarrier', 'TipCarrier', 'PlateCarrier', 'PlateHolder',
      'Trash', 'Well',
      'Lid', 'PetriDish', 'PetriDishHolder',
      'TubeRack', 'Tube',
      'PlateAdapter', 'ResourceStack'
    ];
    return standardTypes.some(t =>
      type === t || type.includes(t) || type.endsWith(t)
    );
  }

  isPlateType(type: string): boolean {
    return type.includes('Plate') || type === 'Microplate';
  }

  isTipRackType(type: string): boolean {
    return type.includes('TipRack') || type.includes('Tips');
  }

  isTroughType(type: string): boolean {
    return type.includes('Trough') || type.includes('Reservoir');
  }

  isCarrierType(type: string): boolean {
    return type.includes('Carrier');
  }

  isLidType(type: string): boolean {
    return type.includes('Lid');
  }

  isPetriDishType(type: string): boolean {
    return type.includes('PetriDish');
  }

  isTubeType(type: string): boolean {
    return type.includes('Tube');
  }

  isPlateAdapterType(type: string): boolean {
    return type.includes('Adapter');
  }

  isWellOrSpot(type: string): boolean {
    return type === 'Well' || type === 'TipSpot' || type === 'Container';
  }

  /* State Helpers */

  /**
   * Resolve volume from resource or parent state.
   */
  getVolume(res: PlrResource, parent: PlrResource | null = null, index: number = -1): number {
    // 1. Direct state
    const s = this.getAllState(res);
    if (s?.volume !== undefined) return s.volume;

    // 2. Parent state
    if (parent) {
      const parentState = this.getAllState(parent);
      if (parentState && Array.isArray(parentState.volumes)) {
        // Use provided index or fallback to indexOf
        const idx = index >= 0 ? index : parent.children.indexOf(res);
        if (idx >= 0 && idx < parentState.volumes.length) {
          return parentState.volumes[idx] || 0;
        }
      }
    }
    return 0;
  }

  hasLiquid(res: PlrResource, parent: PlrResource | null = null, index: number = -1): boolean {
    const vol = this.getVolume(res, parent, index);
    if (vol > 0) return true;

    // Check liquid mask if no specific volume found
    if (parent) {
      const parentState = this.getAllState(parent);
      if (parentState?.liquid_mask) {
         const idx = index >= 0 ? index : parent.children.indexOf(res);
         // Optimization: We could cache decoded masks if needed
         const numChildren = parent.children.length;
         const liquids = this.decodeBitmask(parentState.liquid_mask, numChildren);
         return idx >= 0 && idx < liquids.length ? liquids[idx] : false;
      }
    }
    return false;
  }

  /**
   * Calculates the background gradient for liquid fill.
   */
  getLiquidStyle(res: PlrResource, parent: PlrResource | null = null, index: number = -1): string {
    const volume = this.getVolume(res, parent, index);
    
    // If no volume but hasLiquid is true (via mask), show generic fill
    if (volume <= 0 && this.hasLiquid(res, parent, index)) {
      const liquidColor = res.color || 'rgba(59, 130, 246, 0.8)';
      return `linear-gradient(to top, ${liquidColor} 50%, transparent 50%)`; // 50% fill for unknown volume
    }

    if (volume <= 0) return '';

    const maxVol = res.max_volume || 1000; // default if missing
    const fillRatio = Math.min(volume / maxVol, 1) * 100;

    // Default liquid color (blue-ish) or specific if available
    const liquidColor = res.color || 'rgba(59, 130, 246, 0.8)';

    return `linear-gradient(to top, ${liquidColor} ${fillRatio}%, transparent ${fillRatio}%)`;
  }

  hasTip(res: PlrResource, parent: PlrResource | null, index: number = -1): boolean {
    // 1. Check individual state
    const s = this.getAllState(res);
    if (s && s.has_tip !== undefined) {
      return !!s.has_tip;
    }

    // 2. Check parent state (bitmask/array logic) if applicable
    if (parent && this.isTipRackType(parent.type)) {
      const parentState = this.getAllState(parent);
      if (parentState) {
        const idx = index >= 0 ? index : parent.children.indexOf(res);
        if (idx < 0) return false;

        // 2a. Array
        if (Array.isArray(parentState.tips)) {
          if (idx < parentState.tips.length) {
            return !!parentState.tips[idx];
          }
        }
        // 2b. Bitmask
        if (parentState.tip_mask) {
          const numChildren = parent.children.length;
          const tips = this.decodeBitmask(parentState.tip_mask, numChildren);
          if (idx < tips.length) {
            return tips[idx];
          }
        }
      }
    }

    // Default to false if unknown
    return false;
  }

  isEmpty(res: PlrResource, parent: PlrResource | null, index: number = -1): boolean {
    return !this.hasLiquid(res, parent, index) && !this.hasTip(res, parent, index);
  }

  shouldShowLabel(res: PlrResource): boolean {
    return res.size_x > 20 && res.size_y > 20 && !this.isWellOrSpot(res.type);
  }

  isGhost(res: PlrResource): boolean {
    return res.name.startsWith('ghost_');
  }

  /**
   * Consolidated state lookup
   */
  getAllState(res: PlrResource): any {
    const stateMap = this.state();
    return stateMap ? stateMap[res.name] : null;
  }

  /* =========================================
     Bitmask Decoding Utilities (P4 Optimization)
     ========================================= */

  /**
   * Decode a hex bitmask string to a boolean array.
   * Used for tip_mask and liquid_mask fields.
   * @param hexMask Hex string like "fff" or "0xfff"
   * @param length Expected length of the boolean array
   */
  decodeBitmask(hexMask: string, length: number): boolean[] {
    try {
      const cleanHex = hexMask.replace(/^0x/i, '');
      const bigInt = BigInt('0x' + cleanHex);
      const result: boolean[] = [];
      for (let i = 0; i < length; i++) {
        result.push((bigInt & (1n << BigInt(i))) !== 0n);
      }
      return result;
    } catch (e) {
      console.warn('Error decoding bitmask:', hexMask, e);
      return new Array(length).fill(false);
    }
  }

  /* Rails Helper */
  getRails(): DeckRail[] {
    const res = this.resource();
    if (!res?.num_rails) return [];

    const spec = this.deckCatalog.getDeckDefinition(res.type);
    const defaultSpec = this.deckCatalog.getHamiltonSTARSpec();

    const railPositions = spec?.railPositions || defaultSpec?.railPositions || [];
    const spacing = spec?.railSpacing || defaultSpec?.railSpacing || 22.5;
    const compatible = spec?.compatibleCarriers || defaultSpec?.compatibleCarriers || [];

    return railPositions.slice(0, res.num_rails).map((xPos, i) => ({
      index: i,
      xPosition: xPos,
      width: spacing,
      compatibleCarrierTypes: compatible as string[]
    }));
  }

  /**
   * Check if the current deck is slot-based (like OT-2) vs rail-based (like Hamilton).
   */
  isSlotBasedDeck(): boolean {
    const res = this.resource();
    if (!res) return false;

    // Check if deck spec defines it as slot-based
    const spec = this.deckCatalog.getDeckDefinition(res.type);
    if (spec?.layoutType === 'slot-based') return true;

    // Fallback: Check for Opentrons-style type names
    const type = res.type.toLowerCase();
    return type.includes('otdeck') || type.includes('ot2') || type.includes('opentrons');
  }

  /**
   * Get slot positions for slot-based decks.
   * Returns slot specifications with positions and labels.
   */
  getSlots(): DeckSlotSpec[] {
    const res = this.resource();
    if (!res) return [];

    const spec = this.deckCatalog.getDeckDefinition(res.type);
    if (spec?.slots) {
      return spec.slots;
    }

    // Fallback: try to get OT-2 spec directly if type detection didn't work
    if (this.isSlotBasedDeck()) {
      const otSpec = this.deckCatalog.getOTDeckSpec();
      return otSpec?.slots || [];
    }

    return [];
  }
}

