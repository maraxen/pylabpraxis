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
  templateUrl: './run-filters.component.html',
  styles: [`
    .filters-container {
      display: flex !important;
      flex-wrap: nowrap !important;
      align-items: center;
      gap: 1rem;
      overflow-x: auto !important;
      padding-bottom: 0.5rem;
      width: 100%;
      
      scrollbar-width: thin;
      &::-webkit-scrollbar {
        height: 4px;
      }
    }

    .filter-group {
      flex-shrink: 0;
    }

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
