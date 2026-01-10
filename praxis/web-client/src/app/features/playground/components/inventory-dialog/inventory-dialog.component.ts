
import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal, ViewChild } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormBuilder, FormControl, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatBadgeModule } from '@angular/material/badge';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule, MatSelectionListChange } from '@angular/material/list';
import { MatRadioModule } from '@angular/material/radio';
import { MatSelectModule } from '@angular/material/select';
import { MatStepper, MatStepperModule } from '@angular/material/stepper';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PraxisSelectComponent, SelectOption } from '@shared/components/praxis-select/praxis-select.component';
import { getMachineCategoryIcon, getResourceCategoryIcon } from '@shared/constants/asset-icons';
import { FilterHeaderComponent } from '../../../assets/components/filter-header/filter-header.component';
import { Machine, Resource } from '../../../assets/models/asset.models';
import { AssetService } from '../../../assets/services/asset.service';

export interface InventoryItem {
  type: 'machine' | 'resource';
  asset: Machine | Resource;
  category: string;
  variableName: string;
  count?: number;
  backend?: string;
}

@Component({
  selector: 'app-inventory-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatStepperModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatCardModule,
    MatListModule,
    MatRadioModule,
    MatDividerModule,
    MatTabsModule,
    MatExpansionModule,
    MatBadgeModule,
    MatTooltipModule,
    PraxisSelectComponent,
    FilterHeaderComponent
  ],
  template: `
    <h2 mat-dialog-title>Playground Inventory</h2>
    <mat-dialog-content class="inventory-dialog-content">
      <mat-tab-group (selectedIndexChange)="onTabChange($event)" [selectedIndex]="activeTab()">
        <!-- Tab 1: Quick Add -->
        <mat-tab label="Quick Add">
          <div class="tab-padding">
            <div class="quick-add-container">
              <app-filter-header
                searchPlaceholder="Search machines and resources..."
                [filterCount]="quickFiltersCount()"
                [searchValue]="quickSearch()"
                (searchChange)="quickSearch.set($event)"
                (clearFilters)="clearQuickFilters()">
                
                <div class="filters-grid" filterContent>
                  <div class="filter-group">
                    <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-1 block">Asset Type</label>
                    <app-praxis-select
                      [options]="assetTypeOptions"
                      [formControl]="quickFilterType"
                      placeholder="All Types">
                    </app-praxis-select>
                  </div>

                  <div class="filter-group">
                    <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-1 block">Category</label>
                    <app-praxis-select
                      [options]="categoryOptions()"
                      [formControl]="quickFilterCategory"
                      placeholder="All Categories">
                    </app-praxis-select>
                  </div>
                </div>
              </app-filter-header>

              <div class="quick-results">
                <h3>Recommended & Recent</h3>
                <mat-list>
                  @for (item of filteredQuickAssets(); track item.accession_id) {
                    <mat-list-item class="result-item">
                      <mat-icon matListItemIcon>{{ getAssetIcon(item) }}</mat-icon>
                      <div matListItemTitle class="flex items-center gap-2">
                        {{ item.name }}
                        <span class="category-badge">{{ formatCategory(getCategory(item)) }}</span>
                      </div>
                      <div matListItemLine>{{ getAssetDescription(item) }}</div>
                      <button mat-stroked-button color="primary" matListItemMeta (click)="quickAdd(item)">
                        <mat-icon>add</mat-icon> Add
                      </button>
                    </mat-list-item>
                  }
                  @if (filteredQuickAssets().length === 0) {
                    <div class="empty-state">No matching assets found.</div>
                  }
                </mat-list>
              </div>
            </div>
          </div>
        </mat-tab>

        <!-- Tab 2: Browse & Add -->
        <mat-tab label="Browse & Add">
          <div class="tab-padding">
            <mat-stepper #stepper [linear]="true" class="polished-stepper">
              <!-- Step icons -->
              <ng-template matStepperIcon="edit"><mat-icon>edit</mat-icon></ng-template>
              <ng-template matStepperIcon="done"><mat-icon>check_circle</mat-icon></ng-template>
              <ng-template matStepperIcon="number" let-index="index">
                @if (index === 0) { <mat-icon>person</mat-icon> }
                @else if (index === 1) { <mat-icon>folder</mat-icon> }
                @else if (index === 2) { <mat-icon>grid_view</mat-icon> }
                @else if (index === 3) { <mat-icon>settings</mat-icon> }
                @else { {{index + 1}} }
              </ng-template>

              <!-- Step 1: Asset Type -->
              <mat-step [stepControl]="typeForm" [completed]="typeForm.valid">
                <ng-template matStepLabel>Type</ng-template>
                <div class="step-wrapper">
                  <mat-radio-group [formControl]="typeControl" class="type-cards">
                    <mat-card class="type-card" [class.selected]="typeControl.value === 'machine'" (click)="typeControl.setValue('machine')">
                      <mat-icon class="large-icon">precision_manufacturing</mat-icon>
                      <h3>Machine</h3>
                      <p>Robots and Liquid Handlers</p>
                    </mat-card>
                    <mat-card class="type-card" [class.selected]="typeControl.value === 'resource'" (click)="typeControl.setValue('resource')">
                      <mat-icon class="large-icon">category</mat-icon>
                      <h3>Resource</h3>
                      <p>Plates, Tips, and Labware</p>
                    </mat-card>
                  </mat-radio-group>
                  <div class="step-actions">
                    <button mat-flat-button color="primary" matStepperNext [disabled]="typeControl.invalid">Continue</button>
                  </div>
                </div>
              </mat-step>

              <!-- Step 2: Category -->
              <mat-step [stepControl]="categoryForm" [completed]="categoryForm.valid">
                <ng-template matStepLabel>Category</ng-template>
                <div class="step-wrapper">
                  @if (availableCategories().length > 0) {
                    <div class="chip-container">
                      <mat-chip-listbox [formControl]="categoryControl">
                        @for (cat of availableCategories(); track cat) {
                          <mat-chip-option [value]="cat">
                            <mat-icon matChipAvatar>{{ getCategoryIcon(cat) }}</mat-icon>
                            {{ formatCategory(cat) }}
                          </mat-chip-option>
                        }
                      </mat-chip-listbox>
                    </div>
                  } @else {
                    <div class="empty-state">
                      <mat-icon>category</mat-icon>
                      <p>No categories available. Please select an asset type first.</p>
                    </div>
                  }
                  <div class="step-actions">
                    <button mat-button matStepperPrevious>Back</button>
                    <button mat-flat-button color="primary" matStepperNext [disabled]="categoryControl.invalid">Continue</button>
                  </div>
                </div>
              </mat-step>

              <!-- Step 3: Selection -->
              <mat-step [stepControl]="selectionForm" [completed]="selectionForm.valid">
                <ng-template matStepLabel>Selection</ng-template>
                <div class="step-wrapper">
                  <mat-form-field appearance="outline" class="full-width search-field">
                    <mat-label>Filter assets</mat-label>
                    <input matInput [formControl]="searchControl" placeholder="Type to filter...">
                    <mat-icon matSuffix>search</mat-icon>
                  </mat-form-field>

                  <div class="asset-selection-list">
                    <mat-selection-list [multiple]="false" (selectionChange)="onAssetSelect($event)">
                      @for (item of filteredAssets(); track item.accession_id) {
                        <mat-list-option [value]="item" [selected]="selectionForm.get('asset')?.value === item">
                          <mat-icon matListItemIcon>{{ getCategoryIcon(currentCategory) }}</mat-icon>
                          <h3 matListItemTitle>{{ item.name }}</h3>
                          <p matListItemLine>{{ getAssetDescription(item) }}</p>
                        </mat-list-option>
                      }
                    </mat-selection-list>
                  </div>
                  
                  <div class="step-actions">
                    <button mat-button matStepperPrevious>Back</button>
                    <button mat-flat-button color="primary" matStepperNext [disabled]="selectionForm.invalid">Continue</button>
                  </div>
                </div>
              </mat-step>

              <!-- Step 4: Specifications -->
              <mat-step [stepControl]="specsForm">
                <ng-template matStepLabel>Specs</ng-template>
                <div class="step-wrapper">
                  <form [formGroup]="specsForm" class="specs-form">
                    <mat-form-field appearance="outline" class="full-width">
                      <mat-label>Variable Name</mat-label>
                      <input matInput formControlName="variableName">
                      <mat-hint>Python-valid identifier</mat-hint>
                    </mat-form-field>

                    @if (currentType === 'machine') {
                      <mat-form-field appearance="outline" class="full-width">
                        <mat-label>Backend</mat-label>
                        <mat-select formControlName="backend">
                          <mat-option value="simulated">Simulated (Default)</mat-option>
                        </mat-select>
                      </mat-form-field>
                    }

                    @if (currentType === 'resource') {
                      <mat-form-field appearance="outline" class="full-width">
                        <mat-label>Count</mat-label>
                        <input matInput type="number" formControlName="count" min="1">
                      </mat-form-field>
                    }
                  </form>
                  <div class="step-actions">
                    <button mat-button matStepperPrevious>Back</button>
                    <button mat-raised-button color="primary" (click)="addToList()">Add to Inventory</button>
                  </div>
                </div>
              </mat-step>
            </mat-stepper>
          </div>
        </mat-tab>

        <!-- Tab 3: Current Items -->
        <mat-tab label="Current Items">
          <ng-template matTabLabel>
            <span [matBadge]="addedItems().length" [matBadgeHidden]="addedItems().length === 0" matBadgeOverlap="false" matBadgeColor="accent">
              Current Items
            </span>
          </ng-template>
          <div class="tab-padding">
            <div class="current-items-container">
              <div class="items-header">
                <h3>Inventory Queue ({{ addedItems().length }} items)</h3>
                <button mat-button color="warn" (click)="clearAll()" [disabled]="addedItems().length === 0">
                  <mat-icon>delete_sweep</mat-icon> Clear All
                </button>
              </div>

              <mat-divider></mat-divider>

              <div class="inventory-list-scroll">
                <mat-list>
                  @for (item of addedItems(); track $index) {
                    <mat-list-item class="inventory-card-item">
                      <mat-icon matListItemIcon>{{ item.type === 'machine' ? 'precision_manufacturing' : 'category' }}</mat-icon>
                      <div matListItemTitle class="item-title-field">
                        <mat-form-field appearance="outline" class="compact-field">
                          <input matInput [(ngModel)]="item.variableName" placeholder="Variable Name" matTooltip="Edit variable name">
                        </mat-form-field>
                      </div>
                      <div matListItemLine>
                        {{ item.asset.name }} • <span class="category-badge">{{ formatCategory(item.category) }}</span>
                      </div>
                      <button mat-icon-button matListItemMeta (click)="removeItem($index)" color="warn">
                        <mat-icon>remove_circle_outline</mat-icon>
                      </button>
                    </mat-list-item>
                  }
                  @if (addedItems().length === 0) {
                    <div class="empty-state">No items added to the inventory yet. Browse or Quick Add to start.</div>
                  }
                </mat-list>
              </div>

              <div class="confirm-actions">
                <button mat-button (click)="close()">Cancel</button>
                <button mat-raised-button color="primary" [disabled]="addedItems().length === 0" (click)="confirm()">
                  Insert Assets into Notebook
                </button>
              </div>
            </div>
          </div>
        </mat-tab>
      </mat-tab-group>
    </mat-dialog-content>
  `,
  styles: [`
    .inventory-dialog-content {
      padding: 0 !important;
      height: 650px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .tab-padding {
      padding: 24px;
      height: 550px;
      overflow-y: auto;
    }

    /* Quick Add Styles */
    .quick-add-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .filter-panel {
      box-shadow: none;
      border: 1px solid var(--mat-sys-outline-variant);
      border-radius: 8px !important;
    }

    .filters-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      padding-top: 8px;
    }

    .quick-results {
      margin-top: 8px;
      h3 {
        font-size: 0.9rem;
        font-weight: 500;
        color: var(--mat-sys-on-surface-variant);
        margin-bottom: 8px;
      }
    }

    .result-item {
      border-bottom: 1px solid var(--mat-sys-outline-variant);
      &:last-child { border-bottom: none; }
    }

    .category-badge {
      font-size: 10px;
      background: var(--mat-sys-surface-variant);
      padding: 2px 6px;
      border-radius: 4px;
      text-transform: uppercase;
      font-weight: 600;
    }

    /* Stepper Polish */
    .polished-stepper {
      background: transparent;
    }

    .step-wrapper {
      padding: 16px 4px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .type-cards {
      display: flex;
      gap: 20px;
    }

    .type-card {
      flex: 1;
      padding: 24px;
      text-align: center;
      cursor: pointer;
      border: 2px solid transparent;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      
      &:hover {
        background-color: var(--mat-sys-surface-container-high);
        transform: translateY(-2px);
      }

      &.selected {
        border-color: var(--mat-sys-primary);
        background-color: var(--mat-sys-primary-container);
        color: var(--mat-sys-on-primary-container);
      }

      .large-icon {
        font-size: 48px;
        width: 48px;
        height: 48px;
        margin-bottom: 12px;
        color: var(--mat-sys-primary);
      }

      h3 { margin: 0 0 4px 0; font-size: 1.1rem; }
      p { margin: 0; font-size: 0.85rem; opacity: 0.7; }
    }

    .chip-container {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .asset-selection-list {
      max-height: 250px;
      overflow-y: auto;
      border: 1px solid var(--mat-sys-outline-variant);
      border-radius: 8px;
    }

    .step-actions {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      margin-top: 8px;
    }

    /* Current Items Styles */
    .current-items-container {
      display: flex;
      flex-direction: column;
      height: 100%;
    }

    .items-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      h3 { margin: 0; font-size: 1rem; font-weight: 500; }
    }

    .inventory-list-scroll {
      flex: 1;
      overflow-y: auto;
      margin-top: 12px;
    }

    .inventory-card-item {
      border-radius: 8px;
      margin-bottom: 8px;
      background: var(--mat-sys-surface-container-low);
      border: 1px solid var(--mat-sys-outline-variant);
    }

    .item-title-field {
      display: flex;
      align-items: center;
      .compact-field {
        width: 200px;
        margin-top: 8px;
      }
    }

    :host ::ng-deep .compact-field {
      .mat-mdc-form-field-subscript-wrapper { display: none; }
      .mat-mdc-text-field-wrapper { height: 36px; padding: 0 8px; }
      .mat-mdc-form-field-flex { height: 36px; }
      input { font-family: monospace; font-size: 0.9rem; }
    }

    .confirm-actions {
      padding-top: 24px;
      margin-top: auto;
      display: flex;
      justify-content: flex-end;
      gap: 12px;
    }

    .full-width { width: 100%; }
    .empty-state {
      padding: 40px;
      text-align: center;
      color: var(--mat-sys-on-surface-variant);
      font-style: italic;
    }
  `]
})
export class InventoryDialogComponent {
  @ViewChild('stepper') stepper!: MatStepper;

