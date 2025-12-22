import { Component, ChangeDetectionStrategy, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormControl } from '@angular/forms';
import { FieldType, FieldTypeConfig, FormlyModule } from '@ngx-formly/core';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { AssetService } from '../../features/assets/services/asset.service';
import { Observable, of } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, startWith, map } from 'rxjs/operators';
import { AssetBase } from '../../features/assets/models/asset.models';

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
      <mat-option *ngFor="let asset of filteredAssets$ | async" [value]="asset">
        {{ asset.name }} <span class="accession-id">({{ asset.accession_id }})</span>
      </mat-option>
    </mat-autocomplete>
  `,
  styles: [`
    .accession-id {
      font-size: 0.8em;
      color: var(--mat-sys-color-on-surface-variant);
      margin-left: 8px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AssetSelectorComponent extends FieldType<FieldTypeConfig> implements OnInit {
  private assetService = inject(AssetService);
  filteredAssets$!: Observable<AssetBase[]>;

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
    const source$ = type === 'machine' 
      ? this.assetService.getMachines() 
      : this.assetService.getResources();

    return (source$ as Observable<AssetBase[]>).pipe(
      map((assets: AssetBase[]) => {
        if (!query) return assets;
        const lowerQuery = query.toLowerCase();
        return assets.filter(asset => 
          asset.name.toLowerCase().includes(lowerQuery) || 
          asset.accession_id.toLowerCase().includes(lowerQuery)
        );
      })
    );
  }

  displayFn(asset: AssetBase): string {
    return asset && asset.name ? asset.name : '';
  }
}