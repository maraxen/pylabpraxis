import { Component, signal } from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import { ActiveRunsPanelComponent } from './components/active-runs-panel.component';
import { RunHistoryTableComponent } from './components/run-history-table.component';
import { RunFiltersComponent, FilterState } from './components/run-filters.component';
import { RunStatsPanelComponent } from './components/run-stats-panel.component';

/**
 * Main dashboard for the Execution Monitor feature.
 * Displays active runs and run history.
 */
@Component({
  selector: 'app-execution-monitor',
  standalone: true,
  imports: [
    MatCardModule,
    MatIconModule,
    ActiveRunsPanelComponent,
    RunHistoryTableComponent,
    RunFiltersComponent,
    RunStatsPanelComponent
],
  template: `
    <div class="p-6 max-w-screen-2xl mx-auto">
      <!-- Header -->
      <div class="flex items-center gap-4 mb-8">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500/20 to-teal-500/20 flex items-center justify-center border border-green-500/20">
          <mat-icon class="text-green-400 !w-6 !h-6 !text-[24px]">monitor_heart</mat-icon>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-sys-text-primary mb-1">Execution Monitor</h1>
          <p class="text-sys-text-secondary">Track and analyze protocol executions</p>
        </div>
      </div>

      <!-- Summary Statistics -->
      <app-run-stats-panel></app-run-stats-panel>

      <!-- Active Runs Panel -->
      <app-active-runs-panel></app-active-runs-panel>

      <!-- Filters -->
      <app-run-filters (filtersChange)="onFiltersChange($event)"></app-run-filters>

      <!-- Run History Table -->
      <app-run-history-table [filters]="currentFilters()" data-tour-id="run-history-table"></app-run-history-table>
    </div>
  `,
})
export class ExecutionMonitorComponent {
  readonly currentFilters = signal<FilterState | null>(null);

  onFiltersChange(filters: FilterState): void {
    this.currentFilters.set(filters);
  }
}
