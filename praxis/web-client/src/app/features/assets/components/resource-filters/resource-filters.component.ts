import { Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatInputModule } from '@angular/material/input';
import { Machine, ResourceStatus } from '../../models/asset.models';
import { getResourceCategoryIcon } from '@shared/constants/asset-icons';

export type ResourceSortOption = 'name' | 'category' | 'count';

export interface ResourceFilterState {
  search: string;
  status: string[];
  category: string[];
  machine_id: string | null;
  show_discarded: boolean;
  sort_by: ResourceSortOption;
  sort_order: 'asc' | 'desc';
}

@Component({
  selector: 'app-resource-filters',
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
    MatSlideToggleModule,
    MatInputModule
  ],
  template: `
    <div class="filters-container flex flex-wrap items-center gap-4 p-4 rounded-xl border border-[var(--theme-border)] bg-surface-container mb-4">
      
      <!-- Search Input -->
      <div class="filter-group min-w-[200px] flex-1">
        <mat-form-field appearance="outline" class="w-full dense-field">
          <mat-icon matPrefix>search</mat-icon>
          <input matInput 
                 placeholder="Search resources..." 
                 [(ngModel)]="searchTerm"
                 (ngModelChange)="onFilterChange()">
          @if (searchTerm) {
            <button matSuffix mat-icon-button aria-label="Clear" (click)="searchTerm=''; onFilterChange()">
              <mat-icon>close</mat-icon>
            </button>
          }
        </mat-form-field>
      </div>

      <!-- Resource Type (Category) Filter -->
      <div class="filter-group min-w-[160px]">
        <mat-form-field appearance="outline" class="w-full dense-field">
          <mat-label>Type</mat-label>
          <mat-select
            [multiple]="true"
            [(ngModel)]="selectedCategories"
            (selectionChange)="onFilterChange()"
            placeholder="All types">
            @for (cat of categories(); track cat) {
              <mat-option [value]="cat">
                <mat-icon class="align-middle mr-2 text-sys-primary">{{ getCategoryIcon(cat) }}</mat-icon>
                {{ cat }}
              </mat-option>
            }
          </mat-select>
        </mat-form-field>
      </div>

      <!-- Location (Machine) Filter -->
      <div class="filter-group min-w-[160px]">
        <mat-form-field appearance="outline" class="w-full dense-field">
          <mat-label>Location</mat-label>
          <mat-select
            [(ngModel)]="selectedMachineId"
            (selectionChange)="onFilterChange()"
            placeholder="Any location">
            <mat-option [value]="null">Any location</mat-option>
            @for (machine of machines(); track machine.accession_id) {
              <mat-option [value]="machine.accession_id">{{ machine.name }}</mat-option>
            }
          </mat-select>
        </mat-form-field>
      </div>

      <!-- Status Filter Chips -->
      <div class="filter-group">
        <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-2 block">Status</label>
        <mat-chip-listbox
          [multiple]="true"
          [(ngModel)]="selectedStatuses"
          (change)="onFilterChange()"
          aria-label="Filter by status">
            <mat-chip-option value="available" class="status-available">Available</mat-chip-option>
            <mat-chip-option value="in_use" class="status-in_use">In Use</mat-chip-option>
            <mat-chip-option value="reserved" class="status-reserved">Reserved</mat-chip-option>
        </mat-chip-listbox>
      </div>

      <!-- Sort By -->
      <div class="filter-group min-w-[140px]">
        <mat-form-field appearance="outline" class="w-full dense-field">
          <mat-label>Sort by</mat-label>
          <mat-select
            [(ngModel)]="sortBy"
            (selectionChange)="onFilterChange()">
            <mat-option value="name">Name</mat-option>
            <mat-option value="category">Type</mat-option>
            <mat-option value="count">Quantity</mat-option>
          </mat-select>
        </mat-form-field>
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

      <!-- Show Discarded Toggle -->
      <div class="filter-group flex flex-col justify-end pb-1">
        <mat-slide-toggle
            [(ngModel)]="showDiscarded"
            (change)="onFilterChange()"
            color="warn">
            Show Discarded
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
      .mat-mdc-form-field-icon-prefix { padding: 8px 0 0 8px; }
    }

    /* Status Chip Colors */
    .status-available { --mdc-chip-elevated-selected-container-color: rgba(34, 197, 94, 0.2); --mdc-chip-selected-label-text-color: rgb(34, 197, 94); }
    .status-in_use { --mdc-chip-elevated-selected-container-color: rgba(59, 130, 246, 0.2); --mdc-chip-selected-label-text-color: rgb(59, 130, 246); }
    .status-reserved { --mdc-chip-elevated-selected-container-color: rgba(168, 85, 247, 0.2); --mdc-chip-selected-label-text-color: rgb(168, 85, 247); }
  `]
})
export class ResourceFiltersComponent {
  categories = input<string[]>([]);
  machines = input<Machine[]>([]);

  filtersChange = output<ResourceFilterState>();

  searchTerm = '';
  selectedStatuses: string[] = [];
  selectedCategories: string[] = [];
  selectedMachineId: string | null = null;
  showDiscarded = false;
  sortBy: ResourceSortOption = 'name';
  sortOrder: 'asc' | 'desc' = 'asc';

  onFilterChange(): void {
    this.filtersChange.emit(this.getCurrentFilters());
  }

  getCurrentFilters(): ResourceFilterState {
    return {
      search: this.searchTerm,
      status: this.selectedStatuses,
      category: this.selectedCategories,
      machine_id: this.selectedMachineId,
      show_discarded: this.showDiscarded,
      sort_by: this.sortBy,
      sort_order: this.sortOrder
    };
  }

  hasActiveFilters(): boolean {
    return (
      this.searchTerm !== '' ||
      this.selectedStatuses.length > 0 ||
      this.selectedCategories.length > 0 ||
      this.selectedMachineId !== null ||
      this.showDiscarded ||
      this.sortBy !== 'name' || // Default sort might be name asc
      this.sortOrder !== 'asc'
    );
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.selectedStatuses = [];
    this.selectedCategories = [];
    this.selectedMachineId = null;
    this.showDiscarded = false;
    this.sortBy = 'name';
    this.sortOrder = 'asc';
    this.onFilterChange();
  }

  getCategoryIcon(cat: string): string {
    return getResourceCategoryIcon(cat);
  }
}
