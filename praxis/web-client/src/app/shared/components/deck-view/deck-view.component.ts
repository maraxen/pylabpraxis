import { Component, ChangeDetectionStrategy, Input, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PlrResource, PlrState } from '@core/models/plr.models';

@Component({
  selector: 'app-deck-view',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="deck-container" [style.width.px]="containerWidth()" [style.height.px]="containerHeight()">
      <!-- Background Rails/Slots -->
      @if (resource()?.num_rails) {
         <div class="rails-container absolute inset-0 pointer-events-none">
           @for (rail of getRails(); track $index) {
             <div class="rail-line" [style.left.px]="scaleX(100 + ($index * 22.5))"></div>
           }
         </div>
      }

      <!-- Render the root resource and its children recursively -->
      <ng-container *ngTemplateOutlet="resourceTpl; context: { $implicit: resource() }"></ng-container>
    </div>

    <ng-template #resourceTpl let-res>
      <div class="resource-node"
           [attr.data-type]="res.type"
           [title]="res.name + ' (' + res.type + ')'"
           [style.left.px]="scaleX(res.location.x)"
           [style.top.px]="scaleY(res.location.y)"
           [style.width.px]="scaleDim(res.size_x)"
           [style.height.px]="scaleDim(res.size_y)"
           [class.is-root]="res === resource()"
           [class.is-ghost]="isGhost(res)"
           [class.is-well]="res.type === 'Well'"
           [class.type-plate]="isPlateType(res.type)"
           [class.type-tiprack]="isTipRackType(res.type)"
           [class.type-trough]="isTroughType(res.type)"
           [class.type-carrier]="isCarrierType(res.type)"
           [class.type-trash]="res.type === 'Trash'"
           [class.type-lid]="isLidType(res.type)"
           [class.type-petridish]="isPetriDishType(res.type)"
           [class.type-tube]="isTubeType(res.type)"
           [class.type-adapter]="isPlateAdapterType(res.type)"
           [class.has-liquid]="res.type === 'Well' && hasLiquid(res)"
           [class.has-tip]="res.type === 'Well' && hasTip(res)"
           [class.empty]="res.type === 'Well' && isEmpty(res)"
           [style.background-color]="getCustomColor(res)">

        <!-- Label for significant resources -->
        <div class="resource-label" *ngIf="shouldShowLabel(res)">
          {{ res.name }}
        </div>

        <!-- Recursively render children -->
        @for (child of res.children; track child.name) {
          <ng-container *ngTemplateOutlet="resourceTpl; context: { $implicit: child }"></ng-container>
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
      background: var(--plr-bg, #1a1a2e);
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
      --plr-bg: #1a1a2e;
      --plr-deck-bg: #2d2d44;
      --plr-deck-border: #4a4a6a;
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
      border: 1px solid rgba(255, 255, 255, 0.15);
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
      font-size: 9px;
      font-weight: 500;
      color: var(--plr-label);
      pointer-events: none;
      text-align: center;
      padding: 2px 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
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
      background: var(--plr-rail);
      border-radius: 2px;
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
      text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
      color: #1e293b;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeckViewComponent {
  // Inputs
  resource = signal<PlrResource | null>(null);
  state = signal<PlrState | null>(null);

  @Input({ alias: 'resource', required: true }) set _resource(val: PlrResource | null) {
    this.resource.set(val);
  }

  @Input({ alias: 'state' }) set _state(val: PlrState | null) {
    this.state.set(val);
  }

  // Configuration
  pixelsPerMm = 0.5; // Scale factor

  containerWidth = computed(() => {
    const res = this.resource();
    return res ? res.size_x * this.pixelsPerMm : 0;
  });

  containerHeight = computed(() => {
    const res = this.resource();
    return res ? res.size_y * this.pixelsPerMm : 0;
  });

  scaleX(val: number): number {
    return val * this.pixelsPerMm;
  }

  // PLR Y-axis is usually bottom-up. Web is top-down.
  // However, usually PLR resources children coordinates are relative to parent.
  // Standard transformation: (0,0) in PLR is bottom-left. 
  // If we render strictly as nested divs, top-left (0,0) in CSS works if we assume 
  // the data is already transformed OR if we transform it.
  // 
  // If PLR gives us "x=100, y=100" relative to parent bottom-left...
  // CSS top = parentHeight - (y + height).
  // 
  // For now, I will assume a direct mapping (x->left, y->top) to see what happens.
  // If it's inverted, I'll fix it. usually Deck visualizers flip the Y axis.
  // Let's implement the flip logic assuming standard Cartesian (bottom-left origin).
  // But wait, the recursive structure means I need to know parent height to flip.
  // 
  // Simplification: Let's assume direct mapping first (top-left origin) as many 
  // web-facing conversions do this. If it looks upside down, I'll invert.

  scaleY(val: number): number {
    return val * this.pixelsPerMm;
    // To flip Y (Cartesian to Screen):
    // We need parent height. 
    // This is hard in a recursive template without passing parent context.
    // For this MVP, let's try direct mapping. 
  }

  scaleDim(val: number): number {
    return val * this.pixelsPerMm;
  }

  /**
   * Returns custom color only if explicitly set on resource.
   * Otherwise returns null to let CSS classes handle theming.
   */
  getCustomColor(res: PlrResource): string | null {
    // Only return color if explicitly set and not a standard type
    if (res.color && !this.isStandardType(res.type)) {
      return res.color;
    }
    return null;
  }

  /**
   * Check if type is a standard PLR type with CSS styling
   */
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

  /**
   * Type classification helpers for CSS classes
   */
  isPlateType(type: string): boolean {
    return type === 'Plate' ||
           type === 'Microplate' ||
           type === 'WellPlate' ||
           type.includes('Plate') ||
           type.endsWith('Plate');
  }

  isTipRackType(type: string): boolean {
    return type === 'TipRack' ||
           type.includes('TipRack') ||
           type.includes('Tips') ||
           type.endsWith('Tips');
  }

  isTroughType(type: string): boolean {
    return type === 'Trough' ||
           type === 'Reservoir' ||
           type.includes('Trough') ||
           type.includes('Reservoir');
  }

  isCarrierType(type: string): boolean {
    return type === 'Carrier' ||
           type.includes('Carrier') ||
           type.endsWith('Carrier');
  }

  isLidType(type: string): boolean {
    return type === 'Lid' || type.endsWith('Lid');
  }

  isPetriDishType(type: string): boolean {
    return type === 'PetriDish' ||
           type === 'PetriDishHolder' ||
           type.includes('PetriDish');
  }

  isTubeType(type: string): boolean {
    return type === 'Tube' ||
           type === 'TubeRack' ||
           type.includes('Tube');
  }

  isPlateAdapterType(type: string): boolean {
    return type === 'PlateAdapter' || type.includes('Adapter');
  }

  /**
   * Well state helpers
   */
  hasLiquid(res: PlrResource): boolean {
    const state = this.state();
    if (!state || !state[res.name]) return false;
    return !!state[res.name].volume && state[res.name].volume > 0;
  }

  hasTip(res: PlrResource): boolean {
    const state = this.state();
    if (!state || !state[res.name]) return false;
    return !!state[res.name].has_tip;
  }

  isEmpty(res: PlrResource): boolean {
    return !this.hasLiquid(res) && !this.hasTip(res);
  }

  shouldShowLabel(res: PlrResource): boolean {
    // Only show labels for larger items, not wells/tips
    return res.size_x > 20 && res.size_y > 20 && !['Well', 'Tip'].includes(res.type);
  }

  isGhost(res: PlrResource): boolean {
    return res.name.startsWith('ghost_');
  }

  getRails(): number[] {
    const num = this.resource()?.num_rails || 0;
    return Array(num).fill(0);
  }
}
