
import { Component, inject, signal, computed, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatStepper, MatStepperModule } from '@angular/material/stepper';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';
import { MatListModule, MatSelectionListChange } from '@angular/material/list';
import { MatRadioModule } from '@angular/material/radio';
import { MatDividerModule } from '@angular/material/divider';
import { AssetService } from '../../../assets/services/asset.service';
import { Machine, Resource } from '../../../assets/models/asset.models';
import { getResourceCategoryIcon, getMachineCategoryIcon } from '@shared/constants/asset-icons';
import { toSignal } from '@angular/core/rxjs-interop';

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
    MatDividerModule
  ],
  template: `
    <h2 mat-dialog-title>Add to Playground Inventory</h2>
    <mat-dialog-content>
      <div class="dialog-layout">
        <!-- Main Stepper Area -->
        <div class="stepper-container">
          <mat-stepper #stepper [linear]="true" orientation="vertical">
            <!-- Step 1: Asset Type -->
            <mat-step [stepControl]="typeForm">
              <ng-template matStepLabel>Select Asset Type</ng-template>
              <form [formGroup]="typeForm" class="step-content type-selection">
                <mat-radio-group formControlName="type" class="type-radio-group">
                  <mat-card 
                    class="type-card" 
                    [class.selected]="typeForm.get('type')?.value === 'machine'"
                    (click)="typeForm.get('type')?.setValue('machine')">
                    <mat-icon class="large-icon">precision_manufacturing</mat-icon>
                    <h3>Machine</h3>
                    <p>Robots and Liquid Handlers</p>
                    <mat-radio-button value="machine" class="hidden-radio"></mat-radio-button>
                  </mat-card>

                  <mat-card 
                    class="type-card" 
                    [class.selected]="typeForm.get('type')?.value === 'resource'"
                    (click)="typeForm.get('type')?.setValue('resource')">
                    <mat-icon class="large-icon">category</mat-icon>
                    <h3>Resource</h3>
                    <p>Plates, Tips, and Labware</p>
                    <mat-radio-button value="resource" class="hidden-radio"></mat-radio-button>
                  </mat-card>
                </mat-radio-group>
                <div class="step-actions">
                  <button mat-button matStepperNext [disabled]="typeForm.invalid">Next</button>
                </div>
              </form>
            </mat-step>

            <!-- Step 2: Category -->
            <mat-step [stepControl]="categoryForm">
              <ng-template matStepLabel>Select Category</ng-template>
              <div class="step-content">
                <mat-chip-listbox aria-label="Category Selection" [selectable]="true">
                   @for (cat of availableCategories(); track cat) {
                     <mat-chip-option 
                        [selected]="categoryForm.get('category')?.value === cat"
                        (selectionChange)="selectCategory(cat)">
                        <mat-icon matChipAvatar>{{ getCategoryIcon(cat) }}</mat-icon>
                        {{ cat }}
                     </mat-chip-option>
                   }
                </mat-chip-listbox>
                <div class="step-actions">
                  <button mat-button matStepperPrevious>Back</button>
                  <button mat-button matStepperNext [disabled]="categoryForm.invalid">Next</button>
                </div>
              </div>
            </mat-step>

            <!-- Step 3: Selection -->
            <mat-step [stepControl]="selectionForm">
              <ng-template matStepLabel>Select Asset</ng-template>
              <div class="step-content">
                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Search Assets</mat-label>
                  <input matInput [formControl]="searchControl" placeholder="Filter by name...">
                  <mat-icon matSuffix>search</mat-icon>
                </mat-form-field>

                <mat-selection-list [multiple]="false" (selectionChange)="onAssetSelect($event)">
                  @for (item of filteredAssets(); track item.accession_id) {
                    <mat-list-option [value]="item">
                      <mat-icon matListItemIcon>{{ getCategoryIcon(currentCategory) }}</mat-icon>
                      <h3 matListItemTitle>{{ item.name }}</h3>
                      <p matListItemLine>{{ getAssetDescription(item) }}</p>
                    </mat-list-option>
                  }
                  @if (filteredAssets().length === 0) {
                     <div class="empty-state">No assets found in this category.</div>
                  }
                </mat-selection-list>
                
                <div class="step-actions">
                  <button mat-button matStepperPrevious>Back</button>
                  <button mat-button matStepperNext [disabled]="selectionForm.invalid">Next</button>
                </div>
              </div>
            </mat-step>

            <!-- Step 4: Specifications -->
            <mat-step [stepControl]="specsForm">
              <ng-template matStepLabel>Configure</ng-template>
              <form [formGroup]="specsForm" class="step-content">
                
                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Variable Name</mat-label>
                  <input matInput formControlName="variableName" placeholder="e.g. my_plate">
                  <mat-hint>This name will be used in the Python code</mat-hint>
                  <mat-error *ngIf="specsForm.get('variableName')?.hasError('required')">Required</mat-error>
                  <mat-error *ngIf="specsForm.get('variableName')?.hasError('pattern')">Must be valid Python identifier</mat-error>
                </mat-form-field>

                @if (currentType === 'machine') {
                  <mat-form-field appearance="outline" class="full-width">
                    <mat-label>Backend</mat-label>
                    <mat-select formControlName="backend">
                      <mat-option value="simulated">Simulated (Default)</mat-option>
                      <!-- Add other backends if available/relevant -->
                    </mat-select>
                  </mat-form-field>
                }

                @if (currentType === 'resource') {
                  <mat-form-field appearance="outline" class="full-width">
                    <mat-label>Count</mat-label>
                    <input matInput type="number" formControlName="count" min="1">
                  </mat-form-field>
                }

                <div class="step-actions">
                  <button mat-button matStepperPrevious>Back</button>
                  <button mat-raised-button color="primary" (click)="addToList()">Add to List</button>
                </div>
              </form>
            </mat-step>
          </mat-stepper>
        </div>

        <!-- Right Side: Added Items List -->
        <div class="added-items-sidebar">
          <h3>Items to Add</h3>
          <mat-list>
            @for (item of addedItems(); track $index) {
              <mat-list-item>
                <mat-icon matListItemIcon>{{ item.type === 'machine' ? 'precision_manufacturing' : 'category' }}</mat-icon>
                <h4 matListItemTitle>{{ item.variableName }}</h4>
                <p matListItemLine>{{ item.asset.name }}</p>
                <button mat-icon-button matListItemMeta (click)="removeItem($index)">
                  <mat-icon>delete</mat-icon>
                </button>
              </mat-list-item>
            }
            @if (addedItems().length === 0) {
              <div class="empty-list">No items added yet.</div>
            }
          </mat-list>
          
          <div class="sidebar-actions">
            <button mat-button (click)="close()">Cancel</button>
            <button mat-raised-button color="primary" [disabled]="addedItems().length === 0" (click)="confirm()">
              Insert All ({{ addedItems().length }})
            </button>
          </div>
        </div>
      </div>
    </mat-dialog-content>
  `,
  styles: [`
    .dialog-layout {
      display: flex;
      height: 600px;
      gap: 24px;
    }
    
    .stepper-container {
      flex: 1;
      overflow-y: auto;
    }

    .added-items-sidebar {
      width: 250px;
      border-left: 1px solid var(--mat-sys-outline-variant);
      padding-left: 24px;
      display: flex;
      flex-direction: column;
    }

    .step-content {
      padding: 16px 0;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .type-radio-group {
      display: flex;
      gap: 16px;
    }

    .type-card {
      flex: 1;
      padding: 16px;
      text-align: center;
      cursor: pointer;
      border: 2px solid transparent;
      transition: all 0.2s;
      
      &.selected {
        border-color: var(--mat-sys-primary);
        background-color: var(--mat-sys-surface-variant);
      }

      &:hover {
        background-color: var(--mat-sys-surface-container-high);
      }
    }

    .hidden-radio {
      display: none;
    }

    .large-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
      margin-bottom: 8px;
    }

    .step-actions {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      margin-top: 16px;
    }

    .full-width {
      width: 100%;
    }

    .empty-state, .empty-list {
      color: var(--mat-sys-on-surface-variant);
      font-style: italic;
      padding: 16px;
      text-align: center;
    }

    .sidebar-actions {
      margin-top: auto;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    mat-dialog-content {
       overflow: hidden; /* Let layout handle scroll */
       max-height: 80vh;
    }
  `]
})
export class InventoryDialogComponent {
  @ViewChild('stepper') stepper!: MatStepper;

