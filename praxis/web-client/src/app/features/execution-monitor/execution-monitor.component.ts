import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import { ActiveRunsPanelComponent } from './components/active-runs-panel.component';
import { RunHistoryTableComponent } from './components/run-history-table.component';

/**
 * Main dashboard for the Execution Monitor feature.
 * Displays active runs and run history.
 */
@Component({
  selector: 'app-execution-monitor',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    ActiveRunsPanelComponent,
    RunHistoryTableComponent,
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

      <!-- Active Runs Panel -->
      <app-active-runs-panel></app-active-runs-panel>

      <!-- Run History Table -->
      <app-run-history-table></app-run-history-table>
    </div>
  `,
})
export class ExecutionMonitorComponent { }
