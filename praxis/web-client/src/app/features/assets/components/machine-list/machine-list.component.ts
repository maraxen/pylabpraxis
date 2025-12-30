import { Component, ChangeDetectionStrategy, inject, signal, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatMenuModule, MatMenuTrigger } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';
import { MatDialog } from '@angular/material/dialog';
import { AssetService } from '../../services/asset.service';
import { Machine, MachineStatus } from '../../models/asset.models';
import { AssetStatusChipComponent, AssetStatusType } from '../asset-status-chip/asset-status-chip.component';
import { LocationBreadcrumbComponent } from '../location-breadcrumb/location-breadcrumb.component';
import { MachineDetailsDialogComponent } from './machine-details-dialog.component';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged, startWith, switchMap, filter, finalize } from 'rxjs/operators';
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
    MatMenuModule,
    MatDividerModule,
    ReactiveFormsModule,
    ReactiveFormsModule,
    AssetStatusChipComponent,
    LocationBreadcrumbComponent
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
            <app-asset-status-chip [status]="machine.status" [showLabel]="true" />
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

        <!-- Location Column -->
        <ng-container matColumnDef="location">
          <th mat-header-cell *matHeaderCellDef> Location </th>
          <td mat-cell *matCellDef="let machine">
              <app-location-breadcrumb [location]="machine.location"></app-location-breadcrumb>
          </td>
        </ng-container>

        <!-- Actions Column -->
        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef> Actions </th>
          <td mat-cell *matCellDef="let machine">
            <button mat-icon-button color="primary" matTooltip="View Details" (click)="viewDetails(machine)">
              <mat-icon>info</mat-icon>
            </button>
            <button mat-icon-button color="accent" matTooltip="Edit Machine" (click)="editMachine(machine)">
              <mat-icon>edit</mat-icon>
            </button>
            <button mat-icon-button color="warn" matTooltip="Delete Machine" (click)="deleteMachine(machine)">
              <mat-icon>delete</mat-icon>
            </button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;" 
            (contextmenu)="onContextMenu($event, row)"
            class="machine-row"></tr>

        <!-- Row shown when there is no matching data. -->
        <tr class="mat-row" *matNoDataRow>
          <td class="mat-cell" colspan="5">No machines matching the filter "{{ filterControl.value }}"</td>
        </tr>
      </table>

      <!-- Context Menu -->
      <div style="visibility: hidden; position: fixed"
           [style.left]="contextMenuPosition.x"
           [style.top]="contextMenuPosition.y"
           [matMenuTriggerFor]="contextMenu">
      </div>
      <mat-menu #contextMenu="matMenu">
        <ng-template matMenuContent let-item="item">
          <button mat-menu-item (click)="editMachine(item)">
            <mat-icon>edit</mat-icon>
            <span>Edit</span>
          </button>
          <button mat-menu-item (click)="duplicateMachine(item)">
            <mat-icon>content_copy</mat-icon>
            <span>Duplicate</span>
          </button>
          <mat-divider></mat-divider>
          <button mat-menu-item (click)="deleteMachine(item)">
            <mat-icon color="warn">delete</mat-icon>
            <span style="color: var(--mat-sys-error)">Delete</span>
          </button>
        </ng-template>
      </mat-menu>
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

    .machine-row:hover {
      background-color: var(--mat-sys-surface-container-highest);
      cursor: pointer;
    }

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
  private dialog = inject(MatDialog);
  machines = signal<Machine[]>([]);
  filteredMachines = signal<Machine[]>([]);
  filterControl = new FormControl('', { nonNullable: true });

  displayedColumns: string[] = ['name', 'status', 'model', 'manufacturer', 'location', 'actions'];

  @ViewChild(MatMenuTrigger) contextMenuTrigger!: MatMenuTrigger;
  contextMenuPosition = { x: '0px', y: '0px' };

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

  onContextMenu(event: MouseEvent, machine: Machine) {
    event.preventDefault();
    this.contextMenuPosition.x = event.clientX + 'px';
    this.contextMenuPosition.y = event.clientY + 'px';
    this.contextMenuTrigger.menuData = { item: machine };
    this.contextMenuTrigger.openMenu();
  }

  viewDetails(machine: Machine) {
    this.dialog.open(MachineDetailsDialogComponent, {
      width: '800px', // Wider to accommodate tabs and deck view
      data: { machine }
    });
  }

  editMachine(machine: Machine) {
    console.log('Edit machine:', machine);
    // Placeholder for future implementation
  }

  duplicateMachine(machine: Machine) {
    console.log('Duplicate machine:', machine);
    // Placeholder for future implementation
  }

  deleteMachine(machine: Machine) {
    if (confirm(`Are you sure you want to delete machine "${machine.name}"?`)) {
      this.assetService.deleteMachine(machine.accession_id).subscribe({
        next: () => {
          this.loadMachines();
        },
        error: (err) => console.error('Error deleting machine', err)
      });
    }
  }
}

