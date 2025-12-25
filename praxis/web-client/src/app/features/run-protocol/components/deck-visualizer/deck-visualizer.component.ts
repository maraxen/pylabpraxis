import { Component, ChangeDetectionStrategy, Input, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DeckLayout, DeckSlot } from '../../models/deck-layout.models';

@Component({
    selector: 'app-deck-visualizer',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="deck-visualizer-wrapper">
      <div class="visualizer-header">
        <h4>Deck Configuration Visualizer</h4>
        <div class="legend">
          <div class="legend-item"><span class="color plate"></span> Plate</div>
          <div class="legend-item"><span class="color tip-rack"></span> Tip Rack</div>
          <div class="legend-item"><span class="color empty"></span> Empty Slot</div>
        </div>
      </div>

      <div class="svg-container">
        @if (layout()) {
          <svg
            [attr.viewBox]="'0 0 ' + layout()!.width + ' ' + layout()!.height"
            preserveAspectRatio="xMidYMid meet"
            class="deck-svg"
          >
            <!-- Background -->
            <rect
              [attr.width]="layout()!.width"
              [attr.height]="layout()!.height"
              fill="var(--sys-surface-container-high)"
              rx="8"
            />

            <!-- Slots -->
            @for (slot of layout()!.slots; track slot.id) {
              <g [attr.transform]="'translate(' + slot.x + ',' + slot.y + ')'">
                <!-- Slot Outline -->
                <rect
                  [attr.width]="slot.width"
                  [attr.height]="slot.height"
                  class="slot-rect"
                  [class.has-resource]="!!slot.resource"
                  rx="4"
                />

                <!-- Slot ID -->
                <text
                  [attr.x]="slot.width / 2"
                  [attr.y]="slot.height / 2"
                  text-anchor="middle"
                  dominant-baseline="middle"
                  class="slot-label"
                >
                  {{ slot.id }}
                </text>

                <!-- Resource -->
                @if (slot.resource) {
                  <g>
                    <rect
                      [attr.x]="slot.width * 0.1"
                      [attr.y]="slot.height * 0.1"
                      [attr.width]="slot.width * 0.8"
                      [attr.height]="slot.height * 0.8"
                      [attr.fill]="getResourceColor(slot.resource)"
                      rx="2"
                      class="resource-rect"
                    >
                      <title>{{ slot.resource.name }} ({{ slot.resource.type }})</title>
                    </rect>
                    <text
                      [attr.x]="slot.width / 2"
                      [attr.y]="slot.height * 0.9"
                      text-anchor="middle"
                      class="resource-label"
                    >
                      {{ slot.resource.name }}
                    </text>
                  </g>
                }
              </g>
            }
          </svg>
        }
      </div>
    </div>
  `,
    styles: [`
    :host {
      display: block;
      width: 100%;
      height: 100%;
    }

    .deck-visualizer-wrapper {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: var(--sys-surface-container-low);
      border-radius: 12px;
      padding: 16px;
      border: 1px solid var(--sys-outline-variant);
    }

    .visualizer-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }

    .visualizer-header h4 {
      margin: 0;
      color: var(--sys-on-surface);
    }

    .legend {
      display: flex;
      gap: 12px;
      font-size: 0.8rem;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .color {
      width: 12px;
      height: 12px;
      border-radius: 2px;
      display: inline-block;
    }

    .color.plate { background: #3f51b5; }
    .color.tip-rack { background: #009688; }
    .color.empty { border: 1px dashed #666; }

    .svg-container {
      flex: 1;
      min-height: 0;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .deck-svg {
      width: 100%;
      height: 100%;
      max-height: 600px;
    }

    .slot-rect {
      fill: var(--sys-surface-container);
      stroke: var(--sys-outline);
      stroke-width: 1;
      transition: all 0.2s ease;
    }

    .slot-rect.has-resource {
      stroke: var(--sys-primary);
      stroke-width: 2;
    }

    .slot-label {
      font-size: 10px;
      fill: var(--sys-on-surface-variant);
      opacity: 0.5;
      pointer-events: none;
    }

    .resource-rect {
      cursor: pointer;
      filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
    }

    .resource-label {
      font-size: 8px;
      fill: white;
      pointer-events: none;
      font-weight: bold;
    }
  `],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeckVisualizerComponent {
    @Input({ required: true }) set layoutData(value: DeckLayout | null) {
        this.layout.set(value);
    }

    layout = signal<DeckLayout | null>(null);

    getResourceColor(resource: any): string {
        if (resource.color) return resource.color;
        switch (resource.type) {
            case 'plate': return 'var(--sys-primary)';
            case 'tip_rack': return 'var(--sys-tertiary)';
            default: return 'var(--sys-secondary)';
        }
    }
}
