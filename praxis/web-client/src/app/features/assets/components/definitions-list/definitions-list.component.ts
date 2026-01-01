import { Component, ChangeDetectionStrategy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatTabsModule } from '@angular/material/tabs';
import { AssetService } from '../../services/asset.service';
import { ResourceDefinition } from '../../models/asset.models';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged, startWith } from 'rxjs/operators';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { getPropertyTooltip } from '@shared/constants/resource-tooltips';
import { MachineDefinitionAccordionComponent } from '../machine-definition-accordion/machine-definition-accordion.component';

@Component({
  selector: 'app-definitions-list',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatInputModule,
    MatFormFieldModule,
    MatTabsModule,
    ReactiveFormsModule,
    MachineDefinitionAccordionComponent
  ],
  template: `
    <div class="definitions-list-container">
      <mat-tab-group animationDuration="0ms">
        <mat-tab>
          <ng-template mat-tab-label>
            <div class="flex items-center gap-2">
              <mat-icon class="!w-5 !h-5 !text-[18px]">precision_manufacturing</mat-icon>
              <span>Machine Types</span>
            </div>
          </ng-template>
          <app-machine-definition-accordion></app-machine-definition-accordion>
        </mat-tab>

        <mat-tab>
          <ng-template mat-tab-label>
            <div class="flex items-center gap-2">
              <mat-icon class="!w-5 !h-5 !text-[18px]">science</mat-icon>
              <span>Resource Types</span>
            </div>
          </ng-template>
          <div class="resource-tab-content">
            <mat-form-field appearance="outline" class="filter-field">
              <mat-label>Filter Resource Definitions</mat-label>
              <input matInput [formControl]="resourceFilterControl">
              <mat-icon matSuffix>search</mat-icon>
            </mat-form-field>

            <table mat-table [dataSource]="filteredResourceDefinitions()" class="mat-elevation-z2">
              <ng-container matColumnDef="name">
                <th mat-header-cell *matHeaderCellDef> Name </th>
                <td mat-cell *matCellDef="let def"> {{ def.name }} </td>
              </ng-container>

              <ng-container matColumnDef="type">
                <th mat-header-cell *matHeaderCellDef> Type </th>
                <td mat-cell *matCellDef="let def"> {{ def.resource_type || 'N/A' }} </td>
              </ng-container>

              <ng-container matColumnDef="manufacturer">
                <th mat-header-cell *matHeaderCellDef> Manufacturer </th>
                <td mat-cell *matCellDef="let def"> {{ def.manufacturer || 'N/A' }} </td>
              </ng-container>

              <ng-container matColumnDef="model">
                <th mat-header-cell *matHeaderCellDef> Model </th>
                <td mat-cell *matCellDef="let def"> {{ def.model || 'N/A' }} </td>
              </ng-container>

              <ng-container matColumnDef="consumable">
                <th mat-header-cell *matHeaderCellDef> Consumable </th>
                <td mat-cell *matCellDef="let def">
                  <mat-icon
                    [color]="def.is_consumable ? 'primary' : 'warn'"
                    [matTooltip]="def.is_consumable ? getPropertyTooltip('consumable') : 'Non-consumable: can be reused across protocols'"
                  >
                    {{ def.is_consumable ? 'check_circle' : 'cancel' }}
                  </mat-icon>
                </td>
              </ng-container>

              <ng-container matColumnDef="actions">
                <th mat-header-cell *matHeaderCellDef> Actions </th>
                <td mat-cell *matCellDef="let def">
                  <button mat-icon-button color="primary" matTooltip="View Details">
                    <mat-icon>info</mat-icon>
                  </button>
                </td>
              </ng-container>

              <tr mat-header-row *matHeaderRowDef="displayedResourceColumns"></tr>
              <tr mat-row *matRowDef="let row; columns: displayedResourceColumns;"></tr>

              <tr class="mat-row" *matNoDataRow>
                <td class="mat-cell" colspan="6">No resource definitions matching the filter "{{ resourceFilterControl.value }}"</td>
              </tr>
            </table>
          </div>
        </mat-tab>
      </mat-tab-group>
    </div>
  `,
  styles: [`
    .definitions-list-container {
      padding: 16px;
    }

    .filter-field {
      width: 100%;
      margin-bottom: 16px;
    }

    .mat-elevation-z2 {
      width: 100%;
    }

    .mat-no-data-row {
      text-align: center;
      font-style: italic;
      color: var(--mat-sys-color-on-surface-variant);
    }

    mat-tab-group {
      margin-top: 16px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DefinitionsListComponent {
  private assetService = inject(AssetService);

  resourceDefinitions = signal<ResourceDefinition[]>([]);
  filteredResourceDefinitions = signal<ResourceDefinition[]>([]);
  resourceFilterControl = new FormControl('', { nonNullable: true });

  displayedResourceColumns: string[] = ['name', 'type', 'manufacturer', 'model', 'consumable', 'actions'];

  constructor() {
    this.loadResourceDefinitions();

    this.resourceFilterControl.valueChanges.pipe(
      takeUntilDestroyed(),
      debounceTime(300),
      distinctUntilChanged(),
      startWith('')
    ).subscribe(filterValue => {
      this.applyResourceFilter(filterValue);
    });
  }

  private loadResourceDefinitions(): void {
    this.assetService.getResourceDefinitions().subscribe(
      (data) => {
        this.resourceDefinitions.set(data);
        this.applyResourceFilter(this.resourceFilterControl.value);
      },
      (error) => {
        console.error('Error fetching resource definitions:', error);
      }
    );
  }

  private applyResourceFilter(filterValue: string): void {
    const lowerCaseFilter = filterValue.toLowerCase();
    this.filteredResourceDefinitions.set(
      this.resourceDefinitions().filter(def =>
        def.name.toLowerCase().includes(lowerCaseFilter) ||
        def.resource_type?.toLowerCase().includes(lowerCaseFilter) ||
        def.manufacturer?.toLowerCase().includes(lowerCaseFilter) ||
        def.model?.toLowerCase().includes(lowerCaseFilter)
      )
    );
  }

  getPropertyTooltip(property: string): string {
    return getPropertyTooltip(property);
  }
}
