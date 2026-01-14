import {
  Component,
  Input,
  Output,
  EventEmitter,
  OnInit,
  OnDestroy,
  ChangeDetectionStrategy,
  signal,
  effect,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { Subject, debounceTime, distinctUntilChanged } from 'rxjs';

import { PraxisSelectComponent } from '../praxis-select/praxis-select.component';
import { PraxisMultiselectComponent } from '../praxis-multiselect/praxis-multiselect.component';
import { ViewTypeToggleComponent } from './view-type-toggle.component';
import { GroupBySelectComponent } from './group-by-select.component';
import {
  ViewControlsState,
  ViewControlsConfig,
  ViewType,
} from './view-controls.types';

@Component({
  selector: 'app-view-controls',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatSelectModule,
    MatFormFieldModule,
    PraxisSelectComponent,
    PraxisMultiselectComponent,
    ViewTypeToggleComponent,
    GroupBySelectComponent,
  ],
  template: `
<div class="view-controls-container">
  <!-- Search -->
  <div class="search-wrapper">
    <mat-icon class="search-icon">search</mat-icon>
    <input
      type="text"
      class="search-input"
      [placeholder]="config.defaults?.search || 'Search...'"
      [value]="state.search"
      (input)="onSearchInput($event)"
      aria-label="Search"
    />
    @if (state.search) {
      <button mat-icon-button class="clear-search" (click)="clearSearch()">
        <mat-icon>close</mat-icon>
      </button>
    }
  </div>

  <div class="controls-actions">
    <!-- View Type -->
    @if (config.viewTypes && config.viewTypes.length > 1) {
      <app-view-type-toggle
        [viewType]="state.viewType"
        [availableTypes]="config.viewTypes"
        (viewTypeChange)="onViewTypeChange($event)"
      ></app-view-type-toggle>
    }

    <!-- Group By -->
    @if (config.groupByOptions && config.groupByOptions.length > 0) {
      <app-group-by-select
        [value]="state.groupBy"
        [options]="config.groupByOptions"
        (valueChange)="onGroupByChange($event)"
      ></app-group-by-select>
    }

    <!-- Filters -->
    <div class="filters-row">
      @for (filterConfig of config.filters; track filterConfig.key) {
        @switch (filterConfig.type) {
          @case ('multiselect') {
            <app-praxis-multiselect
              [label]="filterConfig.label"
              [options]="filterConfig.options || []"
              [value]="state.filters[filterConfig.key]"
              (valueChange)="onFilterChange(filterConfig.key, $event)"
            ></app-praxis-multiselect>
          }
          @case ('chips') {
            <app-praxis-multiselect
              [label]="filterConfig.label"
              [options]="filterConfig.options || []"
              [value]="state.filters[filterConfig.key]"
              (valueChange)="onFilterChange(filterConfig.key, $event)"
            ></app-praxis-multiselect>
          }
          @case ('select') {
            <app-praxis-select
              [placeholder]="filterConfig.label"
              [options]="filterConfig.options || []"
              [value]="state.filters[filterConfig.key]?.[0]"
              (valueChange)="onFilterChange(filterConfig.key, [$event])"
            ></app-praxis-select>
          }
          @case ('toggle') {
            <button 
              mat-stroked-button
              class="filter-toggle-btn"
              [class.active]="state.filters[filterConfig.key]"
              (click)="onFilterChange(filterConfig.key, !state.filters[filterConfig.key])"
              [matTooltip]="filterConfig.label"
            >
              <mat-icon>{{ state.filters[filterConfig.key] ? 'check_box' : 'check_box_outline_blank' }}</mat-icon>
              {{ filterConfig.label }}
            </button>
          }
        }
      }
    </div>

    <!-- Sort -->
    @if (config.sortOptions && config.sortOptions.length > 0) {
      <div class="sort-controls">
        <mat-form-field appearance="outline" class="sort-field" subscriptSizing="dynamic">
          <mat-label>Sort By</mat-label>
          <mat-select [value]="state.sortBy" (selectionChange)="onSortByChange($event.value)">
            @for (option of config.sortOptions; track option.value) {
              <mat-option [value]="option.value">{{ option.label }}</mat-option>
            }
          </mat-select>
        </mat-form-field>
        <button
          mat-icon-button
          class="sort-order-btn"
          [matTooltip]="state.sortOrder === 'asc' ? 'Sort Ascending' : 'Sort Descending'"
          (click)="toggleSortOrder()"
        >
          <mat-icon>{{ state.sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward' }}</mat-icon>
        </button>
      </div>
    }

    <!-- Clear All -->
    @if (hasActiveFilters) {
      <button mat-button class="clear-all-btn" (click)="clearAll()">
        Clear Filters
      </button>
    }
  </div>
</div>
  `,
  styles: [`
:host {
  display: block;
}

.view-controls-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 8px 0;
  flex-wrap: wrap;
}

.search-wrapper {
  position: relative;
  flex: 1;
  min-width: 200px;
  max-width: 400px;
  display: flex;
  align-items: center;

  .search-icon {
    position: absolute;
    left: 12px;
    font-size: 18px;
    width: 18px;
    height: 18px;
    color: var(--theme-text-secondary);
    pointer-events: none;
  }

  .search-input {
    width: 100%;
    height: 36px;
    padding: 0 40px;
    border-radius: 18px;
    border: 1px solid var(--theme-border);
    background-color: var(--theme-surface-elevated);
    color: var(--theme-text-primary);
    font-size: 14px;
    transition: all 0.2s ease;

    &:focus {
      outline: none;
      border-color: var(--primary-color);
      box-shadow: 0 0 0 2px rgba(var(--primary-color-rgb), 0.1);
    }

    &::placeholder {
      color: var(--theme-text-secondary);
      opacity: 0.6;
    }
  }

  .clear-search {
    position: absolute;
    right: 8px;
    width: 24px;
    height: 24px;
    line-height: 24px;
    
    .mat-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
    }
  }
}

.controls-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filters-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;

  app-praxis-select, app-praxis-multiselect {
    min-width: 140px;
  }
}

.filter-toggle-btn {
  height: 32px;
  border-radius: 16px;
  font-size: 13px;
  padding: 0 12px;
  border: 1px solid var(--theme-border);
  background: transparent;
  color: var(--theme-text-primary);
  display: flex;
  align-items: center;
  gap: 6px;

  &.active {
    background-color: var(--theme-surface-elevated);
    border-color: var(--primary-color);
    color: var(--primary-color);
  }

  .mat-icon {
    font-size: 18px;
    width: 18px;
    height: 18px;
  }
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 4px;

  .sort-field {
    width: 140px;
    ::ng-deep {
      .mat-mdc-text-field-wrapper {
        height: 32px !important;
        padding: 0 8px !important;
      }
      .mat-mdc-form-field-infix {
        padding: 0 !important;
        min-height: auto !important;
      }
      .mat-mdc-form-field-label-wrapper {
        top: -8px;
      }
    }
  }

  .sort-order-btn {
    width: 32px;
    height: 32px;
    line-height: 32px;
    .mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
    }
  }
}

.clear-all-btn {
  height: 32px;
  font-size: 13px;
  color: var(--theme-text-secondary);
  &:hover {
    color: var(--primary-color);
  }
}

@media (max-width: 768px) {
  .view-controls-container {
    flex-direction: column;
    align-items: stretch;
  }
  .search-wrapper {
    max-width: none;
  }
  .controls-actions {
    justify-content: flex-start;
  }
}
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ViewControlsComponent implements OnInit, OnDestroy {
  @Input() config: ViewControlsConfig = {};

  @Input() set state(value: ViewControlsState) {
    this._state.set(value);
  }
  get state(): ViewControlsState {
    return this._state();
  }

  @Output() stateChange = new EventEmitter<ViewControlsState>();
  @Output() viewTypeChange = new EventEmitter<ViewType>();
  @Output() groupByChange = new EventEmitter<string | null>();
  @Output() filtersChange = new EventEmitter<Record<string, any[]>>();
  @Output() sortChange = new EventEmitter<{
    sortBy: string;
    sortOrder: 'asc' | 'desc';
  }>();
  @Output() searchChange = new EventEmitter<string>();

  private _state = signal<ViewControlsState>({
    viewType: 'card',
    groupBy: null,
    filters: {},
    sortBy: '',
    sortOrder: 'asc',
    search: '',
  });

  private searchSubject = new Subject<string>();
  private searchSubscription = this.searchSubject
    .pipe(debounceTime(300), distinctUntilChanged())
    .subscribe((value) => {
      this.updateState({ search: value });
      this.searchChange.emit(value);
    });

  constructor() {
    effect(() => {
      const currentState = this._state();
      this.persistState(currentState);
    });
  }

  ngOnInit() {
    this.initializeState();
  }

  ngOnDestroy() {
    this.searchSubscription.unsubscribe();
  }

  private initializeState() {
    const persisted = this.loadPersistedState();
    const defaults = this.config.defaults || {};

    const initialState: ViewControlsState = {
      ...this._state(),
      ...defaults,
      ...persisted,
    };

    // Ensure all filter keys from config are present in state
    if (this.config.filters) {
      this.config.filters.forEach(f => {
        if (initialState.filters[f.key] === undefined) {
          initialState.filters[f.key] = [];
        }
      });
    }

    this._state.set(initialState);
  }

  get hasActiveFilters(): boolean {
    const s = this._state();
    const hasSearch = !!s.search;
    const hasFilters = Object.entries(s.filters).some(([key, v]) => {
      const config = this.config.filters?.find(f => f.key === key);
      if (config?.type === 'toggle') {
        return v === true;
      }
      return Array.isArray(v) ? v.length > 0 : !!v;
    });
    const hasGroupBy = !!s.groupBy;
    return hasSearch || hasFilters || hasGroupBy;
  }

  onSearchInput(event: Event) {
    const input = event.target as HTMLInputElement;
    this.searchSubject.next(input.value);
  }

  clearSearch() {
    this.searchSubject.next('');
    // We also need to manually update the state since the subject might not emit if it was already empty
    this.updateState({ search: '' });
    this.searchChange.emit('');
  }

  onViewTypeChange(viewType: ViewType) {
    this.updateState({ viewType });
    this.viewTypeChange.emit(viewType);
  }

  onGroupByChange(groupBy: string | null) {
    this.updateState({ groupBy });
    this.groupByChange.emit(groupBy);
  }

  onFilterChange(key: string, value: any) {
    const newFilters = { ...this.state.filters, [key]: value };
    this.updateState({ filters: newFilters });
    this.filtersChange.emit(newFilters);
  }

  onSortByChange(sortBy: string) {
    this.updateState({ sortBy });
    this.sortChange.emit({ sortBy, sortOrder: this.state.sortOrder });
  }

  toggleSortOrder() {
    const sortOrder = this.state.sortOrder === 'asc' ? 'desc' : 'asc';
    this.updateState({ sortOrder });
    this.sortChange.emit({ sortBy: this.state.sortBy, sortOrder });
  }

  clearAll() {
    const clearedFilters: Record<string, unknown[]> = {};
    if (this.config.filters) {
      this.config.filters.forEach(f => clearedFilters[f.key] = []);
    }

    const newState: Partial<ViewControlsState> = {
      search: '',
      groupBy: null,
      filters: clearedFilters,
    };

    this.updateState(newState);
    this.searchChange.emit('');
    this.groupByChange.emit(null);
    this.filtersChange.emit(clearedFilters);
  }

  private updateState(patch: Partial<ViewControlsState>) {
    const newState = { ...this.state, ...patch };
    this._state.set(newState);
    this.stateChange.emit(newState);
  }

  private loadPersistedState(): Partial<ViewControlsState> {
    if (!this.config.storageKey) return {};
    try {
      const stored = localStorage.getItem(`viewControls.${this.config.storageKey}`);
      return stored ? JSON.parse(stored) : {};
    } catch (e) {
      console.warn('Failed to load persisted view controls state', e);
      return {};
    }
  }

  private persistState(state: ViewControlsState): void {
    if (!this.config.storageKey) return;
    try {
      localStorage.setItem(`viewControls.${this.config.storageKey}`, JSON.stringify(state));
    } catch (e) {
      console.warn('Failed to persist view controls state', e);
    }
  }
}
