import { Component, ChangeDetectionStrategy, signal, computed, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule } from '@angular/forms';
import { PlotlyModule } from 'angular-plotly.js';
import { interval, Subscription } from 'rxjs';

interface TransferDataPoint {
    timestamp: Date;
    well: string;
    volumeTransferred: number;
    cumulativeVolume: number;
    temperature?: number;
    pressure?: number;
}

// Mock transfer data for demo
function generateMockTransferData(): TransferDataPoint[] {
    const wells = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3'];
    const data: TransferDataPoint[] = [];
    const baseTime = new Date();
    baseTime.setHours(baseTime.getHours() - 1);

    wells.forEach(well => {
        let cumulative = 0;
        for (let i = 0; i < 12; i++) {
            const volume = 50 + Math.random() * 100;
            cumulative += volume;
            data.push({
                timestamp: new Date(baseTime.getTime() + i * 5 * 60 * 1000),
                well,
                volumeTransferred: Math.round(volume * 10) / 10,
                cumulativeVolume: Math.round(cumulative * 10) / 10,
                temperature: 22 + Math.random() * 3,
                pressure: 101 + Math.random() * 2
            });
        }
    });

    return data;
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
        FormsModule,
        PlotlyModule
    ],
    template: `
    <div class="data-page">
      <header class="page-header">
        <h1>Data Visualization</h1>
        <p class="subtitle">Analyze experiment data and transfer volumes</p>
      </header>

      <mat-card class="config-card">
        <mat-card-content>
          <div class="config-row">
            <!-- X-Axis Selector -->
            <mat-form-field appearance="outline">
              <mat-label>X-Axis</mat-label>
              <mat-select [(ngModel)]="xAxis" (ngModelChange)="updateChart()">
                <mat-option value="timestamp">Time</mat-option>
                <mat-option value="well">Well</mat-option>
              </mat-select>
            </mat-form-field>

            <!-- Y-Axis Selector -->
            <mat-form-field appearance="outline">
              <mat-label>Y-Axis</mat-label>
              <mat-select [(ngModel)]="yAxis" (ngModelChange)="updateChart()">
                <mat-option value="volumeTransferred">Volume Transferred (µL)</mat-option>
                <mat-option value="cumulativeVolume">Cumulative Volume (µL)</mat-option>
                <mat-option value="temperature">Temperature (°C)</mat-option>
                <mat-option value="pressure">Pressure (kPa)</mat-option>
              </mat-select>
            </mat-form-field>

            <!-- Well Filter -->
            <div class="well-filter">
              <span class="filter-label">Filter by Well:</span>
              <mat-chip-set>
                @for (well of allWells; track well) {
                  <mat-chip
                    [class.selected]="selectedWells().includes(well)"
                    (click)="toggleWell(well)">
                    {{ well }}
                  </mat-chip>
                }
              </mat-chip-set>
              <button mat-button (click)="selectAllWells()">All</button>
              <button mat-button (click)="clearWells()">Clear</button>
            </div>
          </div>
        </mat-card-content>
      </mat-card>

      <mat-card class="chart-card">
        <mat-card-header>
          <mat-card-title>{{ chartTitle() }}</mat-card-title>
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
      </div>
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
      gap: 8px;
      flex-wrap: wrap;
    }

    .filter-label {
      font-size: 0.9rem;
      color: var(--sys-on-surface-variant);
      white-space: nowrap;
    }

    mat-chip.selected {
      background: var(--sys-primary) !important;
      color: var(--sys-on-primary) !important;
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
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
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
  `],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DataVisualizationComponent implements OnInit, OnDestroy {
    allWells = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3'];
    selectedWells = signal<string[]>(['A1', 'A2', 'A3']);
    xAxis = 'timestamp';
    yAxis = 'volumeTransferred';

    private mockData = signal<TransferDataPoint[]>([]);
    private updateSubscription?: Subscription;

    chartConfig = {
        displayModeBar: true,
        responsive: true,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };

    ngOnInit() {
        this.mockData.set(generateMockTransferData());

        // Simulate live data updates every 5 seconds
        this.updateSubscription = interval(5000).subscribe(() => {
            const newData = [...this.mockData()];
            const latestTime = new Date();
            this.selectedWells().forEach(well => {
                const volume = 50 + Math.random() * 100;
                const lastPoint = newData.filter(d => d.well === well).pop();
                newData.push({
                    timestamp: latestTime,
                    well,
                    volumeTransferred: Math.round(volume * 10) / 10,
                    cumulativeVolume: (lastPoint?.cumulativeVolume || 0) + volume,
                    temperature: 22 + Math.random() * 3,
                    pressure: 101 + Math.random() * 2
                });
            });
            this.mockData.set(newData);
        });
    }

    ngOnDestroy() {
        this.updateSubscription?.unsubscribe();
    }

    filteredData = computed(() => {
        return this.mockData().filter(d => this.selectedWells().includes(d.well));
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
        return `${yLabels[this.yAxis]} over ${xLabels[this.xAxis]}`;
    });

    chartData = computed(() => {
        const data = this.filteredData();
        const wells = [...new Set(data.map(d => d.well))];

        if (this.xAxis === 'well') {
            // Bar chart grouped by well
            const grouped = wells.map(well => {
                const wellData = data.filter(d => d.well === well);
                const total = wellData.reduce((sum, d) => sum + (d as any)[this.yAxis], 0);
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
                y: wellData.map(d => (d as any)[this.yAxis]),
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
                title: { text: this.xAxis === 'timestamp' ? 'Time' : 'Well', font: { color: 'var(--sys-on-surface)' } }
            },
            yaxis: {
                gridcolor: 'rgba(128,128,128,0.2)',
                tickfont: { color: 'var(--sys-on-surface)' },
                title: { text: yLabels[this.yAxis], font: { color: 'var(--sys-on-surface)' } }
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

    selectAllWells() {
        this.selectedWells.set([...this.allWells]);
    }

    clearWells() {
        this.selectedWells.set([]);
    }

    updateChart() {
        // Triggers reactivity through signal updates
    }
}
