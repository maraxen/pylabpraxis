import { Component, ChangeDetectionStrategy, inject, signal, ViewChild, computed } from '@angular/core';

import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatMenuModule, MatMenuTrigger } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog } from '@angular/material/dialog';
import { AssetService } from '../../services/asset.service';
import { Machine, MachineStatus, MachineDefinition } from '../../models/asset.models';
import { AssetStatusChipComponent, AssetStatusType } from '../asset-status-chip/asset-status-chip.component';
import { LocationBreadcrumbComponent } from '../location-breadcrumb/location-breadcrumb.component';
import { MachineFiltersComponent, MachineFilterState } from '../machine-filters/machine-filters.component';
import { MaintenanceBadgeComponent } from '../maintenance-badge/maintenance-badge.component';
import { calculateMaintenanceStatus } from '../../utils/maintenance.utils';
import { MachineDetailsDialogComponent } from './machine-details-dialog.component';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged, startWith, switchMap, filter, finalize } from 'rxjs/operators';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { AppStore } from '../../../../core/store/app.store';

@Component({
  selector: 'app-machine-list',
  standalone: true,
  imports: [
    MatTableModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatInputModule,
    MatFormFieldModule,
    MatMenuModule,
    MatDividerModule,
    MatChipsModule,
    ReactiveFormsModule,
    AssetStatusChipComponent,
    LocationBreadcrumbComponent,
    MachineFiltersComponent,
    MaintenanceBadgeComponent
],
  template: `
    <div class="machine-list-container">
      <app-machine-filters
        [machines]="machines()"
        [machineDefinitions]="machineDefinitions()"
        (filtersChange)="onFiltersChange($event)">
      </app-machine-filters>

      <table mat-table [dataSource]="filteredMachines()" class="mat-elevation-z2">
        <!-- Name Column -->
        <ng-container matColumnDef="name">
          <th mat-header-cell *matHeaderCellDef> Name </th>
          <td mat-cell *matCellDef="let machine"> {{ machine.name }} </td>
        </ng-container>

        <!-- Simulated Indicator -->
        <ng-container matColumnDef="simulated">
          <th mat-header-cell *matHeaderCellDef> Mode </th>
          <td mat-cell *matCellDef="let machine">
            @if (machine.is_simulation_override) {
              <mat-chip class="simulated-chip" [highlighted]="false">
                <mat-icon class="chip-icon">computer</mat-icon>
                Simulated
              </mat-chip>
            } @else {
              <mat-chip class="physical-chip" [highlighted]="false">
                <mat-icon class="chip-icon">precision_manufacturing</mat-icon>
                Physical
              </mat-chip>
            }
          </td>
        </ng-container>

        <!-- Status Column -->
        <ng-container matColumnDef="status">
          <th mat-header-cell *matHeaderCellDef> Status </th>
          <td mat-cell *matCellDef="let machine">
            <app-asset-status-chip [status]="machine.status" [showLabel]="true" />
          </td>
        </ng-container>

        <!-- Category Column -->
        <ng-container matColumnDef="category">
          <th mat-header-cell *matHeaderCellDef> Category </th>
          <td mat-cell *matCellDef="let machine"> {{ machine.machine_category || 'Unknown' }} </td>
        </ng-container>

        <!-- Model Column -->
        <ng-container matColumnDef="model">
          <th mat-header-cell *matHeaderCellDef> Model </th>
          <td mat-cell *matCellDef="let machine"> {{ machine.model || 'N/A' }} </td>
        </ng-container>

        <!-- Location Column -->
        <ng-container matColumnDef="location">
          <th mat-header-cell *matHeaderCellDef> Location </th>
          <td mat-cell *matCellDef="let machine">
              <app-location-breadcrumb [location]="machine.location"></app-location-breadcrumb>
          </td>
        </ng-container>

        <!-- Maintenance Column -->
        <ng-container matColumnDef="maintenance">
          <th mat-header-cell *matHeaderCellDef> Maintenance </th>
          <td mat-cell *matCellDef="let machine">
              <app-maintenance-badge [machine]="machine" />
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

        <tr mat-header-row *matHeaderRowDef="displayedColumns()"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns();" 
            (contextmenu)="onContextMenu($event, row)"
            class="machine-row"></tr>

        <!-- Row shown when there is no matching data. -->
        <tr class="mat-row" *matNoDataRow>
          <td class="mat-cell" colspan="7">No machines matching the selected filters</td>
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
      padding: 0 16px 16px 16px;
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

    .simulated-chip {
      --mdc-chip-container-height: 24px;
      font-size: 0.75rem;
      background: rgba(59, 130, 246, 0.15);
      color: rgb(59, 130, 246);
    }

    .physical-chip {
      --mdc-chip-container-height: 24px;
      font-size: 0.75rem;
      background: rgba(34, 197, 94, 0.15);
      color: rgb(34, 197, 94);
    }

    :host ::ng-deep .chip-icon {
      font-size: 14px;
      width: 14px;
      height: 14px;
      margin-right: 4px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MachineListComponent {
  private assetService = inject(AssetService);
  private dialog = inject(MatDialog);
  private store = inject(AppStore);

  machines = signal<Machine[]>([]);
  filteredMachines = signal<Machine[]>([]);
  machineDefinitions = signal<MachineDefinition[]>([]);
  activeFilters = signal<MachineFilterState | null>(null);

  displayedColumns = computed(() => {
    const cols = ['name', 'simulated', 'status', 'category', 'model', 'location'];
    if (this.store.maintenanceEnabled()) {
      cols.push('maintenance');
    }
    cols.push('actions');
    return cols;
  });

  @ViewChild(MatMenuTrigger) contextMenuTrigger!: MatMenuTrigger;
  contextMenuPosition = { x: '0px', y: '0px' };

  constructor() {
    this.loadMachines();
    this.loadMachineDefinitions();
  }

  loadMachines(): void {
    console.debug('[ASSET-DEBUG] loadMachines: Calling assetService.getMachines()');
    this.assetService.getMachines().subscribe(
      (data) => {
        console.debug('[ASSET-DEBUG] loadMachines: Received', data.length, 'machines:', data);
        this.machines.set(data);
        if (this.activeFilters()) {
          this.applyFilters(this.activeFilters()!);
        } else {
          this.filteredMachines.set(data);
        }
      },
      (error) => {
        console.error('[ASSET-DEBUG] loadMachines: Error fetching machines:', error);
      }
    );
  }

  loadMachineDefinitions(): void {
    this.assetService.getMachineDefinitions().subscribe({
      next: (defs) => this.machineDefinitions.set(defs),
      error: (err) => console.error('[ASSET-DEBUG] Error loading machine definitions:', err)
    });
  }

  onFiltersChange(filters: MachineFilterState) {
    this.activeFilters.set(filters);
    this.applyFilters(filters);
  }

  private applyFilters(filters: MachineFilterState): void {
    let filtered = this.machines();

    // 1. Search Filter
    if (filters.search) {
      const search = filters.search.toLowerCase();
      filtered = filtered.filter(m =>
        m.name.toLowerCase().includes(search) ||
        m.machine_category?.toLowerCase().includes(search) ||
        m.model?.toLowerCase().includes(search) ||
        m.manufacturer?.toLowerCase().includes(search)
      );
    }

    // 2. Status Filter
    if (filters.status.length > 0) {
      filtered = filtered.filter(m => filters.status.includes(m.status));
    }

    // 3. Category Filter
    if (filters.categories.length > 0) {
      filtered = filtered.filter(m =>
        m.machine_category && filters.categories.includes(m.machine_category)
      );
    }

    // 4. Simulated Filter
    if (filters.simulated !== null) {
      filtered = filtered.filter(m =>
        (m.is_simulation_override ?? false) === filters.simulated
      );
    }

    // 5. Backend Filter (requires machine definition lookup)
    // For now, skip backend filtering as it requires joining with definitions

    // 6. Sort
    filtered.sort((a, b) => {
      let valA: any = '';
      let valB: any = '';

      switch (filters.sort_by) {
        case 'name':
          valA = a.name.toLowerCase();
          valB = b.name.toLowerCase();
          break;
        case 'category':
          valA = (a.machine_category || '').toLowerCase();
          valB = (b.machine_category || '').toLowerCase();
          break;
        case 'created_at':
          valA = new Date(a.created_at || 0).getTime();
          valB = new Date(b.created_at || 0).getTime();
          break;
        case 'status':
          valA = a.status;
          valB = b.status;
          break;
      }

      if (filters.sort_order === 'asc') {
        return valA > valB ? 1 : -1;
      } else {
        return valA < valB ? 1 : -1;
      }
    });

    this.filteredMachines.set(filtered);
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

  editMachine(_machine: Machine) {
    // TODO: Implement machine editing
  }

  duplicateMachine(_machine: Machine) {
    // TODO: Implement machine duplication
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

