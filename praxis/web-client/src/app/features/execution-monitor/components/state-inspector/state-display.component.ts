/**
 * StateDisplayComponent
 * 
 * Simple component to display a state snapshot with tips, deck items, and liquid summary.
 */

import { Component, input, computed } from '@angular/core';

import { MatIconModule } from '@angular/material/icon';

import { StateSnapshot } from '@core/models/simulation.models';

@Component({
    selector: 'app-state-display',
    standalone: true,
    imports: [MatIconModule],
    template: `
    <div class="state-display">
      <!-- Tips State -->
      <div class="state-row">
        <mat-icon [class.active]="state().tips.tips_loaded">
          {{ state().tips.tips_loaded ? 'check_circle' : 'radio_button_unchecked' }}
        </mat-icon>
        <span class="state-label">Tips</span>
        <span class="state-value">
          {{ state().tips.tips_loaded ? state().tips.tips_count + ' loaded' : 'None' }}
        </span>
      </div>
      
      <!-- On Deck -->
      <div class="state-row">
        <mat-icon>grid_view</mat-icon>
        <span class="state-label">On Deck</span>
        <span class="state-value">{{ state().on_deck.length }} items</span>
      </div>
      
      <!-- Liquid Summary -->
      @if (liquidSummary().length > 0) {
        <div class="state-row">
          <mat-icon>water_drop</mat-icon>
          <span class="state-label">Liquids</span>
        </div>
        @for (item of liquidSummary(); track item.resource) {
          <div class="liquid-entry">
            <span class="resource-name">{{ item.resource }}</span>
            <span class="volume-summary">{{ item.summary }}</span>
          </div>
        }
      }
    </div>
  `,
    styles: [`
    .state-display {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .state-row {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.75rem;
    }

    .state-row mat-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
      color: var(--sys-on-surface-variant);
    }

    .state-row mat-icon.active {
      color: var(--sys-primary);
    }

    .state-label {
      flex: 1;
      color: var(--sys-on-surface-variant);
    }

    .state-value {
      font-family: 'Fira Code', monospace;
      color: var(--sys-on-surface);
    }

    .liquid-entry {
      display: flex;
      justify-content: space-between;
      padding-left: 24px;
      font-size: 0.625rem;
    }

    .resource-name {
      color: var(--sys-on-surface-variant);
    }

    .volume-summary {
      font-family: 'Fira Code', monospace;
      color: var(--sys-on-surface);
    }
  `]
})
export class StateDisplayComponent {
    state = input.required<StateSnapshot>();

    liquidSummary = computed(() => {
        const liquids = this.state().liquids;
        if (!liquids) return [];

        return Object.entries(liquids).map(([resource, wells]) => {
            const wellCount = Object.keys(wells).length;
            const totalVolume = Object.values(wells).reduce((sum, v) => sum + v, 0);
            return {
                resource,
                summary: `${wellCount} wells, ${totalVolume.toFixed(0)}µL total`
            };
        });
    });
}
