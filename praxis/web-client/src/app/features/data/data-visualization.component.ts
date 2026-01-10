import { Component, ChangeDetectionStrategy, signal, computed, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { FormsModule } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { PraxisSelectComponent, SelectOption } from '@shared/components/praxis-select/praxis-select.component';
import { PraxisAutocompleteComponent } from '@shared/components/praxis-autocomplete/praxis-autocomplete.component';
import { WellSelectorDialogComponent } from '@shared/components/well-selector-dialog/well-selector-dialog.component';
import { FilterHeaderComponent } from '../assets/components/filter-header/filter-header.component';
import { PlotlyModule } from 'angular-plotly.js';
import { interval, Subscription } from 'rxjs';
import { ProtocolService } from '../protocols/services/protocol.service';
import { ProtocolDefinition } from '../protocols/models/protocol.models';

interface TransferDataPoint {
  timestamp: Date;
  well: string;
  volumeTransferred: number;
  cumulativeVolume: number;
  temperature?: number;
  pressure?: number;
}

interface MockRun {
  id: string;
  protocolName: string;
  protocolId: string;
  status: 'completed' | 'running' | 'failed';
  startTime: Date;
  endTime?: Date;
  wellCount: number;
  totalVolume: number;
}

// Seeded random number generator for deterministic data
class SeededRandom {
  private seed: number;

  constructor(seed: number) {
    this.seed = seed;
  }

  next(): number {
    const x = Math.sin(this.seed++) * 10000;
    return x - Math.floor(x);
  }

  range(min: number, max: number): number {
    return min + this.next() * (max - min);
  }
}

// Generate deterministic data based on protocol and run
function generateSeededTransferData(protocolId: string, runId: string): TransferDataPoint[] {
  // Create seed from protocol and run IDs for deterministic output
  const seedValue = hashCode(protocolId + runId);
  const rng = new SeededRandom(seedValue);

  const wells = ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'C1', 'C2', 'C3', 'C4'];
  const data: TransferDataPoint[] = [];
  const baseTime = new Date();
  baseTime.setHours(baseTime.getHours() - 1);

  wells.forEach(well => {
    let cumulative = 0;
    const numPoints = Math.floor(rng.range(8, 15));
    for (let i = 0; i < numPoints; i++) {
      const volume = rng.range(40, 120);
      cumulative += volume;
      data.push({
        timestamp: new Date(baseTime.getTime() + i * 5 * 60 * 1000),
        well,
        volumeTransferred: Math.round(volume * 10) / 10,
        cumulativeVolume: Math.round(cumulative * 10) / 10,
        temperature: 22 + rng.range(0, 3),
        pressure: 101 + rng.range(0, 2)
      });
    }
  });

  return data;
}

function hashCode(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash);
}

// Generate mock run history based on protocols
function generateMockRuns(protocols: ProtocolDefinition[]): MockRun[] {
  const runs: MockRun[] = [];
  const now = new Date();

  protocols.forEach((protocol, pIdx) => {
    // Generate 2-4 runs per protocol
    const numRuns = 2 + (hashCode(protocol.accession_id) % 3);
    for (let i = 0; i < numRuns; i++) {
      const rng = new SeededRandom(hashCode(protocol.accession_id + i.toString()));
      const startOffset = rng.range(1, 72); // 1-72 hours ago
      const duration = rng.range(5, 45); // 5-45 minutes
      const startTime = new Date(now.getTime() - startOffset * 60 * 60 * 1000);
      const endTime = new Date(startTime.getTime() + duration * 60 * 1000);

      runs.push({
        id: `run-${protocol.accession_id.slice(0, 8)}-${i + 1}`,
        protocolName: protocol.name,
        protocolId: protocol.accession_id,
        status: i === 0 && pIdx === 0 ? 'running' : (rng.next() > 0.1 ? 'completed' : 'failed'),
        startTime,
        endTime: i === 0 && pIdx === 0 ? undefined : endTime,
        wellCount: Math.floor(rng.range(6, 96)),
        totalVolume: Math.round(rng.range(500, 5000))
      });
    }
  });

  // Sort by start time descending
  return runs.sort((a, b) => b.startTime.getTime() - a.startTime.getTime());
}

