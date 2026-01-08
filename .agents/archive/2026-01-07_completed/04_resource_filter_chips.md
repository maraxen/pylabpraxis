# Prompt 4: Resource Filter Chips Integration

**Priority**: P2
**Difficulty**: Medium
**Type**: Well-Specified Feature

> **IMPORTANT**: Do NOT use the browser agent. Verify with automated tests only.

---

## Context

Phase 3 of Chip Filter Standardization requires integrating the existing `FilterChipComponent` with the Resource Inventory view. The component exists but isn't connected to the resource filtering system.

**Related backlog**: `.agents/backlog/chip_filter_standardization.md`

---

## Current State

- `FilterChipComponent` exists at `shared/components/filter-chip/`
- `MachineFiltersComponent` already uses chip pattern (Phases 4-6 done)
- Resource inventory uses older filter UI

---

## Tasks

### 1. Create ResourceFiltersComponent

Create `praxis/web-client/src/app/features/assets/components/resource-filters/resource-filters.component.ts`:

```typescript
import { Component, input, output, signal, computed, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { Resource, ResourceStatus } from '../../models/asset.models';

export interface ResourceFilterState {
  search: string;
  status: ResourceStatus[];
  categories: string[];
  brands: string[];
  sort_by: 'name' | 'category' | 'created_at';
  sort_order: 'asc' | 'desc';
}

@Component({
  selector: 'app-resource-filters',
  standalone: true,
  imports: [
    FormsModule,
    MatFormFieldModule,
    MatChipsModule,
    MatIconModule,
    MatButtonModule,
    MatInputModule,
  ],
  template: `
    <div class="filters-container">
      <!-- Search -->
      <div class="filter-group search-group">
        <mat-form-field appearance="outline" class="search-field">
          <mat-icon matPrefix>search</mat-icon>
          <input matInput placeholder="Search resources..." [(ngModel)]="searchTerm" (ngModelChange)="onFilterChange()" />
          @if (searchTerm) {
            <button matSuffix mat-icon-button (click)="searchTerm = ''; onFilterChange()">
              <mat-icon>close</mat-icon>
            </button>
          }
        </mat-form-field>
      </div>

      <!-- Category Chips -->
      <div class="filter-group">
        <label class="filter-label">Category</label>
        <mat-chip-listbox [multiple]="true" [(ngModel)]="selectedCategories" (change)="onFilterChange()">
          @for (cat of availableCategories(); track cat) {
            <mat-chip-option [value]="cat">{{ cat }}</mat-chip-option>
          }
        </mat-chip-listbox>
      </div>

      <!-- Status Chips -->
      <div class="filter-group">
        <label class="filter-label">Status</label>
        <mat-chip-listbox [multiple]="true" [(ngModel)]="selectedStatuses" (change)="onFilterChange()">
          <mat-chip-option value="available">Available</mat-chip-option>
          <mat-chip-option value="in_use">In Use</mat-chip-option>
          <mat-chip-option value="maintenance">Maintenance</mat-chip-option>
          <mat-chip-option value="discarded">Discarded</mat-chip-option>
        </mat-chip-listbox>
      </div>

      <!-- Brand Chips (collapse if >5) -->
      @if (availableBrands().length <= 5) {
        <div class="filter-group">
          <label class="filter-label">Brand</label>
          <mat-chip-listbox [multiple]="true" [(ngModel)]="selectedBrands" (change)="onFilterChange()">
            @for (brand of availableBrands(); track brand) {
              <mat-chip-option [value]="brand">{{ brand }}</mat-chip-option>
            }
          </mat-chip-listbox>
        </div>
      } @else {
        <!-- TODO: Dropdown for many brands -->
      }

      <!-- Clear -->
      @if (hasActiveFilters()) {
        <button mat-stroked-button (click)="clearFilters()" class="clear-btn">
          <mat-icon>filter_alt_off</mat-icon> Clear
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
    .filter-group { flex-shrink: 0; }
    .search-group { flex: 1; min-width: 200px; max-width: 300px; }
    .filter-label {
      display: block;
      font-size: 0.75rem;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--mat-sys-on-surface-variant);
      margin-bottom: 8px;
    }
    .search-field { width: 100%; }
    .clear-btn { margin-left: auto; align-self: center; }
  `]
})
export class ResourceFiltersComponent implements OnInit {
  resources = input<Resource[]>([]);
  filtersChange = output<ResourceFilterState>();

  searchTerm = '';
  selectedStatuses: ResourceStatus[] = [];
  selectedCategories: string[] = [];
  selectedBrands: string[] = [];
  sortBy: 'name' | 'category' | 'created_at' = 'name';
  sortOrder: 'asc' | 'desc' = 'asc';

  availableCategories = computed(() => {
    const cats = new Set<string>();
    this.resources().forEach(r => {
      if (r.plr_category) cats.add(r.plr_category);
    });
    return Array.from(cats).sort();
  });

  availableBrands = computed(() => {
    const brands = new Set<string>();
    this.resources().forEach(r => {
      if (r.definition?.vendor) brands.add(r.definition.vendor);
    });
    return Array.from(brands).sort();
  });

  ngOnInit(): void {
    this.onFilterChange();
  }

  onFilterChange(): void {
    this.filtersChange.emit({
      search: this.searchTerm,
      status: this.selectedStatuses,
      categories: this.selectedCategories,
      brands: this.selectedBrands,
      sort_by: this.sortBy,
      sort_order: this.sortOrder,
    });
  }

  hasActiveFilters(): boolean {
    return this.searchTerm !== '' || 
           this.selectedStatuses.length > 0 || 
           this.selectedCategories.length > 0 ||
           this.selectedBrands.length > 0;
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.selectedStatuses = [];
    this.selectedCategories = [];
    this.selectedBrands = [];
    this.onFilterChange();
  }
}
```

### 2. Create Unit Tests

Create `resource-filters.component.spec.ts`:

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ResourceFiltersComponent } from './resource-filters.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('ResourceFiltersComponent', () => {
  let component: ResourceFiltersComponent;
  let fixture: ComponentFixture<ResourceFiltersComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ResourceFiltersComponent, NoopAnimationsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(ResourceFiltersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should emit filter state on change', () => {
    const spy = vi.spyOn(component.filtersChange, 'emit');
    component.searchTerm = 'test';
    component.onFilterChange();
    expect(spy).toHaveBeenCalledWith(expect.objectContaining({ search: 'test' }));
  });

  it('should detect active filters', () => {
    expect(component.hasActiveFilters()).toBe(false);
    component.searchTerm = 'test';
    expect(component.hasActiveFilters()).toBe(true);
  });

  it('should clear all filters', () => {
    component.searchTerm = 'test';
    component.selectedStatuses = ['available'];
    component.clearFilters();
    expect(component.searchTerm).toBe('');
    expect(component.selectedStatuses).toEqual([]);
  });
});
```

### 3. Integrate into Resource List

Update `resource-list.component.ts` to use the new filter component.

---

## Verification

```bash
cd praxis/web-client && npm test -- --include='**/resource-filters*'
```

---

## Success Criteria

- [x] `ResourceFiltersComponent` created with chip UI
- [x] Category, Status, Brand chips working
- [x] Search integration working
- [x] Brand dropdown for >5 brands (TODO marker acceptable)
- [x] Unit tests pass
