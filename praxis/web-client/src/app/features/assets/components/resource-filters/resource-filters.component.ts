import { Component, Input, output, computed, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { Resource, ResourceStatus, Machine } from '../../models/asset.models';
import { PraxisMultiselectComponent } from '../../../../shared/components/praxis-multiselect/praxis-multiselect.component';
import { FilterOption, FilterResultService } from '../../../../shared/services/filter-result.service';
import { extractUniqueNameParts } from '../../../../shared/utils/name-parser';

export interface ResourceFilterState {
  search: string;
  status: ResourceStatus[];
  categories: string[];
  brands: string[];
  machine_id: string | null;
  show_discarded: boolean;
  sort_by: 'name' | 'category' | 'created_at' | 'count';
  sort_order: 'asc' | 'desc';
}

@Component({
  selector: 'app-resource-filters',
  standalone: true,
  imports: [
    FormsModule,
    MatFormFieldModule,
    MatIconModule,
    MatButtonModule,
    MatInputModule,
    MatSelectModule,
    PraxisMultiselectComponent,
  ],
  template: `
    <div class="filters-container">
      <div class="filters-row">
        <!-- Category Chip Dropdown -->
        <div class="filter-group">
          <label class="filter-label">Category</label>
          <app-praxis-multiselect 
            label="Category" 
            [options]="categoryOptions()" 
            [value]="selectedCategories()"
            (valueChange)="selectedCategories.set($any($event)); onFilterChange()"></app-praxis-multiselect>
        </div>

        <!-- Status Chip Dropdown -->
        <div class="filter-group">
          <label class="filter-label">Status</label>
          <app-praxis-multiselect 
            label="Status" 
            [options]="statusOptions()" 
            [value]="selectedStatuses()"
            (valueChange)="selectedStatuses.set($any($event)); onFilterChange()"></app-praxis-multiselect>
        </div>

        <!-- Brand Chip Dropdown -->
        <div class="filter-group">
          <label class="filter-label">Brand</label>
          <app-praxis-multiselect 
            label="Brand" 
            [options]="brandOptions()" 
            [value]="selectedBrands()"
            (valueChange)="selectedBrands.set($any($event)); onFilterChange()"></app-praxis-multiselect>
        </div>
      </div>

      <!-- Clear -->
      @if (hasActiveFilters()) {
        <div class="filter-group clear-group">
          <button mat-stroked-button (click)="clearFilters()" class="clear-btn">
            <mat-icon>filter_alt_off</mat-icon> Clear
          </button>
        </div>
      }
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

    .filter-group {
      flex: 0 1 auto;
      min-width: 140px;
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

    .clear-group {
        margin-left: auto;
        display: flex;
        align-items: center;
        align-self: flex-end;
    }

    .clear-btn {
      height: 40px;
      border-radius: 8px;
    }
  `]
})
export class ResourceFiltersComponent implements OnInit {
  private _resources = signal<Resource[]>([]);
  @Input() set resources(val: Resource[]) { this._resources.set(val || []); }

  private _categoriesInput = signal<string[]>([]);
  @Input() set categories(val: string[]) { this._categoriesInput.set(val || []); }

  private _machines = signal<Machine[]>([]);
  @Input() set machines(val: Machine[]) { this._machines.set(val || []); }

  filtersChange = output<ResourceFilterState>();

  private filterResultService = inject(FilterResultService);

  // State Signals
  @Input() set search(val: string) {
    if (this.searchTerm() !== val) {
       this.searchTerm.set(val);
       this.onFilterChange();
    }
  }
  searchTerm = signal('');
  selectedStatuses = signal<ResourceStatus[]>([]);
  selectedCategories = signal<string[]>([]);
  selectedBrands = signal<string[]>([]);
  selectedMachineId = signal<string | null>(null);
  showDiscarded = signal(false);
  sortBy = signal<'name' | 'category' | 'created_at' | 'count'>('name');
  sortOrder = signal<'asc' | 'desc'>('asc');

  // Base options
  baseCategories = computed(() => {
    if (this._categoriesInput().length > 0) return this._categoriesInput();
    const cats = new Set<string>();
    this._resources().forEach(r => {
      if ((r as any).plr_category) cats.add((r as any).plr_category);
    });
    return Array.from(cats).sort();
  });

  baseBrands = computed(() => {
    const brands = new Set<string>();
    this._resources().forEach(r => {
      if ((r as any).definition?.vendor) brands.add((r as any).definition.vendor);
    });
    return Array.from(brands).sort();
  });