  private fb = inject(FormBuilder);
  private assetService = inject(AssetService);
  private dialogRef = inject(MatDialogRef<InventoryDialogComponent>);

  addedItems = signal<InventoryItem[]>([]);
  activeTab = signal(0);

  // Data sources
  machines = toSignal(this.assetService.getMachines(), { initialValue: [] as Machine[] });
  resources = toSignal(this.assetService.getResources(), { initialValue: [] as Resource[] });

  // Control for stepper
  typeControl = new FormControl<'machine' | 'resource' | ''>('', { nonNullable: true, validators: [Validators.required] });
  categoryControl = new FormControl('', { nonNullable: true, validators: [Validators.required] });

  // Forms
  typeForm = this.fb.group({ type: this.typeControl });
  categoryForm = this.fb.group({ category: this.categoryControl });
  selectionForm = this.fb.group({
    asset: [null as Machine | Resource | null, Validators.required]
  });

  searchControl = this.fb.control('');

  specsForm = this.fb.group({
    variableName: ['', [Validators.required, Validators.pattern(/^[a-zA-Z_][a-zA-Z0-9_]*$/)]],
    count: [1],
    backend: ['simulated']
  });

  // Quick Add Filters
  readonly assetTypeOptions: SelectOption[] = [
    { label: 'All Types', value: 'all', icon: 'apps' },
    { label: 'Machines', value: 'machine', icon: 'precision_manufacturing' },
    { label: 'Resources', value: 'resource', icon: 'science' }
  ];

