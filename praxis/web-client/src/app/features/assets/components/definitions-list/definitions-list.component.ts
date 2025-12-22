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
import { MachineDefinition, ResourceDefinition } from '../../models/asset.models';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged, startWith } from 'rxjs/operators';
import { FormControl, ReactiveFormsModule } from '@angular/forms';

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
    ReactiveFormsModule
  ],
  template: `
    <div class="definitions-list-container">
      <mat-tab-group animationDuration="0ms">
        <mat-tab label="Machine Definitions">
          <mat-form-field appearance="outline" class="filter-field">
            <mat-label>Filter Machine Definitions</mat-label>
            <input matInput [formControl]="machineFilterControl">
            <mat-icon matSuffix>search</mat-icon>
          </mat-form-field>

          <table mat-table [dataSource]="filteredMachineDefinitions()" class="mat-elevation-z2">
            <ng-container matColumnDef="name">
              <th mat-header-cell *matHeaderCellDef> Name </th>
              <td mat-cell *matCellDef="let def"> {{ def.name }} </td>
            </ng-container>

            <ng-container matColumnDef="category">
              <th mat-header-cell *matHeaderCellDef> Category </th>
              <td mat-cell *matCellDef="let def"> {{ def.machine_category || 'N/A' }} </td>
            </ng-container>

            <ng-container matColumnDef="manufacturer">
              <th mat-header-cell *matHeaderCellDef> Manufacturer </th>
              <td mat-cell *matCellDef="let def"> {{ def.manufacturer || 'N/A' }} </td>
            </ng-container>

            <ng-container matColumnDef="model">
              <th mat-header-cell *matHeaderCellDef> Model </th>
              <td mat-cell *matCellDef="let def"> {{ def.model || 'N/A' }} </td>
            </ng-container>

            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef> Actions </th>
              <td mat-cell *matCellDef="let def">
                <button mat-icon-button color="primary" matTooltip="View Details">
                  <mat-icon>info</mat-icon>
                </button>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedMachineColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedMachineColumns;"></tr>

            <tr class="mat-row" *matNoDataRow>
              <td class="mat-cell" colspan="5">No machine definitions matching the filter "{{ machineFilterControl.value }}"</td>
            </tr>
          </table>
        </mat-tab>

        <mat-tab label="Resource Definitions">
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
                <mat-icon [color]="def.is_consumable ? 'primary' : 'warn'">
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

  machineDefinitions = signal<MachineDefinition[]>([]);
  filteredMachineDefinitions = signal<MachineDefinition[]>([]);
  machineFilterControl = new FormControl('', { nonNullable: true });

  resourceDefinitions = signal<ResourceDefinition[]>([]);
  filteredResourceDefinitions = signal<ResourceDefinition[]>([]);
  resourceFilterControl = new FormControl('', { nonNullable: true });

  displayedMachineColumns: string[] = ['name', 'category', 'manufacturer', 'model', 'actions'];
  displayedResourceColumns: string[] = ['name', 'type', 'manufacturer', 'model', 'consumable', 'actions'];

  constructor() {
    this.loadMachineDefinitions();
    this.loadResourceDefinitions();

    this.machineFilterControl.valueChanges.pipe(
      takeUntilDestroyed(),
      debounceTime(300),
      distinctUntilChanged(),
      startWith('')
    ).subscribe(filterValue => {
      this.applyMachineFilter(filterValue);
    });

    this.resourceFilterControl.valueChanges.pipe(
      takeUntilDestroyed(),
      debounceTime(300),
      distinctUntilChanged(),
      startWith('')
    ).subscribe(filterValue => {
      this.applyResourceFilter(filterValue);
    });
  }

  private loadMachineDefinitions(): void {
    this.assetService.getMachineDefinitions().subscribe(
      (data) => {
        this.machineDefinitions.set(data);
        this.applyMachineFilter(this.machineFilterControl.value);
      },
      (error) => {
        console.error('Error fetching machine definitions:', error);
        // TODO: Integrate global error handling / snackbar
      }
    );
  }

  private applyMachineFilter(filterValue: string): void {
    const lowerCaseFilter = filterValue.toLowerCase();
    this.filteredMachineDefinitions.set(
      this.machineDefinitions().filter(def =>
        def.name.toLowerCase().includes(lowerCaseFilter) ||
        def.machine_category?.toLowerCase().includes(lowerCaseFilter) ||
        def.manufacturer?.toLowerCase().includes(lowerCaseFilter) ||
        def.model?.toLowerCase().includes(lowerCaseFilter)
      )
    );
  }

  private loadResourceDefinitions(): void {
    this.assetService.getResourceDefinitions().subscribe(
      (data) => {
        this.resourceDefinitions.set(data);
        this.applyResourceFilter(this.resourceFilterControl.value);
      },
      (error) => {
        console.error('Error fetching resource definitions:', error);
        // TODO: Integrate global error handling / snackbar
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
}