  private fb = inject(FormBuilder);
  private assetService = inject(AssetService);
  private dialogRef = inject(MatDialogRef<InventoryDialogComponent>);

  addedItems = signal<InventoryItem[]>([]);

  // Data sources
  machines = toSignal(this.assetService.getMachines(), { initialValue: [] as Machine[] });
  resources = toSignal(this.assetService.getResources(), { initialValue: [] as Resource[] });

  // Forms
  typeForm = this.fb.group({
    type: ['', Validators.required]
  });

  categoryForm = this.fb.group({
    category: ['', Validators.required]
  });

  searchControl = this.fb.control('');

  selectionForm = this.fb.group({
    asset: [null as Machine | Resource | null, Validators.required]
  });

  specsForm = this.fb.group({
    variableName: ['', [Validators.required, Validators.pattern(/^[a-zA-Z_][a-zA-Z0-9_]*$/)]],
    count: [1],
    backend: ['simulated']
  });

  // Computed
  currentType = '';
  currentCategory = '';

  constructor() {
    // Reset forms when type changes
    this.typeForm.get('type')?.valueChanges.subscribe(val => {
      if (val) {
        this.currentType = val;
        this.categoryForm.reset();
        this.selectionForm.reset();
        this.specsForm.reset({ count: 1, backend: 'simulated' });
      }
    });

    // Reset selection when category changes
    this.categoryForm.get('category')?.valueChanges.subscribe(val => {
      if (val) {
        this.currentCategory = val;
        this.selectionForm.reset();
      }
    });

    // Auto-generate variable name when asset selected
    this.selectionForm.get('asset')?.valueChanges.subscribe((val: any) => {
      if (val) {
        const safeName = val.name.toLowerCase().replace(/[^a-z0-9_]/g, '_');
        // Make unique-ish?
        this.specsForm.patchValue({ variableName: safeName });
        // Also set default backend/count info if needed
      }
    });
  }

