import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';

import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { interval, Subscription } from 'rxjs';
import { switchMap, startWith } from 'rxjs/operators';

import { RunHistoryService } from '../services/run-history.service';
import { RunSummary } from '../models/monitor.models';

/**
 * Displays a list of currently active (running, queued, pending) protocol runs.
 * Polls for updates every 5 seconds.
 */
@Component({
  selector: 'app-active-runs-panel',
  standalone: true,
  imports: [
    RouterLink,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule
  ],
  template: `
    <div class="praxis-card mb-6">
      <div class="card-header border-b border-[var(--theme-border)] bg-[var(--mat-sys-surface-variant)]">
        <div class="flex items-center justify-between w-full">
          <div class="flex items-center gap-2">
            <mat-icon class="text-[var(--mat-sys-success)]">play_circle</mat-icon>
            <h2 class="text-lg font-semibold text-sys-text-primary">Active Runs</h2>
            @if (isLoading()) {
              <mat-spinner diameter="18" class="ml-2"></mat-spinner>
            }
          </div>
        </div>
      </div>
      <div class="card-content">
        @if (activeRuns().length === 0 && !isLoading()) {
          <div class="empty-state text-center py-8 text-sys-text-tertiary opacity-60">
            <mat-icon class="!w-12 !h-12 !text-[48px] mb-2">hourglass_empty</mat-icon>
            <p>No active runs at the moment</p>
          </div>
        } @else {
          <div class="runs-list space-y-3">
            @for (run of activeRuns(); track run.accession_id) {
              <div class="praxis-card-min group cursor-pointer hover:bg-[var(--mat-sys-surface-variant)] transition-all"
                   routerLink="/app/monitor/{{ run.accession_id }}">
                <div class="flex items-center justify-between gap-3">
                  <div class="flex items-center gap-3 min-w-0">
                    <mat-icon [class]="runHistoryService.getStatusColor(run.status)">
                      {{ runHistoryService.getStatusIcon(run.status) }}
                    </mat-icon>
                    <div class="min-w-0">
                      <div class="font-medium text-sys-text-primary truncate group-hover:text-primary transition-colors">
                        {{ run.protocol_name || run.name || 'Unnamed Run' }}
                      </div>
                      <div class="text-xs text-sys-text-secondary truncate">
                        {{ run.status }} · Started {{ formatTime(run.start_time || run.created_at) }}
                      </div>
                    </div>
                  </div>
                  <mat-icon class="!w-4 !h-4 !text-[16px] opacity-0 group-hover:opacity-100 transition-opacity">chevron_right</mat-icon>
                </div>
              </div>
            }
          </div>
        }
      </div>
    </div>
  `,
  styles: [`
    /* Local overrides if any (none needed for now) */
  `],
})
export class ActiveRunsPanelComponent implements OnInit, OnDestroy {
  readonly runHistoryService = inject(RunHistoryService);

  readonly activeRuns = signal<RunSummary[]>([]);
  readonly isLoading = signal(true);

  private pollSubscription?: Subscription;
  private readonly POLL_INTERVAL_MS = 5000;

  ngOnInit(): void {
    // Poll for active runs every 5 seconds
    this.pollSubscription = interval(this.POLL_INTERVAL_MS)
      .pipe(
        startWith(0),
        switchMap(() => this.runHistoryService.getActiveRuns())
      )
      .subscribe({
        next: (runs) => {
          this.activeRuns.set(runs);
          this.isLoading.set(false);
        },
        error: (err) => {
          console.error('[ActiveRunsPanel] Error fetching active runs:', err);
          this.isLoading.set(false);
        },
      });
  }

  ngOnDestroy(): void {
    this.pollSubscription?.unsubscribe();
  }

  formatTime(isoDate?: string): string {
    if (!isoDate) return '-';
    try {
      return new Date(isoDate).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoDate;
    }
  }
}