  quickSearch = signal('');
  quickFilterType = new FormControl('all', { nonNullable: true });
  quickFilterCategory = new FormControl('all', { nonNullable: true });

  // Signals for form controls to drive computed values
  quickFilterTypeValue = toSignal(this.quickFilterType.valueChanges, { initialValue: 'all' });
  quickFilterCategoryValue = toSignal(this.quickFilterCategory.valueChanges, { initialValue: 'all' });

  // Browser Tab Signals
  typeValue = toSignal(this.typeControl.valueChanges, { initialValue: '' });
  categoryValue = toSignal(this.categoryControl.valueChanges, { initialValue: '' });
  searchValue = toSignal(this.searchControl.valueChanges, { initialValue: '' });

  machineCategories = computed(() => {
    const cats = new Set<string>();
    this.machines()?.forEach(m => {
      if (m.machine_category) cats.add(m.machine_category);
    });
    return Array.from(cats).sort();
  });

  resourceCategories = computed(() => {
    const cats = new Set<string>();
    this.resources()?.forEach(r => {
      const cat = this.getResourceCategory(r);
      if (cat) cats.add(cat);
    });
    return Array.from(cats).sort();
  });

  categoryOptions = computed<SelectOption[]>(() => {
    const type = this.quickFilterTypeValue();
    const allLabel: SelectOption = { label: 'All Categories', value: 'all' };

    // Helper to map string[] to SelectOption[]
    const mapCats = (cats: string[]) => cats.map(c => ({ label: this.formatCategory(c), value: c }));

    if (type === 'machine') {
      return [allLabel, ...mapCats(this.machineCategories())];
    }
    
    if (type === 'resource') {
      return [allLabel, ...mapCats(this.resourceCategories())];
    }

    // If 'all', return grouped with separators
    return [
      allLabel,
      { label: '── Machines ──', value: 'HEADER_MACHINES', disabled: true },
      ...mapCats(this.machineCategories()),
      { label: '── Resources ──', value: 'HEADER_RESOURCES', disabled: true },
      ...mapCats(this.resourceCategories())
    ];
  });