  availableCategories = computed(() => {
    const type = this.typeForm.get('type')?.value;
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
    const type = this.typeForm.get('type')?.value;
    const category = this.categoryForm.get('category')?.value;
    const search = this.searchControl.value?.toLowerCase() || '';

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

  getCategoryIcon(cat: string): string {
    const type = this.typeForm.get('type')?.value;
    if (type === 'machine') return getMachineCategoryIcon(cat);
    return getResourceCategoryIcon(cat);
  }

  getResourceCategory(r: Resource): string {
    return r.plr_definition?.plr_category || r.asset_type || 'Other';
  }

  selectCategory(cat: string) {
    this.categoryForm.get('category')?.setValue(cat);
  }

  onAssetSelect(event: MatSelectionListChange) {
    const selected = event.options[0].value;
    this.selectionForm.get('asset')?.setValue(selected);
  }

  addToList() {
    if (this.specsForm.valid && this.selectionForm.valid) {
      const item: InventoryItem = {
        type: this.currentType as 'machine' | 'resource',
        asset: this.selectionForm.value.asset!,
        category: this.currentCategory,
        variableName: this.specsForm.value.variableName!,
        count: this.specsForm.value.count || 1,
        backend: this.specsForm.value.backend || undefined
      };

      this.addedItems.update(items => [...items, item]);

      // Reset for next item (keep type/category?)
      // Assuming user might want to add multiple of same type/cat
      this.stepper.reset();
      // Actually maybe better to just reset selection and specs?
      // Resetting entire stepper sends back to start. 
      // If we want to allow quick add of similar items, maybe stay on this step?
      // The prompt says "allows adding multiple items before closing".
      // Let's reset to start to be safe/clean.
    }
  }

  removeItem(index: number) {
    this.addedItems.update(items => items.filter((_, i) => i !== index));
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
}
