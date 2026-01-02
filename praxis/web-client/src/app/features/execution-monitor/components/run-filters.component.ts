import { Component, inject, signal, output, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';

import { ProtocolService } from '../../protocols/services/protocol.service';
import { ProtocolDefinition } from '../../protocols/models/protocol.models';
import { RunStatus, RunHistoryParams } from '../models/monitor.models';

export interface FilterState {
  status: RunStatus[];
  protocol_id: string | string[] | null;
  sort_by: 'created_at' | 'start_time' | 'status';
  sort_order: 'asc' | 'desc';
}

/**
 * Filter controls for run history.
 * Emits filter changes to parent component.
 */
@Component({
  selector: 'app-run-filters',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatSelectModule,
    MatFormFieldModule,
    MatChipsModule,
    MatIconModule,
    MatButtonModule,
    MatButtonToggleModule,
  ],
  template: `
    <div class="filters-container flex flex-wrap items-center gap-4 p-4 rounded-xl border border-[var(--theme-border)] bg-surface-container mb-4">
      <!-- Status Filter -->
      <div class="filter-group">
        <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-2 block">Status</label>
        <mat-chip-listbox
          [multiple]="true"
          [(ngModel)]="selectedStatuses"
          (change)="onFilterChange()"
          aria-label="Filter by status">
          @for (status of allStatuses; track status) {
            <mat-chip-option [value]="status" [class]="getStatusChipClass(status)">
              {{ status }}
            </mat-chip-option>
          }
        </mat-chip-listbox>
      </div>

      <!-- Protocol Filter -->
      <div class="filter-group min-w-[200px]">
        <mat-form-field appearance="outline" class="w-full dense-field">
          <mat-label>Protocol</mat-label>
          <mat-select
            [multiple]="true"
            [(ngModel)]="selectedProtocolIds"
            (selectionChange)="onFilterChange()"
            placeholder="All protocols">
            <!-- <mat-option [value]="null">All protocols</mat-option> -->
            @for (protocol of protocols(); track protocol.accession_id) {
              <mat-option [value]="protocol.accession_id">
                {{ protocol.name }}
              </mat-option>
            }
          </mat-select>
        </mat-form-field>
      </div>

      <!-- Sort By -->
      <div class="filter-group min-w-[160px]">
        <mat-form-field appearance="outline" class="w-full dense-field">
          <mat-label>Sort by</mat-label>
          <mat-select
            [(ngModel)]="sortBy"
            (selectionChange)="onFilterChange()">
            <mat-option value="created_at">Date Created</mat-option>
            <mat-option value="start_time">Start Time</mat-option>
            <mat-option value="status">Status</mat-option>
          </mat-select>
        </mat-form-field>
      </div>

      <!-- Sort Order Toggle -->
      <div class="filter-group">
        <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-2 block">Order</label>
        <mat-button-toggle-group
          [(ngModel)]="sortOrder"
          (change)="onFilterChange()"
          aria-label="Sort order">
          <mat-button-toggle value="desc" aria-label="Newest first">
            <mat-icon>arrow_downward</mat-icon>
          </mat-button-toggle>
          <mat-button-toggle value="asc" aria-label="Oldest first">
            <mat-icon>arrow_upward</mat-icon>
          </mat-button-toggle>
        </mat-button-toggle-group>
      </div>

      <!-- Clear Filters -->
      @if (hasActiveFilters()) {
        <button
          mat-stroked-button
          (click)="clearFilters()"
          class="ml-auto"
          aria-label="Clear all filters">
          <mat-icon>filter_alt_off</mat-icon>
          Clear
        </button>
      }
    </div>
  `,
  styles: [`
    .filters-container {
      container-type: inline-size;
    }

    .filter-group {
      flex-shrink: 0;
    }

    /* Dense form fields */
    :host ::ng-deep .dense-field {
      .mat-mdc-form-field-subscript-wrapper {
        display: none;
      }
      .mat-mdc-text-field-wrapper {
        height: 40px;
      }
      .mat-mdc-form-field-flex {
        height: 40px;
      }
    }

    /* Status chip colors */
    .status-running {
      --mdc-chip-elevated-selected-container-color: rgba(34, 197, 94, 0.2);
      --mdc-chip-selected-label-text-color: rgb(34, 197, 94);
    }
    .status-completed {
      --mdc-chip-elevated-selected-container-color: rgba(107, 114, 128, 0.2);
      --mdc-chip-selected-label-text-color: rgb(107, 114, 128);
    }
    .status-failed {
      --mdc-chip-elevated-selected-container-color: rgba(239, 68, 68, 0.2);
      --mdc-chip-selected-label-text-color: rgb(239, 68, 68);
    }
    .status-queued, .status-preparing {
      --mdc-chip-elevated-selected-container-color: rgba(245, 158, 11, 0.2);
      --mdc-chip-selected-label-text-color: rgb(245, 158, 11);
    }
    .status-pending {
      --mdc-chip-elevated-selected-container-color: rgba(59, 130, 246, 0.2);
      --mdc-chip-selected-label-text-color: rgb(59, 130, 246);
    }
    .status-cancelled {
      --mdc-chip-elevated-selected-container-color: rgba(156, 163, 175, 0.2);
      --mdc-chip-selected-label-text-color: rgb(156, 163, 175);
    }
    .status-paused {
      --mdc-chip-elevated-selected-container-color: rgba(234, 179, 8, 0.2);
      --mdc-chip-selected-label-text-color: rgb(234, 179, 8);
    }

    /* Responsive: stack on small containers */
    @container (max-width: 600px) {
      .filters-container {
        flex-direction: column;
        align-items: stretch;
      }
      .filter-group {
        width: 100%;
      }
    }
  `],
})
export class RunFiltersComponent implements OnInit {
  private readonly protocolService = inject(ProtocolService);

