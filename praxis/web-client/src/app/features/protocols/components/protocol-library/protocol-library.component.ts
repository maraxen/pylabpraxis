import { Component, ChangeDetectionStrategy, inject, signal, computed } from '@angular/core';

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
import { FormControl, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { FilterHeaderComponent } from '../../../assets/components/filter-header/filter-header.component';
import { PraxisSelectComponent, SelectOption } from '../../../../shared/components/praxis-select/praxis-select.component';

import { ProtocolDetailDialogComponent } from '../protocol-detail-dialog/protocol-detail-dialog.component';

@Component({
  selector: 'app-protocol-library',
  standalone: true,
  imports: [
    MatTableModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatInputModule,
    MatFormFieldModule,
    MatDialogModule,
    ReactiveFormsModule,
    FormsModule,
    MatProgressSpinnerModule,
    FilterHeaderComponent,
    PraxisSelectComponent
  ],
  template: `
    <div class="p-6 max-w-screen-2xl mx-auto h-full flex flex-col">
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 class="text-3xl font-bold text-sys-text-primary mb-1">Protocol Library</h1>
          <p class="text-sys-text-secondary">Manage and execute your experimental protocols</p>
        </div>
        <button mat-flat-button class="!bg-gradient-to-br !from-primary !to-primary-dark !text-white !rounded-xl !px-6 !py-6 !font-semibold shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all hover:-translate-y-0.5" (click)="uploadProtocol()" [disabled]="isLoading()" data-tour-id="import-protocol-btn">
          <mat-icon>upload</mat-icon>
          Upload Protocol
        </button>
      </div>

      <div class="bg-surface border border-[var(--theme-border)] rounded-3xl overflow-hidden backdrop-blur-xl flex flex-col flex-1 min-h-0 shadow-xl">
        <app-filter-header
          searchPlaceholder="Search protocols..."
          [searchValue]="searchQuery()"
          [filterCount]="filterCount()"
          (searchChange)="onSearchChange($event)"
          (clearFilters)="clearFilters()">

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4" filterContent>
            <!-- Category Filter -->
            <div class="flex flex-col gap-1">
              <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide px-1">Category</label>
              <app-praxis-select
                [options]="categoryOptions()"
                [ngModel]="selectedCategory()"
                (ngModelChange)="selectedCategory.set($event)"
                placeholder="All Categories">
              </app-praxis-select>
            </div>

            <!-- Type Filter -->
            <div class="flex flex-col gap-1">
              <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide px-1">Type</label>
              <app-praxis-select
                [options]="typeOptions"
                [ngModel]="selectedType()"
                (ngModelChange)="selectedType.set($event)"
                placeholder="All Types">
              </app-praxis-select>
            </div>

            <!-- Status Filter -->
            <div class="flex flex-col gap-1">
              <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide px-1">Status</label>
              <app-praxis-select
                [options]="statusOptions"
                [ngModel]="selectedStatus()"
                (ngModelChange)="selectedStatus.set($event)"
                placeholder="All Statuses">
              </app-praxis-select>
            </div>
          </div>

        </app-filter-header>

        <div class="flex-1 overflow-auto bg-[var(--mat-sys-surface-variant)] relative">
           @if (isLoading()) {
             <div class="absolute inset-0 flex items-center justify-center bg-white/50 dark:bg-black/50 z-10 backdrop-blur-sm">
               <mat-spinner diameter="40"></mat-spinner>
             </div>
           }
           
          @if (filteredProtocols().length > 0) {
            <table mat-table [dataSource]="filteredProtocols()" class="!bg-transparent w-full" data-tour-id="protocol-table">
              <!-- Name Column -->
              <ng-container matColumnDef="name">
                <th mat-header-cell *matHeaderCellDef class="!bg-surface-elevated/50 !text-sys-text-secondary !font-medium !text-sm border-b !border-[var(--theme-border)] px-6 py-4"> Name </th>
                <td mat-cell *matCellDef="let protocol" class="!text-sys-text-primary border-b !border-[var(--theme-border)] px-6 py-4">
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
                <th mat-header-cell *matHeaderCellDef class="!bg-surface-elevated/50 !text-sys-text-secondary !font-medium !text-sm border-b !border-[var(--theme-border)] px-6 py-4"> Version </th>
                <td mat-cell *matCellDef="let protocol" class="!text-sys-text-secondary border-b !border-[var(--theme-border)] px-6 py-4"> 
                  <span class="font-mono text-xs bg-[var(--theme-surface-elevated)] px-2 py-1 rounded text-sys-text-secondary">{{ protocol.version }}</span>
                </td>
              </ng-container>

              <!-- Description Column -->
              <ng-container matColumnDef="description">
                <th mat-header-cell *matHeaderCellDef class="!bg-surface-elevated/50 !text-sys-text-secondary !font-medium !text-sm border-b !border-[var(--theme-border)] px-6 py-4"> Description </th>
                <td mat-cell *matCellDef="let protocol" class="!text-sys-text-secondary opacity-70 border-b !border-[var(--theme-border)] px-6 py-4 max-w-md truncate"> {{ protocol.description || 'No description' }} </td>
              </ng-container>

              <!-- Category Column -->
              <ng-container matColumnDef="category">
                <th mat-header-cell *matHeaderCellDef class="!bg-surface-elevated/50 !text-sys-text-secondary !font-medium !text-sm border-b !border-[var(--theme-border)] px-6 py-4"> Category </th>
                <td mat-cell *matCellDef="let protocol" class="!text-sys-text-secondary border-b !border-[var(--theme-border)] px-6 py-4">
                  @if (protocol.category) {
                    <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-400/10 text-blue-300 border border-blue-400/20">
                      {{ protocol.category }}
                    </span>
                  } @else {
                    <span class="text-sys-text-tertiary italic">Uncategorized</span>
                  }
                </td>
              </ng-container>

              <!-- Actions Column -->
              <ng-container matColumnDef="actions">
                <th mat-header-cell *matHeaderCellDef class="!bg-surface-elevated/50 !text-sys-text-secondary !font-medium !text-sm border-b !border-[var(--theme-border)] px-6 py-4 text-right"> Actions </th>
                <td mat-cell *matCellDef="let protocol" class="border-b !border-[var(--theme-border)] px-6 py-4">
                  <div class="flex justify-end gap-2">
                    <button mat-icon-button class="!text-green-400 hover:!bg-green-400/20 transition-all" matTooltip="Run Protocol" (click)="$event.stopPropagation(); runProtocol(protocol)">
                      <mat-icon>play_arrow</mat-icon>
                    </button>
                  </div>
                </td>
              </ng-container>

              <tr mat-header-row *matHeaderRowDef="displayedColumns" class="!h-12"></tr>
              <tr mat-row *matRowDef="let row; columns: displayedColumns;" (click)="viewDetails(row)" class="hover:bg-[var(--mat-sys-surface-variant)] transition-colors cursor-pointer !h-16"></tr>
            </table>
          } @else {
            <div class="flex flex-col items-center justify-center h-full text-sys-text-tertiary py-20">
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
  searchQuery = signal('');
  isLoading = signal(false);

  // Filter Signals
  selectedCategory = signal<string | null>(null);
  selectedType = signal<string>('all');
  selectedStatus = signal<string>('all');

  // Filter Options
  categoryOptions = computed<SelectOption[]>(() => {
    const cats = new Set<string>();
    this.protocols().forEach(p => {
      if (p.category) cats.add(p.category);
    });
    return [
      { label: 'All Categories', value: null },
      ...Array.from(cats).sort().map(c => ({ label: c, value: c }))
    ];
  });

  typeOptions: SelectOption[] = [
    { label: 'All Types', value: 'all' },
    { label: 'Top Level', value: 'top_level' },
    { label: 'Sub-Protocol', value: 'sub' }
  ];

  statusOptions: SelectOption[] = [
    { label: 'All Statuses', value: 'all' },
    { label: 'Passed', value: 'passed' },
    { label: 'Failed', value: 'failed' },
    { label: 'Not Simulated', value: 'none' }
  ];

  filterCount = computed(() => {
    let count = 0;
    if (this.selectedCategory() !== null) count++;
    if (this.selectedType() !== 'all') count++;
    if (this.selectedStatus() !== 'all') count++;
    return count;
  });

  filteredProtocols = computed(() => {
    const query = this.searchQuery().toLowerCase();
    const category = this.selectedCategory();
    const type = this.selectedType();
    const status = this.selectedStatus();

    return this.protocols().filter(protocol => {
      // Search filter
      const matchesSearch = !query ||
        protocol.name.toLowerCase().includes(query) ||
        protocol.description?.toLowerCase().includes(query) ||
        protocol.category?.toLowerCase().includes(query);

      // Category filter
      const matchesCategory = !category || protocol.category === category;

      // Type filter
      const matchesType = type === 'all' ||
        (type === 'top_level' && protocol.is_top_level) ||
        (type === 'sub' && !protocol.is_top_level);

      // Status filter
      let matchesStatus = true;
      if (status === 'passed') {
        matchesStatus = protocol.simulation_result?.passed === true;
      } else if (status === 'failed') {
        matchesStatus = !!protocol.simulation_result && protocol.simulation_result.passed === false;
      } else if (status === 'none') {
        matchesStatus = !protocol.simulation_result;
      }

      return matchesSearch && matchesCategory && matchesType && matchesStatus;
    });
  });

  displayedColumns: string[] = ['name', 'version', 'description', 'category', 'actions'];

  constructor() {
    this.loadProtocols();
  }

  loadProtocols(): void {
    this.isLoading.set(true);
    this.protocolService.getProtocols().pipe(
      finalize(() => this.isLoading.set(false))
    ).subscribe(
      (data) => {
        this.protocols.set(data);
      },
      (error) => {
        console.error('Error fetching protocols:', error);
      }
    );
  }

  viewDetails(protocol: ProtocolDefinition) {
    this.dialog.open(ProtocolDetailDialogComponent, {
      data: { protocol },
      width: '700px',
      maxWidth: '90vw',
      maxHeight: '90vh',
      panelClass: 'praxis-dialog-panel'
    });
  }

  runProtocol(protocol: ProtocolDefinition) {
    this.router.navigate(['/run'], { queryParams: { protocolId: protocol.accession_id } });
  }

  onSearchChange(value: string) {
    this.searchQuery.set(value);
  }

  clearFilters() {
    this.selectedCategory.set(null);
    this.selectedType.set('all');
    this.selectedStatus.set('all');
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
          next: () => {
            this.loadProtocols(); // Refresh list
          },
          error: (err) => console.error('[ProtocolLibrary] Upload failed:', err)
        });
      }
    };
    fileInput.click();
  }
}