@Component({
  selector: 'app-data-visualization',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatSelectModule,
    MatFormFieldModule,
    MatChipsModule,
    MatIconModule,
    MatButtonModule,
    MatTableModule,
    MatTooltipModule,
    PlotlyModule,
    FormsModule,
    PraxisSelectComponent,
    PraxisAutocompleteComponent,
    FilterHeaderComponent
  ],
  template: `
    <div class="data-page">
      <header class="page-header">
        <h1>Data Visualization</h1>
        <p class="subtitle">Analyze experiment data and transfer volumes</p>
      </header>

      <!-- Filter Header -->
      <app-filter-header
        searchPlaceholder="Filter runs and protocols..."
        [searchValue]="searchQuery()"
        (searchChange)="searchQuery.set($event)"
        (clearFilters)="clearFilters()">
        
        <div class="selector-row" filterContent>
          <div class="protocol-select">
            <label class="text-xs font-medium text-sys-on-surface-variant mb-1 block uppercase tracking-wide">Protocol</label>
            <app-praxis-autocomplete
              label="Protocol"
              [options]="protocolOptions()"
              [(ngModel)]="selectedProtocolId"
              (ngModelChange)="onProtocolChange($event)"
              placeholder="Search protocols..."
            ></app-praxis-autocomplete>
          </div>

          <div class="run-select">
            <label class="text-xs font-medium text-sys-on-surface-variant mb-1 block uppercase tracking-wide">Run</label>
            <app-praxis-autocomplete
              label="Run"
              [options]="runOptions()"
              [(ngModel)]="selectedRunId"
              (ngModelChange)="onRunChange($event)"
              placeholder="Search runs..."
            ></app-praxis-autocomplete>
          </div>
        </div>
      </app-filter-header>

      <!-- Chart Configuration -->
      <mat-card class="config-card">
        <mat-card-content>
          <div class="config-row">
            <div>
              <label class="text-xs font-medium text-sys-on-surface-variant mb-1 block">X-Axis</label>
              <app-praxis-select
                placeholder="X-Axis"
                [options]="xAxisOptions"
                [ngModel]="xAxis()"
                (ngModelChange)="xAxis.set($event)"
              ></app-praxis-select>
            </div>

            <div>
              <label class="text-xs font-medium text-sys-on-surface-variant mb-1 block">Y-Axis</label>
              <app-praxis-select
                placeholder="Y-Axis"
                [options]="yAxisOptions"
                [ngModel]="yAxis()"
                (ngModelChange)="yAxis.set($event)"
              ></app-praxis-select>
            </div>

            <div class="well-filter">
              <button mat-stroked-button (click)="openWellSelector()">
                <mat-icon>grid_view</mat-icon>
                {{ selectedWells().length > 0
                   ? selectedWells().length + ' wells selected'
                   : 'Select Wells' }}
              </button>

              <!-- Show selected wells as preview chips (collapsed if >5) -->
              @if (selectedWells().length > 0 && selectedWells().length <= 5) {
                <mat-chip-set>
                  @for (well of selectedWells(); track well) {
                    <mat-chip (removed)="removeWell(well)">
                      {{ well }}
                      <button matChipRemove>
                        <mat-icon>cancel</mat-icon>
                      </button>
                    </mat-chip>
                  }
                </mat-chip-set>
              }

              @if (selectedWells().length > 5) {
                <span class="text-sm text-sys-on-surface-variant">
                  {{ selectedWells().slice(0, 3).join(', ') }}... and {{ selectedWells().length - 3 }} more
                </span>
              }

              <div class="well-actions">
                <button mat-button (click)="selectAllWells()">All</button>
                <button mat-button (click)="clearWells()">Clear</button>
              </div>
            </div>
          </div>
        </mat-card-content>
      </mat-card>

      <!-- Main Chart -->
      <mat-card class="chart-card">
        <mat-card-header>
          <mat-card-title>{{ chartTitle() }}</mat-card-title>
          @if (selectedRun()) {
            <mat-card-subtitle>
              Run: {{ selectedRun()?.id }} | Started: {{ selectedRun()?.startTime | date:'medium' }}
            </mat-card-subtitle>
          }
        </mat-card-header>
        <mat-card-content>
          <div class="chart-container">
            <plotly-plot
              [data]="chartData()"
              [layout]="chartLayout()"
              [config]="chartConfig"
              [useResizeHandler]="true"
              [style]="{position: 'relative', width: '100%', height: '100%'}">
            </plotly-plot>
          </div>
        </mat-card-content>
      </mat-card>

      <!-- Stats Grid -->
      <div class="stats-grid">
        <mat-card class="stat-card">
          <mat-card-content>
            <mat-icon>science</mat-icon>
            <div class="stat-value">{{ totalVolume() | number:'1.0-0' }} µL</div>
            <div class="stat-label">Total Volume Transferred</div>
          </mat-card-content>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-content>
            <mat-icon>grid_view</mat-icon>
            <div class="stat-value">{{ selectedWells().length }}</div>
            <div class="stat-label">Wells Selected</div>
          </mat-card-content>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-content>
            <mat-icon>timeline</mat-icon>
            <div class="stat-value">{{ filteredData().length }}</div>
            <div class="stat-label">Data Points</div>
          </mat-card-content>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-content>
            <mat-icon>history</mat-icon>
            <div class="stat-value">{{ runs().length }}</div>
            <div class="stat-label">Total Runs</div>
          </mat-card-content>
        </mat-card>
      </div>

      <!-- Run History Table -->
      <mat-card class="history-card">
        <mat-card-header>
          <mat-card-title>Run History</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <table mat-table [dataSource]="filteredRunsTable()" class="run-table">
            <ng-container matColumnDef="status">
              <th mat-header-cell *matHeaderCellDef>Status</th>
              <td mat-cell *matCellDef="let run">
                <mat-icon [class]="'status-' + run.status" [matTooltip]="run.status">
                  {{ run.status === 'completed' ? 'check_circle' : run.status === 'running' ? 'pending' : 'error' }}
                </mat-icon>
              </td>
            </ng-container>

            <ng-container matColumnDef="protocol">
              <th mat-header-cell *matHeaderCellDef>Protocol</th>
              <td mat-cell *matCellDef="let run">{{ run.protocolName }}</td>
            </ng-container>

            <ng-container matColumnDef="startTime">
              <th mat-header-cell *matHeaderCellDef>Started</th>
              <td mat-cell *matCellDef="let run">{{ run.startTime | date:'short' }}</td>
            </ng-container>

            <ng-container matColumnDef="duration">
              <th mat-header-cell *matHeaderCellDef>Duration</th>
              <td mat-cell *matCellDef="let run">
                {{ run.endTime ? formatDuration(run.startTime, run.endTime) : 'Running...' }}
              </td>
            </ng-container>

            <ng-container matColumnDef="wells">
              <th mat-header-cell *matHeaderCellDef>Wells</th>
              <td mat-cell *matCellDef="let run">{{ run.wellCount }}</td>
            </ng-container>

            <ng-container matColumnDef="volume">
              <th mat-header-cell *matHeaderCellDef>Volume</th>
              <td mat-cell *matCellDef="let run">{{ run.totalVolume | number:'1.0-0' }} µL</td>
            </ng-container>

            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef></th>
              <td mat-cell *matCellDef="let run">
                <button mat-icon-button matTooltip="View Details" (click)="selectRun(run)">
                  <mat-icon>visibility</mat-icon>
                </button>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns;"
                [class.selected-row]="row.id === selectedRunId"
                (click)="selectRun(row)"></tr>
          </table>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .data-page {
      padding: 24px;
      max-width: 1400px;
      margin: 0 auto;
    }

    .page-header {
      margin-bottom: 24px;
    }

    .page-header h1 {
      margin: 0;
      font-size: 2rem;
      font-weight: 500;
    }

    .subtitle {
      margin: 4px 0 0;
      color: var(--sys-on-surface-variant);
    }

    .selector-card {
      margin-bottom: 16px;
    }

    .selector-row {
      display: flex;
      gap: 16px;
      align-items: center;
      flex-wrap: wrap;
    }

    .protocol-select {
      min-width: 250px;
    }

    .run-select {
      min-width: 350px;
      flex: 1;
    }

    .run-option {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .run-option mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
    }

    .config-card {
      margin-bottom: 24px;
    }

    .config-row {
      display: flex;
      gap: 16px;
      align-items: center;
      flex-wrap: wrap;
    }

    .config-row mat-form-field {
      min-width: 180px;
    }

    .well-filter {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      background: var(--sys-surface-container-low);
      padding: 12px 16px;
      border-radius: 12px;
      border: 1px solid var(--sys-outline-variant);
    }

    .well-actions {
      display: flex;
      gap: 4px;
      margin-left: auto;
    }

    .filter-label {
      font-size: 0.9rem;
      color: var(--sys-on-surface-variant);
      white-space: nowrap;
    }

    mat-chip {
      --mdc-chip-label-text-size: 12px;
      height: 32px !important;
    }

    .chart-card {
      margin-bottom: 24px;
    }

    .chart-container {
      width: 100%;
      height: 450px;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }

    .stat-card mat-card-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: 24px;
    }

    .stat-card mat-icon {
      font-size: 32px;
      width: 32px;
      height: 32px;
      color: var(--sys-primary);
      margin-bottom: 8px;
    }

    .stat-value {
      font-size: 1.5rem;
      font-weight: 600;
      color: var(--sys-on-surface);
    }

    .stat-label {
      font-size: 0.85rem;
      color: var(--sys-on-surface-variant);
    }

    .history-card {
      margin-top: 24px;
    }

    .run-table {
      width: 100%;
    }

    .run-table tr.selected-row {
      background: var(--sys-surface-variant);
    }

    .run-table tr:hover {
      background: var(--sys-surface-container-high);
      cursor: pointer;
    }

    .status-completed {
      color: #4caf50;
    }

    .status-running {
      color: #ff9800;
    }

    .status-failed {
      color: #f44336;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DataVisualizationComponent implements OnInit, OnDestroy {
  private protocolService = inject(ProtocolService);
  private dialog = inject(MatDialog);

  // Table columns
  displayedColumns = ['status', 'protocol', 'startTime', 'duration', 'wells', 'volume', 'actions'];

  // Well configuration
  allWells = Array.from({ length: 96 }, (_, i) => {
    const row = String.fromCharCode(65 + Math.floor(i / 12));
    const col = (i % 12) + 1;
    return `${row}${col}`;
  });
  selectedWells = signal<string[]>(['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4']); // Initial selection

  // Chart configuration
  xAxis = signal<string>('timestamp');
  yAxis = signal<string>('volumeTransferred');

  // Selection state
  selectedProtocolId = '';
  selectedRunId = '';
  searchQuery = signal('');

  // Data signals
  protocols = signal<ProtocolDefinition[]>([]);
  runs = signal<MockRun[]>([]);
  private transferData = signal<TransferDataPoint[]>([]);
  private updateSubscription?: Subscription;

  protocolOptions = computed(() => {
    const protos = this.protocols();
    return [
      { label: 'All Protocols', value: '' },
      ...protos.map(p => ({ label: p.name, value: p.accession_id }))
    ];
  });

  runOptions = computed(() => {
    return this.filteredRuns().map(r => ({
      label: `${r.protocolName} - ${r.startTime.toLocaleString()}`,
      value: r.id,
      icon: r.status === 'completed' ? 'check_circle' : r.status === 'running' ? 'pending' : 'error'
    }));
  });

  readonly xAxisOptions: SelectOption[] = [
    { label: 'Time', value: 'timestamp' },
    { label: 'Well', value: 'well' }
  ];

  readonly yAxisOptions: SelectOption[] = [
    { label: 'Volume Transferred (µL)', value: 'volumeTransferred' },
    { label: 'Cumulative Volume (µL)', value: 'cumulativeVolume' },
    { label: 'Temperature (°C)', value: 'temperature' },
    { label: 'Pressure (kPa)', value: 'pressure' }
  ];

  chartConfig = {
    displayModeBar: true,
    responsive: true,
    modeBarButtonsToRemove: ['lasso2d', 'select2d']
  };

  // Computed: filter runs by selected protocol
  filteredRuns = computed(() => {
    const runs = this.runs();
    if (!this.selectedProtocolId) return runs;
    return runs.filter(r => r.protocolId === this.selectedProtocolId);
  });

  filteredRunsTable = computed(() => {
    const runs = this.filteredRuns();
    const q = this.searchQuery().toLowerCase();
    if (!q) return runs;
    return runs.filter(r => 
      r.protocolName.toLowerCase().includes(q) || 
      r.id.toLowerCase().includes(q) ||
      r.status.toLowerCase().includes(q)
    );
  });

  // Computed: get selected run object
  selectedRun = computed(() => {
    return this.runs().find(r => r.id === this.selectedRunId) || null;
  });

  ngOnInit() {
    // Load protocols first to populate filter options
    this.protocolService.getProtocols().subscribe({
      next: (protocols) => {
        this.protocols.set(protocols);
      },
      error: (e) => console.warn('Failed to load protocols', e)
    });

    // Load runs (from seeded DB or backend)
    this.protocolService.getRuns().subscribe({
      next: (runs) => {
        if (runs && runs.length > 0) {
          // Map backend/SQLite run objects to MockRun interface for visualization
          const mappedRuns: MockRun[] = runs.map(r => {
            const name = r.name || r.protocol_name || 'Unknown Protocol';
            // Infer well count based on protocol name/type
            let wellCount = 96;
            if (name.includes('Simple') || name.includes('Transfer')) wellCount = 12;
            
            return {
              id: r.accession_id,
              protocolName: name,
              protocolId: r.top_level_protocol_definition_accession_id || r.protocol_definition_accession_id || 'unknown',
              status: (r.status || 'failed').toLowerCase() as 'completed' | 'running' | 'failed',
              startTime: r.started_at ? new Date(r.started_at) : new Date(r.created_at),
              endTime: r.completed_at ? new Date(r.completed_at) : undefined,
              wellCount: wellCount, 
              totalVolume: 1000 // Default for seeded runs
            };
          });
          
          this.runs.set(mappedRuns);

          // Auto-select first run
          if (mappedRuns.length > 0) {
            this.selectedRunId = mappedRuns[0].id;
            this.loadRunData(mappedRuns[0]);
          }
        } else {
          // Fallback to client-side mock generation if no runs found (e.g. empty DB)
          this.generateFallbackData();
        }
      },
      error: (e) => {
        console.warn('Failed to load runs, using fallback', e);
        this.generateFallbackData();
      }
    });

    // Simulate live data updates for running experiments
    this.updateSubscription = interval(5000).subscribe(() => {
      const run = this.selectedRun();
      if (run?.status === 'running') {
        this.addLiveDataPoint();
      }
    });
  }

  private generateFallbackData() {
    // Original mock generation logic as fallback
    if (this.protocols().length === 0) {
      const fallbackProtocols: ProtocolDefinition[] = [
        { accession_id: 'proto-001', name: 'Simple Transfer', is_top_level: true, version: '1.0', parameters: [], assets: [] },
        { accession_id: 'proto-002', name: 'Serial Dilution', is_top_level: true, version: '1.0', parameters: [], assets: [] },
        { accession_id: 'proto-003', name: 'Plate Replication', is_top_level: true, version: '1.0', parameters: [], assets: [] }
      ];
      this.protocols.set(fallbackProtocols);
    }
    
    const mockRuns = generateMockRuns(this.protocols());
    this.runs.set(mockRuns);
    if (mockRuns.length > 0) {
      this.selectedRunId = mockRuns[0].id;
      this.loadRunData(mockRuns[0]);
    }
  }

  ngOnDestroy() {
    this.updateSubscription?.unsubscribe();
  }

  onProtocolChange(protocolId: string) {
    this.selectedProtocolId = protocolId;
    // Auto-select first run of filtered list
    const filtered = this.filteredRuns();
    if (filtered.length > 0) {
      this.selectedRunId = filtered[0].id;
      this.loadRunData(filtered[0]);
    }
  }

  onRunChange(runId: string) {
    const run = this.runs().find(r => r.id === runId);
    if (run) {
      this.loadRunData(run);
    }
  }

  selectRun(run: MockRun) {
    this.selectedRunId = run.id;
    this.loadRunData(run);
  }

  clearFilters() {
    this.searchQuery.set('');
    this.selectedProtocolId = '';
    // Reset to all runs
    const allRuns = this.runs();
    if (allRuns.length > 0) {
        this.selectRun(allRuns[0]);
    }
  }

  private loadRunData(run: MockRun) {
    // Generate deterministic data for this run
    const data = generateSeededTransferData(run.protocolId, run.id);
    this.transferData.set(data);
  }

  private addLiveDataPoint() {
    const run = this.selectedRun();
    if (!run) return;

    const rng = new SeededRandom(Date.now());
    const newData = [...this.transferData()];
    const latestTime = new Date();

    this.selectedWells().slice(0, 3).forEach(well => {
      const volume = rng.range(40, 120);
      const lastPoint = newData.filter(d => d.well === well).pop();
      newData.push({
        timestamp: latestTime,
        well,
        volumeTransferred: Math.round(volume * 10) / 10,
        cumulativeVolume: (lastPoint?.cumulativeVolume || 0) + volume,
        temperature: 22 + rng.range(0, 3),
        pressure: 101 + rng.range(0, 2)
      });
    });
    this.transferData.set(newData);
  }

  formatDuration(start: Date, end: Date): string {
    const diffMs = end.getTime() - start.getTime();
    const minutes = Math.floor(diffMs / 60000);
    const seconds = Math.floor((diffMs % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  }

  filteredData = computed(() => {
    return this.transferData().filter(d => this.selectedWells().includes(d.well));
  });

  totalVolume = computed(() => {
    return this.filteredData().reduce((sum, d) => sum + d.volumeTransferred, 0);
  });

  chartTitle = computed(() => {
    const yLabels: Record<string, string> = {
      'volumeTransferred': 'Volume Transferred',
      'cumulativeVolume': 'Cumulative Volume',
      'temperature': 'Temperature',
      'pressure': 'Pressure'
    };
    const xLabels: Record<string, string> = {
      'timestamp': 'Time',
      'well': 'Well'
    };
    return `${yLabels[this.yAxis()]} over ${xLabels[this.xAxis()]}`;
  });

  chartData = computed(() => {
    const data = this.filteredData();
    const wells = [...new Set(data.map(d => d.well))];

    if (this.xAxis() === 'well') {
      // Bar chart grouped by well
      const grouped = wells.map(well => {
        const wellData = data.filter(d => d.well === well);
        const total = wellData.reduce((sum, d) => sum + (d as Record<string, any>)[this.yAxis()], 0);
        return { well, value: total / wellData.length };
      });

      return [{
        x: grouped.map(g => g.well),
        y: grouped.map(g => g.value),
        type: 'bar',
        marker: { color: '#00e5ff' }
      }];
    }

    // Line chart over time, one trace per well
    return wells.map((well, i) => {
      const wellData = data.filter(d => d.well === well).sort((a, b) =>
        a.timestamp.getTime() - b.timestamp.getTime()
      );
      const colors = ['#00e5ff', '#ff6b6b', '#4ecdc4', '#ffd93d', '#c3aed6', '#667eea', '#f093fb', '#a8e6cf', '#fdcb6e'];

      return {
        x: wellData.map(d => d.timestamp.toLocaleTimeString()),
        y: wellData.map(d => (d as Record<string, any>)[this.yAxis()]),
        type: 'scatter',
        mode: 'lines+markers',
        name: well,
        line: { color: colors[i % colors.length] },
        marker: { color: colors[i % colors.length] }
      };
    });
  });

  chartLayout = computed(() => {
    const yLabels: Record<string, string> = {
      'volumeTransferred': 'Volume (µL)',
      'cumulativeVolume': 'Cumulative Volume (µL)',
      'temperature': 'Temperature (°C)',
      'pressure': 'Pressure (kPa)'
    };

    return {
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      xaxis: {
        gridcolor: 'rgba(128,128,128,0.2)',
        tickfont: { color: 'var(--sys-on-surface)' },
        title: { text: this.xAxis() === 'timestamp' ? 'Time' : 'Well', font: { color: 'var(--sys-on-surface)' } }
      },
      yaxis: {
        gridcolor: 'rgba(128,128,128,0.2)',
        tickfont: { color: 'var(--sys-on-surface)' },
        title: { text: yLabels[this.yAxis()], font: { color: 'var(--sys-on-surface)' } }
      },
      margin: { t: 20, r: 30, l: 60, b: 50 },
      autosize: true,
      showlegend: this.selectedWells().length > 1,
      legend: {
        font: { color: 'var(--sys-on-surface)' }
      }
    };
  });

  toggleWell(well: string) {
    const current = this.selectedWells();
    if (current.includes(well)) {
      this.selectedWells.set(current.filter(w => w !== well));
    } else {
      this.selectedWells.set([...current, well]);
    }
  }

  removeWell(well: string) {
    this.selectedWells.update(wells => wells.filter(w => w !== well));
  }

  openWellSelector() {
    const dialogRef = this.dialog.open(WellSelectorDialogComponent, {
      data: {
        plateType: '96',
        initialSelection: this.selectedWells(),
        mode: 'multi',
        title: 'Select Wells for Visualization'
      },
      width: '800px',
      maxHeight: '90vh'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result?.confirmed) {
        this.selectedWells.set(result.wells);
      }
    });
  }

  selectAllWells() {
    this.selectedWells.set([...this.allWells]);
  }

  clearWells() {
    this.selectedWells.set([]);
  }
}