  quickFiltersCount = computed(() => {
    let count = 0;
    if (this.quickFilterTypeValue() !== 'all') count++;
    if (this.quickFilterCategoryValue() !== 'all') count++;
    return count;
  });

  // Computed
  currentType = '';
  currentCategory = '';

  constructor() {
    // Sync theme if needed
    // Reset forms when type changes
    this.typeControl.valueChanges.subscribe(val => {
      if (val) {
        this.currentType = val;
        this.categoryControl.reset();
        this.selectionForm.reset();
        this.specsForm.reset({ count: 1, backend: 'simulated' });
      }
    });

    // Reset selection when category changes
    this.categoryControl.valueChanges.subscribe(val => {
      if (val) {
        this.currentCategory = val;
        this.selectionForm.reset();
      }
    });

    // Auto-generate variable name when asset selected
    this.selectionForm.get('asset')?.valueChanges.subscribe((val: Machine | Resource | null) => {
      if (val) {
        this.generateVariableName(val);
      }
    });

    // Reset quick filter category when quick filter type changes
    this.quickFilterType.valueChanges.subscribe(() => {
      this.quickFilterCategory.setValue('all');
    });
  }

  allAssetOptions = computed(() => {
    const machinery = this.machines()?.map(m => ({
      label: m.name,
      value: { type: 'machine', asset: m },
      icon: 'precision_manufacturing'
    })) || [];
    const res = this.resources()?.map(r => ({
      label: r.name,
      value: { type: 'resource', asset: r },
      icon: 'category'
    })) || [];
    return [...machinery, ...res] as SelectOption[];
  });

