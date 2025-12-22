import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, FormControl } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatChipsModule } from '@angular/material/chips';
import { AssetService } from '../services/asset.service';
import { ResourceStatus, ResourceDefinition } from '../models/asset.models';
import { Observable, map, startWith, of, combineLatest, BehaviorSubject } from 'rxjs';

// Resource categories for filtering
type ResourceCategory = 'all' | 'plate' | 'tip_rack' | 'trough' | 'tube' | 'carrier' | 'other';

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
    MatChipsModule
  ],
  template: `
    <h2 mat-dialog-title>Add New Resource</h2>
    <mat-dialog-content>
      <form [formGroup]="form" class="flex flex-col gap-4 py-4">
        <mat-form-field appearance="outline">
          <mat-label>Name</mat-label>
          <input matInput formControlName="name" placeholder="e.g. Tip Rack 1">
          <mat-error *ngIf="form.get('name')?.hasError('required')">Name is required</mat-error>
        </mat-form-field>

        <!-- Category Filter Chips -->
        <div class="category-chips">
          <span class="chip-label">Filter by type:</span>
          <mat-chip-listbox [value]="selectedCategory" (change)="onCategoryChange($event.value)">
            <mat-chip-option value="all">All</mat-chip-option>
            <mat-chip-option value="plate">Plates</mat-chip-option>
            <mat-chip-option value="tip_rack">Tip Racks</mat-chip-option>
            <mat-chip-option value="trough">Troughs</mat-chip-option>
            <mat-chip-option value="tube">Tubes</mat-chip-option>
            <mat-chip-option value="carrier">Carriers</mat-chip-option>
          </mat-chip-listbox>
        </div>

        <mat-form-field appearance="outline">
          <mat-label>Resource Type (PLR Definition)</mat-label>
          <input
            matInput
            [formControl]="definitionSearchControl"
            [matAutocomplete]="defAuto"
            placeholder="Search 374+ resource types...">
          <mat-autocomplete
            #defAuto="matAutocomplete"
            [displayWith]="displayDefinition.bind(this)"
            (optionSelected)="onDefinitionSelected($event.option.value)">
            <mat-option *ngFor="let def of filteredDefinitions$ | async" [value]="def">
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
          <mat-hint>Type to search by name, vendor, or specifications</mat-hint>
        </mat-form-field>

        <div *ngIf="selectedDefinition" class="bg-surface-container rounded-lg p-3 text-sm">
          <div class="font-medium text-primary">{{ getDisplayName(selectedDefinition) }}</div>
          <div class="text-on-surface-variant text-xs" *ngIf="selectedDefinition.fqn">{{ selectedDefinition.fqn }}</div>
          <div class="text-on-surface-variant mt-1" *ngIf="selectedDefinition.description">{{ selectedDefinition.description }}</div>
          <div class="flex gap-4 mt-2 text-xs text-on-surface-variant flex-wrap">
            <span *ngIf="selectedDefinition.vendor" class="def-badge vendor">{{ selectedDefinition.vendor | titlecase }}</span>
            <span *ngIf="selectedDefinition.num_items" class="def-badge">{{ selectedDefinition.num_items }} wells</span>
            <span *ngIf="selectedDefinition.plate_type" class="def-badge">{{ selectedDefinition.plate_type }}</span>
            <span *ngIf="selectedDefinition.well_volume_ul" class="def-badge">{{ selectedDefinition.well_volume_ul }}µL</span>
            <span *ngIf="selectedDefinition.tip_volume_ul" class="def-badge tip">{{ selectedDefinition.tip_volume_ul }}µL tip</span>
            <span *ngIf="selectedDefinition.is_consumable" class="def-badge consumable">Consumable</span>
          </div>
        </div>

        <mat-form-field appearance="outline">
            <mat-label>Status</mat-label>
            <mat-select formControlName="status">
                <mat-option [value]="ResourceStatus.AVAILABLE">Available</mat-option>
                <mat-option [value]="ResourceStatus.IN_USE">In Use</mat-option>
                <mat-option [value]="ResourceStatus.DEPLETED">Depleted</mat-option>
            </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Parent ID (Optional)</mat-label>
          <input matInput formControlName="parent_accession_id" placeholder="UUID of parent container">
        </mat-form-field>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button mat-flat-button color="primary" [disabled]="form.invalid" (click)="save()">Save</button>
    </mat-dialog-actions>
  `,
  styles: [`
    .bg-surface-container {
      background: var(--mat-sys-surface-container, rgba(255,255,255,0.05));
    }
    .text-primary {
      color: var(--mat-sys-primary, #bb86fc);
    }
    .text-on-surface-variant {
      color: var(--mat-sys-on-surface-variant, #999);
    }
    .category-chips {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .chip-label {
      font-size: 12px;
      color: var(--mat-sys-on-surface-variant, #888);
    }
    .def-option {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
    }
    .def-name {
      font-weight: 500;
    }
    .def-meta {
      display: flex;
      gap: 6px;
      font-size: 11px;
    }
    .def-tag {
      background: var(--mat-sys-surface-variant, rgba(255,255,255,0.1));
      padding: 2px 6px;
      border-radius: 4px;
      color: var(--mat-sys-on-surface-variant, #aaa);
    }
    .def-tag.tip {
      background: var(--mat-sys-tertiary-container, rgba(255,200,100,0.2));
      color: var(--mat-sys-on-tertiary-container, #c0a060);
    }
    .def-badge {
      background: var(--mat-sys-surface-variant, rgba(255,255,255,0.1));
      padding: 2px 8px;
      border-radius: 4px;
    }
    .def-badge.vendor {
      background: var(--mat-sys-primary-container, rgba(100,100,255,0.2));
      color: var(--mat-sys-on-primary-container, #9999ff);
    }
    .def-badge.consumable {
      background: var(--mat-sys-secondary-container, rgba(100,255,100,0.2));
      color: var(--mat-sys-on-secondary-container, #99ff99);
    }
    .def-badge.tip {
      background: var(--mat-sys-tertiary-container, rgba(255,200,100,0.2));
      color: var(--mat-sys-on-tertiary-container, #c0a060);
    }
  `]
})
export class ResourceDialogComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<ResourceDialogComponent>);
  private assetService = inject(AssetService);

  ResourceStatus = ResourceStatus;

  definitions: ResourceDefinition[] = [];
  definitionSearchControl = new FormControl<string | ResourceDefinition>('');
  filteredDefinitions$: Observable<ResourceDefinition[]> = of([]);
  selectedDefinition: ResourceDefinition | null = null;
  selectedCategory: ResourceCategory = 'all';
  private categorySubject = new BehaviorSubject<ResourceCategory>('all');

  form = this.fb.group({
    name: ['', Validators.required],
    status: [ResourceStatus.AVAILABLE],
    resource_definition_accession_id: [null as string | null],
    parent_accession_id: [null as string | null]
  });

  ngOnInit() {
    // Load resource definitions
    this.assetService.getResourceDefinitions().subscribe(defs => {
      this.definitions = defs;
      // Setup filtering after definitions are loaded
      this.filteredDefinitions$ = combineLatest([
        this.definitionSearchControl.valueChanges.pipe(startWith('')),
        this.categorySubject
      ]).pipe(
        map(([value, category]) => this.filterDefinitions(value, category))
      );
    });
  }

  onCategoryChange(category: ResourceCategory) {
    this.selectedCategory = category;
    this.categorySubject.next(category);
  }

  private filterDefinitions(value: string | ResourceDefinition | null, category: ResourceCategory): ResourceDefinition[] {
    // First filter by category
    let filtered = category === 'all'
      ? this.definitions
      : this.definitions.filter(def => def.plr_category === category);

    // Then filter by search text
    if (value) {
      const filterValue = typeof value === 'string'
        ? value.toLowerCase()
        : value.name.toLowerCase();

      // Support natural language search: "corning 96 flat"
      const searchTerms = filterValue.split(/\s+/).filter(t => t.length > 0);

      filtered = filtered.filter(def => {
        // Check if ALL search terms match some field
        return searchTerms.every(term => {
          const searchableText = [
            def.name,
            def.fqn,
            def.manufacturer,
            def.vendor,
            def.resource_type,
            def.plate_type,
            def.num_items?.toString(),
            def.well_volume_ul?.toString(),
            def.tip_volume_ul?.toString()
          ].filter(Boolean).join(' ').toLowerCase();

          return searchableText.includes(term);
        });
      });
    }

    return filtered.slice(0, 50); // Limit results for performance
  }

  displayDefinition(def: ResourceDefinition | null): string {
    if (!def) return '';
    return this.getDisplayName(def);
  }

  getDisplayName(def: ResourceDefinition): string {
    // Format: [Vendor] FactoryFunctionName
    const functionName = def.fqn
      ? def.fqn.split('.').pop() || def.name
      : def.name;

    if (def.vendor) {
      return `[${def.vendor.charAt(0).toUpperCase() + def.vendor.slice(1)}] ${functionName}`;
    }
    return functionName;
  }

  getModulePath(fqn: string): string {
    // Show module path without the function name
    const parts = fqn.split('.');
    if (parts.length > 2) {
      return parts.slice(0, -1).join('.');
    }
    return fqn;
  }

  getShortFqn(fqn: string): string {
    // Show only the last two parts of the FQN for brevity
    const parts = fqn.split('.');
    return parts.length > 2 ? parts.slice(-2).join('.') : fqn;
  }

  onDefinitionSelected(def: ResourceDefinition) {
    this.selectedDefinition = def;
    this.form.patchValue({
      resource_definition_accession_id: def.accession_id
    });
  }

  save() {
    if (this.form.valid) {
      this.dialogRef.close(this.form.value);
    }
  }
}
