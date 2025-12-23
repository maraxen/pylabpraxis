import { Component, ChangeDetectionStrategy, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { FieldType, FieldTypeConfig, FormlyModule } from '@ngx-formly/core';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { AssetService } from '../../features/assets/services/asset.service';
import { Observable, forkJoin } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, startWith, map } from 'rxjs/operators';
import { AssetBase, Resource, ResourceDefinition } from '../../features/assets/models/asset.models';

@Component({
  selector: 'app-asset-selector',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatAutocompleteModule,
    MatInputModule,
    MatFormFieldModule,
    FormlyModule
  ],
  template: `
    <input
      type="text"
      matInput
      [formControl]="formControl"
      [formlyAttributes]="field"
      [matAutocomplete]="auto"
      [placeholder]="to.placeholder || 'Select Asset'"
    />
    <mat-autocomplete #auto="matAutocomplete" [displayWith]="displayFn">
      <mat-option *ngFor="let asset of filteredAssets$ | async" [value]="asset" class="asset-option">
        <div class="flex flex-col">
          <div>
            {{ asset.name }} <span class="accession-id">({{ asset.accession_id }})</span>
          </div>
          <div class="asset-tags" *ngIf="getAssetDetails(asset)">
            {{ getAssetDetails(asset) }}
          </div>
        </div>
      </mat-option>
    </mat-autocomplete>
  `,
  styles: [`
    .accession-id {
      font-size: 0.8em;
      color: var(--mat-sys-color-on-surface-variant);
      margin-left: 8px;
    }
    .asset-option {
      line-height: 1.2;
      padding-top: 8px;
      padding-bottom: 8px;
    }
    .asset-tags {
      font-size: 0.75em;
      color: var(--mat-sys-secondary);
      display: flex;
      gap: 8px;
      margin-top: 2px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AssetSelectorComponent extends FieldType<FieldTypeConfig> implements OnInit {
  private assetService = inject(AssetService);
  filteredAssets$!: Observable<AssetBase[]>;
  private definitionsMap = new Map<string, ResourceDefinition>();

  ngOnInit() {
    const assetType = this.to['assetType'] || 'machine'; // 'machine' or 'resource'

    this.filteredAssets$ = this.formControl.valueChanges.pipe(
      startWith(''),
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(value => {
        const name = typeof value === 'string' ? value : value?.name;
        return this.searchAssets(name, assetType);
      })
    );
  }

  private searchAssets(query: string, type: 'machine' | 'resource'): Observable<AssetBase[]> {
    if (type === 'machine') {
      return this.assetService.getMachines().pipe(
        map(assets => this.filterAssets(assets, query))
      );
    } else {
      return forkJoin({
        resources: this.assetService.getResources(),
        definitions: this.assetService.getResourceDefinitions()
      }).pipe(
        map(({ resources, definitions }) => {
          // Update definitions map
          definitions.forEach(d => this.definitionsMap.set(d.accession_id, d));

          let filtered = resources;

          // Apply plrTypeFilter if present
          const typeFilter = this.to['plrTypeFilter'];
          if (typeFilter) {
            filtered = filtered.filter(r => {
              const def = this.definitionsMap.get((r as Resource).resource_definition_accession_id || '');
              return def && def.plr_category === typeFilter;
            });
          }

          return this.filterAssets(filtered, query);
        })
      );
    }
  }

  private filterAssets(assets: AssetBase[], query: string): AssetBase[] {
    if (!query) return assets;
    const lowerQuery = query.toLowerCase();
    return assets.filter(asset => 
      asset.name.toLowerCase().includes(lowerQuery) || 
      asset.accession_id.toLowerCase().includes(lowerQuery)
    );
  }

  displayFn(asset: AssetBase): string {
    return asset && asset.name ? asset.name : '';
  }

  getAssetDetails(asset: AssetBase): string {
    const res = asset as Resource;
    if (!res.resource_definition_accession_id) return '';
    const def = this.definitionsMap.get(res.resource_definition_accession_id);
    if (!def) return '';

    const parts = [];
    if (def.num_items) parts.push(`${def.num_items}`);
    if (def.plate_type) parts.push(def.plate_type);
    if (def.tip_volume_ul) parts.push(`${def.tip_volume_ul}µL`);

    return parts.join(' • ');
  }
}