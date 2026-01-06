import { Component, inject, signal, output, OnInit, input } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { Machine } from '../../models/asset.models';

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
    MatSelectModule,
    MatFormFieldModule,
    MatChipsModule,
    MatIconModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatSlideToggleModule
],
  template: `
    <div class="filters-container flex flex-wrap items-center gap-4 p-4 rounded-xl border border-[var(--theme-border)] bg-surface-container mb-2">
      
      <!-- Status Filter -->
      <div class="filter-group">
        <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-2 block">Status</label>
        <mat-chip-listbox
          [multiple]="true"
          [(ngModel)]="selectedStatuses"
          (change)="onFilterChange()"
          aria-label="Filter by status">
            <mat-chip-option value="available" class="status-available">Available</mat-chip-option>
            <mat-chip-option value="in_use" class="status-in_use">In Use</mat-chip-option>
            <mat-chip-option value="error" class="status-error">Error</mat-chip-option>
            <mat-chip-option value="maintenance" class="status-maintenance">Maintenance</mat-chip-option>
        </mat-chip-listbox>
      </div>

      <!-- Category Filter -->
      <div class="filter-group min-w-[160px]">
        <mat-form-field appearance="outline" class="w-full dense-field">
          <mat-label>Category</mat-label>
          <mat-select
            [multiple]="true"
            [(ngModel)]="selectedCategories"
            (selectionChange)="onFilterChange()"
            placeholder="All categories">
            @for (cat of categories(); track cat) {
              <mat-option [value]="cat">{{ cat }}</mat-option>
            }
          </mat-select>
        </mat-form-field>
      </div>

      <!-- Machine Location Filter (for Resources) -->
      @if (showMachineFilter()) {
        <div class="filter-group min-w-[160px]">
        <mat-form-field appearance="outline" class="w-full dense-field">
            <mat-label>Location (Machine)</mat-label>
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
      }

      <!-- Sort By -->
      <div class="filter-group min-w-[160px]">
        <mat-form-field appearance="outline" class="w-full dense-field">
          <mat-label>Sort by</mat-label>
          <mat-select
            [(ngModel)]="sortBy"
            (selectionChange)="onFilterChange()">
            <mat-option value="name">Name</mat-option>
            <mat-option value="category">Category</mat-option>
            <mat-option value="created_at">Date Added</mat-option>
            <mat-option value="status">Status</mat-option>
            @if (showMachineFilter()) {
                <mat-option value="machine_location_accession_id">Location</mat-option>
            }
            <!-- <mat-option value="last_used_at">Last Used</mat-option> -->
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
  showMachineFilter = input<boolean>(false);

  filtersChange = output<AssetFilterState>();

  selectedStatuses: string[] = [];
  selectedCategories: string[] = [];
  selectedMachineId: string | null = null;
  selectedWorkcellId: string | null = null;
  maintenanceDue = false;
  sortBy: AssetSortOption = 'created_at';
  sortOrder: 'asc' | 'desc' = 'desc';

  onFilterChange(): void {
    this.filtersChange.emit(this.getCurrentFilters());
  }

  getCurrentFilters(): AssetFilterState {
    return {
      status: this.selectedStatuses,
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
      this.maintenanceDue ||
      this.sortBy !== 'created_at' ||
      this.sortOrder !== 'desc'
    );
  }

  clearFilters(): void {
    this.selectedStatuses = [];
    this.selectedCategories = [];
    this.selectedMachineId = null;
    this.maintenanceDue = false;
    this.sortBy = 'created_at';
    this.sortOrder = 'desc';
    this.onFilterChange();
  }
}
