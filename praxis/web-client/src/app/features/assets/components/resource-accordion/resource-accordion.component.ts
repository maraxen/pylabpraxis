import { Component, ChangeDetectionStrategy, inject, signal, computed, OnInit } from '@angular/core';

import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatBadgeModule } from '@angular/material/badge';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule, ReactiveFormsModule, FormControl } from '@angular/forms';
import { AssetService } from '../../services/asset.service';
import { Resource, ResourceStatus, ResourceDefinition, Machine } from '../../models/asset.models';
import { ResourceInstancesDialogComponent } from './resource-instances-dialog.component';
import { AssetStatusChipComponent, AssetStatusType } from '../asset-status-chip/asset-status-chip.component';
import { debounceTime, distinctUntilChanged, startWith } from 'rxjs/operators';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { getCategoryTooltip, getPropertyTooltip } from '@shared/constants/resource-tooltips';
import { getResourceCategoryIcon } from '@shared/constants/asset-icons';
import { inferCategory } from '../../utils/category-inference';
import { ResourceFiltersComponent, ResourceFilterState } from '../resource-filters/resource-filters.component';
import { getUiGroup, UI_GROUP_ORDER, shouldHideCategory, ResourceUiGroup } from '../../utils/resource-category-groups';
import { ResourceChipsComponent } from '../resource-chips/resource-chips.component';
import { getDisplayLabel } from '../../utils/resource-name-parser';
import { AppStore } from '../../../../core/store/app.store';

export interface ResourceGroup {
  category: string;
  definitions: ResourceDefinitionGroup[];
  totalCount: number;
  consumableStatus: 'all' | 'none' | 'mixed'; // 'mixed' = dashed outline
}

export interface ResourceDefinitionGroup {
  definition: ResourceDefinition;
  instances: Resource[];
  count: number | null; // null = infinite (only for consumables)
  isInfinite: boolean;
  isConsumable: boolean;
  isReusable: boolean;
  activeCount: number;
  discardedCount: number;
  primaryStatus: AssetStatusType | null; // Most relevant status for chip display
}

