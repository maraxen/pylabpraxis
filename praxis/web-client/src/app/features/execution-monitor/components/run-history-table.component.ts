import { Component, inject, signal, input, effect, OnInit } from '@angular/core';

import { RouterLink } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';

import { RunHistoryService } from '../services/run-history.service';
import { RunSummary, RunStatus } from '../models/monitor.models';
import { FilterState } from './run-filters.component';

/**
 * Displays a paginated table of historical protocol runs.
 */
@Component({
  selector: 'app-run-history-table',
  standalone: true,
  imports: [
    RouterLink,
    MatTableModule,
    MatPaginatorModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    NgxSkeletonLoaderModule
],
  template: `
    <div class="history-container">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-sys-text-primary">Run History</h2>
      </div>

      @if (isLoading() && runs().length === 0) {
        <div class="skeleton-container flex flex-col gap-3">
             <ngx-skeleton-loader count="1" appearance="line" [theme]="{ height: '48px', 'border-radius': '12px', 'margin-bottom': '0' }"></ngx-skeleton-loader>
             <ngx-skeleton-loader count="5" appearance="line" [theme]="{ height: '64px', 'border-radius': '12px', 'margin-bottom': '0' }"></ngx-skeleton-loader>
        </div>
      } @else if (runs().length === 0 && !isLoading()) {
        <div class="empty-state text-center py-12 text-sys-text-tertiary border border-[var(--theme-border)] rounded-2xl bg-surface">
          <mat-icon class="!w-16 !h-16 !text-[64px] opacity-30 mb-4">history</mat-icon>
          <p class="text-lg">No runs yet</p>
          <p class="text-sm opacity-70">Execute a protocol to see run history here</p>
        </div>
      } @else {
        <div class="table-container rounded-2xl border border-[var(--theme-border)] overflow-hidden bg-surface">
          <table mat-table [dataSource]="runs()" class="w-full">
            <!-- Status Column -->
            <ng-container matColumnDef="status">
              <th mat-header-cell *matHeaderCellDef class="!bg-surface-container">Status</th>
              <td mat-cell *matCellDef="let run" class="!py-3">
                <div class="flex items-center gap-2">
                  <mat-icon [class]="runHistoryService.getStatusColor(run.status)" class="!w-5 !h-5 !text-[20px]">
                    {{ runHistoryService.getStatusIcon(run.status) }}
                  </mat-icon>
                  <span class="text-sm font-medium">{{ run.status }}</span>
                </div>
              </td>
            </ng-container>

            <!-- Protocol Name Column -->
            <ng-container matColumnDef="protocol">
              <th mat-header-cell *matHeaderCellDef class="!bg-surface-container">Protocol</th>
              <td mat-cell *matCellDef="let run" class="!py-3">
                <span class="font-medium text-sys-text-primary">
                  {{ run.protocol_name || run.name || 'Unnamed' }}
                </span>
              </td>
            </ng-container>

            <!-- Started Column -->
            <ng-container matColumnDef="started">
              <th mat-header-cell *matHeaderCellDef class="!bg-surface-container">Started</th>
              <td mat-cell *matCellDef="let run" class="!py-3 text-sys-text-secondary">
                {{ formatDate(run.start_time || run.created_at) }}
              </td>
            </ng-container>

            <!-- Duration Column -->
            <ng-container matColumnDef="duration">
              <th mat-header-cell *matHeaderCellDef class="!bg-surface-container">Duration</th>
              <td mat-cell *matCellDef="let run" class="!py-3 text-sys-text-secondary">
                {{ runHistoryService.formatDuration(run.duration_ms) }}
              </td>
            </ng-container>

            <!-- Actions Column -->
            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef class="!bg-surface-container w-16"></th>
              <td mat-cell *matCellDef="let run" class="!py-3">
                <button mat-icon-button [routerLink]="['/app/monitor', run.accession_id]" aria-label="View run details">
                  <mat-icon>visibility</mat-icon>
                </button>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns;"
                class="hover:bg-surface-container cursor-pointer"
                [routerLink]="['/app/monitor', row.accession_id]"></tr>
          </table>
        </div>

        <mat-paginator
          [length]="totalRuns()"
          [pageSize]="pageSize"
          [pageSizeOptions]="[10, 25, 50]"
          (page)="onPageChange($event)"
          aria-label="Select page of runs"
          class="mt-4">
        </mat-paginator>
      }
    </div>
  `,
  styles: [`
    .history-container {
      margin-top: 24px;
    }
    table {
      width: 100%;
    }
    th.mat-header-cell {
      font-weight: 600;
      color: var(--mat-sys-on-surface-variant);
    }
    tr.mat-mdc-row:hover {
      background-color: var(--mat-sys-surface-variant);
    }
  `],
})
export class RunHistoryTableComponent implements OnInit {
  readonly runHistoryService = inject(RunHistoryService);

  /** Filter state from parent */
  readonly filters = input<FilterState | null>(null);

  readonly runs = signal<RunSummary[]>([]);
  readonly isLoading = signal(true);
  readonly totalRuns = signal(0);

  readonly displayedColumns = ['status', 'protocol', 'started', 'duration', 'actions'];
  readonly pageSize = 10;
  private currentOffset = 0;

  constructor() {
    // React to filter changes
    effect(() => {
      const currentFilters = this.filters();
      // Reset to first page when filters change
      this.currentOffset = 0;
      this.loadRuns();
    });
  }

  ngOnInit(): void {
    // Initial load handled by effect
  }

  loadRuns(): void {
    this.isLoading.set(true);
    const currentFilters = this.filters();

    this.runHistoryService
      .getRunHistory({
        limit: this.pageSize,
        offset: this.currentOffset,
        status: currentFilters?.status?.length ? currentFilters.status : undefined,
        protocol_id: currentFilters?.protocol_id ?? undefined,
        sort_by: currentFilters?.sort_by ?? 'created_at',
        sort_order: currentFilters?.sort_order ?? 'desc',
      })
      .subscribe({
        next: (runs) => {
          this.runs.set(runs);
          // For now, estimate total; backend should return this
          this.totalRuns.set(runs.length < this.pageSize ? this.currentOffset + runs.length : this.currentOffset + runs.length + 1);
          this.isLoading.set(false);
        },
        error: (err) => {
          console.error('[RunHistoryTable] Error loading runs:', err);
          this.isLoading.set(false);
        },
      });
  }

  onPageChange(event: PageEvent): void {
    this.currentOffset = event.pageIndex * event.pageSize;
    this.loadRuns();
  }

  formatDate(isoDate?: string): string {
    if (!isoDate) return '-';
    try {
      return new Date(isoDate).toLocaleString([], {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoDate;
    }
  }
}
