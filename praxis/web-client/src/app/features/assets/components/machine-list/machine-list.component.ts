import { Component, ChangeDetectionStrategy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { AssetService } from '../../services/asset.service';
import { Machine, MachineStatus } from '../../models/asset.models';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged, startWith, switchMap } from 'rxjs/operators';
import { FormControl, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-machine-list',
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
    <div class="machine-list-container">
      <mat-form-field appearance="outline" class="filter-field">
        <mat-label>Filter Machines</mat-label>
        <input matInput [formControl]="filterControl">
        <mat-icon matSuffix>search</mat-icon>
      </mat-form-field>

      <table mat-table [dataSource]="filteredMachines()" class="mat-elevation-z2">
        <!-- Name Column -->
        <ng-container matColumnDef="name">
          <th mat-header-cell *matHeaderCellDef> Name </th>
          <td mat-cell *matCellDef="let machine"> {{ machine.name }} </td>
        </ng-container>

        <!-- Status Column -->
        <ng-container matColumnDef="status">
          <th mat-header-cell *matHeaderCellDef> Status </th>
          <td mat-cell *matCellDef="let machine">
            <span class="status-badge" [ngClass]="machine.status">
              {{ machine.status | titlecase }}
            </span>
          </td>
        </ng-container>

        <!-- Model Column -->
        <ng-container matColumnDef="model">
          <th mat-header-cell *matHeaderCellDef> Model </th>
          <td mat-cell *matCellDef="let machine"> {{ machine.model || 'N/A' }} </td>
        </ng-container>

        <!-- Manufacturer Column -->
        <ng-container matColumnDef="manufacturer">
          <th mat-header-cell *matHeaderCellDef> Manufacturer </th>
          <td mat-cell *matCellDef="let machine"> {{ machine.manufacturer || 'N/A' }} </td>
        </ng-container>

        <!-- Actions Column -->
        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef> Actions </th>
          <td mat-cell *matCellDef="let machine">
            <button mat-icon-button color="primary" matTooltip="View Details">
              <mat-icon>info</mat-icon>
            </button>
            <button mat-icon-button color="accent" matTooltip="Edit Machine">
              <mat-icon>edit</mat-icon>
            </button>
            <button mat-icon-button color="warn" matTooltip="Delete Machine">
              <mat-icon>delete</mat-icon>
            </button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>

        <!-- Row shown when there is no matching data. -->
        <tr class="mat-row" *matNoDataRow>
          <td class="mat-cell" colspan="5">No machines matching the filter "{{ filterControl.value }}"</td>
        </tr>
      </table>
    </div>
  `,
  styles: [`
    .machine-list-container {
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

    .status-badge.idle { background-color: var(--mat-sys-color-primary); }
    .status-badge.running { background-color: var(--mat-sys-color-secondary); }
    .status-badge.offline { background-color: var(--mat-sys-color-error); }
    .status-badge.error { background-color: var(--mat-sys-color-warn); }
    .status-badge.maintenance { background-color: var(--mat-sys-color-tertiary); }
    .status-badge.unknown { background-color: var(--mat-sys-color-outline); }

    .mat-no-data-row {
      text-align: center;
      font-style: italic;
      color: var(--mat-sys-color-on-surface-variant);
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MachineListComponent {
  private assetService = inject(AssetService);
  machines = signal<Machine[]>([]);
  filteredMachines = signal<Machine[]>([]);
  filterControl = new FormControl('', { nonNullable: true });

  displayedColumns: string[] = ['name', 'status', 'model', 'manufacturer', 'actions'];

  constructor() {
    this.loadMachines();

    this.filterControl.valueChanges.pipe(
      takeUntilDestroyed(),
      debounceTime(300),
      distinctUntilChanged(),
      startWith('')
    ).subscribe(filterValue => {
      this.applyFilter(filterValue);
    });
  }

  loadMachines(): void {
    this.assetService.getMachines().subscribe(
      (data) => {
        this.machines.set(data);
        this.applyFilter(this.filterControl.value);
      },
      (error) => {
        console.error('Error fetching machines:', error);
        // TODO: Integrate global error handling / snackbar
      }
    );
  }

  private applyFilter(filterValue: string): void {
    const lowerCaseFilter = filterValue.toLowerCase();
    this.filteredMachines.set(
      this.machines().filter(machine =>
        machine.name.toLowerCase().includes(lowerCaseFilter) ||
        machine.status.toLowerCase().includes(lowerCaseFilter) ||
        machine.model?.toLowerCase().includes(lowerCaseFilter) ||
        machine.manufacturer?.toLowerCase().includes(lowerCaseFilter)
      )
    );
  }
}
