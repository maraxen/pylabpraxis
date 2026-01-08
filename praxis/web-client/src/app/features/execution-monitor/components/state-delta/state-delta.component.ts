import { Component, input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

export interface StateDelta {
    key: string;
    before: number | string;
    after: number | string;
    change: number | string;
}

@Component({
    selector: 'app-state-delta',
    standalone: true,
    imports: [CommonModule, MatIconModule, MatTooltipModule],
    changeDetection: ChangeDetectionStrategy.OnPush,
    template: `
    <div class="state-delta-container">
      @for (delta of deltas(); track delta.key) {
        <div class="delta-row" [class.positive]="isPositive(delta)" [class.negative]="isNegative(delta)">
          <span class="delta-key">{{ formatKey(delta.key) }}</span>
          <span class="delta-change">
            @if (isPositive(delta)) {
              <mat-icon class="icon-sm">arrow_upward</mat-icon>
            } @else if (isNegative(delta)) {
              <mat-icon class="icon-sm">arrow_downward</mat-icon>
            }
            {{ formatChange(delta.change) }}
          </span>
          <span class="delta-values">
            {{ delta.before }} → {{ delta.after }}
          </span>
        </div>
      }
      @if (deltas().length === 0) {
        <div class="no-changes">No state changes</div>
      }
    </div>
  `,
    styles: [`
    .state-delta-container {
      font-size: 0.875rem;
      padding: 8px;
    }
    .delta-row {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 4px 0;
      border-bottom: 1px solid var(--mat-sys-outline-variant);
    }
    .delta-key {
      flex: 1;
      font-family: monospace;
      color: var(--mat-sys-on-surface);
    }
    .delta-change {
      display: flex;
      align-items: center;
      gap: 2px;
      font-weight: 600;
    }
    .delta-values {
      color: var(--mat-sys-on-surface-variant);
      font-size: 0.75rem;
    }
    .positive .delta-change { color: #22c55e; }
    .negative .delta-change { color: #ef4444; }
    .icon-sm { font-size: 14px; width: 14px; height: 14px; }
    .no-changes { 
      color: var(--mat-sys-on-surface-variant); 
      font-style: italic;
    }
  `]
})
export class StateDeltaComponent {
    deltas = input<StateDelta[]>([]);

    isPositive(delta: StateDelta): boolean {
        return typeof delta.change === 'number' && delta.change > 0;
    }

    isNegative(delta: StateDelta): boolean {
        return typeof delta.change === 'number' && delta.change < 0;
    }

    formatKey(key: string): string {
        // source['A1'].volume → A1.volume
        return key.replace(/.*\['?([^']+)'?\]\./, '$1.');
    }

    formatChange(change: number | string): string {
        if (typeof change === 'number') {
            return change > 0 ? `+${change}` : `${change}`;
        }
        return String(change);
    }
}
