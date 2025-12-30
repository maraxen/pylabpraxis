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
    <div class="p-6 max-w-screen-2xl mx-auto h-full flex flex-col">
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 class="text-3xl font-bold text-white mb-1">Protocol Library</h1>
          <p class="text-white/70">Manage and execute your experimental protocols</p>
        </div>
        <button mat-flat-button class="!bg-gradient-to-br !from-primary !to-primary-dark !text-white !rounded-xl !px-6 !py-6 !font-semibold shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all hover:-translate-y-0.5" (click)="uploadProtocol()" [disabled]="isLoading()">
          <mat-icon>upload</mat-icon>
          Upload Protocol
        </button>
      </div>

      <div class="bg-surface border border-white/10 rounded-3xl overflow-hidden backdrop-blur-xl flex flex-col flex-1 min-h-0 shadow-xl">
        <div class="p-4 border-b border-white/10 bg-white/5 flex gap-4 items-center">
          <mat-icon class="text-white/50">search</mat-icon>
          <input 
            [formControl]="filterControl" 
            placeholder="Search protocols..." 
            class="bg-transparent border-none outline-none text-white placeholder-white/30 w-full h-full text-lg"
          >
          @if (isLoading()) {
            <mat-spinner diameter="24" class="mr-2"></mat-spinner>
          }
        </div>

        <div class="flex-1 overflow-auto bg-white/5 relative">
           
          @if (filteredProtocols().length > 0) {
            <table mat-table [dataSource]="filteredProtocols()" class="!bg-transparent w-full">
              <!-- Name Column -->
              <ng-container matColumnDef="name">
                <th mat-header-cell *matHeaderCellDef class="!bg-surface-elevated/50 !text-white/70 !font-medium !text-sm border-b !border-white/10 px-6 py-4"> Name </th>
                <td mat-cell *matCellDef="let protocol" class="!text-white border-b !border-white/5 px-6 py-4">
                  <div class="flex flex-col">
                    <div class="flex items-center gap-2">
                      <span class="font-medium text-base">{{ protocol.name }}</span>
                      @if (protocol.is_top_level) {
                        <span class="px-2 py-0.5 rounded-md bg-primary/20 text-primary text-[10px] font-bold uppercase tracking-wider border border-primary/20">Top Level</span>
                      }
                    </div>
                  </div>
                </td>
              </ng-container>

              <!-- Version Column -->
              <ng-container matColumnDef="version">
                <th mat-header-cell *matHeaderCellDef class="!bg-surface-elevated/50 !text-white/70 !font-medium !text-sm border-b !border-white/10 px-6 py-4"> Version </th>
                <td mat-cell *matCellDef="let protocol" class="!text-white/70 border-b !border-white/5 px-6 py-4"> 
                  <span class="font-mono text-xs bg-white/10 px-2 py-1 rounded text-white/80">{{ protocol.version }}</span>
                </td>
              </ng-container>

              <!-- Description Column -->
              <ng-container matColumnDef="description">
                <th mat-header-cell *matHeaderCellDef class="!bg-surface-elevated/50 !text-white/70 !font-medium !text-sm border-b !border-white/10 px-6 py-4"> Description </th>
                <td mat-cell *matCellDef="let protocol" class="!text-white/50 border-b !border-white/5 px-6 py-4 max-w-md truncate"> {{ protocol.description || 'No description' }} </td>
              </ng-container>

              <!-- Category Column -->
              <ng-container matColumnDef="category">
                <th mat-header-cell *matHeaderCellDef class="!bg-surface-elevated/50 !text-white/70 !font-medium !text-sm border-b !border-white/10 px-6 py-4"> Category </th>
                <td mat-cell *matCellDef="let protocol" class="!text-white/70 border-b !border-white/5 px-6 py-4">
                  @if (protocol.category) {
                    <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-400/10 text-blue-300 border border-blue-400/20">
                      {{ protocol.category }}
                    </span>
                  } @else {
                    <span class="text-white/20 italic">Uncategorized</span>
                  }
                </td>
              </ng-container>

              <!-- Actions Column -->
              <ng-container matColumnDef="actions">
                <th mat-header-cell *matHeaderCellDef class="!bg-surface-elevated/50 !text-white/70 !font-medium !text-sm border-b !border-white/10 px-6 py-4 text-right"> Actions </th>
                <td mat-cell *matCellDef="let protocol" class="border-b !border-white/5 px-6 py-4">
                  <div class="flex justify-end gap-2">
                    <button mat-icon-button class="!text-white/60 hover:!text-primary transition-colors" matTooltip="View Details" (click)="viewDetails(protocol)">
                      <mat-icon>info</mat-icon>
                    </button>
                    <button mat-icon-button class="!text-green-400 hover:!bg-green-400/20 transition-all" matTooltip="Run Protocol" (click)="runProtocol(protocol)">
                      <mat-icon>play_arrow</mat-icon>
                    </button>
                  </div>
                </td>
              </ng-container>

              <tr mat-header-row *matHeaderRowDef="displayedColumns" class="!h-12"></tr>
              <tr mat-row *matRowDef="let row; columns: displayedColumns;" class="hover:bg-white/5 transition-colors cursor-default !h-16"></tr>
            </table>
          } @else {
            <div class="flex flex-col items-center justify-center h-full text-white/40 py-20">
              <mat-icon class="!w-16 !h-16 !text-[64px] opacity-20 mb-4">science</mat-icon>
              <p class="text-lg font-medium">No protocols found</p>
              <p class="text-sm opacity-60">Try adjusting your search or upload a new protocol</p>
            </div>
          }
        </div>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      height: 100%;
    }
    
    /* Mat Table Overrides for Transparency */
    ::ng-deep .mat-mdc-table {
      background: transparent !important;
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