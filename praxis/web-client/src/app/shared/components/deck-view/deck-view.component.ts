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
           [title]="res.name + ' (' + res.type + ')'"
           [style.left.px]="scaleX(res.location.x)"
           [style.top.px]="scaleY(res.location.y)"
           [style.width.px]="scaleDim(res.size_x)"
           [style.height.px]="scaleDim(res.size_y)"
           [class.is-root]="res === resource()"
           [class.is-ghost]="isGhost(res)"
           [class.is-well]="res.type === 'Well'"
           [style.background-color]="getColor(res)">
        
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
    :host {
      display: block;
      overflow: auto;
      background: #f5f5f5;
      padding: 20px;
    }

    .deck-container {
      position: relative;
      background: white;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
      transform-origin: top left;
    }

    .resource-node {
      position: absolute;
      border: 1px solid rgba(0,0,0,0.1);
      box-sizing: border-box;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .resource-node:hover {
      border-color: var(--sys-primary);
      z-index: 10;
      box-shadow: 0 0 0 1px var(--sys-primary);
    }

    .is-root {
      /* Root usually defines the container, so we might reset its pos relative to container */
      position: relative; 
      left: 0 !important;
      top: 0 !important;
      border: none;
      background: #eee;
    }

    .resource-label {
      font-size: 10px;
      color: rgba(0,0,0,0.6);
      pointer-events: none;
      text-align: center;
      padding: 2px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
    }

    .rails-container {
      z-index: 0;
    }
    
    .rail-line {
      position: absolute;
      top: 63px; /* Standard Hamilton rail start Y */
      bottom: 63px; /* Standard Hamilton rail end Y */
      width: 2px;
      background-color: rgba(0, 0, 0, 0.05);
      border-right: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Ghost styling */
    .is-ghost {
       border: 2px dashed rgba(0, 0, 0, 0.3) !important;
       background-color: rgba(0, 0, 0, 0.02) !important; 
    }

    /* Well styling */
    .is-well {
      border-radius: 50%; /* Assume round wells for now */
      border: 1px solid rgba(0,0,0,0.1); 
    }

    /* Override for rectangular wells if needed, based on cross_section_type */
    .resource-node[data-shape='rect'] {
       border-radius: 1px;
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

  getColor(res: PlrResource): string {
    if (res.color) return res.color;
    if (res.type === 'Plate') return 'rgba(200, 200, 255, 0.5)';
    if (res.type === 'TipRack') return 'rgba(255, 200, 200, 0.5)';
    if (res.type === 'Well') return 'white'; // detailed view might be too heavy
    return 'rgba(0,0,0,0.02)';
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
