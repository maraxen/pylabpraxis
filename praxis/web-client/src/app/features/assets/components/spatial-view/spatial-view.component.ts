import { Component, inject, signal, computed, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { forkJoin } from 'rxjs';

import { AssetService } from '../../services/asset.service';
import { AssetFiltersComponent, AssetFilterState } from '../asset-filters/asset-filters.component';
import { AssetStatusChipComponent } from '../asset-status-chip/asset-status-chip.component';
import { Machine, Resource, Workcell } from '../../models/asset.models';

@Component({
  selector: 'app-spatial-view',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    AssetFiltersComponent,
    AssetStatusChipComponent
  ],
  template: `
    <div class="h-full flex flex-col bg-[var(--mat-sys-surface-variant)]">
      <!-- Filters Header -->
      <div class="p-4 pb-0 bg-[var(--mat-sys-surface)] border-b border-[var(--theme-border)] z-10">
        <app-asset-filters
          [categories]="categories()"
          [machines]="machines()"
          [workcells]="workcells()"
          [showMachineFilter]="true"
          [showWorkcellFilter]="true"
          (filtersChange)="onFiltersChange($event)">
        </app-asset-filters>
      </div>

      <!-- Main Content -->
      <div class="flex-1 overflow-y-auto p-6 relative">
        @if (isLoading()) {
          <div class="absolute inset-0 flex items-center justify-center bg-white/50 dark:bg-black/50 z-20 backdrop-blur-sm">
            <mat-spinner diameter="40"></mat-spinner>
          </div>
        }

        <!-- Results Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          @for (asset of filteredAssets(); track asset.accession_id) {
            <div class="asset-card group relative bg-[var(--mat-sys-surface)] border border-[var(--theme-border)] rounded-2xl p-5 hover:shadow-lg hover:-translate-y-1 transition-all duration-200 cursor-pointer">
              <!-- Type Indicator -->
              <div class="absolute top-4 right-4 text-[10px] uppercase font-bold tracking-wider px-2 py-1 rounded bg-[var(--mat-sys-surface-variant)] text-sys-text-tertiary">
                {{ isMachine(asset) ? 'Machine' : 'Resource' }}
              </div>

              <!-- Icon & Name -->
              <div class="flex items-start gap-4 mb-4">
                <div class="w-12 h-12 rounded-xl flex items-center justify-center shrink-0" 
                     [ngClass]="getIconBgClass(asset)">
                  <mat-icon [class]="getIconTextClass(asset)">{{ getIcon(asset) }}</mat-icon>
                </div>
                <div class="min-w-0 flex-1">
                  <h3 class="font-bold text-lg text-sys-text-primary truncate mb-1" [matTooltip]="asset.name">{{ asset.name }}</h3>
                  <p class="text-xs text-sys-text-secondary truncate">{{ getAssetSubtitle(asset) }}</p>
                </div>
              </div>

              <!-- Metadata Grid -->
              <div class="grid grid-cols-2 gap-y-3 gap-x-2 text-sm mb-4">
                <div class="flex flex-col">
                  <span class="text-[10px] uppercase text-sys-text-tertiary font-bold tracking-wider mb-0.5">Status</span>
                  <app-asset-status-chip [status]="asset.status" class="w-fit" />
                </div>
                
                <div class="flex flex-col">
                  <span class="text-[10px] uppercase text-sys-text-tertiary font-bold tracking-wider mb-0.5">Location</span>
                  <div class="flex items-center gap-1.5 text-sys-text-secondary truncate">
                    <mat-icon class="!w-3 !h-3 !text-[12px] opacity-70">location_on</mat-icon>
                    <span class="truncate" [matTooltip]="getLocationLabel(asset)">{{ getLocationLabel(asset) }}</span>
                  </div>
                </div>
              </div>

              <!-- Footer / Quick Actions -->
              <div class="pt-3 border-t border-[var(--theme-border)] flex items-center justify-between opacity-60 group-hover:opacity-100 transition-opacity">
                <span class="text-xs text-sys-text-tertiary font-mono">{{ getShortId(asset.accession_id) }}</span>
                <!-- Could add action buttons here later -->
              </div>
            </div>
          }
        </div>

        @if (!isLoading() && filteredAssets().length === 0) {
          <div class="flex flex-col items-center justify-center h-[60vh] text-sys-text-tertiary">
            <div class="w-20 h-20 rounded-full bg-[var(--mat-sys-surface-variant)] flex items-center justify-center mb-4">
              <mat-icon class="!w-10 !h-10 !text-[40px] opacity-50">filter_list_off</mat-icon>
            </div>
            <h3 class="text-lg font-medium text-sys-text-secondary mb-1">No assets found</h3>
            <p>Try adjusting your filters or search terms</p>
          </div>
        }
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      height: 100%;
    }

    .asset-card {
      min-height: 200px;
      display: flex;
      flex-direction: column;
      background: linear-gradient(135deg, var(--mat-sys-surface) 0%, var(--mat-sys-surface-container-low) 100%);
      position: relative;
      overflow: hidden;
    }

    .asset-card::before {
      content: '';
      position: absolute;
      top: -20%;
      right: -10%;
      width: 100px;
      height: 100px;
      background: radial-gradient(circle at center, var(--mat-sys-primary) 0%, transparent 70%);
      opacity: 0.03;
      pointer-events: none;
    }

    .asset-card:hover {
      border-color: var(--mat-sys-primary);
      box-shadow: 0 8px 24px -12px var(--mat-sys-primary);
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class SpatialViewComponent implements OnInit {
  private assetService = inject(AssetService);

  // Data Signals
  machines = signal<Machine[]>([]);
  resources = signal<Resource[]>([]);
  // Placeholder workcells until service supports them, or derive from machines?
  // We'll derive unique workcell IDs from machines for now if not available directly
  workcells = signal<Workcell[]>([]);

  isLoading = signal(true);

  // Filter State
  currentFilters = signal<AssetFilterState>({
    status: [],
    search: '',
    category: [],
    machine_id: null,
    workcell_id: null,
    maintenance_due: false,
    sort_by: 'created_at',
    sort_order: 'desc'
  });

  // Derived
  categories = computed(() => {
    // Collect all unique categories from machines and resources
    const cats = new Set<string>();
    this.machines().forEach(m => {
      if (m.machine_category) cats.add(m.machine_category);
    });
    // Resources might use 'plr_category' from definition, or we can just ignore for now
    // as Resource logic is a bit more complex. 
    // Let's rely on machine categories primarily for now or strictly map resources.
    return Array.from(cats).sort();
  });

  allAssets = computed(() => {
    return [...this.machines(), ...this.resources()];
  });

  filteredAssets = computed(() => {
    let assets = this.allAssets();
    const filters = this.currentFilters();

    // 1. Search
    if (filters.search) {
      const q = filters.search.toLowerCase();
      assets = assets.filter(a =>
        a.name.toLowerCase().includes(q) ||
        (a.fqn || '').toLowerCase().includes(q) ||
        (a.location_label || '').toLowerCase().includes(q)
      );
    }

    // 2. Status
    if (filters.status.length > 0) {
      assets = assets.filter(a => filters.status.includes(a.status));
    }

    // 3. Category
    if (filters.category.length > 0) {
      // Only machines really have 'category' easily accessible on the asset itself (machine_category)
      // Resources have it on definition. For simplicity, filtering machines by category.
      assets = assets.filter(a => {
        if (this.isMachine(a)) {
          return a.machine_category && filters.category.includes(a.machine_category);
        }
        return false; // Or true if we don't want to filter resources out
      });
    }

    // 4. Machine ID (Location)
    if (filters.machine_id) {
      assets = assets.filter(a => {
        // Include the machine itself? No, usually "Location: Machine X" means things *in* machine X.
        // But if it's the machine itself, it matches ID.
        if (a.accession_id === filters.machine_id) return true;
        // If resource, check location
        if (!this.isMachine(a)) {
          return (a as Resource).machine_location_accession_id === filters.machine_id;
        }
        return false;
      });
    }

    // 5. Workcell ID
    if (filters.workcell_id) {
      assets = assets.filter(a => {
        // Machines have workcell_accession_id directly?
        // Need to check Machine interface update if workcell_accession_id is there
        // Based on backend it is.
        return (a as Machine | Resource).workcell_accession_id === filters.workcell_id;
      });
    }

    // 6. Sorting
    assets.sort((a, b) => {
      let valA: any = '';
      let valB: any = '';

      // Helper to get value
      const getVal = (item: any, field: string) => {
        if (field === 'name') return item.name?.toLowerCase() || '';
        if (field === 'created_at') return new Date(item.created_at || 0).getTime();
        if (field === 'status') return item.status;
        if (field === 'category') return (item.machine_category || item.asset_type || '').toLowerCase();
        return '';
      };

      valA = getVal(a, filters.sort_by);
      valB = getVal(b, filters.sort_by);

      if (valA < valB) return filters.sort_order === 'asc' ? -1 : 1;
      if (valA > valB) return filters.sort_order === 'asc' ? 1 : -1;
      return 0;
    });

    return assets;
  });

  ngOnInit() {
    this.refreshData();
  }

  refreshData() {
    this.isLoading.set(true);
    forkJoin({
      machines: this.assetService.getMachines(),
      resources: this.assetService.getResources()
    }).subscribe({
      next: (res) => {
        this.machines.set(res.machines);
        this.resources.set(res.resources);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Failed to load assets', err);
        this.isLoading.set(false);
      }
    });
  }

  onFiltersChange(filters: AssetFilterState) {
    this.currentFilters.set(filters);
  }

  // Helpers
  isMachine(asset: any): asset is Machine {
    return 'machine_category' in asset; // Crude check, or check status enum values
  }

  getIcon(asset: any): string {
    if (this.isMachine(asset)) {
      if (asset.machine_category?.toLowerCase().includes('liquid')) return 'water_drop';
      return 'precision_manufacturing';
    }
    return 'science'; // Resource
  }

  getIconBgClass(asset: any): string {
    if (this.isMachine(asset)) return 'bg-blue-500/10';
    return 'bg-orange-500/10';
  }

  getIconTextClass(asset: any): string {
    if (this.isMachine(asset)) return 'text-blue-500';
    return 'text-orange-500';
  }

  getAssetSubtitle(asset: any): string {
    if (this.isMachine(asset)) return (asset as Machine).model || (asset as Machine).manufacturer || 'Unknown Model';
    return (asset as Resource).resource_definition_accession_id ? 'Resource' : 'Custom Resource'; // Could fetch definition name
  }

  getLocationLabel(asset: any): string {
    return asset.location_label || 'Unassigned';
  }

  getShortId(id: string): string {
    return id.substring(0, 8);
  }
}
