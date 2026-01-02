import { Component, ChangeDetectionStrategy, Input, signal } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';
import { PlrDeckData, PlrResourceDetails } from '@core/models/plr.models';
import { DeckViewComponent } from '@shared/components/deck-view/deck-view.component';

@Component({
  selector: 'app-deck-visualizer',
  standalone: true,
  imports: [CommonModule, DeckViewComponent, DecimalPipe],
  template: `
    <div class="deck-visualizer-wrapper">
      <div class="visualizer-header">
        <h4>Deck Configuration Visualizer</h4>
        @if (inspectedResource()) {
          <button class="close-inspector-btn" (click)="clearInspection()">
            <span class="material-icons">close</span>
          </button>
        }
      </div>

      <div class="content-area">
        <div class="view-container" [class.has-inspector]="inspectedResource()">
          <app-deck-view
            *ngIf="data()"
            [resource]="data()!.resource"
            [state]="data()!.state"
            (resourceSelected)="onResourceSelected($event)">
          </app-deck-view>
          
          <div *ngIf="!data()" class="empty-state">
            No deck data available
          </div>
        </div>

        <!-- Inspector Panel -->
        @if (inspectedResource(); as res) {
          <div class="inspector-panel">
            <div class="inspector-header">
              <h5>Resource Inspector</h5>
            </div>
            
            <div class="inspector-content">
              <div class="inspector-section">
                <div class="section-title">Identity</div>
                <div class="property-row">
                  <span class="property-label">Name</span>
                  <span class="property-value">{{ res.name }}</span>
                </div>
                <div class="property-row">
                  <span class="property-label">Type</span>
                  <span class="property-value type-badge">{{ res.type }}</span>
                </div>
                @if (res.parentName) {
                  <div class="property-row">
                    <span class="property-label">Parent</span>
                    <span class="property-value">{{ res.parentName }}</span>
                  </div>
                }
                @if (res.slotId) {
                  <div class="property-row">
                    <span class="property-label">Slot ID</span>
                    <span class="property-value">{{ res.slotId }}</span>
                  </div>
                }
              </div>

              <div class="inspector-section">
                <div class="section-title">Location</div>
                <div class="property-row">
                  <span class="property-label">X</span>
                  <span class="property-value">{{ res.location.x | number:'1.2-2' }} mm</span>
                </div>
                <div class="property-row">
                  <span class="property-label">Y</span>
                  <span class="property-value">{{ res.location.y | number:'1.2-2' }} mm</span>
                </div>
                <div class="property-row">
                  <span class="property-label">Z</span>
                  <span class="property-value">{{ res.location.z | number:'1.2-2' }} mm</span>
                </div>
              </div>

              <div class="inspector-section">
                <div class="section-title">Dimensions</div>
                <div class="property-row">
                  <span class="property-label">Width (X)</span>
                  <span class="property-value">{{ res.dimensions.x | number:'1.1-1' }} mm</span>
                </div>
                <div class="property-row">
                  <span class="property-label">Depth (Y)</span>
                  <span class="property-value">{{ res.dimensions.y | number:'1.1-1' }} mm</span>
                </div>
                <div class="property-row">
                  <span class="property-label">Height (Z)</span>
                  <span class="property-value">{{ res.dimensions.z | number:'1.1-1' }} mm</span>
                </div>
              </div>

              @if (res.volume !== undefined || res.maxVolume !== undefined || res.hasTip !== undefined) {
                <div class="inspector-section">
                  <div class="section-title">State</div>
                  @if (res.volume !== undefined) {
                    <div class="property-row">
                      <span class="property-label">Volume</span>
                      <span class="property-value volume-value">{{ res.volume | number:'1.0-1' }} µL</span>
                    </div>
                  }
                  @if (res.maxVolume !== undefined) {
                    <div class="property-row">
                      <span class="property-label">Max Volume</span>
                      <span class="property-value">{{ res.maxVolume | number:'1.0-1' }} µL</span>
                    </div>
                  }
                  @if (res.hasTip !== undefined) {
                    <div class="property-row">
                      <span class="property-label">Tip</span>
                      <span class="property-value" [class.tip-present]="res.hasTip" [class.tip-absent]="!res.hasTip">
                        {{ res.hasTip ? 'Present' : 'Absent' }}
                      </span>
                    </div>
                  }
                  @if (res.liquidClass) {
                    <div class="property-row">
                      <span class="property-label">Liquid Class</span>
                      <span class="property-value">{{ res.liquidClass }}</span>
                    </div>
                  }
                </div>
              }
            </div>
          </div>
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
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
    }

    .visualizer-header h4 {
      margin: 0;
      color: var(--sys-on-surface);
    }

    .close-inspector-btn {
      background: transparent;
      border: none;
      color: var(--sys-on-surface-variant);
      cursor: pointer;
      padding: 4px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .close-inspector-btn:hover {
      background: var(--sys-surface-container);
    }

    .close-inspector-btn .material-icons {
      font-size: 20px;
    }

    .content-area {
      flex: 1;
      display: flex;
      gap: 16px;
      min-height: 0;
      overflow: hidden;
    }

    .view-container {
      flex: 1;
      min-height: 0;
      overflow: hidden;
      border-radius: 8px;
      background: transparent;
      display: flex;
      flex-direction: column;
      transition: flex 0.2s ease;
    }

    .view-container.has-inspector {
      flex: 2;
    }
    
    app-deck-view {
      flex: 1;
      overflow: auto;
    }

    .empty-state {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: var(--sys-outline);
    }

    /* Inspector Panel */
    .inspector-panel {
      width: 280px;
      min-width: 280px;
      background: var(--sys-surface-container);
      border-radius: 12px;
      border: 1px solid var(--sys-outline-variant);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      animation: slideIn 0.2s ease;
    }

    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateX(20px);
      }
      to {
        opacity: 1;
        transform: translateX(0);
      }
    }

    .inspector-header {
      padding: 12px 16px;
      border-bottom: 1px solid var(--sys-outline-variant);
      background: var(--sys-surface-container-high);
    }

    .inspector-header h5 {
      margin: 0;
      font-size: 14px;
      font-weight: 600;
      color: var(--sys-on-surface);
    }

    .inspector-content {
      flex: 1;
      overflow-y: auto;
      padding: 12px 16px;
    }

    .inspector-section {
      margin-bottom: 16px;
    }

    .inspector-section:last-child {
      margin-bottom: 0;
    }

    .section-title {
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--sys-primary);
      margin-bottom: 8px;
    }

    .property-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 4px 0;
      font-size: 12px;
    }

    .property-label {
      color: var(--sys-on-surface-variant);
    }

    .property-value {
      color: var(--sys-on-surface);
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }

    .type-badge {
      background: var(--sys-surface-container-highest);
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 10px;
    }

    .volume-value {
      color: var(--sys-tertiary);
      font-weight: 500;
    }

    .tip-present {
      color: var(--sys-secondary);
      font-weight: 500;
    }

    .tip-absent {
      color: var(--sys-outline);
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeckVisualizerComponent {
  // Inputs
  @Input({ required: true }) set layoutData(value: PlrDeckData | null) {
    this.data.set(value);
  }

  // Signals
  data = signal<PlrDeckData | null>(null);
  inspectedResource = signal<PlrResourceDetails | null>(null);

  onResourceSelected(details: PlrResourceDetails) {
    this.inspectedResource.set(details);
  }

  clearInspection() {
    this.inspectedResource.set(null);
  }
}

