import { Component, inject, signal, output, OnInit, input, effect, computed } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatTooltipModule } from '@angular/material/tooltip';
import { AriaSelectComponent, SelectOption } from '../../../../shared/components/aria-select/aria-select.component';
import { AriaMultiselectComponent } from '../../../../shared/components/aria-multiselect/aria-multiselect.component';
import { Machine, Workcell } from '../../models/asset.models';
import { extractUniqueNameParts } from '../../../../shared/utils/name-parser';

export type AssetSortOption =
  | 'name'
  | 'category'
  | 'created_at'
  //   | 'last_used_at' 
  | 'status'
  | 'machine_location_accession_id'
  | 'workcell_accession_id';

export interface AssetFilterState {
  status: string[];
  search: string;
  category: string[];
  machine_id: string | null;
  workcell_id: string | null;
  maintenance_due: boolean;
  sort_by: AssetSortOption;
  sort_order: 'asc' | 'desc';
}

@Component({
  selector: 'app-asset-filters',
  standalone: true,
  imports: [
    FormsModule,
    MatFormFieldModule,
    MatChipsModule,
    MatIconModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatSlideToggleModule,
    MatTooltipModule,
    MatInputModule,
    AriaSelectComponent,
    AriaMultiselectComponent
  ],
  template: `
    <div class="filters-container flex flex-wrap items-center gap-4 p-4 rounded-xl border border-[var(--theme-border)] bg-surface-container mb-2">
      
      <!-- Text Search -->
      <div class="filter-group min-w-[200px] flex-1">
        <mat-form-field appearance="outline" class="w-full dense-field">
          <mat-icon matPrefix>search</mat-icon>
          <input matInput [(ngModel)]="searchTerm" (input)="onFilterChange()" placeholder="Search assets...">
          @if (searchTerm) {
            <button matSuffix mat-icon-button aria-label="Clear" (click)="searchTerm = ''; onFilterChange()">
              <mat-icon>close</mat-icon>
            </button>
          }
        </mat-form-field>
      </div>

      <!-- Status Filter -->
      <div class="filter-group min-w-[200px]">
        <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-1 block">Status</label>
        <app-aria-multiselect
          label="Status"
          [options]="mappedStatusOptions()"
          [selectedValue]="selectedStatuses"
          [multiple]="true"
          (selectedValueChange)="selectedStatuses = $event; onFilterChange()"
        ></app-aria-multiselect>
      </div>

      <!-- Category Filter -->
      <div class="filter-group min-w-[200px]">
        <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-1 block">Category</label>
        <app-aria-multiselect
          label="Category"
          [options]="mappedCategoryOptions()"
          [selectedValue]="selectedCategories"
          [multiple]="true"
          (selectedValueChange)="selectedCategories = $event; onFilterChange()"
        ></app-aria-multiselect>
      </div>

      <!-- Machine Location Filter (for Resources) -->
      @if (showMachineFilter()) {
        <div class="filter-group min-w-[200px]">
          <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-1 block">Location</label>
          <app-aria-select
            label="Location"
            [options]="mappedMachineOptions()"
            [(ngModel)]="selectedMachineId"
            (ngModelChange)="onFilterChange()"
            [placeholder]="'Any location'"
          ></app-aria-select>
        </div>
      }

      <!-- Workcell Filter -->
      @if (showWorkcellFilter()) {
        <div class="filter-group min-w-[200px]">
          <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-1 block">Workcell</label>
          <app-aria-select
            label="Workcell"
            [options]="mappedWorkcellOptions()"
            [(ngModel)]="selectedWorkcellId"
            (ngModelChange)="onFilterChange()"
            [placeholder]="'Any workcell'"
          ></app-aria-select>
        </div>
      }

      <!-- Sort By -->
      <div class="filter-group min-w-[200px]">
        <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-1 block">Sort by</label>
        <app-aria-select
          label="Sort by"
          [options]="mappedSortOptions()"
          [(ngModel)]="sortBy"
          (ngModelChange)="onFilterChange()"
        ></app-aria-select>
      </div>

      <!-- Sort Order -->
      <div class="filter-group">
        <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-2 block">Order</label>
        <mat-button-toggle-group
          hideSingleSelectionIndicator
          [(ngModel)]="sortOrder"
          (change)="onFilterChange()"
          aria-label="Sort order">
          <mat-button-toggle value="asc" aria-label="Ascending">
            <mat-icon>arrow_upward</mat-icon>
          </mat-button-toggle>
          <mat-button-toggle value="desc" aria-label="Descending">
            <mat-icon>arrow_downward</mat-icon>
          </mat-button-toggle>
        </mat-button-toggle-group>
      </div>

      <!-- Maintenance Toggle -->
      <div class="filter-group flex flex-col justify-end pb-1">
        <mat-slide-toggle
            [(ngModel)]="maintenanceDue"
            (change)="onFilterChange()"
            color="warn">
            Maintenance Due
        </mat-slide-toggle>
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
    .filters-container { container-type: inline-size; }
    .filter-group { flex-shrink: 0; }
    
    :host ::ng-deep .dense-field {
      .mat-mdc-form-field-subscript-wrapper { display: none; }
      .mat-mdc-text-field-wrapper { height: 40px; }
      .mat-mdc-form-field-flex { height: 40px; }
    }

    /* Status Chip Colors */
    .status-available { --mdc-chip-elevated-selected-container-color: rgba(34, 197, 94, 0.2); --mdc-chip-selected-label-text-color: rgb(34, 197, 94); }
    .status-in_use { --mdc-chip-elevated-selected-container-color: rgba(59, 130, 246, 0.2); --mdc-chip-selected-label-text-color: rgb(59, 130, 246); }
    .status-error { --mdc-chip-elevated-selected-container-color: rgba(239, 68, 68, 0.2); --mdc-chip-selected-label-text-color: rgb(239, 68, 68); }
    .status-maintenance { --mdc-chip-elevated-selected-container-color: rgba(245, 158, 11, 0.2); --mdc-chip-selected-label-text-color: rgb(245, 158, 11); }
  `]
})
export class AssetFiltersComponent {
  categories = input<string[]>([]);
  machines = input<Machine[]>([]);
  workcells = input<Workcell[]>([]);
  showMachineFilter = input<boolean>(false);
  showWorkcellFilter = input<boolean>(false);

