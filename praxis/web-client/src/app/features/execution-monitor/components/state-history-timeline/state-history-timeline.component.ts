/**
 * StateHistoryTimelineComponent
 * 
 * Sparkline-style visualization showing state changes over time.
 * Displays mini-charts for tips loaded, well volumes, etc.
 */

import { Component, input, output, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

import { StateHistory, OperationStateSnapshot, TimelineMetric } from '@core/models/simulation.models';

@Component({
    selector: 'app-state-history-timeline',
    standalone: true,
    imports: [CommonModule, MatIconModule, MatTooltipModule],
    template: `
    <div class="timeline-container">
      <div class="timeline-header">
        <mat-icon>insights</mat-icon>
        <h4>State Timeline</h4>
      </div>
      
      @if (!stateHistory() || stateHistory()!.operations.length === 0) {
        <div class="empty-state">
          <span>No state data available</span>
        </div>
      } @else {
        <div class="metrics-container">
          @for (metric of metrics(); track metric.id) {
            <div class="metric-row">
              <span class="metric-label" [matTooltip]="metric.id">
                {{ metric.label }}
              </span>
              <div class="sparkline-container">
                <div class="sparkline">
                  @for (value of metric.values; track $index; let i = $index) {
                    <div 
                      class="bar"
                      [class.active]="i === currentIndex()"
                      [class.filled]="value > 0"
                      [style.height.%]="normalizeValue(value, metric)"
                      [matTooltip]="formatTooltip(metric, value, i)"
                      (click)="onBarClick(i)">
                    </div>
                  }
                </div>
              </div>
              @if (metric.unit) {
                <span class="metric-unit">{{ metric.unit }}</span>
              }
            </div>
          }
        </div>
        
        <!-- Legend -->
        <div class="timeline-legend">
          <span class="legend-item">
            <span class="legend-color unchanged"></span> Unchanged
          </span>
          <span class="legend-item">
            <span class="legend-color filled"></span> Value present
          </span>
          <span class="legend-item">
            <span class="legend-color active"></span> Current
          </span>
        </div>
      }
    </div>
  `,
    styles: [`
    .timeline-container {
      display: flex;
      flex-direction: column;
      gap: 12px;
      padding: 16px;
      background: var(--sys-surface-container-low);
      border-radius: 12px;
      border: 1px solid var(--sys-outline-variant);
    }

    .timeline-header {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .timeline-header h4 {
      margin: 0;
      font-size: 0.875rem;
      font-weight: 600;
      color: var(--sys-on-surface);
    }

    .timeline-header mat-icon {
      color: var(--sys-primary);
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .empty-state {
      padding: 24px;
      text-align: center;
      color: var(--sys-on-surface-variant);
      font-size: 0.75rem;
    }

    .metrics-container {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .metric-row {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .metric-label {
      width: 80px;
      font-size: 0.625rem;
      font-weight: 500;
      color: var(--sys-on-surface-variant);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .sparkline-container {
      flex: 1;
      height: 24px;
      background: var(--sys-surface-container);
      border-radius: 4px;
      overflow: hidden;
    }

    .sparkline {
      display: flex;
      height: 100%;
      gap: 1px;
      align-items: flex-end;
      padding: 2px;
    }

    .bar {
      flex: 1;
      min-height: 2px;
      background: var(--sys-surface-variant);
      border-radius: 1px;
      transition: all 0.15s ease;
      cursor: pointer;
    }

    .bar:hover {
      background: var(--sys-primary-container);
    }

    .bar.filled {
      background: var(--sys-primary);
      opacity: 0.6;
    }

    .bar.active {
      background: var(--sys-tertiary);
      opacity: 1;
    }

    .metric-unit {
      width: 40px;
      font-size: 0.625rem;
      color: var(--sys-on-surface-variant);
      text-align: right;
    }

    .timeline-legend {
      display: flex;
      gap: 16px;
      padding-top: 8px;
      border-top: 1px solid var(--sys-outline-variant);
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.625rem;
      color: var(--sys-on-surface-variant);
    }

    .legend-color {
      width: 12px;
      height: 8px;
      border-radius: 2px;
    }

    .legend-color.unchanged {
      background: var(--sys-surface-variant);
    }

    .legend-color.filled {
      background: var(--sys-primary);
      opacity: 0.6;
    }

    .legend-color.active {
      background: var(--sys-tertiary);
    }
  `]
})
export class StateHistoryTimelineComponent {
    /** Full state history */
    stateHistory = input<StateHistory | null>(null);

    /** Current operation index to highlight */
    currentIndex = input(0);

    /** Emitted when user clicks on a bar */
    operationSelected = output<number>();

    /** Extracted metrics from state history */
    metrics = computed<TimelineMetric[]>(() => {
        const history = this.stateHistory();
        if (!history || history.operations.length === 0) return [];

        return this.extractMetrics(history.operations);
    });

    onBarClick(index: number): void {
        this.operationSelected.emit(index);
    }

    normalizeValue(value: number, metric: TimelineMetric): number {
        const maxValue = Math.max(...metric.values, 1);
        return Math.max(10, (value / maxValue) * 100);
    }

    formatTooltip(metric: TimelineMetric, value: number, index: number): string {
        const unit = metric.unit || '';
        return `Op ${index + 1}: ${value}${unit}`;
    }

    private extractMetrics(operations: OperationStateSnapshot[]): TimelineMetric[] {
        const metrics: TimelineMetric[] = [];

        // Tips loaded metric
        const tipsValues = operations.map(op =>
            op.state_after.tips.tips_loaded ? op.state_after.tips.tips_count : 0
        );
        metrics.push({
            id: 'tips',
            label: 'Tips',
            values: tipsValues,
            unit: 'tips'
        });

        // Extract liquid volumes for each resource
        const allResources = new Set<string>();
        operations.forEach(op => {
            Object.keys(op.state_after.liquids || {}).forEach(r => allResources.add(r));
        });

        for (const resource of allResources) {
            // Get total volume across all wells for this resource
            const volumeValues = operations.map(op => {
                const wells = op.state_after.liquids?.[resource] || {};
                return Object.values(wells).reduce((sum, v) => sum + v, 0);
            });

            // Only add if there's actually volume data
            if (volumeValues.some(v => v > 0)) {
                metrics.push({
                    id: `liquid_${resource}`,
                    label: resource.slice(0, 10),
                    values: volumeValues,
                    unit: 'µL'
                });
            }
        }

        return metrics;
    }
}
