import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, FormControl } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { AssetService, ResourceFacets, FacetItem } from '../services/asset.service';
import { ResourceStatus, ResourceDefinition, ActiveFilters } from '../models/asset.models';
import { Observable, map, startWith, of, combineLatest, BehaviorSubject, forkJoin, switchMap, debounceTime, finalize, tap, catchError, shareReplay } from 'rxjs';
import { FacetChipCarouselComponent, ChipOption } from '../../../shared/components/facet-chip-carousel.component';

@Component({
  selector: 'app-resource-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatAutocompleteModule,
    MatChipsModule,
    MatIconModule,
    MatTooltipModule,
    FacetChipCarouselComponent
  ],
  template: `
    <h2 mat-dialog-title>
      <div class="flex items-center gap-2">
        <button mat-icon-button *ngIf="currentStep === 2" (click)="resetToStep1()">
          <mat-icon>arrow_back</mat-icon>
        </button>
        {{ currentStep === 1 ? 'Select Resource Category' : 'Add New ' + getSelectedCategoryLabel() }}
      </div>
    </h2>

    <mat-dialog-content>
      <!-- STEP 1: Category Selection -->
      <div *ngIf="currentStep === 1" class="category-grid">
        <!-- Skeleton Loading for Categories (shows while categories$ is null) -->
        <ng-container *ngIf="categories$ | async as categories; else loadingTemplate">
          
          <ng-container *ngIf="categories.length > 0; else noCategories">
            <button *ngFor="let cat of categories; trackBy: trackByValue" 
                    class="category-card" 
                    (click)="selectCategory(cat)">
              <div class="cat-icon">
                <mat-icon>{{ getCategoryIcon(cat.value) }}</mat-icon>
              </div>
              <div class="cat-info">
                <span class="cat-name">{{ formatValue(cat.value) }}</span>
                <span class="cat-count">{{ cat.count }} types</span>
              </div>
            </button>
          </ng-container>

          <ng-template #noCategories>
            <div class="no-data-message">No categories found.</div>
          </ng-template>

        </ng-container>

        <ng-template #loadingTemplate>
          <div *ngFor="let i of [1,2,3,4,5,6]" class="category-card skeleton-card">
            <div class="skeleton-pulse icon-placeholder"></div>
            <div class="skeleton-pulse text-placeholder"></div>
            <div class="skeleton-pulse text-placeholder-sm"></div>
          </div>
        </ng-template>
      </div>

      <!-- STEP 2: Detailed Filtering & Form -->
      <div *ngIf="currentStep === 2" class="step-2-container">
        <form [formGroup]="form" class="flex flex-col gap-4 py-4">
          
          <!-- Dynamic Facets -->
          <ng-container *ngIf="facets$ | async as facets; else loadingSubFacets">
            <div class="facets-section">
              <app-facet-chip-carousel
                *ngIf="facets.vendor.length > 0"
                label="Vendor"
                [options]="facets.vendor"
                [selectedValues]="activeFilters.vendor"
                [allowInvert]="true"
                [inverted]="invertedFilters['vendor']"
                (invertedChange)="onInvertChange('vendor', $event)"
                (selectionChange)="onFacetChange('vendor', $event)">
              </app-facet-chip-carousel>

              <app-facet-chip-carousel
                *ngIf="facets.num_items.length > 0"
                label="Wells/Tips"
                [options]="facets.num_items"
                [selectedValues]="activeFilters.num_items"
                [allowInvert]="true"
                [inverted]="invertedFilters['num_items']"
                (invertedChange)="onInvertChange('num_items', $event)"
                (selectionChange)="onFacetChange('num_items', $event)">
              </app-facet-chip-carousel>

              <app-facet-chip-carousel
                *ngIf="facets.plate_type.length > 0"
                label="Plate Type"
                [options]="facets.plate_type"
                [selectedValues]="activeFilters.plate_type"
                [allowInvert]="true"
                [inverted]="invertedFilters['plate_type']"
                (invertedChange)="onInvertChange('plate_type', $event)"
                (selectionChange)="onFacetChange('plate_type', $event)">
              </app-facet-chip-carousel>
            </div>
          </ng-container>

          <ng-template #loadingSubFacets>
            <div class="facets-section skeleton-section">
               <div class="skeleton-row" *ngFor="let i of [1,2,3]">
                 <div class="skeleton-pulse label-skeleton"></div>
                 <div class="skeleton-pulse chips-skeleton"></div>
               </div>
            </div>
          </ng-template>

          <!-- Type Search -->
          <mat-form-field appearance="outline">
            <mat-label>Resource Model</mat-label>
            <input
              matInput
              [formControl]="definitionSearchControl"
              [matAutocomplete]="defAuto"
              placeholder="Search {{ filteredDefinitionsCount }} models...">
            <mat-autocomplete
              #defAuto="matAutocomplete"
              [displayWith]="displayDefinition.bind(this)"
              (optionSelected)="onDefinitionSelected($event.option.value)">
              <mat-option *ngFor="let def of filteredDefinitions$ | async; trackBy: trackByAccession" [value]="def">
                <span class="def-option">
                  <span class="def-name">{{ getDisplayName(def) }}</span>
                  <span class="def-meta">
                    <span *ngIf="def.num_items" class="def-tag">{{ def.num_items }}-well</span>
                    <span *ngIf="def.plate_type" class="def-tag">{{ def.plate_type }}</span>
                    <span *ngIf="def.well_volume_ul" class="def-tag">{{ def.well_volume_ul }}µL</span>
                    <span *ngIf="def.tip_volume_ul" class="def-tag tip">{{ def.tip_volume_ul }}µL tip</span>
                  </span>
                </span>
              </mat-option>
              <mat-option *ngIf="(filteredDefinitions$ | async)?.length === 0" disabled>
                No matching definitions found
              </mat-option>
            </mat-autocomplete>
          </mat-form-field>

          <!-- Name & Status -->
          <mat-form-field appearance="outline">
            <mat-label>Name</mat-label>
            <input matInput formControlName="name" placeholder="e.g. My Plate 1">
            <mat-error *ngIf="form.get('name')?.hasError('required')">Name is required</mat-error>
          </mat-form-field>

          <div class="form-row">
            <mat-form-field appearance="outline" class="half-width">
                <mat-label>Status</mat-label>
                <mat-select formControlName="status">
                    <mat-option [value]="ResourceStatus.AVAILABLE">Available</mat-option>
                    <mat-option [value]="ResourceStatus.IN_USE">In Use</mat-option>
                    <mat-option [value]="ResourceStatus.DEPLETED">Depleted</mat-option>
                </mat-select>
            </mat-form-field>

            <mat-form-field appearance="outline" class="half-width">
              <mat-label>Parent ID (Optional)</mat-label>
              <input matInput formControlName="parent_accession_id" placeholder="UUID of parent">
            </mat-form-field>
          </div>
        </form>
      </div>
    </mat-dialog-content>

    <mat-dialog-actions align="end" *ngIf="currentStep === 2">
      <button mat-button mat-dialog-close>Cancel</button>
      <button mat-flat-button color="primary" [disabled]="form.invalid" (click)="save()">Save Resource</button>
    </mat-dialog-actions>
  `,
  styles: [`
    :host { display: block; }
    mat-form-field { width: 100%; margin-bottom: 8px; }
    
    .category-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
      gap: 12px;
      padding: 16px 0;
    }
    
    .category-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 16px;
      background: var(--mat-sys-surface-container, #f5f5f5);
      border: 1px solid var(--mat-sys-outline-variant, #e0e0e0);
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
      color: var(--mat-sys-on-surface);
      position: relative;
      overflow: hidden;
      
      &:hover {
        background: var(--mat-sys-surface-container-high, #eee);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
      }

      &.skeleton-card {
        cursor: default;
        pointer-events: none;
        background: var(--mat-sys-surface-container-low);
        
        .icon-placeholder { width: 40px; height: 40px; margin-bottom: 12px; border-radius: 50%; }
        .text-placeholder { width: 80%; height: 16px; margin-bottom: 8px; }
        .text-placeholder-sm { width: 50%; height: 12px; }
      }
    }
    
    .cat-icon {
      margin-bottom: 8px;
      mat-icon {
        font-size: 32px;
        width: 32px;
        height: 32px;
        color: var(--mat-sys-primary);
      }
    }
    
    .cat-info { text-align: center; }
    .cat-name { display: block; font-weight: 500; font-size: 14px; margin-bottom: 2px; }
    .cat-count { display: block; font-size: 11px; color: var(--mat-sys-on-surface-variant); }

    .facets-section {
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding: 12px;
      background: var(--mat-sys-surface-container-low, rgba(255,255,255,0.02));
      border-radius: 8px;
      margin-bottom: 16px;
      min-height: 120px; 

      &.skeleton-section {
        justify-content: center;
        .skeleton-row {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
          
          .label-skeleton { width: 80px; height: 20px; }
          .chips-skeleton { flex: 1; height: 32px; border-radius: 16px; }
        }
      }
    }
    
    .def-option { display: flex; justify-content: space-between; align-items: center; width: 100%; }
    .def-name { font-weight: 500; }
    .def-meta { display: flex; gap: 6px; font-size: 11px; }
    .def-tag {
      background: var(--mat-sys-surface-variant, rgba(255,255,255,0.1));
      padding: 2px 6px;
      border-radius: 4px;
      color: var(--mat-sys-on-surface-variant, #aaa);
      
      &.tip {
        background: var(--mat-sys-tertiary-container);
        color: var(--mat-sys-on-tertiary-container);
      }
    }

    .form-row {
      display: flex;
      gap: 12px;
      .half-width { flex: 1; }
    }
  `]
})
export class ResourceDialogComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<ResourceDialogComponent>);
  private assetService = inject(AssetService);
  private cdr = inject(ChangeDetectorRef);

  ResourceStatus = ResourceStatus;

  // Step 1 State
  currentStep: 1 | 2 = 1;
  categories$: Observable<FacetItem[]> = of([]);

  // Step 2 State
  facets$: Observable<ResourceFacets | null> = of(null);
  definitions: ResourceDefinition[] = [];
  definitionSearchControl = new FormControl<string | ResourceDefinition>('');
  filteredDefinitions$: Observable<ResourceDefinition[]> = of([]);
  selectedDefinition: ResourceDefinition | null = null;
  filteredDefinitionsCount = 0;

  activeFilters: ActiveFilters = {
    plr_category: [],
    vendor: [],
    num_items: [],
    plate_type: []
  };

  // Track inverted state: true means EXCLUDE selected values
  invertedFilters: Record<string, boolean> = {
    vendor: false,
    num_items: false,
    plate_type: false
  };

  private filtersSubject = new BehaviorSubject<ActiveFilters>(this.activeFilters);
  // Separate trigger for step 2 initialization to reset facets
  private step2TriggerSubject = new BehaviorSubject<boolean>(false);

  form = this.fb.group({
    name: ['', Validators.required],
    status: [ResourceStatus.AVAILABLE],
    resource_definition_accession_id: [null as string | null],
    parent_accession_id: [null as string | null]
  });

  ngOnInit() {
    this.categories$ = this.assetService.getFacets().pipe(
      map(facets => {
        if (facets && facets.plr_category) {
          return facets.plr_category.filter(c => c.count > 0);
        }
        return [];
      }),
      shareReplay(1)
    );

    // Setup facets stream
    this.facets$ = combineLatest([this.filtersSubject, this.step2TriggerSubject]).pipe(
      debounceTime(100),
      switchMap(([filters, isStep2]) => {
        if (isStep2) {
          return forkJoin({
            facets: this.assetService.getFacets(filters),
            definitions: this.assetService.getResourceDefinitions()
          }).pipe(
            tap(res => {
              this.filterDefinitions(this.definitionSearchControl.value, filters, res.definitions);
            }),
            map(res => res.facets),
            catchError(err => {
              console.error('Error loading facets:', err);
              return of(null);
            })
          );
        }
        return of(null);
      }),
      shareReplay(1)
    );

    // Setup search filter
    this.definitionSearchControl.valueChanges.pipe(
      startWith('')
    ).subscribe(value => {
      this.filterDefinitions(value, this.activeFilters);
    });
  }

  selectCategory(cat: FacetItem) {
    this.currentStep = 2;
    this.activeFilters = { ...this.activeFilters, plr_category: [cat.value] };
    this.step2TriggerSubject.next(true); // Signal we entered step 2
    this.filtersSubject.next(this.activeFilters);
  }

  resetToStep1() {
    this.currentStep = 1;
    this.step2TriggerSubject.next(false);
    this.activeFilters = {
      plr_category: [],
      vendor: [],
      num_items: [],
      plate_type: []
    };
    this.invertedFilters = {
      vendor: false,
      num_items: false,
      plate_type: false
    };
    this.filtersSubject.next(this.activeFilters);
    this.form.reset({ status: ResourceStatus.AVAILABLE });
    this.definitionSearchControl.setValue('');
  }

  onFacetChange(facetName: keyof ActiveFilters, values: (string | number)[]) {
    this.activeFilters = { ...this.activeFilters, [facetName]: values };
    this.filtersSubject.next(this.activeFilters);
  }

  onInvertChange(facetName: string, isInverted: boolean) {
    this.invertedFilters[facetName] = isInverted;
    this.filterDefinitions(this.definitionSearchControl.value, this.activeFilters);
  }

  private filterDefinitions(value: string | ResourceDefinition | null, filters: ActiveFilters, preloadedDefs?: ResourceDefinition[]) {
    const source$ = preloadedDefs ? of(preloadedDefs) : this.assetService.getResourceDefinitions();

    source$.subscribe(defs => {
      let filtered = defs;

      const checkFilter = (itemValue: any, filterValues: (string | number)[], inverted: boolean) => {
        if (!filterValues.length) return true;
        const match = itemValue && filterValues.includes(itemValue);
        return inverted ? !match : match;
      };

      if (filters.plr_category.length > 0) {
        filtered = filtered.filter(d => d.plr_category && filters.plr_category.includes(d.plr_category));
      }

      filtered = filtered.filter(d => checkFilter(d.vendor, filters.vendor, this.invertedFilters['vendor']));
      filtered = filtered.filter(d => checkFilter(d.num_items, filters.num_items, this.invertedFilters['num_items']));
      filtered = filtered.filter(d => checkFilter(d.plate_type, filters.plate_type, this.invertedFilters['plate_type']));

      if (value) {
        const term = typeof value === 'string' ? value.toLowerCase() : value.name.toLowerCase();
        const terms = term.split(/\s+/);
        filtered = filtered.filter(d => {
          const text = [d.name, d.fqn, d.vendor, d.plate_type].join(' ').toLowerCase();
          return terms.every(t => text.includes(t));
        });
      }

      this.filteredDefinitionsCount = filtered.length;
      this.filteredDefinitions$ = of(filtered);
    });
  }

  // Formatting helpers
  getCategoryIcon(cat: string | number): string {
    const map: Record<string, string> = {
      'plate': 'grid_on',
      'tip_rack': 'apps',
      'trough': 'water_drop',
      'tube': 'science',
      'lid': 'layers',
      'carrier': 'inventory_2'
    };
    return map[cat.toString()] || 'category';
  }

  formatValue(value: string | number): string {
    if (typeof value === 'number') return value.toString();
    return value.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }

  getSelectedCategoryLabel(): string {
    if (this.activeFilters.plr_category.length > 0) {
      return this.formatValue(this.activeFilters.plr_category[0]);
    }
    return 'Resource';
  }

  displayDefinition(def: ResourceDefinition | null): string {
    return def ? this.getDisplayName(def) : '';
  }

  getDisplayName(def: ResourceDefinition): string {
    const fn = def.fqn ? def.fqn.split('.').pop() : def.name;
    return def.vendor ? `[${def.vendor}] ${fn}` : fn || '';
  }

  onDefinitionSelected(def: ResourceDefinition) {
    this.selectedDefinition = def;
    this.form.patchValue({ resource_definition_accession_id: def.accession_id });
  }

  save() {
    if (this.form.valid) {
      this.dialogRef.close(this.form.value);
    }
  }

  trackByValue(index: number, item: FacetItem): any {
    return item.value;
  }

  trackByAccession(index: number, item: ResourceDefinition): string {
    return item.accession_id;
  }
}
