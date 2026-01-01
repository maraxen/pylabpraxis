import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
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
        CommonModule,
        RouterLink,
        MatCardModule,
        MatIconModule,
        MatButtonModule,
        MatProgressSpinnerModule,
    ],
    template: `
    <mat-card class="active-runs-card">
      <mat-card-header>
        <div class="flex items-center gap-2">
          <mat-icon class="text-green-500">play_circle</mat-icon>
          <mat-card-title>Active Runs</mat-card-title>
          @if (isLoading()) {
            <mat-spinner diameter="18" class="ml-2"></mat-spinner>
          }
        </div>
      </mat-card-header>
      <mat-card-content class="pt-4">
        @if (activeRuns().length === 0 && !isLoading()) {
          <div class="empty-state text-center py-8 text-sys-text-tertiary">
            <mat-icon class="!w-12 !h-12 !text-[48px] opacity-30 mb-2">hourglass_empty</mat-icon>
            <p>No active runs</p>
          </div>
        } @else {
          <div class="runs-list space-y-2">
            @for (run of activeRuns(); track run.accession_id) {
              <div class="run-item p-3 rounded-lg bg-surface-variant hover:bg-surface-container transition-colors cursor-pointer"
                   [routerLink]="['/app/monitor', run.accession_id]">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <mat-icon [class]="runHistoryService.getStatusColor(run.status)">
                      {{ runHistoryService.getStatusIcon(run.status) }}
                    </mat-icon>
                    <div>
                      <div class="font-medium text-sys-text-primary">
                        {{ run.protocol_name || run.name || 'Unnamed Run' }}
                      </div>
                      <div class="text-sm text-sys-text-secondary">
                        {{ run.status }} · Started {{ formatTime(run.start_time || run.created_at) }}
                      </div>
                    </div>
                  </div>
                  <button mat-icon-button [routerLink]="['/app/monitor', run.accession_id]" aria-label="View run details">
                    <mat-icon>chevron_right</mat-icon>
                  </button>
                </div>
              </div>
            }
          </div>
        }
      </mat-card-content>
    </mat-card>
  `,
    styles: [`
    .active-runs-card {
      background: var(--mat-sys-surface-container-low);
      border: 1px solid var(--mat-sys-outline-variant);
    }
    mat-card-header {
      padding-bottom: 0;
    }
    .run-item.running {
      border-left: 3px solid var(--mat-sys-primary);
    }
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