  // Filtered datasets for each axis (delta counting)

  dataFilteredBySearch = computed(() => {
    const term = this.searchTerm().toLowerCase();
    if (!term) return this._resources();
    return this._resources().filter(r =>
      r.name.toLowerCase().includes(term) ||
      (r as any).plr_category?.toLowerCase().includes(term) ||
      (r as any).definition?.vendor?.toLowerCase().includes(term)
    );
  });

  dataForCategory = computed(() => {
    let data = this.dataFilteredBySearch();
    const statuses = this.selectedStatuses();
    const brands = this.selectedBrands();

    if (statuses.length > 0) {
      data = data.filter(r => statuses.includes(r.status));
    }
    if (brands.length > 0) {
      data = data.filter(r => (r as any).definition?.vendor && brands.includes((r as any).definition.vendor));
    }
    return data;
  });

  dataForStatus = computed(() => {
    let data = this.dataFilteredBySearch();
    const cats = this.selectedCategories();
    const brands = this.selectedBrands();

    if (cats.length > 0) {
      data = data.filter(r => (r as any).plr_category && cats.includes((r as any).plr_category));
    }
    if (brands.length > 0) {
      data = data.filter(r => (r as any).definition?.vendor && brands.includes((r as any).definition.vendor));
    }
    return data;
  });

  dataForBrand = computed(() => {
    let data = this.dataFilteredBySearch();
    const cats = this.selectedCategories();
    const statuses = this.selectedStatuses();

    if (cats.length > 0) {
      data = data.filter(r => (r as any).plr_category && cats.includes((r as any).plr_category));
    }
    if (statuses.length > 0) {
      data = data.filter(r => statuses.includes(r.status));
    }
    return data;
  });

  // Final options with counts
  categoryOptions = computed(() => {
    const rawCategories = this.baseCategories();
    const uniqueParts = extractUniqueNameParts(rawCategories);
    const options: FilterOption[] = rawCategories.map(c => ({
      label: uniqueParts.get(c) || c,
      value: c,
      fullName: c
    }));

    return this.filterResultService.computeOptionMetrics(
      this.dataForCategory(),
      (item, value) => (item as any).plr_category === value,
      options,
      this.selectedCategories(),
      true
    );
  });

  statusOptions = computed(() => {
    const statuses: ResourceStatus[] = [
      ResourceStatus.AVAILABLE,
      ResourceStatus.IN_USE,
      ResourceStatus.RESERVED,
      ResourceStatus.DEPLETED,
      ResourceStatus.EXPIRED
    ];
    const options: FilterOption[] = statuses.map(s => ({
      label: s.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value: s
    }));
    return this.filterResultService.computeOptionMetrics(
      this.dataForStatus(),
      (item, value) => item.status === value,
      options,
      this.selectedStatuses(),
      true
    );
  });

  brandOptions = computed(() => {
    const rawBrands = this.baseBrands();
    const uniqueParts = extractUniqueNameParts(rawBrands);
    const options: FilterOption[] = rawBrands.map(b => ({
      label: uniqueParts.get(b) || b,
      value: b,
      fullName: b
    }));

    return this.filterResultService.computeOptionMetrics(
      this.dataForBrand(),
      (item, value) => (item as any).definition?.vendor === value,
      options,
      this.selectedBrands(),
      true
    );
  });

  ngOnInit(): void {
    this.onFilterChange();
  }

  onFilterChange(): void {
    this.filtersChange.emit({
      search: this.searchTerm(),
      status: this.selectedStatuses(),
      categories: this.selectedCategories(),
      brands: this.selectedBrands(),
      machine_id: this.selectedMachineId(),
      show_discarded: this.showDiscarded(),
      sort_by: this.sortBy(),
      sort_order: this.sortOrder(),
    });
  }

  hasActiveFilters(): boolean {
    return this.searchTerm() !== '' ||
      this.selectedStatuses().length > 0 ||
      this.selectedCategories().length > 0 ||
      this.selectedBrands().length > 0 ||
      this.selectedMachineId() !== null ||
      this.showDiscarded();
  }

  clearFilters(): void {
    this.searchTerm.set('');
    this.selectedStatuses.set([]);
    this.selectedCategories.set([]);
    this.selectedBrands.set([]);
    this.selectedMachineId.set(null);
    this.showDiscarded.set(false);
    this.onFilterChange();
  }
}
