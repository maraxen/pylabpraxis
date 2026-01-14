import { Component, effect, inject, input, OnDestroy, OnInit, signal } from '@angular/core';

import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { RouterLink } from '@angular/router';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';

import { RunSummary, FilterState } from '../models/monitor.models';
import { RunHistoryService } from '../services/run-history.service';

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
    <div class="history-container praxis-card mt-6">
      <div class="card-header border-b border-[var(--theme-border)] bg-[var(--mat-sys-surface-variant)]">
        <h2 class="text-xl font-semibold text-sys-text-primary">Run History</h2>
      </div>

      <div class="card-content !p-0">
        @if (isLoading() && runs().length === 0) {
          <div class="skeleton-container flex flex-col gap-3 p-4">
               <ngx-skeleton-loader count="1" appearance="line" [theme]="{ height: '48px', 'border-radius': '12px', 'margin-bottom': '0' }"></ngx-skeleton-loader>
               <ngx-skeleton-loader count="5" appearance="line" [theme]="{ height: '64px', 'border-radius': '12px', 'margin-bottom': '0' }"></ngx-skeleton-loader>
          </div>
        } @else if (runs().length === 0 && !isLoading()) {
          <div class="empty-state text-center py-12 text-sys-text-tertiary opacity-60">
            <mat-icon class="!w-16 !h-16 !text-[64px] mb-4">history</mat-icon>
            <p class="text-lg">No runs yet</p>
            <p class="text-sm">Execute a protocol to see run history here</p>
          </div>
        } @else {
          <div class="table-container overflow-hidden">
            <table mat-table [dataSource]="runs()" class="w-full">
              <!-- Status Column -->
              <ng-container matColumnDef="status">
                <th mat-header-cell *matHeaderCellDef class="!bg-[var(--mat-sys-surface-container)]">Status</th>
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
                <th mat-header-cell *matHeaderCellDef class="!bg-[var(--mat-sys-surface-container)]">Protocol</th>
                <td mat-cell *matCellDef="let run" class="!py-3">
                  <span class="font-medium text-sys-text-primary">
                    {{ run.protocol_name || run.name || 'Unnamed' }}
                  </span>
                </td>
              </ng-container>
  
              <!-- Started Column -->
              <ng-container matColumnDef="started">
                <th mat-header-cell *matHeaderCellDef class="!bg-[var(--mat-sys-surface-container)]">Started</th>
                <td mat-cell *matCellDef="let run" class="!py-3 text-sys-text-secondary">
                  {{ formatDate(run.start_time || run.created_at) }}
                </td>
              </ng-container>
  
              <!-- Duration Column -->
              <ng-container matColumnDef="duration">
                <th mat-header-cell *matHeaderCellDef class="!bg-[var(--mat-sys-surface-container)]">Duration</th>
                <td mat-cell *matCellDef="let run" class="!py-3 text-sys-text-secondary">
                  {{ runHistoryService.formatDuration(run.duration_ms) }}
                </td>
              </ng-container>
  
              <!-- Actions Column -->
              <ng-container matColumnDef="actions">
                <th mat-header-cell *matHeaderCellDef class="!bg-[var(--mat-sys-surface-container)] w-16"></th>
                <td mat-cell *matCellDef="let run" class="!py-3">
                  <button mat-icon-button [routerLink]="['/app/monitor', run.accession_id]" aria-label="View run details">
                    <mat-icon>visibility</mat-icon>
                  </button>
                </td>
              </ng-container>
  
              <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
              <tr mat-row *matRowDef="let row; columns: displayedColumns;"
                  class="hover:bg-[var(--mat-sys-surface-variant)] cursor-pointer"
                  [routerLink]="['/app/monitor', row.accession_id]"></tr>
            </table>
          </div>
        }
      </div>

      @if (runs().length > 0) {
        <div class="card-actions bg-[var(--mat-sys-surface-container)] !p-0">
          <mat-paginator
            [length]="totalRuns()"
            [pageSize]="pageSize"
            [pageSizeOptions]="[10, 25, 50]"
            (page)="onPageChange($event)"
            aria-label="Select page of runs"
            class="w-full !bg-transparent">
          </mat-paginator>
        </div>
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
export class RunHistoryTableComponent implements OnInit, OnDestroy {
  readonly runHistoryService = inject(RunHistoryService);

  /** Filter state from parent */
  readonly filters = input<FilterState | null>(null);
  readonly search = input<string>('');

  readonly runs = signal<RunSummary[]>([]);
  readonly isLoading = signal(true);
  readonly totalRuns = signal(0);

  readonly displayedColumns = ['status', 'protocol', 'started', 'duration', 'actions'];
  readonly pageSize = 10;
  private currentOffset = 0;
  private refreshInterval?: ReturnType<typeof setInterval>;

  constructor() {
    // React to filter/search changes
    effect(() => {
      const _currentFilters = this.filters();
      const _search = this.search();
      // Reset to first page when filters/search change
      this.currentOffset = 0;
      this.loadRuns();
    });
  }

  ngOnInit(): void {
    // Initial load handled by effect

    // Auto-refresh every 10 seconds
    this.refreshInterval = setInterval(() => {
      this.loadRuns();
    }, 10000);
  }

  ngOnDestroy(): void {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
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
        machine_id: currentFilters?.machine_id ?? undefined,
        sort_by: currentFilters?.sort_by ?? 'created_at',
        sort_order: currentFilters?.sort_order ?? 'desc',
        search: this.search() || undefined
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