@Component({
  selector: 'app-resource-accordion',
  standalone: true,
  imports: [
    MatExpansionModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatBadgeModule,
    MatSlideToggleModule,
    MatDialogModule,
    MatChipsModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule,
    ReactiveFormsModule,
    AssetStatusChipComponent,
    ResourceFiltersComponent,
    ResourceChipsComponent
  ],
  template: `
    <div class="resource-accordion-container">
      <!-- Resource Filters -->
      <app-resource-filters
        [categories]="categories()"
        [machines]="machines()"
        (filtersChange)="onFiltersChange($event)">
      </app-resource-filters>

      <mat-accordion multi="true">
        @for (group of filteredGroups(); track group.category) {
          <mat-expansion-panel class="category-panel">
            <mat-expansion-panel-header>
              <mat-panel-title>
                <mat-icon class="category-icon" [matTooltip]="getCategoryTooltip(group.category)">{{ getCategoryIcon(group.category) }}</mat-icon>
                <span [matTooltip]="getCategoryTooltip(group.category)">{{ group.category }}</span>
              </mat-panel-title>
              <mat-panel-description>
                <span class="count-badge">{{ group.totalCount }} types</span>
                @if (group.consumableStatus !== 'none') {
                  <mat-chip
                    class="consumable-chip"
                    [class.mixed]="group.consumableStatus === 'mixed'"
                    [matTooltip]="group.consumableStatus === 'mixed'
                      ? 'Some items in this category are consumable (used up during protocols)'
                      : getPropertyTooltip('consumable')"
                  >
                    Consumable
                  </mat-chip>
                }
              </mat-panel-description>
            </mat-expansion-panel-header>

            <div class="definition-list">
              @for (defGroup of group.definitions; track defGroup.definition.accession_id) {
                <div class="definition-item" (click)="openInstancesDialog(defGroup)">
                  <div class="def-info">
                    <span class="def-name">{{ getDisplayLabel(defGroup.definition) }}</span>
                    <!-- Prioritized chip ordering: Status (if itemized) → Count → Type flags → Vendor -->
                    <div class="def-chips">
                      @if (defGroup.isConsumable && defGroup.primaryStatus) {
                        <app-asset-status-chip [status]="defGroup.primaryStatus" [showLabel]="true" />
                      }
                      
                      <app-resource-chips 
                        [definition]="defGroup.definition" 
                        [showVendor]="true"
                        [showDisplayName]="false">
                      </app-resource-chips>

                      @if (defGroup.isConsumable) {
                        <mat-chip class="info-chip consumable" [matTooltip]="getPropertyTooltip('consumable')">Consumable</mat-chip>
                      }
                    </div>
                  </div>
                  <div class="def-counts">
                    @if (defGroup.isConsumable && defGroup.isInfinite) {
                      <span class="count infinite" [matTooltip]="getPropertyTooltip('infinite')">∞</span>
                    } @else {
                      <span
                        class="count"
                        [class.low]="defGroup.activeCount < 3"
                        [matTooltip]="defGroup.activeCount < 3 ? getPropertyTooltip('low-stock') : 'Available quantity'"
                      >
                        {{ defGroup.isConsumable ? defGroup.activeCount : 1 }}
                      </span>
                    }
                    @if (activeFilters().show_discarded && defGroup.discardedCount > 0) {
                      <span class="count discarded" [matTooltip]="getPropertyTooltip('depleted')">
                        ({{ defGroup.discardedCount }} discarded)
                      </span>
                    }
                    @if (defGroup.isReusable) {
                      <mat-icon class="reusable-icon" [matTooltip]="getPropertyTooltip('reusable')">refresh</mat-icon>
                    }
                  </div>
                  <mat-icon class="chevron">chevron_right</mat-icon>
                </div>
              }
            </div>
          </mat-expansion-panel>
        }
      </mat-accordion>

      @if (filteredGroups().length === 0) {
        <div class="empty-state">
          <mat-icon>inventory_2</mat-icon>
          <p>No resources matching current filters</p>
        </div>
      }
    </div>
  `,
  styles: [`
    .resource-accordion-container {
      padding: 0 16px 16px 16px;
    }

    .accordion-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }

    .accordion-header h3 {
      margin: 0;
      font-size: 1.1rem;
      font-weight: 500;
    }

    .discard-toggle {
      font-size: 0.85rem;
    }

    .filter-field {
      width: 100%;
      margin-bottom: 16px;
    }

    .category-panel {
      margin-bottom: 8px;
    }

    .category-icon {
      margin-right: 8px;
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .count-badge {
      background: var(--sys-primary-container);
      color: var(--sys-on-primary-container);
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.75rem;
      margin-right: 8px;
    }

    .consumable-chip {
      font-size: 0.65rem;
      min-height: 20px;
      padding: 0 6px;
    }

    /* Dashed outline for mixed consumable categories */
    .consumable-chip.mixed {
      border: 2px dashed var(--sys-outline);
      background: transparent;
    }

    .definition-list {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .definition-item {
      display: flex;
      align-items: center;
      padding: 12px 16px;
      background: linear-gradient(to right, var(--sys-surface-container), var(--sys-surface-container-low));
      border: 1px solid var(--sys-outline-variant);
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .definition-item:hover {
      background: linear-gradient(to right, var(--sys-surface-container-high), var(--sys-surface-container));
      border-color: var(--sys-primary);
      transform: translateX(4px);
    }

    .def-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .def-name {
      font-weight: 500;
      font-size: 0.9rem;
    }

    .def-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin-top: 4px;
    }

    .info-chip {
      --mdc-chip-container-height: 20px;
      font-size: 0.65rem;
      font-weight: 500;
    }

    .info-chip.consumable {
      --mdc-chip-elevated-container-color: var(--sys-tertiary-container);
      --mdc-chip-label-text-color: var(--sys-on-tertiary-container);
    }

    .info-chip.vendor {
      --mdc-chip-elevated-container-color: var(--sys-surface-container-high);
      --mdc-chip-label-text-color: var(--sys-on-surface-variant);
    }

    .def-meta {
      font-size: 0.75rem;
      color: var(--sys-on-surface-variant);
    }

    .def-counts {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-right: 8px;
    }

    .count {
      font-weight: 600;
      font-size: 1rem;
    }

    .count.infinite {
      font-size: 1.5rem;
      color: var(--sys-primary);
    }

    .count.low {
      color: var(--sys-error);
    }

    .count.discarded {
      font-size: 0.75rem;
      color: var(--sys-on-surface-variant);
    }

    .reusable-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
      color: var(--sys-tertiary);
    }

    .chevron {
      color: var(--sys-on-surface-variant);
    }

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 48px;
      color: var(--sys-on-surface-variant);
    }

    .empty-state mat-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
      margin-bottom: 16px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ResourceAccordionComponent implements OnInit {
  private assetService = inject(AssetService);
  private dialog = inject(MatDialog);
  private store = inject(AppStore);

  resources = signal<Resource[]>([]);
  definitions = signal<ResourceDefinition[]>([]);
  machines = signal<Machine[]>([]);

  // Filter State
  activeFilters = signal<ResourceFilterState>({
    search: '',
    status: [],
    categories: [],
    brands: [],
    machine_id: null,
    show_discarded: false,
    sort_by: 'name',
    sort_order: 'asc'
  });

  constructor() {
    // Removed old filterControl logic
  }

  // Computed Categories for Filter
  categories = computed(() => {
    return this.resourceGroups().map(g => g.category).sort();
  });

  resourceGroups = computed(() => {
    const defs = this.definitions();
    const res = this.resources();

    // Group definitions by category
    const categoryMap = new Map<ResourceUiGroup, ResourceDefinitionGroup[]>();

    defs.forEach(def => {
      if (shouldHideCategory(def.plr_category)) return;
      const category = getUiGroup(def.plr_category);
      const isConsumable = (def as any).is_consumable ?? false;
      const instances = res.filter(r => r.resource_definition_accession_id === def.accession_id);
      const activeInstances = instances.filter(r =>
        r.status !== ResourceStatus.DEPLETED && r.status !== ResourceStatus.EXPIRED
      );
      const discardedInstances = instances.filter(r =>
        r.status === ResourceStatus.DEPLETED || r.status === ResourceStatus.EXPIRED
      );

      // Compute primary status for chip display (priority: reserved > in_use > error statuses > available)
      const statusPriority: Record<string, number> = {
        'reserved': 1,
        'in_use': 2,
        'depleted': 3,
        'expired': 4,
        'available': 5,
        'unknown': 6
      };
      let primaryStatus: AssetStatusType | null = null;
      if (isConsumable && activeInstances.length > 0) {
        // Find the highest priority status among active instances
        const sortedByPriority = activeInstances.sort((a, b) =>
          (statusPriority[a.status] || 99) - (statusPriority[b.status] || 99)
        );
        primaryStatus = sortedByPriority[0]?.status as AssetStatusType || null;
      }

      const defGroup: ResourceDefinitionGroup = {
        definition: def,
        instances: instances,
        count: (def as any).default_count ?? null,
        // Only consumables can be infinite; non-consumables always show "1"
        // Infinite if enabled in settings AND item is consumable
        isInfinite: isConsumable && this.store.infiniteConsumables(),
        isConsumable: isConsumable,
        isReusable: (def as any).is_reusable ?? false,
        activeCount: activeInstances.length,
        discardedCount: discardedInstances.length,
        primaryStatus: primaryStatus
      };

      if (!categoryMap.has(category)) {
        categoryMap.set(category, []);
      }
      categoryMap.get(category)!.push(defGroup);
    });

    // Convert to array
    const groups: ResourceGroup[] = [];
    categoryMap.forEach((defGroups, category) => {
      const consumableCount = defGroups.filter(d => d.isConsumable).length;
      let consumableStatus: 'all' | 'none' | 'mixed';
      if (consumableCount === 0) {
        consumableStatus = 'none';
      } else if (consumableCount === defGroups.length) {
        consumableStatus = 'all';
      } else {
        consumableStatus = 'mixed';
      }

      groups.push({
        category,
        definitions: defGroups,
        totalCount: defGroups.length,
        consumableStatus
      });
    });

    // Sort by UI_GROUP_ORDER
    return groups.sort((a, b) => {
      const idxA = UI_GROUP_ORDER.indexOf(a.category as ResourceUiGroup);
      const idxB = UI_GROUP_ORDER.indexOf(b.category as ResourceUiGroup);
      return idxA - idxB;
    });
  });

  // Filtered groups based on all filters
  filteredGroups = computed(() => {
    const filters = this.activeFilters();
    let groups = this.resourceGroups();

    // 1. Filter by Category
    if (filters.categories.length > 0) {
      groups = groups.filter(g => filters.categories.includes(g.category));
    }

    return groups.map(group => {
      // Filter definitions within the group and update counts based on filters
      const filteredDefs = group.definitions.map(defGroup => {
        // Apply Filters to Instances first
        let matchingInstances = defGroup.instances;

        // Default: Hide discarded unless requested
        // (Note: If specific status filter is applied, we might want to respect that, but typically discarded requires opt-in)
        if (!filters.show_discarded) {
          matchingInstances = matchingInstances.filter(inst =>
            inst.status !== ResourceStatus.DEPLETED && inst.status !== ResourceStatus.EXPIRED
          );
        }

        // Status Filter
        if (filters.status.length > 0) {
          matchingInstances = matchingInstances.filter(inst =>
            filters.status.includes(inst.status)
          );
        }

        // Location Filter (Machine)
        if (filters.machine_id) {
          const machineId = filters.machine_id;
          matchingInstances = matchingInstances.filter(inst =>
            inst.location && inst.location.startsWith(machineId)
          );
        }

        // Search Filter (Name or Category) - Applies to Definition
        if (filters.search) {
          const searchLower = filters.search.toLowerCase();
          const matchesName = defGroup.definition.name.toLowerCase().includes(searchLower);
          const matchesCategory = group.category.toLowerCase().includes(searchLower);

          if (!matchesName && !matchesCategory) {
            // Check if any instance matches FQN/Asset ID? 
            // For now, if name matches, we show ALL matching instances (filtered by status).
            // If name doesn't match, we hide definition.
            return null;
          }
        }

        // If status/location filter is active, and no instances match, hide the definition
        // EXCEPTION: If filter is only SEARCH, we usually show the definition (with 0 count if none).
        // But if filtering by physical properties (Location/Status), 0 matches usually means hide.
        const hasActiveFilters = filters.status.length > 0 || filters.machine_id;
        if (hasActiveFilters && matchingInstances.length === 0) {
          return null;
        }

        // Recalculate derived properties for the filtered view
        const activeCount = matchingInstances.length;

        // Compute primary Status for chip
        const statusPriority: Record<string, number> = {
          'reserved': 1, 'in_use': 2, 'depleted': 3, 'expired': 4, 'available': 5, 'unknown': 6
        };

        let primaryStatus: AssetStatusType | null = null;
        if (defGroup.isConsumable && matchingInstances.length > 0) {
          const sorted = [...matchingInstances].sort((a, b) =>
            (statusPriority[a.status] || 99) - (statusPriority[b.status] || 99)
          );
          primaryStatus = sorted[0]?.status as AssetStatusType || null;
        }

        return {
          ...defGroup,
          instances: matchingInstances, // instances passed to dialog will only be the matching ones
          activeCount: activeCount,
          primaryStatus: primaryStatus
        } as ResourceDefinitionGroup;

      }).filter((d): d is ResourceDefinitionGroup => d !== null);

      // Sort Definitions
      filteredDefs.sort((a, b) => {
        let valA: any = '';
        let valB: any = '';

        switch (filters.sort_by) {
          case 'name':
            valA = a.definition.name.toLowerCase();
            valB = b.definition.name.toLowerCase();
            break;
          case 'count':
            valA = a.activeCount;
            valB = b.activeCount;
            break;
          case 'category':
            break;
        }

        if (filters.sort_order === 'asc') {
          return valA > valB ? 1 : -1;
        } else {
          return valA < valB ? 1 : -1;
        }
      });

      return {
        ...group,
        definitions: filteredDefs,
        totalCount: filteredDefs.length
      };

    }).filter(group => group.definitions.length > 0).sort((a, b) => {
      // Sort groups if 'category' sort is selected
      if (filters.sort_by === 'category') {
        if (filters.sort_order === 'asc') {
          return a.category.localeCompare(b.category);
        } else {
          return b.category.localeCompare(a.category);
        }
      }
      return a.category.localeCompare(b.category); // Default category sort
    });
  });

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.assetService.getResources().subscribe(resources => {
      this.resources.set(resources);
    });

    this.assetService.getResourceDefinitions().subscribe(defs => {
      this.definitions.set(defs);
    });
    this.assetService.getMachines().subscribe(machines => {
      this.machines.set(machines);
    });
  }

  onFiltersChange(filters: ResourceFilterState) {
    this.activeFilters.set(filters);
  }

  getCategoryIcon(category: string): string {
    switch (category) {
      case 'Carriers': return 'grid_view';
      case 'Holders': return 'biotech';
      case 'Plates': return 'dataset';
      case 'TipRacks': return 'apps';
      case 'Containers': return 'science';
      case 'Other': return 'category';
      default: return getResourceCategoryIcon(category);
    }
  }

  getDisplayLabel(def: ResourceDefinition): string {
    return getDisplayLabel(def);
  }

  getCategoryTooltip(category: string): string {
    return getCategoryTooltip(category);
  }

  getPropertyTooltip(property: string): string {
    return getPropertyTooltip(property);
  }

  openInstancesDialog(defGroup: ResourceDefinitionGroup) {
    this.dialog.open(ResourceInstancesDialogComponent, {
      width: '600px',
      data: {
        definition: defGroup.definition,
        instances: defGroup.instances,
        showDiscarded: this.activeFilters().show_discarded
      }
    });
  }
}
