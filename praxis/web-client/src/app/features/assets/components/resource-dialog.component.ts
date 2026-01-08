import { Component, inject, OnInit, ChangeDetectorRef, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule, FormBuilder, Validators, FormControl } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { AssetService, ResourceFacets, FacetItem } from '../services/asset.service';
import { ResourceStatus, ResourceDefinition, ActiveFilters } from '../models/asset.models';
import { Observable, map, startWith, of, combineLatest, BehaviorSubject, forkJoin, switchMap, debounceTime, finalize, tap, catchError, shareReplay } from 'rxjs';
import { getResourceCategoryIcon } from '@shared/constants/asset-icons';
import { AriaSelectComponent, SelectOption } from '@shared/components/aria-select/aria-select.component';
import { AriaMultiselectComponent } from '@shared/components/aria-multiselect/aria-multiselect.component';
import { FilterOption } from '@shared/services/filter-result.service';
import { getUiGroup, UI_GROUP_ORDER, shouldHideCategory, ResourceUiGroup, CATEGORY_TO_UI_GROUP, getSubCategory } from '../utils/resource-category-groups';
import { ResourceChipsComponent } from './resource-chips/resource-chips.component';

interface GroupedDefinitions {
  group: ResourceUiGroup;
  icon: string;
  totalCount: number;
  // Sub-categories map (e.g. 'plate_carrier' -> definitions)
  // For non-carrier groups, key might be 'default' or same as group
  subGroups: Map<string, ResourceDefinition[]>;
}

