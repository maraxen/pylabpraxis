import { Component, input, output, computed, OnInit, Input } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatInputModule } from '@angular/material/input';
import { Machine, MachineStatus, MachineDefinition } from '../../models/asset.models';
import { getMachineCategoryIcon } from '@shared/constants/asset-icons';
import { extractUniqueNameParts } from '../../../../shared/utils/name-parser';
import { PraxisSelectComponent, SelectOption } from '@shared/components/praxis-select/praxis-select.component';
import { PraxisMultiselectComponent } from '@shared/components/praxis-multiselect/praxis-multiselect.component';

export type MachineSortOption = 'name' | 'category' | 'created_at' | 'status';

export interface MachineFilterState {
  search: string;
  status: MachineStatus[];
  categories: string[];
  simulated: boolean | null;  // null = all, true = simulated only, false = physical only
  backends: string[];
  sort_by: MachineSortOption;
  sort_order: 'asc' | 'desc';
}

/**
 * Chip-based filter controls for the Machine Registry.
 * 
 * Provides filtering by:
 * - Search (text)
 * - Category (LiquidHandler, PlateReader, HeaterShaker, etc.)
 * - Simulated (filter by is_simulated flag)
 * - Status (idle, running, error, offline)
 * - Backend (STAR, OT2, Chatterbox, Simulator)
 */
@Component({
  selector: 'app-machine-filters',
  standalone: true,
  imports: [
    FormsModule,
    MatFormFieldModule,
    MatChipsModule,
    MatIconModule,
    MatTooltipModule,
    MatInputModule,
    MatButtonToggleModule,
    PraxisSelectComponent,
    PraxisMultiselectComponent
  ],
  template: `
    <div class="filters-container">
      <div class="filters-row selectors-row">
        <!-- Category Filter -->
        <div class="filter-group">
          <label class="filter-label">Category</label>
          <app-praxis-multiselect
            placeholder="Category"
            [options]="mappedCategoryOptions()"
            [value]="selectedCategories"
            (valueChange)="selectedCategories = $any($event); onFilterChange()"
          ></app-praxis-multiselect>
        </div>

        <!-- Status Filter -->
        <div class="filter-group">
          <label class="filter-label">Status</label>
          <app-praxis-multiselect
            placeholder="Status"
            [options]="mappedStatusOptions()"
            [value]="selectedStatuses"
            (valueChange)="selectedStatuses = $any($event); onFilterChange()"
          ></app-praxis-multiselect>
        </div>

        <!-- Backend Filter (if backends available) -->
        @if (availableBackends().length > 0) {
          <div class="filter-group">
            <label class="filter-label">Backend</label>
            <app-praxis-multiselect
              placeholder="Backend"
              [options]="mappedBackendOptions()"
              [value]="selectedBackends"
              (valueChange)="selectedBackends = $any($event); onFilterChange()">
            </app-praxis-multiselect>
          </div>
        }
      </div>

      <div class="filters-row toggles-row">
        <!-- Simulated Filter Toggle -->
        <div class="filter-group toggle-group">
          <label class="filter-label">Mode</label>
          <mat-button-toggle-group
            hideSingleSelectionIndicator
            [(ngModel)]="simulatedFilter"
            (change)="onFilterChange()"
            aria-label="Filter by simulation mode"
            class="praxis-toggle-group"
          >
            <mat-button-toggle [value]="null" matTooltip="Show all machines">
              All
            </mat-button-toggle>
            <mat-button-toggle [value]="false" matTooltip="Physical hardware only">
              <mat-icon>precision_manufacturing</mat-icon>
              Physical
            </mat-button-toggle>
            <mat-button-toggle [value]="true" matTooltip="Simulated only">
              <mat-icon>computer</mat-icon>
              Simulated
            </mat-button-toggle>
          </mat-button-toggle-group>
        </div>

        <!-- Sort Controls -->
        <div class="filter-group sort-group">
          <label class="filter-label">Sort</label>
          <div class="sort-controls">
            <app-praxis-select
              placeholder="Sort by"
              [options]="sortOptions"
              [(ngModel)]="sortBy"
              (ngModelChange)="onFilterChange()"
              class="sort-field-select"
            >
            </app-praxis-select>
            <mat-button-toggle-group
              hideSingleSelectionIndicator
              [(ngModel)]="sortOrder"
              (change)="onFilterChange()"
              aria-label="Sort order"
              class="praxis-toggle-group"
            >
              <mat-button-toggle value="asc" aria-label="Ascending">
                <mat-icon>arrow_upward</mat-icon>
              </mat-button-toggle>
              <mat-button-toggle value="desc" aria-label="Descending">
                <mat-icon>arrow_downward</mat-icon>
              </mat-button-toggle>
            </mat-button-toggle-group>
          </div>
        </div>

        <!-- Clear Filters -->
        @if (hasActiveFilters()) {
          <div class="filter-group clear-group">
            <button
              mat-stroked-button
              (click)="clearFilters()"
              class="clear-btn"
              aria-label="Clear all filters"
            >
              <mat-icon>filter_alt_off</mat-icon>
              Clear
            </button>
          </div>
        }
      </div>
    </div>
  `,
  styles: [`
    .filters-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 16px;
      border-radius: 12px;
      border: 1px solid var(--mat-sys-outline-variant);
      background: var(--mat-sys-surface-container);
      margin-bottom: 16px;
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

    .toggle-group {
        min-width: 200px;
    }

    .sort-group {
        flex: 1;
        min-width: 300px;
    }

    .filter-label {
      display: block;
      font-size: 0.75rem;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--mat-sys-on-surface-variant);
      margin-bottom: 8px;
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

    .sort-controls {
      display: flex;
      gap: 8px;
      align-items: center;
    }

    :host ::ng-deep .sort-field-select {
      width: 160px;
    }

    .clear-group {
        margin-left: auto;
        display: flex;
        align-items: center;
    }

    .clear-btn {
      height: 40px;
      border-radius: 8px;
    }

    :host ::ng-deep .chip-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
      margin-right: 4px;
    }
  `],
})
export class MachineFiltersComponent implements OnInit {
  /** List of machines to derive available filters from */
  machines = input<Machine[]>([]);

