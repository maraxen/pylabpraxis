import { Component, inject, signal, output, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';

import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';

import { ProtocolService } from '../../protocols/services/protocol.service';
import { ProtocolDefinition } from '../../protocols/models/protocol.models';
import { RunStatus } from '../models/monitor.models';

import { PraxisMultiselectComponent } from '@shared/components/praxis-multiselect/praxis-multiselect.component';
import { PraxisSelectComponent, SelectOption } from '@shared/components/praxis-select/praxis-select.component';
import { FilterOption } from '@shared/services/filter-result.service';
import { computed } from '@angular/core';

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
    FormsModule,
    MatIconModule,
    MatButtonModule,
    MatButtonToggleModule,
    PraxisMultiselectComponent,
    PraxisSelectComponent
  ],
  templateUrl: './run-filters.component.html',
  styles: [`
    .filters-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
      /* Padding and border removed as it's inside accordion now */
      width: 100%;
    }

    .filters-row {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      align-items: flex-end;
    }

    .selectors-row {
      border-bottom: 1px solid var(--mat-sys-outline-variant);
      padding-bottom: 16px;
    }

    .filter-group {
      flex: 0 1 auto;
      min-width: 140px;
    }

    .sort-group {
        min-width: 200px;
    }

    .order-group {
        min-width: 120px;
    }

    .praxis-toggle-group {
        height: 40px;
        border-radius: 8px !important;
        overflow: hidden;
        border: 1px solid var(--mat-sys-outline-variant) !important;
        background: var(--mat-sys-surface) !important;
    }

    ::ng-deep .praxis-toggle-group .mat-button-toggle-label-content {
        line-height: 38px !important;
        padding: 0 12px !important;
        font-size: 13px !important;
    }

    .clear-group {
        margin-left: auto;
        display: flex;
        align-items: center;
        align-self: flex-end;
        padding-bottom: 2px;
    }

    .clear-btn {
      height: 40px;
      border-radius: 8px;
    }

    :host ::ng-deep .dense-field {
      .mat-mdc-form-field-subscript-wrapper { display: none; }
      .mat-mdc-text-field-wrapper { height: 40px; }
      .mat-mdc-form-field-flex { height: 40px; padding-top: 0; }
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

  readonly protocolOptions = computed(() =>
    this.protocols().map(p => ({
      label: p.name,
      value: p.accession_id
    }))
  );

  readonly sortOptions: SelectOption[] = [
    { label: 'Date Created', value: 'created_at' },
    { label: 'Start Time', value: 'start_time' },
    { label: 'Status', value: 'status' }
  ];

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

  // Helper to convert RunStatus strings to FilterOptions
  get statusOptions(): FilterOption[] {
    return this.allStatuses.map(status => ({
      label: this.formatStatus(status),
      value: status
    }));
  }

  private formatStatus(status: string): string {
    return status.charAt(0) + status.slice(1).toLowerCase();
  }

  onStatusChange(selected: RunStatus[]) {
    this.selectedStatuses = selected;
    this.onFilterChange();
  }

  onProtocolChange(selected: string[]) {
    this.selectedProtocolIds = selected;
    this.onFilterChange();
  }
}
