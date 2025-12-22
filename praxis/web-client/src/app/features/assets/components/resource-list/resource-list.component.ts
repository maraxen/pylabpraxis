import { Component, ChangeDetectionStrategy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { AssetService } from '../../services/asset.service';
import { Resource, ResourceStatus } from '../../models/asset.models';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged, startWith, switchMap } from 'rxjs/operators';
import { FormControl, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-resource-list',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatInputModule,
    MatFormFieldModule,
    ReactiveFormsModule
  ],
  template: `
    <div class="resource-list-container">
      <mat-form-field appearance="outline" class="filter-field">
        <mat-label>Filter Resources</mat-label>
        <input matInput [formControl]="filterControl">
        <mat-icon matSuffix>search</mat-icon>
      </mat-form-field>

      <table mat-table [dataSource]="filteredResources()" class="mat-elevation-z2">
        <!-- Name Column -->
        <ng-container matColumnDef="name">
          <th mat-header-cell *matHeaderCellDef> Name </th>
          <td mat-cell *matCellDef="let resource"> {{ resource.name }} </td>
        </ng-container>

        <!-- Status Column -->
        <ng-container matColumnDef="status">
          <th mat-header-cell *matHeaderCellDef> Status </th>
          <td mat-cell *matCellDef="let resource">
            <span class="status-badge" [ngClass]="resource.status">
              {{ resource.status | titlecase }}
            </span>
          </td>
        </ng-container>

        <!-- Definition Column -->
        <ng-container matColumnDef="definition">
          <th mat-header-cell *matHeaderCellDef> Definition </th>
          <td mat-cell *matCellDef="let resource"> {{ resource.resource_definition_accession_id || 'N/A' }} </td>
        </ng-container>

        <!-- Parent Column -->
        <ng-container matColumnDef="parent">
          <th mat-header-cell *matHeaderCellDef> Parent </th>
          <td mat-cell *matCellDef="let resource"> {{ resource.parent_accession_id || 'N/A' }} </td>
        </ng-container>

        <!-- Actions Column -->
        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef> Actions </th>
          <td mat-cell *matCellDef="let resource">
            <button mat-icon-button color="primary" matTooltip="View Details">
              <mat-icon>info</mat-icon>
            </button>
            <button mat-icon-button color="accent" matTooltip="Edit Resource">
              <mat-icon>edit</mat-icon>
            </button>
            <button mat-icon-button color="warn" matTooltip="Delete Resource">
              <mat-icon>delete</mat-icon>
            </button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>

        <!-- Row shown when there is no matching data. -->
        <tr class="mat-row" *matNoDataRow>
          <td class="mat-cell" colspan="5">No resources matching the filter "{{ filterControl.value }}"</td>
        </tr>
      </table>
    </div>
  `,
  styles: [`
    .resource-list-container {
      padding: 16px;
    }

    .filter-field {
      width: 100%;
      margin-bottom: 16px;
    }

    .mat-elevation-z2 {
      width: 100%;
    }

    .status-badge {
      padding: 4px 8px;
      border-radius: 4px;
      font-weight: bold;
      color: white;
      font-size: 0.75em;
      text-transform: uppercase;
    }

    .status-badge.available { background-color: var(--mat-sys-color-primary); }
    .status-badge.in_use { background-color: var(--mat-sys-color-secondary); }
    .status-badge.depleted { background-color: var(--mat-sys-color-warn); }
    .status-badge.expired { background-color: var(--mat-sys-color-error); }
    .status-badge.unknown { background-color: var(--mat-sys-color-outline); }

    .mat-no-data-row {
      text-align: center;
      font-style: italic;
      color: var(--mat-sys-color-on-surface-variant);
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ResourceListComponent {
  private assetService = inject(AssetService);
  resources = signal<Resource[]>([]);
  filteredResources = signal<Resource[]>([]);
  filterControl = new FormControl('', { nonNullable: true });

  displayedColumns: string[] = ['name', 'status', 'definition', 'parent', 'actions'];

  constructor() {
    this.loadResources();

    this.filterControl.valueChanges.pipe(
      takeUntilDestroyed(),
      debounceTime(300),
      distinctUntilChanged(),
      startWith('')
    ).subscribe(filterValue => {
      this.applyFilter(filterValue);
    });
  }

  loadResources(): void {
    this.assetService.getResources().subscribe(
      (data) => {
        this.resources.set(data);
        this.applyFilter(this.filterControl.value);
      },
      (error) => {
        console.error('Error fetching resources:', error);
        // TODO: Integrate global error handling / snackbar
      }
    );
  }

  private applyFilter(filterValue: string): void {
    const lowerCaseFilter = filterValue.toLowerCase();
    this.filteredResources.set(
      this.resources().filter(resource =>
        resource.name.toLowerCase().includes(lowerCaseFilter) ||
        resource.status.toLowerCase().includes(lowerCaseFilter) ||
        resource.resource_definition_accession_id?.toLowerCase().includes(lowerCaseFilter) ||
        resource.parent_accession_id?.toLowerCase().includes(lowerCaseFilter)
      )
    );
  }
}