  /** Emits when filters change */
  readonly filtersChange = output<FilterState>();

  readonly protocols = signal<ProtocolDefinition[]>([]);

  readonly allStatuses: RunStatus[] = [
    'RUNNING',
    'QUEUED',
    'PENDING',
    'COMPLETED',
    'FAILED',
    'CANCELLED',
    'PAUSED',
  ];

  // Filter state
  selectedStatuses: RunStatus[] = [];
  selectedProtocolIds: string[] = [];
  sortBy: 'created_at' | 'start_time' | 'status' = 'created_at';
  sortOrder: 'asc' | 'desc' = 'desc';

  ngOnInit(): void {
    this.loadProtocols();
  }

  private loadProtocols(): void {
    this.protocolService.getProtocols().subscribe({
      next: (protocols) => {
        this.protocols.set(protocols);
      },
      error: (err) => {
        console.error('[RunFilters] Failed to load protocols:', err);
      },
    });
  }

  onFilterChange(): void {
    this.filtersChange.emit(this.getCurrentFilters());
  }

  getCurrentFilters(): FilterState {
    return {
      status: this.selectedStatuses,
      protocol_id: this.selectedProtocolIds.length ? this.selectedProtocolIds : null,
      sort_by: this.sortBy,
      sort_order: this.sortOrder,
    };
  }

  hasActiveFilters(): boolean {
    return (
      this.selectedStatuses.length > 0 ||
      this.selectedProtocolIds.length > 0 ||
      this.sortBy !== 'created_at' ||
      this.sortOrder !== 'desc'
    );
  }

  clearFilters(): void {
    this.selectedStatuses = [];
    this.selectedProtocolIds = [];
    this.sortBy = 'created_at';
    this.sortOrder = 'desc';
    this.onFilterChange();
  }

  getStatusChipClass(status: RunStatus): string {
    return `status-${status.toLowerCase()}`;
  }
}