  allCategories = computed(() => {
    const cats = new Set<string>();
    this.machines()?.forEach(m => {
      if (m.machine_category) cats.add(m.machine_category);
    });
    this.resources()?.forEach(r => {
      const cat = this.getResourceCategory(r);
      if (cat) cats.add(cat);
    });
    return Array.from(cats).sort();
  });

  availableCategories = computed(() => {
    const type = this.typeValue();
    const cats = new Set<string>();

    if (type === 'machine') {
      this.machines()?.forEach(m => {
        if (m.machine_category) cats.add(m.machine_category);
      });
    } else if (type === 'resource') {
      this.resources()?.forEach(r => {
        const cat = this.getResourceCategory(r);
        if (cat) cats.add(cat);
      });
    }
    return Array.from(cats).sort();
  });

  filteredAssets = computed(() => {
    const type = this.typeValue();
    const category = this.categoryValue();
    const search = this.searchValue()?.toLowerCase() || '';

    if (!type || !category) return [];

    let list: (Machine | Resource)[] = [];
    if (type === 'machine') {
      list = (this.machines() || []).filter(m => m.machine_category === category);
    } else {
      list = (this.resources() || []).filter(r => this.getResourceCategory(r) === category);
    }

    if (search) {
      list = list.filter(item => item.name.toLowerCase().includes(search));
    }

    return list;
  });

