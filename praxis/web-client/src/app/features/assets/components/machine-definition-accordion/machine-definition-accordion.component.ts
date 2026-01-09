import { Component, ChangeDetectionStrategy, inject, signal, computed, OnInit, Input } from '@angular/core';

import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule, ReactiveFormsModule, FormControl } from '@angular/forms';
import { AssetService } from '../../services/asset.service';
import { MachineDefinition } from '../../models/asset.models';
import { debounceTime, distinctUntilChanged, startWith } from 'rxjs/operators';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { getMachineCategoryTooltip } from '@shared/constants/resource-tooltips';
import { getMachineCategoryIcon } from '@shared/constants/asset-icons';

export interface MachineCategory {
  category: string;
  manufacturers: ManufacturerGroup[];
  totalCount: number;
}

export interface ManufacturerGroup {
  manufacturer: string;
  machines: MachineDefinition[];
  count: number;
}

@Component({
  selector: 'app-machine-definition-accordion',
  standalone: true,
  imports: [
    MatExpansionModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatChipsModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule,
    ReactiveFormsModule
  ],
  template: `
    <div class="accordion-container">
      <div class="accordion-header">
        <h3>Machine Registry</h3>
        <span class="total-badge">{{ definitions().length }} types</span>
      </div>

      <mat-accordion multi="true">
        @for (category of filteredCategories(); track category.category) {
          <mat-expansion-panel class="category-panel">
            <mat-expansion-panel-header>
              <mat-panel-title>
                <mat-icon class="category-icon" [matTooltip]="getCategoryTooltip(category.category)">{{ getCategoryIcon(category.category) }}</mat-icon>
                <span [matTooltip]="getCategoryTooltip(category.category)">{{ category.category }}</span>
              </mat-panel-title>
              <mat-panel-description>
                <span class="count-badge ml-auto">{{ category.totalCount }} types</span>
              </mat-panel-description>
            </mat-expansion-panel-header>

            <!-- Nested accordion for manufacturers -->
            <mat-accordion multi="true" class="nested-accordion">
              @for (mfg of category.manufacturers; track mfg.manufacturer) {
                <mat-expansion-panel class="manufacturer-panel">
                  <mat-expansion-panel-header>
                    <mat-panel-title>
                      <mat-icon class="manufacturer-icon">business</mat-icon>
                      {{ mfg.manufacturer }}
                    </mat-panel-title>
                    <mat-panel-description>
                      <span class="count-badge small">{{ mfg.count }}</span>
                    </mat-panel-description>
                  </mat-expansion-panel-header>

                  <div class="machine-list">
                    @for (machine of mfg.machines; track machine.accession_id) {
                      <div class="machine-item">
                        <div class="machine-info">
                          <span class="machine-name">{{ machine.name }}</span>
                          <div class="machine-chips">
                            @if (machine.capabilities?.['channels']?.length) {
                              @for (ch of machine.capabilities!['channels']; track ch) {
                                <mat-chip class="capability-chip" matTooltip="Number of channels">{{ ch }}-channel</mat-chip>
                              }
                            }
                            @if (machine.capabilities?.['modules']?.length) {
                              @for (mod of machine.capabilities!['modules']; track mod) {
                                <mat-chip class="capability-chip module" [matTooltip]="'Module: ' + mod">{{ mod }}</mat-chip>
                              }
                            }
                          </div>
                        </div>
                        <div class="machine-meta">
                          @if (machine.compatible_backends?.length) {
                            <span class="backends-count" matTooltip="Compatible drivers/backends">
                              {{ machine.compatible_backends!.length }} drivers
                            </span>
                          }
                        </div>
                      </div>
                    }
                  </div>
                </mat-expansion-panel>
              }
            </mat-accordion>
          </mat-expansion-panel>
        }
      </mat-accordion>

      @if (filteredCategories().length === 0) {
        <div class="empty-state">
          <mat-icon>inventory_2</mat-icon>
          <p>No machine types matching "{{ filterValue() }}"</p>
        </div>
      }
    </div>
  `,
  styles: [`
    .accordion-container {
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

    .total-badge {
      background: var(--sys-tertiary-container);
      color: var(--sys-on-tertiary-container);
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 0.8rem;
      font-weight: 500;
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

    .manufacturer-icon {
      margin-right: 8px;
      font-size: 18px;
      width: 18px;
      height: 18px;
      color: var(--sys-on-surface-variant);
    }

    .count-badge {
      background: var(--sys-primary-container);
      color: var(--sys-on-primary-container);
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.75rem;
    }

    .count-badge.small {
      padding: 1px 6px;
      font-size: 0.7rem;
    }

    .nested-accordion {
      padding: 8px 0;
    }

    .manufacturer-panel {
      margin-bottom: 4px;
      padding-top: 4px;
      background: var(--mat-sys-surface-container);
    }

    .machine-list {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .machine-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      background: var(--sys-surface-container);
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.2s ease;
    }

    .machine-item:hover {
      background: var(--sys-surface-container-high);
    }

    .machine-info {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .machine-name {
      font-weight: 500;
      font-size: 0.9rem;
    }

    .machine-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }

    .capability-chip {
      --mdc-chip-container-height: 20px;
      font-size: 0.65rem;
      font-weight: 500;
    }

    .capability-chip.module {
      --mdc-chip-elevated-container-color: var(--sys-tertiary-container);
      --mdc-chip-label-text-color: var(--sys-on-tertiary-container);
    }

    .machine-meta {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .backends-count {
      font-size: 0.7rem;
      color: var(--sys-on-surface-variant);
      background: var(--sys-surface-container-highest);
      padding: 2px 6px;
      border-radius: 4px;
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
export class MachineDefinitionAccordionComponent implements OnInit {
  private assetService = inject(AssetService);

  definitions = signal<MachineDefinition[]>([]);
  // Removed filterControl
  filterValue = signal('');

  @Input() set search(val: string) {
    this.filterValue.set(val);
  }

  constructor() {
    // Removed valueChanges subscription
  }

  categoryGroups = computed(() => {
    const defs = this.definitions();
    const categoryMap = new Map<string, Map<string, MachineDefinition[]>>();

    defs.forEach(def => {
      const category = def.machine_category || 'Other';
      const manufacturer = def.manufacturer || 'Unknown';

      if (!categoryMap.has(category)) {
        categoryMap.set(category, new Map());
      }
      const mfgMap = categoryMap.get(category)!;

      if (!mfgMap.has(manufacturer)) {
        mfgMap.set(manufacturer, []);
      }
      mfgMap.get(manufacturer)!.push(def);
    });

    // Convert to array structure
    const categories: MachineCategory[] = [];
    categoryMap.forEach((mfgMap, category) => {
      const manufacturers: ManufacturerGroup[] = [];
      mfgMap.forEach((machines, manufacturer) => {
        manufacturers.push({
          manufacturer,
          machines: machines.sort((a, b) => a.name.localeCompare(b.name)),
          count: machines.length
        });
      });

      categories.push({
        category,
        manufacturers: manufacturers.sort((a, b) => b.count - a.count),
        totalCount: manufacturers.reduce((sum, m) => sum + m.count, 0)
      });
    });

    return categories.sort((a, b) => b.totalCount - a.totalCount);
  });

  filteredCategories = computed(() => {
    const filter = this.filterValue().toLowerCase();
    if (!filter) {
      return this.categoryGroups();
    }

    return this.categoryGroups()
      .map(category => ({
        ...category,
        manufacturers: category.manufacturers
          .map(mfg => ({
            ...mfg,
            machines: mfg.machines.filter(m =>
              m.name.toLowerCase().includes(filter) ||
              m.manufacturer?.toLowerCase().includes(filter) ||
              category.category.toLowerCase().includes(filter)
            )
          }))
          .filter(mfg => mfg.machines.length > 0)
          .map(mfg => ({ ...mfg, count: mfg.machines.length }))
      }))
      .filter(category => category.manufacturers.length > 0)
      .map(category => ({
        ...category,
        totalCount: category.manufacturers.reduce((sum, m) => sum + m.count, 0)
      }));
  });

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.assetService.getMachineDefinitions().subscribe(defs => {
      this.definitions.set(defs);
    });
  }

  getCategoryIcon(category: string): string {
    return getMachineCategoryIcon(category);
  }

  getCategoryTooltip(category: string): string {
    return getMachineCategoryTooltip(category);
  }
}