  /** List of machine definitions for backend information */
  machineDefinitions = input<MachineDefinition[]>([]);

  /** Emits when filters change */
  filtersChange = output<MachineFilterState>();

  // Filter state
  @Input() set search(value: string) {
    this.searchTerm = value;
    this.onFilterChange();
  }
  searchTerm = '';
  selectedStatuses: MachineStatus[] = [];
  selectedCategories: string[] = [];
  simulatedFilter: boolean | null = null;
  selectedBackends: string[] = [];
  sortBy: MachineSortOption = 'name';
  sortOrder: 'asc' | 'desc' = 'asc';

  // Computed available options based on input machines
  availableCategories = computed(() => {
    const cats = new Set<string>();
    this.machines().forEach(m => {
      if (m.machine_category) cats.add(m.machine_category);
    });
    return Array.from(cats).sort();
  });

  availableBackends = computed(() => {
    const backends = new Set<string>();
    this.machineDefinitions().forEach(def => {
      if (def.compatible_backends) {
        def.compatible_backends.forEach(b => backends.add(b));
      }
    });
    return Array.from(backends).sort();
  });

  categoryMappings = computed(() => {
    return extractUniqueNameParts(this.availableCategories());
  });

  backendMappings = computed(() => {
    return extractUniqueNameParts(this.availableBackends());
  });

  readonly CHIP_COLLAPSE_THRESHOLD = 5;

  shouldCollapseBackends = computed(() =>
    this.availableBackends().length > this.CHIP_COLLAPSE_THRESHOLD
  );

  readonly sortOptions: SelectOption[] = [
    { label: 'Name', value: 'name' },
    { label: 'Category', value: 'category' },
    { label: 'Status', value: 'status' },
    { label: 'Date Added', value: 'created_at' }
  ];

  mappedCategoryOptions = computed(() => {
    return this.availableCategories().map(cat => ({
      label: this.categoryMappings().get(cat) || cat,
      value: cat,
      icon: this.getCategoryIcon(cat)
    }));
  });

  mappedStatusOptions = computed(() => {
    return [
      { label: 'Idle', value: 'idle' as MachineStatus, icon: 'hourglass_empty' },
      { label: 'Running', value: 'running' as MachineStatus, icon: 'play_arrow' },
      { label: 'Error', value: 'error' as MachineStatus, icon: 'error_outline' },
      { label: 'Offline', value: 'offline' as MachineStatus, icon: 'wifi_off' },
      { label: 'Maintenance', value: 'maintenance' as MachineStatus, icon: 'build' }
    ];
  });

  mappedBackendOptions = computed(() => {
    return this.availableBackends().map(backend => ({
      label: this.backendMappings().get(backend) || backend,
      value: backend
    }));
  });

  ngOnInit(): void {
    // Emit initial filter state
    this.onFilterChange();
  }

  onFilterChange(): void {
    this.filtersChange.emit(this.getCurrentFilters());
  }

  getCurrentFilters(): MachineFilterState {
    return {
      search: this.searchTerm,
      status: this.selectedStatuses,
      categories: this.selectedCategories,
      simulated: this.simulatedFilter,
      backends: this.selectedBackends,
      sort_by: this.sortBy,
      sort_order: this.sortOrder,
    };
  }

  hasActiveFilters(): boolean {
    return (
      this.searchTerm !== '' ||
      this.selectedStatuses.length > 0 ||
      this.selectedCategories.length > 0 ||
      this.simulatedFilter !== null ||
      this.selectedBackends.length > 0 ||
      this.sortBy !== 'name' ||
      this.sortOrder !== 'asc'
    );
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.selectedStatuses = [];
    this.selectedCategories = [];
    this.simulatedFilter = null;
    this.selectedBackends = [];
    this.sortBy = 'name';
    this.sortOrder = 'asc';
    this.onFilterChange();
  }

  getCategoryIcon(category: string): string {
    return getMachineCategoryIcon(category);
  }
}
