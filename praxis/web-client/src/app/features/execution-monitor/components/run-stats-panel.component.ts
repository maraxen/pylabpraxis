import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { RunHistoryService } from '../services/run-history.service';
import { RunSummary } from '../models/monitor.models';

interface RunStats {
  totalRuns: number;
  runsToday: number;
  successRate: number;
  avgDurationMs: number;
  completedRuns: number;
  failedRuns: number;
}

/**
 * Displays summary statistics for protocol runs.
 * Shows runs/day, success rate, and average duration.
 */
@Component({
  selector: 'app-run-stats-panel',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatProgressSpinnerModule],
  template: `
    <div class="stats-grid">
      @if (isLoading()) {
        <div class="loading-overlay">
          <mat-spinner diameter="32"></mat-spinner>
        </div>
      } @else {
        <!-- Runs Today -->
        <div class="stat-card">
          <div class="stat-icon runs-today">
            <mat-icon>today</mat-icon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats().runsToday }}</span>
            <span class="stat-label">Runs Today</span>
          </div>
        </div>

        <!-- Total Runs -->
        <div class="stat-card">
          <div class="stat-icon total-runs">
            <mat-icon>history</mat-icon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats().totalRuns }}</span>
            <span class="stat-label">Total Runs</span>
          </div>
        </div>

        <!-- Success Rate -->
        <div class="stat-card">
          <div class="stat-icon success-rate" [class.warning]="stats().successRate < 80">
            <mat-icon>{{ stats().successRate >= 80 ? 'check_circle' : 'warning' }}</mat-icon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats().successRate | number:'1.0-0' }}%</span>
            <span class="stat-label">Success Rate</span>
          </div>
          <div class="stat-detail">
            {{ stats().completedRuns }} / {{ stats().completedRuns + stats().failedRuns }}
          </div>
        </div>

        <!-- Average Duration -->
        <div class="stat-card">
          <div class="stat-icon avg-duration">
            <mat-icon>timer</mat-icon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ formatDuration(stats().avgDurationMs) }}</span>
            <span class="stat-label">Avg Duration</span>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
      position: relative;
      min-height: 88px;
    }

    .loading-overlay {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--mat-sys-surface);
      border-radius: 16px;
      border: 1px solid var(--theme-border);
    }

    .stat-card {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 16px 20px;
      background: var(--mat-sys-surface);
      border: 1px solid var(--theme-border);
      border-radius: 16px;
      transition: all 0.2s ease;

      &:hover {
        border-color: var(--theme-border-hover, var(--theme-border));
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
      }
    }

    .stat-icon {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;

      mat-icon {
        width: 24px;
        height: 24px;
        font-size: 24px;
      }

      &.runs-today {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(99, 102, 241, 0.15));
        mat-icon { color: #3b82f6; }
      }

      &.total-runs {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(168, 85, 247, 0.15));
        mat-icon { color: #8b5cf6; }
      }

      &.success-rate {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(16, 185, 129, 0.15));
        mat-icon { color: #22c55e; }

        &.warning {
          background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(234, 179, 8, 0.15));
          mat-icon { color: #f59e0b; }
        }
      }

      &.avg-duration {
        background: linear-gradient(135deg, rgba(236, 72, 153, 0.15), rgba(219, 39, 119, 0.15));
        mat-icon { color: #ec4899; }
      }
    }

    .stat-content {
      display: flex;
      flex-direction: column;
      min-width: 0;
      flex: 1;
    }

    .stat-value {
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--theme-text-primary);
      line-height: 1.2;
    }

    .stat-label {
      font-size: 0.75rem;
      color: var(--theme-text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      font-weight: 500;
    }

    .stat-detail {
      font-size: 0.75rem;
      color: var(--theme-text-tertiary);
      white-space: nowrap;
    }
  `]
})
export class RunStatsPanelComponent implements OnInit {
  private readonly runHistoryService = inject(RunHistoryService);

  readonly isLoading = signal(true);
  readonly stats = signal<RunStats>({
    totalRuns: 0,
    runsToday: 0,
    successRate: 0,
    avgDurationMs: 0,
    completedRuns: 0,
    failedRuns: 0
  });

  ngOnInit(): void {
    this.loadStats();
  }

  private loadStats(): void {
    // Fetch a larger set of runs to calculate statistics
    this.runHistoryService.getRunHistory({ limit: 100 }).subscribe({
      next: (runs) => {
        this.calculateStats(runs);
        this.isLoading.set(false);
      },
      error: () => {
        this.isLoading.set(false);
      }
    });
  }

  private calculateStats(runs: RunSummary[]): void {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const runsToday = runs.filter(r => {
      const runDate = new Date(r.created_at);
      return runDate >= today;
    }).length;

    const completedRuns = runs.filter(r => r.status === 'COMPLETED').length;
    const failedRuns = runs.filter(r => r.status === 'FAILED').length;
    const finishedRuns = completedRuns + failedRuns;

    const successRate = finishedRuns > 0
      ? (completedRuns / finishedRuns) * 100
      : 100;

    const runsWithDuration = runs.filter(r => r.duration_ms && r.duration_ms > 0);
    const avgDurationMs = runsWithDuration.length > 0
      ? runsWithDuration.reduce((sum, r) => sum + (r.duration_ms || 0), 0) / runsWithDuration.length
      : 0;

    this.stats.set({
      totalRuns: runs.length,
      runsToday,
      successRate,
      avgDurationMs,
      completedRuns,
      failedRuns
    });
  }

  formatDuration(ms: number): string {
    if (!ms || ms === 0) return '-';
    return this.runHistoryService.formatDuration(ms);
  }
}
