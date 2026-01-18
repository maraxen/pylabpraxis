import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal, ViewChild, ChangeDetectionStrategy } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormBuilder, FormControl, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatBadgeModule } from '@angular/material/badge';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
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
import { Machine, Resource, MachineDefinition, ResourceDefinition, MachineStatus, ResourceStatus, MachineFrontendDefinition, MachineBackendDefinition } from '../../../assets/models/asset.models';
import { AssetService } from '../../../assets/services/asset.service';
import { DeckCatalogService } from '../../../run-protocol/services/deck-catalog.service';
import { DeckConfiguration } from '../../../run-protocol/models/deck-layout.models';

export interface InventoryItem {
  type: 'machine' | 'resource';
  asset: Machine | Resource;
  category: string;
  variableName: string;
  count?: number;
  deckConfigId?: string;
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
    FilterHeaderComponent,
    MatProgressSpinnerModule
  ],
  template: `
    <h2 mat-dialog-title>Playground Inventory</h2>
    <mat-dialog-content class="inventory-dialog-content">
      <mat-tab-group (selectedIndexChange)="onTabChange($event)" [selectedIndex]="activeTab()">
        <!-- Tab 0: Quick Add -->
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
                        @if (isTemplate(item)) {
                          <span class="template-badge">Template</span>
                        }
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

        <!-- Tab 1: Browse & Add -->
        <mat-tab label="Browse & Add">
          <div class="tab-padding">
            <mat-stepper #stepper [linear]="true" class="polished-stepper">
              <ng-template matStepperIcon="edit"><mat-icon>edit</mat-icon></ng-template>
              <ng-template matStepperIcon="done"><mat-icon>check_circle</mat-icon></ng-template>
              <ng-template matStepperIcon="number" let-index="index">
                @if (index === 0) { <mat-icon>person</mat-icon> }
                @else if (index === 1) { <mat-icon>folder</mat-icon> }
                @else if (index === 2) { <mat-icon>grid_view</mat-icon> }
                @else if (index === 3) { <mat-icon>settings</mat-icon> }
                @else { {{index + 1}} }
              </ng-template>

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
                          <h3 matListItemTitle class="flex items-center gap-2">
                            {{ item.name }}
                            @if (isTemplate(item)) {
                              <span class="template-badge small">Template</span>
                            }
                          </h3>
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
                      @if ( availableDeckConfigs().length > 0 ) {
                          <mat-form-field appearance="outline" class="full-width">
                            <mat-label>Deck Configuration</mat-label>
                            <mat-select formControlName="deckConfigId">
                              <mat-option [value]="''">Default (Standard)</mat-option>
                              <mat-divider></mat-divider>
                              <mat-optgroup label="User Configurations">
                                @for (config of availableDeckConfigs(); track config.id) {
                                  <mat-option [value]="config.id">
                                    {{ config.name || 'Unnamed Config' }}
                                  </mat-option>
                                }
                              </mat-optgroup>
                            </mat-select>
                            <mat-hint>Select a saved simulation deck layout</mat-hint>
                          </mat-form-field>
                      }
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

        <!-- Tab 2: Current Items -->
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
                        @if (isTemplate(item.asset)) {
                          <span class="template-badge small ml-2">Template</span>
                        }
                      </div>
                      <div matListItemLine *ngIf="item.deckConfigId" class="text-xs text-slate-500">
                         Config: {{ getDeckConfigName(item.deckConfigId) }}
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
      display: flex;
      flex-direction: column;
      overflow: hidden;
      flex: 1;
    }

    .tab-padding {
      padding: 24px;
      overflow-y: auto;
      flex: 1;
    }

    mat-tab-group {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }

    :host ::ng-deep .mat-mdc-tab-body-wrapper {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }

    :host ::ng-deep .mat-mdc-tab-body {
      flex: 1;
      display: flex;
      flex-direction: column;
    }

    :host ::ng-deep .mat-mdc-tab-body-content {
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    .quick-add-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
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

    .template-badge {
      font-size: 10px;
      background: var(--mat-sys-tertiary-container);
      color: var(--mat-sys-on-tertiary-container);
      padding: 2px 6px;
      border-radius: 4px;
      text-transform: uppercase;
      font-weight: 600;
      margin-left: 8px;
    }
    
    .template-badge.small {
      font-size: 9px;
      padding: 1px 4px;
    }

    .polished-stepper {
      background: transparent;
      height: 100%;
      display: flex;
      flex-direction: column;
      --mat-stepper-container-color: transparent;
    }

    :host ::ng-deep {
      .mat-horizontal-stepper-header-container { padding: 0 16px; }
      .mat-horizontal-content-container { padding: 0 !important; flex-grow: 1; overflow-y: auto; }
      .mat-step-header .mat-step-icon-selected { background-color: var(--mat-sys-primary); color: var(--mat-sys-on-primary); }
    }

    .step-wrapper { padding: 16px 24px; display: flex; flex-direction: column; gap: 20px; }
    .type-cards { display: flex; gap: 20px; }
    .type-card {
      flex: 1; padding: 24px; text-align: center; cursor: pointer; border: 2px solid transparent;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      &:hover { background-color: var(--mat-sys-surface-container-high); transform: translateY(-2px); }
      &.selected { border-color: var(--mat-sys-primary); background-color: var(--mat-sys-primary-container); }
      .large-icon { font-size: 48px; width: 48px; height: 48px; margin-bottom: 12px; color: var(--mat-sys-primary); }
      h3 { margin: 0 0 4px 0; font-size: 1.1rem; }
      p { margin: 0; font-size: 0.85rem; opacity: 0.7; }
    }

    .chip-container { display: flex; flex-wrap: wrap; gap: 8px; }
    .asset-selection-list { max-height: 250px; overflow-y: auto; border: 1px solid var(--mat-sys-outline-variant); border-radius: 8px; }
    .step-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 8px; }
    .current-items-container { display: flex; flex-direction: column; height: 100%; }
    .items-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .inventory-list-scroll { flex: 1; overflow-y: auto; margin-top: 12px; }
    .inventory-card-item { border-radius: 8px; margin-bottom: 8px; background: var(--mat-sys-surface-container-low); border: 1px solid var(--mat-sys-outline-variant); }
    .item-title-field { display: flex; align-items: center; .compact-field { width: 200px; margin-top: 8px; } }
    :host ::ng-deep .compact-field { .mat-mdc-form-field-subscript-wrapper { display: none; } .mat-mdc-text-field-wrapper { height: 36px; padding: 0 8px; } input { font-family: monospace; font-size: 0.9rem; } }
    .confirm-actions { padding-top: 24px; margin-top: auto; display: flex; justify-content: flex-end; gap: 12px; }
    .full-width { width: 100%; }
    .empty-state { padding: 40px; text-align: center; color: var(--mat-sys-on-surface-variant); font-style: italic; }

    .catalog-container { display: flex; flex-direction: column; gap: 16px; }
    .catalog-header { margin-bottom: 8px; h3 { margin: 0; font-size: 1.25rem; } p { margin: 0; color: var(--mat-sys-on-surface-variant); } }
    .definitions-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; padding: 16px 0; }
    .definition-card { border: 1px solid var(--mat-sys-outline-variant); box-shadow: none !important; mat-card-title { font-size: 1rem !important; margin-bottom: 0 !important; } mat-card-header { padding: 16px 16px 0 16px; } }
    .category-panel { box-shadow: none !important; border: 1px solid var(--mat-sys-outline-variant); margin-bottom: 8px; border-radius: 8px !important; &.mat-expanded { margin-bottom: 16px; } }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class InventoryDialogComponent {
  @ViewChild('stepper') stepper!: MatStepper;

  private fb = inject(FormBuilder);
  private assetService = inject(AssetService);
  private deckService = inject(DeckCatalogService);
  private dialogRef = inject(MatDialogRef<InventoryDialogComponent>);

  addedItems = signal<InventoryItem[]>([]);
  activeTab = signal(0);
  availableDeckConfigs = signal<{ id: string, name: string, config: DeckConfiguration }[]>([]);

  // Data sources
  machines = toSignal(this.assetService.getMachines(), { initialValue: [] as Machine[] });
  resources = toSignal(this.assetService.getResources(), { initialValue: [] as Resource[] });
  machineDefinitions = toSignal(this.assetService.getMachineDefinitions(), { initialValue: [] as MachineDefinition[] });
  resourceDefinitions = toSignal(this.assetService.getResourceDefinitions(), { initialValue: [] as ResourceDefinition[] });

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
    deckConfigId: ['']
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

  isCreating = signal(false);

  machineCategories = computed(() => {
    const cats = new Set<string>();
    // Instances
    this.machines()?.forEach(m => {
      if (m.machine_category) cats.add(m.machine_category);
    });
    // Definitions
    this.machineDefinitions()?.forEach(d => {
      if (d.machine_category) cats.add(d.machine_category);
    });
    return Array.from(cats).sort();
  });

  resourceCategories = computed(() => {
    const cats = new Set<string>();
    // Instances
    this.resources()?.forEach(r => {
      const cat = this.getResourceCategory(r);
      if (cat) cats.add(cat);
    });
    // Definitions
    this.resourceDefinitions()?.forEach(d => {
      if (d.plr_category) cats.add(d.plr_category);
    });
    return Array.from(cats).sort();
  });

  categoryOptions = computed<SelectOption[]>(() => {
    const type = this.quickFilterTypeValue();
    const allLabel: SelectOption = { label: 'All Categories', value: 'all' };
    const mapCats = (cats: string[]) => cats.map(c => ({ label: this.formatCategory(c), value: c }));

    if (type === 'machine') return [allLabel, ...mapCats(this.machineCategories())];
    if (type === 'resource') return [allLabel, ...mapCats(this.resourceCategories())];

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

  currentType = '';
  currentCategory = '';

  constructor() {
    this.typeControl.valueChanges.subscribe(val => {
      if (val) {
        this.currentType = val;
        this.categoryControl.reset();
        this.selectionForm.reset();
        this.specsForm.reset({ count: 1, deckConfigId: '' });
        this.availableDeckConfigs.set([]);
      }
    });

    this.categoryControl.valueChanges.subscribe(val => {
      if (val) {
        this.currentCategory = val;
        this.selectionForm.reset();
      }
    });

    this.selectionForm.get('asset')?.valueChanges.subscribe((val: Machine | Resource | null) => {
      if (val) {
        this.generateVariableName(val);
        if ('machine_category' in val) {
          const machine = val as Machine;
          this.deckService.getUserDeckConfigurations().subscribe(configs => {
            const compatible = configs.filter(c => {
              if (machine.name.toLowerCase().includes('star') && c.config.deckType.includes('STAR')) return true;
              if (machine.name.toLowerCase().includes('ot') && c.config.deckType.includes('OT')) return true;
              return true;
            });
            this.availableDeckConfigs.set(compatible);
          });
        }
      }
    });

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
    
    // Add virtual machines from definitions
    const virtualMachines = this.machineDefinitions()?.map(d => ({
      label: d.name,
      value: { type: 'machine', asset: this.mapMachineDefinitionToVirtualMachine(d) },
      icon: 'precision_manufacturing'
    })) || [];

    const res = this.resources()?.map(r => ({
      label: r.name,
      value: { type: 'resource', asset: r },
      icon: 'category'
    })) || [];

    // Add virtual resources from definitions
    const virtualResources = this.resourceDefinitions()?.map(d => ({
      label: d.name,
      value: { type: 'resource', asset: this.mapResourceDefinitionToVirtualResource(d) },
      icon: 'category'
    })) || [];

    return [...machinery, ...virtualMachines, ...res, ...virtualResources] as SelectOption[];
  });

  allCategories = computed(() => {
    const cats = new Set<string>();
    this.machines()?.forEach(m => { if (m.machine_category) cats.add(m.machine_category); });
    this.machineDefinitions()?.forEach(d => { if (d.machine_category) cats.add(d.machine_category); });
    this.resources()?.forEach(r => { const cat = this.getResourceCategory(r); if (cat) cats.add(cat); });
    this.resourceDefinitions()?.forEach(d => { if (d.plr_category) cats.add(d.plr_category); });
    return Array.from(cats).sort();
  });

  availableCategories = computed(() => {
    const type = this.typeValue();
    const cats = new Set<string>();
    if (type === 'machine') {
      this.machines()?.forEach(m => { if (m.machine_category) cats.add(m.machine_category); });
      this.machineDefinitions()?.forEach(d => { if (d.machine_category) cats.add(d.machine_category); });
    } else if (type === 'resource') {
      this.resources()?.forEach(r => { const cat = this.getResourceCategory(r); if (cat) cats.add(cat); });
      this.resourceDefinitions()?.forEach(d => { if (d.plr_category) cats.add(d.plr_category); });
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
      // Instances
      const instances = (this.machines() || []).filter(m => m.machine_category === category);
      // Definitions mapped to virtual instances
      // Filter out definitions that already have an instance if desired? 
      // User requested "always allow adding simulation machines", so we show them as templates.
      const templates = (this.machineDefinitions() || [])
        .filter(d => d.machine_category === category)
        .map(d => this.mapMachineDefinitionToVirtualMachine(d));
      
      list = [...instances, ...templates];
    }
    else {
      // Resources
      const instances = (this.resources() || []).filter(r => this.getResourceCategory(r) === category);
      const templates = (this.resourceDefinitions() || [])
        .filter(d => d.plr_category === category)
        .map(d => this.mapResourceDefinitionToVirtualResource(d));
        
      list = [...instances, ...templates];
    }

    if (search) list = list.filter(item => item.name.toLowerCase().includes(search));
    return list;
  });

  filteredQuickAssets = computed(() => {
    const typeFilter = this.quickFilterTypeValue();
    const catFilter = this.quickFilterCategoryValue();
    const search = this.quickSearch().toLowerCase();
    
    // Build combined list
    const machines = [
      ...(this.machines() || []),
      ...(this.machineDefinitions() || []).map(d => this.mapMachineDefinitionToVirtualMachine(d))
    ];
    
    const resources = [
      ...(this.resources() || []),
      ...(this.resourceDefinitions() || []).map(d => this.mapResourceDefinitionToVirtualResource(d))
    ];

    let all: (Machine | Resource)[] = [...machines, ...resources];
    
    if (search) all = all.filter(a => a.name.toLowerCase().includes(search));
    if (typeFilter !== 'all') {
      all = all.filter(a => typeFilter === 'machine' ? 'machine_category' in a : !('machine_category' in a));
    }
    if (catFilter !== 'all') all = all.filter(a => this.getCategory(a) === catFilter);
    return all.slice(0, 10);
  });

  clearQuickFilters() {
    this.quickFilterType.setValue('all');
    this.quickFilterCategory.setValue('all');
    this.quickSearch.set('');
  }

  onTabChange(index: number) { this.activeTab.set(index); }
  onQuickSelect(selected: unknown) {
    const val = selected as { type: string; asset: Machine | Resource };
    if (val && val.asset) this.quickAdd(val.asset);
  }

  onAssetSelect(event: MatSelectionListChange) {
    const asset = event.options[0]?.value;
    if (asset) {
      this.selectionForm.patchValue({ asset });
    }
  }

  addToList() {
    if (this.currentType === 'machine') {
      const asset = this.selectionForm.get('asset')?.value as Machine;
      if (asset) {
        this.addItem({
          type: 'machine',
          asset: asset,
          category: this.getCategory(asset),
          variableName: this.specsForm.get('variableName')?.value || this.deriveSafeVariableName(asset),
          count: 1,
          deckConfigId: this.specsForm.get('deckConfigId')?.value || undefined
        });
      }
    } else {
      const asset = this.selectionForm.get('asset')?.value as Resource;
      if (asset) {
        this.addItem({
          type: 'resource',
          asset: asset,
          category: this.getCategory(asset),
          variableName: this.specsForm.get('variableName')?.value || this.deriveSafeVariableName(asset),
          count: this.specsForm.get('count')?.value || 1
        });
      }
    }
    this.activeTab.set(2);
  }

  quickAdd(asset: Machine | Resource) {
    const type = 'machine_category' in asset ? 'machine' : 'resource';
    this.addItem({
      type,
      asset,
      category: this.getCategory(asset),
      variableName: this.deriveSafeVariableName(asset),
      count: 1
    });
    this.activeTab.set(2);
  }

  private addItem(item: InventoryItem) {
    let finalItem = item;
    if (this.addedItems().some(i => i.variableName === item.variableName)) {
      finalItem = { ...item, variableName: item.variableName + '_' + (this.addedItems().length + 1) };
    }
    this.addedItems.update(items => [...items, finalItem]);
  }

  removeItem(index: number) { this.addedItems.update(items => items.filter((_, i) => i !== index)); }
  clearAll() { this.addedItems.set([]); }
  close() { this.dialogRef.close(); }
  confirm() { this.dialogRef.close(this.addedItems()); }

  // Helpers
  getAssetIcon(item: Machine | Resource): string {
    return 'machine_category' in item ? getMachineCategoryIcon(item.machine_category || '') : getResourceCategoryIcon(this.getResourceCategory(item as Resource));
  }
  getCategoryIcon(cat: string): string {
    return this.typeValue() === 'machine' ? getMachineCategoryIcon(cat) : getResourceCategoryIcon(cat);
  }
  formatCategory(cat: string): string { return cat.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()); }
  getCategory(item: Machine | Resource): string {
    return 'machine_category' in item ? (item.machine_category || 'Other') : this.getResourceCategory(item as Resource);
  }
  private getResourceCategory(r: Resource): string { return r.plr_definition?.category || 'Other'; }
  getAssetDescription(item: Machine | Resource): string { return 'description' in item ? item.description || '' : ''; }
  getDeckConfigName(id: string): string { return this.availableDeckConfigs().find(c => c.id === id)?.name || 'Default'; }

  private generateVariableName(asset: Machine | Resource) {
    this.specsForm.patchValue({ variableName: this.deriveSafeVariableName(asset) });
  }
  private deriveSafeVariableName(asset: Machine | Resource): string {
    return asset.name.toLowerCase().replace(/[^a-z0-9_]/g, '_').replace(/^([0-9])/, '_$1').replace(/_+/g, '_').replace(/_$/, '');
  }

  // Definition Mappers
  private mapMachineDefinitionToVirtualMachine(def: MachineDefinition): Machine {
    return {
      accession_id: crypto.randomUUID(),
      name: `${def.name} ${Math.floor(Math.random() * 100)}`,
      status: MachineStatus.IDLE,
      machine_category: def.machine_category,
      // NEW: Add frontend/backend definition references
      frontend_definition_accession_id: def.frontend_definition_accession_id,
      backend_definition_accession_id: def.accession_id,
      backend_config: {},
      // Keep legacy fields
      machine_type: def.machine_category,
      is_simulation_override: def.backend_type === 'simulator',

      description: def.description,
      manufacturer: def.manufacturer,
      model: def.model,
      connection_info: { backend: 'Simulator', plr_backend: def.fqn },
      plr_definition: def,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
  }

  private mapResourceDefinitionToVirtualResource(def: ResourceDefinition): Resource {
    return {
      accession_id: crypto.randomUUID(),
      name: def.name,
      description: def.description,
      status: ResourceStatus.AVAILABLE,
      resource_definition_accession_id: def.accession_id,
      plr_definition: { 
        ...def, 
        category: def.plr_category || 'Other' 
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
  }

  isTemplate(item: Machine | Resource): boolean {
    if ('machine_category' in item) {
      const machine = item as Machine;
      return machine.backend_definition?.backend_type === 'simulator' ||
             machine.is_simulation_override === true;
    }
    return item.accession_id.startsWith('template-');
  }
}