@Component({
  selector: 'app-resource-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatTooltipModule,
    MatExpansionModule,
    MatSlideToggleModule,
    ResourceChipsComponent,
    AriaSelectComponent,
    AriaMultiselectComponent
  ],
  template: `
    <h2 mat-dialog-title>
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          @if (selectedDefinition) {
            <button mat-icon-button (click)="clearSelection()">
              <mat-icon>arrow_back</mat-icon>
            </button>
          }
          {{ selectedDefinition ? 'Configure Resource' : 'Add Resource' }}
        </div>
    
        <!-- Controls (only visible in browsing mode) -->
        @if (!selectedDefinition) {
          <div class="flex items-center gap-4">
            <mat-slide-toggle
              [checked]="showPlrName()"
              (change)="showPlrName.set($event.checked)"
              color="primary">
              <span class="text-xs">Show PLR Name</span>
            </mat-slide-toggle>
            <button mat-icon-button mat-dialog-close>
              <mat-icon>close</mat-icon>
            </button>
          </div>
        }
      </div>
    </h2>
    
    <mat-dialog-content>
      @if (!selectedDefinition) {
        <div class="selection-shell">
          <mat-form-field appearance="outline" class="w-full search-field praxis-search-field">
            <mat-icon matPrefix>search</mat-icon>
            <input matInput [formControl]="searchControl" placeholder="Search resources...">
            @if (searchControl.value) {
              <button matSuffix mat-icon-button (click)="searchControl.setValue('')">
                <mat-icon>close</mat-icon>
              </button>
            }
          </mat-form-field>

          <div class="filters-row">
            <div class="chip-row" aria-label="Category filters">
              @for (group of groupedDefinitions(); track group) {
                <button type="button"
                        class="filter-chip"
                        [class.active-chip]="categoryFilters().includes(group.group)"
                        (click)="toggleCategoryFilter(group.group)">
                  <mat-icon class="!text-[16px]">{{ group.icon }}</mat-icon>
                  <span>{{ group.group }}</span>
                  <span class="count">{{ group.totalCount }}</span>
                </button>
              }
            </div>

            <div class="vendor-field">
              <label class="text-[11px] uppercase font-bold text-gray-400 mb-1 block">Vendor</label>
              <app-aria-multiselect
                label="Vendor"
                [options]="mappedVendorOptions()"
                [selectedValue]="vendorFilters()"
                [multiple]="true"
                (selectionChange)="updateVendorFilters($event)"
              ></app-aria-multiselect>
            </div>

            <div class="facet-field">
              <label class="text-[11px] uppercase font-bold text-gray-400 mb-1 block">More filters</label>
              <app-aria-select
                label="Add Filter"
                [options]="mappedAvailableFacetOptions()"
                [placeholder]="'Select filter'"
                (ngModelChange)="addFacet($event)"
                [ngModel]="''"
              ></app-aria-select>
            </div>
          </div>

          @if (activeFacetList().length > 0) {
            <div class="active-facets">
              @for (facet of activeFacetList(); track facet) {
                <div class="facet-chip">
                  <div class="facet-title">{{ facetLabel(facet) }}</div>
                  <div class="w-full">
                    <app-aria-multiselect
                      [label]="facetLabel(facet)"
                      [options]="mappedFacetOptions(facet)"
                      [selectedValue]="activeFacetFilters()[facet] || []"
                      [multiple]="true"
                      (selectionChange)="updateFacetValues(facet, $event)"
                    ></app-aria-multiselect>
                  </div>
                  <button mat-icon-button (click)="removeFacet(facet)">
                    <mat-icon>close</mat-icon>
                  </button>
                </div>
              }
            </div>
          }

          @if (isLoading()) {
            <div class="loading-state">
              @for (i of [1,2,3,4]; track i) {
                <div class="skeleton-row"></div>
              }
            </div>
          }



          <div class="models-grid">
            @for (def of filteredDefinitions(); track def) {
              <button type="button" class="model-card" (click)="selectDefinition(def)">
                <div class="flex items-start gap-3 w-full">
                  <div class="model-icon"><mat-icon>{{ getCategoryIcon(getUiGroup(def.plr_category || '')) }}</mat-icon></div>
                  <div class="flex flex-col items-start min-w-0">
                    <div class="flex items-center gap-2 w-full">
                      <span class="font-medium truncate">{{ def.name }}</span>
                      <span class="pill">{{ def.plr_category }}</span>
                    </div>
                    <span class="text-xs text-gray-500 truncate">{{ def.vendor || 'Unknown vendor' }} • {{ def.model || def.resource_type || 'Model N/A' }}</span>
                    <span class="text-[11px] text-gray-400 truncate">{{ def.fqn }}</span>
                  </div>
                </div>
              </button>
            }

            @if (!isLoading() && filteredDefinitions().length === 0) {
              <div class="empty-state">
                <mat-icon>filter_list_off</mat-icon>
                <div>No resources match these filters.</div>
              </div>
            }
          </div>
        </div>
      } @else {
        <div class="config-container">
          <!-- Selected Resource Summary -->
          <div class="selected-summary">
            <div class="summary-icon">
              <mat-icon>{{ getCategoryIcon(selectedUiGroup!) }}</mat-icon>
            </div>
            <div class="summary-details">
              <app-resource-chips
                [definition]="selectedDefinition!"
                [showPlrName]="true"
                [showDisplayName]="true">
              </app-resource-chips>
              <div class="text-sm text-gray-500 mt-1">{{ selectedDefinition!.fqn }}</div>
            </div>
          </div>
          <form [formGroup]="form" class="flex flex-col gap-4 py-4">
            <mat-form-field appearance="outline">
              <mat-label>Name</mat-label>
              <input matInput formControlName="name" placeholder="e.g. My Plate 1">
              @if (form.get('name')?.hasError('required')) {
                <mat-error>Name is required</mat-error>
              }
            </mat-form-field>

            <mat-form-field appearance="outline" class="w-full">
              <mat-label>Description</mat-label>
              <textarea matInput formControlName="description" rows="2" placeholder="Optional description"></textarea>
            </mat-form-field>

            <mat-form-field appearance="outline" class="w-full">
              <mat-label>Physical Location Label</mat-label>
              <input matInput formControlName="location_label" placeholder="e.g. Shelf 2, Box 3">
              <mat-hint>Optional label for physical location</mat-hint>
            </mat-form-field>
            <div class="form-row">
              <div class="half-width">
                <label class="text-xs font-medium text-gray-500 mb-1 block">Status</label>
                <app-aria-select
                  label="Status"
                  formControlName="status"
                  [options]="statusOptions"
                ></app-aria-select>
              </div>
              <mat-form-field appearance="outline" class="half-width">
                <mat-label>Parent ID (Optional)</mat-label>
                <input matInput formControlName="parent_accession_id" placeholder="UUID of parent">
              </mat-form-field>
            </div>
          </form>
        </div>
      }
    
      <!-- STEP 2: CONFIGURE (Form) -->
    
    </mat-dialog-content>
    
    @if (selectedDefinition) {
      <mat-dialog-actions align="end">
        <button mat-button (click)="clearSelection()">Back</button>
        <button mat-flat-button color="primary" [disabled]="form.invalid" (click)="save()">Save Resource</button>
      </mat-dialog-actions>
    }
    `,
  styles: [`
    :host { display: block; height: 100%; max-height: 80vh; }
    mat-dialog-content { height: calc(80vh - 120px); min-width: 600px; }
    .selection-shell { display: flex; flex-direction: column; gap: 16px; }
    .search-field { flex: 0 0 auto; }

    .filters-row { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
    .chip-row { display: flex; flex-wrap: wrap; gap: 8px; }
    .filter-chip { display: inline-flex; align-items: center; gap: 6px; border: 1px solid var(--mat-sys-outline-variant); padding: 8px 10px; border-radius: 999px; background: var(--mat-sys-surface); cursor: pointer; transition: all 0.2s ease; }
    .filter-chip .count { font-size: 11px; color: var(--mat-sys-on-surface-variant); }
    .filter-chip:hover { border-color: var(--mat-sys-primary); box-shadow: 0 6px 12px -10px var(--mat-sys-primary); }
    .active-chip { border-color: var(--mat-sys-primary); background: var(--mat-sys-primary-container); color: var(--mat-sys-on-primary-container); }
    .vendor-field, .facet-field { min-width: 180px; }

    .active-facets { display: flex; flex-direction: column; gap: 10px; }
    .facet-chip { display: grid; grid-template-columns: 1fr 3fr auto; align-items: center; gap: 8px; padding: 10px; border: 1px solid var(--mat-sys-outline-variant); border-radius: 12px; background: var(--mat-sys-surface-container); }
    .facet-title { font-size: 0.85rem; font-weight: 600; color: var(--mat-sys-on-surface-variant); }

    .category-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
    .category-card { padding: 12px; border-radius: 14px; border: 1px solid var(--mat-sys-outline-variant); background: linear-gradient(135deg, var(--mat-sys-surface) 0%, var(--mat-sys-surface-container-low, #f6f8fb) 100%); cursor: pointer; transition: all 0.2s ease; }
    .category-card:hover { border-color: var(--mat-sys-primary); box-shadow: 0 8px 18px -14px var(--mat-sys-primary); transform: translateY(-1px); }
    .category-card.card-active { border-color: var(--mat-sys-primary); background: var(--mat-sys-primary-container); color: var(--mat-sys-on-primary-container); }
    .cat-icon { width: 38px; height: 38px; border-radius: 10px; background: var(--mat-sys-surface-container-high, #e8edf5); display: grid; place-items: center; }

    .models-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
    .model-card { border: 1px solid var(--theme-border, var(--mat-sys-outline-variant)); border-radius: 16px; padding: 14px; background: linear-gradient(135deg, var(--mat-sys-surface) 0%, var(--mat-sys-surface-container-low, #f6f8fb) 100%); width: 100%; text-align: left; transition: all 0.18s ease; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
    .model-card:hover { border-color: var(--mat-sys-primary); box-shadow: 0 10px 22px -14px var(--mat-sys-primary); transform: translateY(-1px); }
    .model-icon { width: 44px; height: 44px; border-radius: 12px; background: var(--mat-sys-surface-container-high, #e8edf5); display: grid; place-items: center; }
    .pill { background: var(--mat-sys-surface-container-high); color: var(--mat-sys-on-surface-variant); padding: 2px 8px; border-radius: 999px; font-size: 11px; }

    .loading-state { padding: 12px; }
    .skeleton-row { height: 48px; background: var(--mat-sys-surface-container-highest); margin-bottom: 8px; border-radius: 8px; animation: pulse 1.5s infinite; opacity: 0.5; }
    @keyframes pulse { 0% { opacity: 0.3; } 50% { opacity: 0.6; } 100% { opacity: 0.3; } }
    .empty-state { grid-column: 1 / -1; text-align: center; padding: 32px; color: var(--mat-sys-on-surface-variant); display: flex; flex-direction: column; gap: 8px; align-items: center; }

    .selected-summary { display: flex; gap: 16px; align-items: center; padding: 16px; background: var(--mat-sys-surface-container); border-radius: 8px; margin-bottom: 24px; border: 1px solid var(--mat-sys-outline-variant); }
    .summary-icon mat-icon { font-size: 32px; width: 32px; height: 32px; }
    .form-row { display: flex; gap: 12px; .half-width { flex: 1; } }
  `]
})
export class ResourceDialogComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<ResourceDialogComponent>);
  private assetService = inject(AssetService);

  ResourceStatus = ResourceStatus;

  // UI State
  showPlrName = signal(false); // Toggle for PLR names
  searchControl = new FormControl('');
  selectedDefinition: ResourceDefinition | null = null;
  selectedUiGroup: ResourceUiGroup | null = null;
  isLoading = signal(true);
  categoryFilters = signal<ResourceUiGroup[]>([]);
  vendorFilters = signal<string[]>([]);
  activeFacetFilters = signal<Record<string, string[]>>({});
  facetOptions = signal<Record<string, string[]>>({});
  filteredDefinitions = signal<ResourceDefinition[]>([]);
  vendors = signal<string[]>([]);

  // Data
  // Loaded once, then filtered locally
  private allDefinitions: ResourceDefinition[] = [];

  readonly statusOptions: SelectOption[] = [
    { label: 'Available', value: ResourceStatus.AVAILABLE },
    { label: 'In Use', value: ResourceStatus.IN_USE },
    { label: 'Depleted', value: ResourceStatus.DEPLETED },
  ];

  mappedVendorOptions = computed(() =>
    this.vendors().map(v => ({ label: v || 'Unknown', value: v }))
  );

  mappedAvailableFacetOptions = computed(() =>
    this.availableFacetKeys().map(k => ({ label: this.facetLabel(k), value: k }))
  );

  mappedFacetOptions(facetKey: string): FilterOption[] {
    return (this.facetOptions()[facetKey] || []).map(opt => ({
      label: opt || 'Unknown',
      value: opt
    }));
  }

  private facetCatalog: Record<string, string> = {
    num_items: 'Item Count',
    plate_type: 'Plate Type',
    tip_volume_ul: 'Tip Volume (uL)',
    well_volume_ul: 'Well Volume (uL)',
    resource_type: 'Resource Type'
  };

  // Filtered definitions grouped for display
  groupedDefinitions = signal<GroupedDefinitions[]>([]);

  form = this.fb.group({
    name: ['', Validators.required],
    status: [ResourceStatus.AVAILABLE],
    resource_definition_accession_id: [null as string | null],
    parent_accession_id: [null as string | null],
    location_label: [''],
    description: ['']
  });

  ngOnInit() {
    this.loadDefinitions();

    // Setup search
    this.searchControl.valueChanges.pipe(
      debounceTime(200),
      startWith('')
    ).subscribe(term => {
      this.applyFilters(term || '');
    });
  }

  private loadDefinitions() {
    this.assetService.getResourceDefinitions().subscribe({
      next: (defs) => {
        // Initial filter of hidden items
        this.allDefinitions = defs.filter(d => !shouldHideCategory(d.plr_category));
        this.vendors.set(this.computeVendors(this.allDefinitions));
        this.facetOptions.set(this.computeFacetOptions(this.allDefinitions));
        this.groupedDefinitions.set(this.buildGroups(this.allDefinitions));
        this.isLoading.set(false);
        this.applyFilters('');
      },
      error: (err) => {
        console.error('Error loading resources', err);
        this.isLoading.set(false);
      }
    });
  }

  private filterDefinitions(searchTerm: string) {
    this.applyFilters(searchTerm);
  }

  private applyFilters(searchTerm: string) {
    const term = (searchTerm || '').toLowerCase();
    const categorySet = new Set(this.categoryFilters());
    const vendorSet = new Set(this.vendorFilters());
    const facetFilters = this.activeFacetFilters();

    const filtered = this.allDefinitions.filter(def => {
      const text = [def.name, def.fqn, def.vendor, def.plr_category].join(' ').toLowerCase();
      if (term && !text.includes(term)) return false;

      const group = getUiGroup(def.plr_category);
      if (categorySet.size && !categorySet.has(group)) return false;

      if (vendorSet.size) {
        const vendorVal = def.vendor || 'Unknown';
        if (!vendorSet.has(vendorVal)) return false;
      }

      // Facet filters
      for (const key of Object.keys(facetFilters)) {
        const values = facetFilters[key];
        if (!values || values.length === 0) continue;
        const defVal: any = (def as any)[key];
        const normalized = defVal === undefined || defVal === null ? '' : defVal.toString();
        if (!values.map(v => v.toString()).includes(normalized)) {
          return false;
        }
      }

      return true;
    });

    this.filteredDefinitions.set(filtered);
  }

  private buildGroups(defs: ResourceDefinition[]): GroupedDefinitions[] {
    const groups = new Map<ResourceUiGroup, GroupedDefinitions>();

    UI_GROUP_ORDER.forEach(g => {
      groups.set(g, {
        group: g,
        icon: this.getCategoryIcon(g),
        totalCount: 0,
        subGroups: new Map()
      });
    });

    defs.forEach(def => {
      const groupName = getUiGroup(def.plr_category);
      const groupData = groups.get(groupName)!;
      const subCat = getSubCategory(def.plr_category);

      groupData.totalCount++;
      if (!groupData.subGroups.has(subCat)) {
        groupData.subGroups.set(subCat, []);
      }
      groupData.subGroups.get(subCat)!.push(def);
    });

    return Array.from(groups.values()).filter(g => g.totalCount > 0);
  }

  private computeVendors(defs: ResourceDefinition[]): string[] {
    const set = new Set<string>();
    defs.forEach(d => set.add(d.vendor || 'Unknown'));
    return Array.from(set).sort();
  }

  private computeFacetOptions(defs: ResourceDefinition[]): Record<string, string[]> {
    const opts: Record<string, Set<string>> = {};
    Object.keys(this.facetCatalog).forEach(k => opts[k] = new Set<string>());

    defs.forEach(def => {
      Object.keys(opts).forEach(key => {
        const val = (def as any)[key];
        if (val !== undefined && val !== null && val !== '') {
          opts[key].add(val.toString());
        }
      });
    });

    return Object.fromEntries(Object.entries(opts).map(([k, v]) => [k, Array.from(v).sort()]));
  }

  toggleCategoryFilter(group: ResourceUiGroup) {
    const next = new Set(this.categoryFilters());
    if (next.has(group)) {
      next.delete(group);
    } else {
      next.add(group);
    }
    this.categoryFilters.set(Array.from(next));
    this.applyFilters(this.searchControl.value || '');
  }

  updateVendorFilters(values: string[]) {
    this.vendorFilters.set(values || []);
    this.applyFilters(this.searchControl.value || '');
  }

  addFacet(key: string) {
    if (!key) return;
    if (this.activeFacetFilters()[key]) return;
    const next = { ...this.activeFacetFilters(), [key]: [] };
    this.activeFacetFilters.set(next);
    this.applyFilters(this.searchControl.value || '');
  }

  updateFacetValues(key: string, values: string[]) {
    const next = { ...this.activeFacetFilters(), [key]: values || [] };
    this.activeFacetFilters.set(next);
    this.applyFilters(this.searchControl.value || '');
  }

  removeFacet(key: string) {
    const next = { ...this.activeFacetFilters() };
    delete next[key];
    this.activeFacetFilters.set(next);
    this.applyFilters(this.searchControl.value || '');
  }

  activeFacetList() {
    return Object.keys(this.activeFacetFilters());
  }

  availableFacetKeys() {
    const active = new Set(Object.keys(this.activeFacetFilters()));
    return Object.keys(this.facetCatalog).filter(k => !active.has(k) && (this.facetOptions()[k]?.length || 0) > 0);
  }

  facetLabel(key: string): string {
    return this.facetCatalog[key] || key;
  }

  selectDefinition(def: ResourceDefinition) {
    this.selectedDefinition = def;
    this.selectedUiGroup = getUiGroup(def.plr_category);
    this.form.patchValue({
      resource_definition_accession_id: def.accession_id,
      // Default name to semantic name? Or empty?
      // Let's keep it empty to force user to name it, or maybe use "New [Type]"
    });
  }

  clearSelection() {
    this.selectedDefinition = null;
    this.selectedUiGroup = null;
    this.form.reset({ status: ResourceStatus.AVAILABLE });
  }

  save() {
    if (this.form.valid) {
      this.dialogRef.close(this.form.value);
    }
  }

  // Formatting helpers
  getCategoryIcon(groupName: string): string {
    switch (groupName) {
      case 'Carriers': return 'grid_view';
      case 'Holders': return 'biotech';
      case 'Plates': return 'dataset';
      case 'TipRacks': return 'apps';
      case 'Containers': return 'science';
      case 'Other': return 'category';
      default: return getResourceCategoryIcon(groupName);
    }
  }

  formatSubCategory(key: string): string {
    return key.replace(/_/g, ' ');
  }

  getUiGroup(category: string): ResourceUiGroup {
    return getUiGroup(category);
  }
}
