import { Component, input, output, signal, computed, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { Machine, MachineStatus, MachineDefinition } from '../../models/asset.models';
import { getMachineCategoryIcon } from '@shared/constants/asset-icons';
import { extractUniqueNameParts } from '../../../../shared/utils/name-parser';
import { AriaSelectComponent, SelectOption } from '@shared/components/aria-select/aria-select.component';
import { AriaMultiselectComponent } from '@shared/components/aria-multiselect/aria-multiselect.component';

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
    MatSlideToggleModule,
    MatTooltipModule,
    MatInputModule,
    MatButtonToggleModule,
    AriaSelectComponent,
    AriaMultiselectComponent
  ],
  template: `
    <div class="filters-container">
      <!-- Search Input -->
      <div class="filter-group search-group">
        <mat-form-field appearance="outline" class="search-field praxis-search-field">
          <mat-icon matPrefix>search</mat-icon>
          <input
            matInput
            placeholder="Search machines..."
            [(ngModel)]="searchTerm"
            (ngModelChange)="onFilterChange()"
          />
          @if (searchTerm) {
            <button
              matSuffix
              mat-icon-button
              aria-label="Clear search"
              (click)="searchTerm = ''; onFilterChange()"
            >
              <mat-icon>close</mat-icon>
            </button>
          }
        </mat-form-field>
      </div>

      <!-- Category Filter -->
      <div class="filter-group">
        <label class="filter-label">Category</label>
        <app-aria-multiselect
          label="Category"
          [options]="mappedCategoryOptions()"
          [multiple]="true"
          [selectedValue]="selectedCategories"
          (selectedValueChange)="selectedCategories = $event; onFilterChange()"
        ></app-aria-multiselect>
      </div>

      <!-- Status Filter -->
      <div class="filter-group">
        <label class="filter-label">Status</label>
        <app-aria-multiselect
          label="Status"
          [options]="mappedStatusOptions()"
          [multiple]="true"
          [selectedValue]="selectedStatuses"
          (selectedValueChange)="selectedStatuses = $event; onFilterChange()"
        ></app-aria-multiselect>
      </div>

      <!-- Simulated Filter Toggle -->
      <div class="filter-group">
        <label class="filter-label">Mode</label>
        <mat-button-toggle-group
          hideSingleSelectionIndicator
          [(ngModel)]="simulatedFilter"
          (change)="onFilterChange()"
          aria-label="Filter by simulation mode"
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

      <!-- Backend Filter (if backends available) -->
      @if (availableBackends().length > 0) {
        <div class="filter-group">
          <label class="filter-label">Backend</label>
          <app-aria-multiselect
            label="Backend"
            [options]="mappedBackendOptions()"
            [multiple]="true"
            [selectedValue]="selectedBackends"
            (selectedValueChange)="selectedBackends = $event; onFilterChange()">
          </app-aria-multiselect>
        </div>
      }

      <!-- Sort Controls -->
      <div class="filter-group">
        <label class="filter-label">Sort</label>
        <div class="sort-controls">
          <app-aria-select
            label="Sort by"
            [options]="sortOptions"
            [(ngModel)]="sortBy"
            (ngModelChange)="onFilterChange()"
            class="sort-field-select"
          >
          </app-aria-select>
          <mat-button-toggle-group
            hideSingleSelectionIndicator
            [(ngModel)]="sortOrder"
            (change)="onFilterChange()"
            aria-label="Sort order"
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
        <button
          mat-stroked-button
          (click)="clearFilters()"
          class="clear-btn"
          aria-label="Clear all filters"
        >
          <mat-icon>filter_alt_off</mat-icon>
          Clear
        </button>
      }
    </div>
  `,
  styles: [`
    .filters-container {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-start;
      gap: 16px;
      padding: 16px;
      border-radius: 12px;
      border: 1px solid var(--mat-sys-outline-variant);
      background: var(--mat-sys-surface-container);
      margin-bottom: 16px;
    }

    .filter-group {
      flex-shrink: 0;
      max-width: 100%;
    }

    mat-chip-listbox {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      max-height: 120px;
      overflow-y: auto;
    }

    .chip-dropdown {
      width: 200px;
      :host ::ng-deep .mat-mdc-form-field-subscript-wrapper { display: none; }
      :host ::ng-deep .mat-mdc-text-field-wrapper { height: 40px; }
      :host ::ng-deep .mat-mdc-form-field-flex { height: 40px; }
    }

    .search-group {
      flex: 1;
      min-width: 200px;
      max-width: 300px;
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

    .search-field {
      width: 100%;
    }

    :host ::ng-deep .search-field,
    :host ::ng-deep .sort-field {
      .mat-mdc-form-field-subscript-wrapper { display: none; }
      .mat-mdc-text-field-wrapper { height: 40px; }
      .mat-mdc-form-field-flex { height: 40px; }
    }

    :host ::ng-deep .sort-field-select {
      width: 140px;
    }

    .sort-controls {
      display: flex;
      gap: 8px;
      align-items: flex-start;
    }

    :host ::ng-deep .chip-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
      margin-right: 4px;
    }

    .clear-btn {
      margin-left: auto;
      align-self: center;
    }

    /* Status chip colors */
    .status-idle {
      --mdc-chip-elevated-selected-container-color: rgba(34, 197, 94, 0.2);
      --mdc-chip-selected-label-text-color: rgb(34, 197, 94);
    }
    .status-running {
      --mdc-chip-elevated-selected-container-color: rgba(59, 130, 246, 0.2);
      --mdc-chip-selected-label-text-color: rgb(59, 130, 246);
    }
    .status-error {
      --mdc-chip-elevated-selected-container-color: rgba(239, 68, 68, 0.2);
      --mdc-chip-selected-label-text-color: rgb(239, 68, 68);
    }
    .status-offline {
      --mdc-chip-elevated-selected-container-color: rgba(107, 114, 128, 0.2);
      --mdc-chip-selected-label-text-color: rgb(107, 114, 128);
    }
    .status-maintenance {
      --mdc-chip-elevated-selected-container-color: rgba(245, 158, 11, 0.2);
      --mdc-chip-selected-label-text-color: rgb(245, 158, 11);
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