  filtersChange = output<AssetFilterState>();

  categoryMappings = computed(() => {
    return extractUniqueNameParts(this.categories());
  });

  mappedCategoryOptions = computed(() => {
    return this.categories().map(cat => ({
      label: this.categoryMappings().get(cat) || cat,
      value: cat
    }));
  });

  mappedStatusOptions = computed<SelectOption[]>(() => [
    { label: 'Available', value: 'available', icon: 'check_circle' },
    { label: 'In Use', value: 'in_use', icon: 'play_circle' },
    { label: 'Error', value: 'error', icon: 'error' },
    { label: 'Maintenance', value: 'maintenance', icon: 'build' }
  ]);

  mappedMachineOptions = computed(() => {
    return [
      { label: 'Any location', value: null },
      ...this.machines().map(m => ({ label: m.name, value: m.accession_id }))
    ];
  });

  mappedWorkcellOptions = computed(() => {
    return [
      { label: 'Any workcell', value: null },
      ...this.workcells().map(w => ({ label: w.name, value: w.accession_id }))
    ];
  });

  private sortOptions: SelectOption[] = [
    { label: 'Name', value: 'name' },
    { label: 'Category', value: 'category' },
    { label: 'Date Added', value: 'created_at' },
    { label: 'Status', value: 'status' }
  ];

  mappedSortOptions = computed(() => {
    const options = [...this.sortOptions];
    if (this.showMachineFilter()) {
      options.push({ label: 'Location', value: 'machine_location_accession_id' });
    }
    return options;
  });

  selectedStatuses: string[] = [];
  selectedCategories: string[] = [];
  selectedMachineId: string | null = null;
  selectedWorkcellId: string | null = null;
  searchTerm: string = '';
  maintenanceDue = false;
  sortBy: AssetSortOption = 'created_at';
  sortOrder: 'asc' | 'desc' = 'desc';

  onFilterChange(): void {
    this.filtersChange.emit(this.getCurrentFilters());
  }

  getCurrentFilters(): AssetFilterState {
    return {
      status: this.selectedStatuses,
      search: this.searchTerm,
      category: this.selectedCategories,
      machine_id: this.selectedMachineId,
      workcell_id: this.selectedWorkcellId,
      maintenance_due: this.maintenanceDue,
      sort_by: this.sortBy,
      sort_order: this.sortOrder
    };
  }

  hasActiveFilters(): boolean {
    return (
      this.selectedStatuses.length > 0 ||
      this.selectedCategories.length > 0 ||
      this.selectedMachineId !== null ||
      this.selectedWorkcellId !== null ||
      this.searchTerm !== '' ||
      this.maintenanceDue ||
      this.sortBy !== 'created_at' ||
      this.sortOrder !== 'desc'
    );
  }

  clearFilters(): void {
    this.selectedStatuses = [];
    this.selectedCategories = [];
    this.selectedMachineId = null;
    this.selectedWorkcellId = null;
    this.searchTerm = '';
    this.maintenanceDue = false;
    this.sortBy = 'created_at';
    this.sortOrder = 'desc';
    this.onFilterChange();
  }
}
