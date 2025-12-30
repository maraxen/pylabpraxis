import { Component, ChangeDetectionStrategy, inject, signal, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
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
import { Resource, ResourceStatus, ResourceDefinition } from '../../models/asset.models';
import { ResourceInstancesDialogComponent } from './resource-instances-dialog.component';
import { AssetStatusChipComponent, AssetStatusType } from '../asset-status-chip/asset-status-chip.component';
import { debounceTime, distinctUntilChanged, startWith } from 'rxjs/operators';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { getCategoryTooltip, getPropertyTooltip } from '@shared/constants/resource-tooltips';

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
    CommonModule,
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
    AssetStatusChipComponent
  ],
  template: `
    <div class="resource-accordion-container">
      <div class="accordion-header">
        <h3>Resource Inventory</h3>
        <mat-slide-toggle [(ngModel)]="showDiscarded" class="discard-toggle">
          Show Discarded
        </mat-slide-toggle>
      </div>

      <!-- Search Bar -->
      <mat-form-field appearance="outline" class="filter-field">
        <mat-label>Filter Resources</mat-label>
        <input matInput [formControl]="filterControl">
        <mat-icon matSuffix>search</mat-icon>
      </mat-form-field>

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
                    <span class="def-name">{{ defGroup.definition.name }}</span>
                    <!-- Prioritized chip ordering: Status (if itemized) → Count → Type flags → Vendor -->
                    <div class="def-chips">
                      @if (defGroup.isConsumable && defGroup.primaryStatus) {
                        <app-asset-status-chip [status]="defGroup.primaryStatus" [showLabel]="true" />
                      }
                      @if (defGroup.definition.num_items) {
                        <mat-chip class="info-chip" [matTooltip]="'Number of items/wells'">{{ defGroup.definition.num_items }} items</mat-chip>
                      }
                      @if (defGroup.definition.plate_type) {
                        <mat-chip class="info-chip" [matTooltip]="'Plate type'">{{ defGroup.definition.plate_type }}</mat-chip>
                      }
                      @if (defGroup.isConsumable) {
                        <mat-chip class="info-chip consumable" [matTooltip]="getPropertyTooltip('consumable')">Consumable</mat-chip>
                      }
                      @if (defGroup.definition.vendor) {
                        <mat-chip class="info-chip vendor" [matTooltip]="'Vendor/Manufacturer'">{{ defGroup.definition.vendor }}</mat-chip>
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
                    @if (showDiscarded && defGroup.discardedCount > 0) {
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
          <p>No resources matching "{{ filterControl.value }}"</p>
        </div>
      }
    </div>
  `,
  styles: [`
    .resource-accordion-container {
      padding: 16px;
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
      background: var(--sys-surface-container);
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.2s ease;
    }

    .definition-item:hover {
      background: var(--sys-surface-container-high);
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

  resources = signal<Resource[]>([]);
  definitions = signal<ResourceDefinition[]>([]);
  showDiscarded = false;
  filterControl = new FormControl('', { nonNullable: true });
  filterValue = signal('');

  constructor() {
    this.filterControl.valueChanges.pipe(
      takeUntilDestroyed(),
      debounceTime(200),
      distinctUntilChanged(),
      startWith('')
    ).subscribe(value => {
      this.filterValue.set(value);
    });
  }

  resourceGroups = computed(() => {
    const defs = this.definitions();
    const res = this.resources();

    // Group definitions by category
    const categoryMap = new Map<string, ResourceDefinitionGroup[]>();

    defs.forEach(def => {
      const category = (def as any).plr_category || 'Other';
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
        isInfinite: isConsumable && ((def as any).default_count === null || (def as any).default_count === undefined),
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

    // Sort by category name
    return groups.sort((a, b) => a.category.localeCompare(b.category));
  });

  // Filtered groups based on search
  filteredGroups = computed(() => {
    const filter = this.filterValue().toLowerCase();
    if (!filter) {
      return this.resourceGroups();
    }

    return this.resourceGroups()
      .map(group => ({
        ...group,
        definitions: group.definitions.filter(def =>
          def.definition.name.toLowerCase().includes(filter) ||
          group.category.toLowerCase().includes(filter)
        )
      }))
      .filter(group => group.definitions.length > 0)
      .map(group => ({
        ...group,
        totalCount: group.definitions.length
      }));
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
  }

  getCategoryIcon(category: string): string {
    const icons: Record<string, string> = {
      'Plate': 'grid_view',
      'TipRack': 'view_comfy',
      'Reservoir': 'water_drop',
      'Trough': 'science',
      'Carrier': 'view_module',
      'Other': 'category'
    };
    return icons[category] || 'category';
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
        showDiscarded: this.showDiscarded
      }
    });
  }
}
