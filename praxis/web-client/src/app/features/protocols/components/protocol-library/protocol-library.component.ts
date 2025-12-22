import { Component, ChangeDetectionStrategy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { ProtocolService } from '../../services/protocol.service';
import { ProtocolDefinition } from '../../models/protocol.models';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged, startWith, finalize } from 'rxjs/operators';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner'; // Import MatProgressSpinnerModule

@Component({
  selector: 'app-protocol-library',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatInputModule,
    MatFormFieldModule,
    MatDialogModule,
    ReactiveFormsModule,
    MatProgressSpinnerModule // Add MatProgressSpinnerModule
  ],
  template: `
    <div class="protocol-library-container">
      <div class="header">
        <h1>Protocol Library</h1>
        <button mat-flat-button color="primary" (click)="uploadProtocol()" [disabled]="isLoading()">
          <mat-icon>upload</mat-icon>
          Upload Protocol
        </button>
      </div>

      <mat-form-field appearance="outline" class="filter-field">
        <mat-label>Filter Protocols</mat-label>
        <input matInput [formControl]="filterControl">
        <mat-icon matSuffix>search</mat-icon>
      </mat-form-field>

      <div class="table-container">
        <div *ngIf="isLoading()" class="spinner-overlay"><mat-spinner diameter="40"></mat-spinner></div>
        <table mat-table [dataSource]="filteredProtocols()" class="mat-elevation-z2">
          <!-- Name Column -->
          <ng-container matColumnDef="name">
            <th mat-header-cell *matHeaderCellDef> Name </th>
            <td mat-cell *matCellDef="let protocol">
              <div class="protocol-name">
                {{ protocol.name }}
                <span *ngIf="protocol.is_top_level" class="top-level-badge">Top Level</span>
              </div>
            </td>
          </ng-container>

          <!-- Version Column -->
          <ng-container matColumnDef="version">
            <th mat-header-cell *matHeaderCellDef> Version </th>
            <td mat-cell *matCellDef="let protocol"> {{ protocol.version }} </td>
          </ng-container>

          <!-- Description Column -->
          <ng-container matColumnDef="description">
            <th mat-header-cell *matHeaderCellDef> Description </th>
            <td mat-cell *matCellDef="let protocol"> {{ protocol.description || 'N/A' }} </td>
          </ng-container>

          <!-- Category Column -->
          <ng-container matColumnDef="category">
            <th mat-header-cell *matHeaderCellDef> Category </th>
            <td mat-cell *matCellDef="let protocol"> {{ protocol.category || 'N/A' }} </td>
          </ng-container>

          <!-- Actions Column -->
          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef> Actions </th>
            <td mat-cell *matCellDef="let protocol">
              <button mat-icon-button color="primary" matTooltip="View Details" (click)="viewDetails(protocol)">
                <mat-icon>info</mat-icon>
              </button>
              <button mat-icon-button color="accent" matTooltip="Run Protocol" (click)="runProtocol(protocol)">
                <mat-icon>play_arrow</mat-icon>
              </button>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>

          <tr class="mat-row" *matNoDataRow>
            <td class="mat-cell" colspan="5">No protocols matching the filter "{{ filterControl.value }}"</td>
          </tr>
        </table>
      </div>
    </div>
  `,
  styles: [`
    .protocol-library-container {
      padding: 16px;
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }

    h1 {
      margin: 0;
      font-size: 1.5rem;
      font-weight: 500;
    }

    .filter-field {
      width: 100%;
      margin-bottom: 16px;
    }

    .table-container {
      position: relative;
      flex: 1;
      overflow: auto; /* For scrollable table if content exceeds height */
    }

    .mat-elevation-z2 {
      width: 100%;
    }

    .protocol-name {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .top-level-badge {
      background-color: var(--mat-sys-color-tertiary-container);
      color: var(--mat-sys-color-on-tertiary-container);
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.75em;
      font-weight: bold;
    }

    .mat-no-data-row {
      text-align: center;
      font-style: italic;
      color: var(--mat-sys-color-on-surface-variant);
    }

    .spinner-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(255, 255, 255, 0.8);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 10;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProtocolLibraryComponent {
  private protocolService = inject(ProtocolService);
  private router = inject(Router);
  private dialog = inject(MatDialog);

  protocols = signal<ProtocolDefinition[]>([]);
  filteredProtocols = signal<ProtocolDefinition[]>([]);
  filterControl = new FormControl('', { nonNullable: true });
  isLoading = signal(false); // New loading signal

  displayedColumns: string[] = ['name', 'version', 'description', 'category', 'actions'];

  constructor() {
    this.loadProtocols();

    this.filterControl.valueChanges.pipe(
      takeUntilDestroyed(),
      debounceTime(300),
      distinctUntilChanged(),
      startWith('')
    ).subscribe(filterValue => {
      this.applyFilter(filterValue);
    });
  }

  loadProtocols(): void { // Made public for potential parent component refresh
    this.isLoading.set(true); // Set loading true before API call
    this.protocolService.getProtocols().pipe(
      finalize(() => this.isLoading.set(false)) // Set loading false after API call completes
    ).subscribe(
      (data) => {
        this.protocols.set(data);
        this.applyFilter(this.filterControl.value);
      },
      (error) => {
        console.error('Error fetching protocols:', error);
        // TODO: Integrate global error handling
      }
    );
  }

  private applyFilter(filterValue: string): void {
    const lowerCaseFilter = filterValue.toLowerCase();
    this.filteredProtocols.set(
      this.protocols().filter(protocol =>
        protocol.name.toLowerCase().includes(lowerCaseFilter) ||
        protocol.description?.toLowerCase().includes(lowerCaseFilter) ||
        protocol.category?.toLowerCase().includes(lowerCaseFilter)
      )
    );
  }

  viewDetails(protocol: ProtocolDefinition) {
    this.router.navigate(['/protocols', protocol.accession_id]);
  }

  runProtocol(protocol: ProtocolDefinition) {
    this.router.navigate(['/run'], { queryParams: { protocolId: protocol.accession_id } });
  }

  uploadProtocol() {
    if (this.isLoading()) return;

    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.py';
    fileInput.onchange = (event: any) => {
      const file = event.target.files[0];
      if (file) {
        this.isLoading.set(true); // Set loading true before API call
        this.protocolService.uploadProtocol(file).pipe(
          finalize(() => this.isLoading.set(false)) // Set loading false after API call completes
        ).subscribe({
          next: (response) => {
            console.log('Upload successful', response);
            this.loadProtocols(); // Refresh list
          },
          error: (err) => console.error('Upload failed', err)
        });
      }
    };
    fileInput.click();
  }
}