  filteredQuickAssets = computed(() => {
    const typeFilter = this.quickFilterTypeValue();
    const catFilter = this.quickFilterCategoryValue();
    const search = this.quickSearch().toLowerCase();

    let all: (Machine | Resource)[] = [...(this.machines() || []), ...(this.resources() || [])];

    if (search) {
      all = all.filter(a => a.name.toLowerCase().includes(search));
    }

    if (typeFilter !== 'all') {
      all = all.filter(a => {
        if (typeFilter === 'machine') return 'machine_category' in a;
        return !('machine_category' in a);
      });
    }

    if (catFilter !== 'all') {
      all = all.filter(a => this.getCategory(a) === catFilter);
    }

    // Limit to 10 results for performance/UX
    return all.slice(0, 10);
  });

  clearQuickFilters() {
    this.quickFilterType.setValue('all');
    this.quickFilterCategory.setValue('all');
    this.quickSearch.set('');
  }

  onTabChange(index: number) {
    this.activeTab.set(index);
  }

  onQuickSelect(selected: unknown) {
    const val = selected as { type: string; asset: Machine | Resource };
    if (val && val.asset) {
      this.quickAdd(val.asset);
    }
  }

  quickAdd(asset: Machine | Resource) {
    const type = 'machine_category' in asset ? 'machine' : 'resource';
    const item: InventoryItem = {
      type,
      asset,
      category: this.getCategory(asset),
      variableName: this.deriveSafeVariableName(asset),
      count: 1,
      backend: type === 'machine' ? 'simulated' : undefined
    };

    // Check for duplicates in variable name
    let finalItem = item;
    const existing = this.addedItems().some(i => i.variableName === item.variableName);
    if (existing) {
      finalItem = { ...item, variableName: item.variableName + '_' + (this.addedItems().length + 1) };
    }

    this.addedItems.update(items => [...items, finalItem]);
    this.activeTab.set(2); // Switch to Current Items
  }

  getAssetIcon(item: Machine | Resource): string {
    if ('machine_category' in item) return 'precision_manufacturing';
    return 'category';
  }

  getCategory(item: Machine | Resource): string {
    if ('machine_category' in item) return (item as Machine).machine_category ?? 'Unknown';
    return this.getResourceCategory(item as Resource);
  }

  getCategoryIcon(cat: string): string {
    const type = this.typeValue();
    if (type === 'machine') return getMachineCategoryIcon(cat);
    return getResourceCategoryIcon(cat);
  }

  getResourceCategory(r: Resource): string {
    return r.plr_definition?.plr_category || r.asset_type || 'Other';
  }

  onAssetSelect(event: MatSelectionListChange) {
    const selected = event.options[0].value;
    this.selectionForm.get('asset')?.setValue(selected);
  }

  private generateVariableName(val: Machine | Resource) {
    const safeName = this.deriveSafeVariableName(val);
    this.specsForm.patchValue({ variableName: safeName });
  }

  private deriveSafeVariableName(val: Machine | Resource): string {
    return val.name.toLowerCase().replace(/[^a-z0-9_]/g, '_').replace(/_+/g, '_');
  }

  addToList() {
    if (this.specsForm.valid && this.selectionForm.value.asset) {
      const item: InventoryItem = {
        type: this.currentType as 'machine' | 'resource',
        asset: this.selectionForm.value.asset,
        category: this.currentCategory,
        variableName: this.specsForm.value.variableName!,
        count: this.specsForm.value.count || 1,
        backend: this.specsForm.value.backend || undefined
      };

      this.addedItems.update(items => [...items, item]);

      // Reset for next item
      this.stepper.reset();
      this.activeTab.set(2); // Show items
    }
  }

  removeItem(index: number) {
    this.addedItems.update(items => items.filter((_, i) => i !== index));
  }

  clearAll() {
    this.addedItems.set([]);
  }

  close() {
    this.dialogRef.close();
  }

  confirm() {
    this.dialogRef.close(this.addedItems());
  }

  getAssetDescription(item: Machine | Resource): string {
    if ('description' in item && item.description) {
      return item.description;
    }
    if (item.plr_definition?.description) {
      return item.plr_definition.description;
    }
    return 'No description';
  }

  formatCategory(cat: string): string {
    if (!cat) return '';
    return cat
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  }
}
