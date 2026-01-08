import { Component, inject, OnInit, ChangeDetectorRef, signal, computed } from '@angular/core';
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
import { MatExpansionModule } from '@angular/material/expansion';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { AssetService, ResourceFacets, FacetItem } from '../services/asset.service';
import { ResourceStatus, ResourceDefinition, ActiveFilters } from '../models/asset.models';
import { Observable, map, startWith, of, combineLatest, BehaviorSubject, forkJoin, switchMap, debounceTime, finalize, tap, catchError, shareReplay } from 'rxjs';
import { getResourceCategoryIcon } from '@shared/constants/asset-icons';
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
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatAutocompleteModule,
    MatChipsModule,
    MatIconModule,
    MatTooltipModule,
    MatExpansionModule,
    MatSlideToggleModule,
    ResourceChipsComponent
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
      <!-- STEP 1: BROWSE (Accordion) -->
      @if (!selectedDefinition) {
        <div class="browse-container">
          <!-- Search Bar -->
          <mat-form-field appearance="outline" class="w-full search-field praxis-search-field">
            <mat-icon matPrefix>search</mat-icon>
            <input matInput [formControl]="searchControl" placeholder="Search resources...">
            @if (searchControl.value) {
              <button matSuffix mat-icon-button (click)="searchControl.setValue('')">
                <mat-icon>close</mat-icon>
              </button>
            }
          </mat-form-field>
          <!-- Loading State -->
          @if (isLoading()) {
            <div class="loading-state">
              @for (i of [1,2,3,4]; track i) {
                <div class="skeleton-row"></div>
              }
            </div>
          }
          <!-- Accordion List -->
          <mat-accordion displayMode="flat" multi="false" class="resource-accordion">
            @for (group of groupedDefinitions(); track group) {
              @if (group.totalCount > 0) {
                <mat-expansion-panel>
                  <mat-expansion-panel-header>
                    <mat-panel-title class="flex items-center gap-3">
                      <mat-icon [color]="'primary'">{{ group.icon }}</mat-icon>
                      <span class="font-medium text-lg">{{ group.group }}</span>
                    </mat-panel-title>
                    <mat-panel-description>
                      {{ group.totalCount }} items
                    </mat-panel-description>
                  </mat-expansion-panel-header>
                  <!-- Group Content -->
                  <div class="group-content">
                    <!-- If Carriers, show sub-accordions or headers -->
                    @if (group.group === 'Carriers') {
                      @for (subEntry of group.subGroups | keyvalue; track subEntry) {
                        <div class="sub-category-section">
                          <h4 class="sub-cat-header">{{ formatSubCategory(subEntry.key) }}</h4>
                          <div class="resource-list">
                            @for (def of subEntry.value; track def) {
                              <button
                                class="resource-item"
                                (click)="selectDefinition(def)">
                                <app-resource-chips
                                  [definition]="def"
                                  [showPlrName]="showPlrName()"
                                  [showVendor]="true"
                                  [showDisplayName]="true">
                                </app-resource-chips>
                              </button>
                            }
                          </div>
                        </div>
                      }
                    } @else {
                      <div class="resource-list">
                        <!-- Flatten all subgroups for non-carrier categories -->
                        @for (subEntry of group.subGroups | keyvalue; track subEntry) {
                          @for (def of subEntry.value; track def) {
                            <button
                              class="resource-item"
                              (click)="selectDefinition(def)">
                              <app-resource-chips
                                [definition]="def"
                                [showPlrName]="showPlrName()"
                                [showVendor]="true"
                                [showDisplayName]="true">
                              </app-resource-chips>
                            </button>
                          }
                        }
                      </div>
                    }
                    <!-- Flat list for others (Plates, etc) -->
                  </div>
                </mat-expansion-panel>
              }
            }
            @if (groupedDefinitions().length === 0 && !isLoading()) {
              <div class="no-results">
                No matching resources found.
              </div>
            }
          </mat-accordion>
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
    
    .browse-container { height: 100%; display: flex; flex-direction: column; }
    .search-field { flex: 0 0 auto; }
    
    .resource-accordion {
      flex: 1;
      overflow-y: auto;
      
      mat-expansion-panel {
        margin-bottom: 8px;
        border: 1px solid var(--mat-sys-outline-variant);
        border-radius: 8px !important;
        
        &.mat-expanded {
          border-color: var(--mat-sys-primary);
        }
      }
    }
    
    .group-content { padding: 16px 0; }
    
    .sub-category-section {
      margin-bottom: 16px;
      &:last-child { margin-bottom: 0; }
    }
    
    .sub-cat-header {
      font-size: 0.85rem;
      font-weight: 500;
      color: var(--mat-sys-on-surface-variant);
      margin: 0 0 8px 0;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding-left: 8px;
      border-left: 3px solid var(--mat-sys-secondary);
    }
    
    .resource-list {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    
    .resource-item {
      display: flex;
      align-items: center;
      width: 100%;
      padding: 8px 12px;
      text-align: left;
      background: transparent;
      border: 1px solid transparent;
      border-radius: 6px;
      cursor: pointer;
      transition: background 0.2s;
      
      &:hover {
        background: var(--mat-sys-surface-container-high);
      }
    }
    
    .selected-summary {
      display: flex;
      gap: 16px;
      align-items: center;
      padding: 16px;
      background: var(--mat-sys-surface-container);
      border-radius: 8px;
      margin-bottom: 24px;
      border: 1px solid var(--mat-sys-outline-variant);
    }
    
    .summary-icon mat-icon { font-size: 32px; width: 32px; height: 32px; }
    
    .form-row { display: flex; gap: 12px; .half-width { flex: 1; } }
    
    .loading-state { padding: 20px; }
    .skeleton-row { 
      height: 48px; 
      background: var(--mat-sys-surface-container-highest); 
      margin-bottom: 8px; 
      border-radius: 8px; 
      animation: pulse 1.5s infinite;
      opacity: 0.5;
    }
    
    @keyframes pulse { 0% { opacity: 0.3; } 50% { opacity: 0.6; } 100% { opacity: 0.3; } }
    
    .no-results {
      text-align: center;
      padding: 32px;
      color: var(--mat-sys-on-surface-variant);
      font-style: italic;
    }
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

  // Data
  // Loaded once, then filtered locally
  private allDefinitions: ResourceDefinition[] = [];

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
      this.filterDefinitions(term || '');
    });
  }

  private loadDefinitions() {
    this.assetService.getResourceDefinitions().subscribe({
      next: (defs) => {
        // Initial filter of hidden items
        this.allDefinitions = defs.filter(d => !shouldHideCategory(d.plr_category));
        this.isLoading.set(false);
        this.filterDefinitions('');
      },
      error: (err) => {
        console.error('Error loading resources', err);
        this.isLoading.set(false);
      }
    });
  }

  private filterDefinitions(searchTerm: string) {
    const term = searchTerm.toLowerCase();

    // Filter
    const filtered = this.allDefinitions.filter(d => {
      if (!term) return true;
      const text = [d.name, d.fqn, d.vendor, d.plr_category].join(' ').toLowerCase();
      return text.includes(term);
    });

    // Group
    const groups = new Map<ResourceUiGroup, GroupedDefinitions>();

    // Initialize all groups to ensure ordering
    UI_GROUP_ORDER.forEach(g => {
      groups.set(g, {
        group: g,
        icon: this.getCategoryIcon(g),
        totalCount: 0,
        subGroups: new Map()
      });
    });

    filtered.forEach(def => {
      const groupName = getUiGroup(def.plr_category);
      const groupData = groups.get(groupName)!;

      // Determine sub-category (mostly for Carriers)
      const subCat = getSubCategory(def.plr_category);

      // Update data
      groupData.totalCount++;
      if (!groupData.subGroups.has(subCat)) {
        groupData.subGroups.set(subCat, []);
      }
      groupData.subGroups.get(subCat)!.push(def);
    });

    // Convert to array and filter empty groups
    const result = Array.from(groups.values())
      .filter(g => g.totalCount > 0);

    this.groupedDefinitions.set(result);
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
}
