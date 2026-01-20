import { Component, ChangeDetectionStrategy, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { FieldType, FieldTypeConfig, FormlyModule } from '@ngx-formly/core';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog } from '@angular/material/dialog';
import { AssetService } from '../../features/assets/services/asset.service';
import { Observable, forkJoin, of } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, startWith, filter, take } from 'rxjs/operators';
import { AssetBase, Resource, ResourceDefinition } from '../../features/assets/models/asset.models';

interface AssetOption {
  asset: AssetBase;
  label: string;
  tags: string[];
}

@Component({
  selector: 'app-asset-selector',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatAutocompleteModule,
    MatInputModule,
    MatFormFieldModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatTooltipModule,
    FormlyModule
  ],
  template: `
    <div class="asset-field-container">
      <!-- Variable Name Header -->
      <div class="field-header">
        <span class="variable-name">{{ props['variableName'] || key }}</span>
        <span class="type-hint">{{ props['plrTypeFilter'] }}</span>
      </div>

      <!-- Auto Toggle Chip -->
      <div class="selection-row">
        <button
          mat-stroked-button
          [class.auto-active]="isAutoMode()"
          [class.auto-inactive]="!isAutoMode()"
          [disabled]="!canUseAuto()"
          (click)="toggleAutoMode()"
          class="auto-chip"
        >
          <mat-icon>{{ isAutoMode() ? 'auto_awesome' : 'auto_awesome_outlined' }}</mat-icon>
          @if (isAutoMode() && autoAsset()) {
            <span class="auto-label">{{ autoAsset()?.name }}</span>
            @for (tag of autoAssetTags(); track tag) {
              <span class="tag-badge">{{ tag }}</span>
            }
          } @else if (isAutoMode()) {
            <span class="auto-label">Auto (Resolving...)</span>
          } @else {
            <span class="auto-label">Auto</span>
          }
        </button>

        @if (!isAutoMode()) {
          <div class="manual-select">
            <mat-form-field appearance="outline" class="asset-input">
              <input
                type="text"
                matInput
                [formControl]="formControl"
                [formlyAttributes]="field"
                [matAutocomplete]="auto"
                [placeholder]="props.placeholder || 'Search...'"
              />
            </mat-form-field>
            <mat-autocomplete #auto="matAutocomplete" [displayWith]="displayFn">
              @for (option of filteredOptions$ | async; track option.asset.accession_id) {
                <mat-option [value]="option.asset" class="asset-option">
                  <div class="asset-content">
                    <div class="asset-main">
                      <span class="asset-name">{{ option.asset.name }}</span>
                      <span class="accession-id">({{ option.asset.accession_id }})</span>
                    </div>
                    @if (option.tags.length > 0) {
                      <div class="asset-tags">
                        @for (tag of option.tags; track tag) {
                          <span class="tag-chip">{{ tag }}</span>
                        }
                      </div>
                    }
                  </div>
                </mat-option>
              }
              @empty {
                <mat-option disabled>No assets found</mat-option>
              }
            </mat-autocomplete>
          </div>
        }
      </div>

      @if (props.description) {
        <div class="field-description">{{ props.description }}</div>
      }
    </div>
  `,
  styles: [`
    .asset-field-container {
      margin-bottom: 20px;
    }
    .field-header {
      display: flex;
      align-items: baseline;
      gap: 8px;
      margin-bottom: 8px;
    }
    .variable-name {
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
      color: var(--sys-primary);
    }
    .type-hint {
      font-size: 0.8em;
      color: var(--sys-on-surface-variant);
      opacity: 0.7;
    }
    .selection-row {
      display: flex;
      align-items: flex-start;
      gap: 12px;
    }
    .auto-chip {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      border-radius: 20px;
      transition: all 0.2s ease;
      min-height: 40px;
    }
    .auto-chip.auto-active {
      background: var(--sys-primary-container);
      border-color: var(--sys-primary);
      color: var(--sys-on-primary-container);
    }
    .auto-chip.auto-inactive {
      background: transparent;
      border-color: var(--sys-outline);
      color: var(--sys-on-surface-variant);
    }
    .auto-chip.auto-inactive:hover {
      border-color: var(--sys-primary);
    }
    .auto-chip:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    .auto-label {
      font-weight: 500;
    }
    .tag-badge {
      background: var(--sys-secondary);
      color: var(--sys-on-secondary);
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 0.75em;
      font-weight: 500;
    }
    .manual-select {
      flex: 1;
    }
    .asset-input {
      width: 100%;
    }
    .asset-option {
      line-height: 1.3;
      padding: 8px 16px;
      min-height: 52px;
    }
    .asset-content {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .asset-main {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .asset-name {
      font-weight: 500;
    }
    .accession-id {
      font-size: 0.8em;
      color: var(--sys-on-surface-variant);
    }
    .asset-tags {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }
    .tag-chip {
      background: var(--sys-secondary-container);
      color: var(--sys-on-secondary-container);
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.7em;
      font-weight: 500;
    }
    .field-description {
      font-size: 0.85em;
      color: var(--sys-on-surface-variant);
      margin-top: 4px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AssetSelectorComponent extends FieldType<FieldTypeConfig> implements OnInit {
  private assetService = inject(AssetService);
  private dialog = inject(MatDialog);

  filteredOptions$!: Observable<AssetOption[]>;
  private definitionsMap = new Map<string, ResourceDefinition>();
  private allAssets = signal<AssetBase[]>([]);

  isAutoMode = signal(true);
  autoAsset = signal<AssetBase | null>(null);
  autoAssetTags = signal<string[]>([]);
  canUseAuto = signal(true);

  ngOnInit() {
    const assetType = this.props['assetType'] || 'machine';

    // Load assets and determine auto selection
    this.loadAssets(assetType);

    // Setup filtered options for manual selection
    this.filteredOptions$ = this.formControl.valueChanges.pipe(
      startWith(''),
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(value => {
        const query = typeof value === 'string' ? value : (value?.name || '');
        return this.getFilteredOptions(query);
      })
    );

    // Set initial value to auto mode
    this.formControl.setValue({ mode: 'auto' });
  }

  private loadAssets(type: 'machine' | 'resource') {
    if (type === 'machine') {
      this.assetService.getMachines().subscribe({
        next: (assets) => {
          this.allAssets.set(assets);
          this.selectBestAuto(assets);
        },
        error: (err) => {
          console.error('[AssetSelector] Error loading machines:', err);
          this.canUseAuto.set(false);
        }
      });
    } else {
      forkJoin({
        resources: this.assetService.getResources(),
        definitions: this.assetService.getResourceDefinitions()
      }).subscribe({
        next: ({ resources, definitions }) => {
          definitions.forEach(d => this.definitionsMap.set(d.accession_id, d));

          let filtered = resources;
          const typeFilter = this.props['plrTypeFilter'];

          if (typeFilter) {
            const lowerFilter = typeFilter.toLowerCase();
            filtered = filtered.filter(r => {
              const def = this.definitionsMap.get(r.resource_definition_accession_id || '');
              if (!def) return false;

              // Check plr_category (case-insensitive)
              if (def.plr_category?.toLowerCase() === lowerFilter) return true;

              // Fallback: check if class name contains the filter
              if (def.name?.toLowerCase().includes(lowerFilter)) return true;

              return false;
            });
          }

          this.allAssets.set(filtered);
          this.selectBestAuto(filtered);
        },
        error: (err) => {
          console.error('[AssetSelector] Error loading resources:', err);
          this.canUseAuto.set(false);
        }
      });
    }
  }

  private calculateAssetScore(asset: AssetBase): number {
    let score = 0;
    const status = (asset as any).status?.toLowerCase() || 'unknown';

    // Status scoring (Lower is better)
    switch (status) {
      case 'available':
      case 'idle':
        score = 0;
        break;
      case 'in_use':
      case 'running':
        score = 10;
        break;
      case 'reserved':
        score = 20;
        break;
      case 'maintenance':
      case 'error':
      case 'depleted':
      case 'expired':
        score = 100;
        break;
      default:
        score = 50;
    }

    // Name length tie-breaker (prefer shorter, simpler names)
    score += (asset.name?.length || 0) / 100;

    return score;
  }

  private selectBestAuto(assets: AssetBase[]) {
    if (assets.length === 0) {
      this.canUseAuto.set(false);
      this.autoAsset.set(null);
      return;
    }

    // Sort by score
    const sorted = [...assets].sort((a, b) => this.calculateAssetScore(a) - this.calculateAssetScore(b));

    // Use autoSelectIndex to pick a unique asset (fallback to 0)
    // We apply the index to the SORTED list, so index 0 is the best available asset
    const autoIndex = this.props['autoSelectIndex'] || 0;
    const assetIndex = Math.min(autoIndex, sorted.length - 1);
    const best = sorted[assetIndex];

    this.autoAsset.set(best);
    this.autoAssetTags.set(this.getAssetTags(best));
    this.canUseAuto.set(true);

    // Update form value with actual asset
    if (this.isAutoMode()) {
      this.formControl.setValue({ mode: 'auto', resolvedAsset: best });
    }
  }

  toggleAutoMode() {
    const newMode = !this.isAutoMode();
    this.isAutoMode.set(newMode);

    if (newMode) {
      const best = this.autoAsset();
      this.formControl.setValue({ mode: 'auto', resolvedAsset: best });
    } else {
      this.formControl.setValue(null);
      // Trigger filtering to show all options
      this.formControl.updateValueAndValidity({ emitEvent: true });
    }
  }

  private getFilteredOptions(query: string): Observable<AssetOption[]> {
    const assets = this.allAssets();
    let filtered = assets;

    if (query) {
      const lowerQuery = query.toLowerCase();
      filtered = assets.filter(a =>
        a.name.toLowerCase().includes(lowerQuery) ||
        a.accession_id.toLowerCase().includes(lowerQuery)
      );
    }

    // Sort by smart score
    filtered.sort((a, b) => this.calculateAssetScore(a) - this.calculateAssetScore(b));

    return of(filtered.map(asset => ({
      asset,
      label: asset.name,
      tags: this.getAssetTags(asset),
    })));
  }

  private getAssetTags(asset: AssetBase): string[] {
    const tags: string[] = [];

    // Add status tag first
    if ((asset as any).status) {
      tags.push((asset as any).status);
    }

    const res = asset as Resource;
    if (res.resource_definition_accession_id) {
      const def = this.definitionsMap.get(res.resource_definition_accession_id);
      if (def) {
        if (def.num_items) tags.push(`${def.num_items}`);
        if (def.plate_type) tags.push(def.plate_type);
        if (def.tip_volume_ul) tags.push(`${def.tip_volume_ul}µL`);
      }
    } else if ((asset as any).machine_type) {
      // Machine fallback
      tags.push((asset as any).machine_type);
    }

    return tags;
  }

  displayFn = (value: AssetBase | { mode: string } | null): string => {
    if (!value) return '';
    if ('mode' in value) return '';
    return (value as AssetBase).name || '';
  };
}