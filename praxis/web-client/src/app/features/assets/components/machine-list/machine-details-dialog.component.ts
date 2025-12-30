import { Component, Inject, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTabsModule } from '@angular/material/tabs';
import { MatChipsModule } from '@angular/material/chips';
import { Machine } from '../../models/asset.models';
import { DeckVisualizerComponent } from '../../../../features/run-protocol/components/deck-visualizer/deck-visualizer.component';
import { AssetStatusChipComponent } from '../asset-status-chip/asset-status-chip.component';
import { LocationBreadcrumbComponent } from '../location-breadcrumb/location-breadcrumb.component';
import { SparklineComponent } from '@shared/components/sparkline/sparkline.component';
import { JsonPipe } from '@angular/common';

@Component({
  selector: 'app-machine-details-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatTabsModule,
    MatChipsModule,
    DeckVisualizerComponent,
    AssetStatusChipComponent,
    LocationBreadcrumbComponent,
    SparklineComponent,
    JsonPipe
  ],
  template: `
    <h2 mat-dialog-title>
      <div class="title-container">
        <mat-icon class="machine-icon">precision_manufacturing</mat-icon>
        <div class="title-text">
          <span>{{ data.machine.name }}</span>
          <span class="subtitle">{{ data.machine.model || 'Unknown Model' }}</span>
        </div>
        <app-asset-status-chip [status]="data.machine.status" [showLabel]="true" />
      </div>
    </h2>

    <mat-dialog-content class="details-content">
      <mat-tab-group animationDuration="0ms">
        <mat-tab label="Overview">
          <div class="overview-grid">
            <div class="detail-item">
              <span class="label">Accession ID</span>
              <span class="p-mono">{{ data.machine.accession_id }}</span>
            </div>
            <div class="detail-item">
              <span class="label">Manufacturer</span>
              <span>{{ data.machine.manufacturer || 'N/A' }}</span>
            </div>
            <div class="detail-item full-width">
              <span class="label">Location</span>
              <app-location-breadcrumb [location]="data.machine.location"></app-location-breadcrumb>
            </div>
            <div class="detail-item full-width">
              <span class="label">Utilization (24h)</span>
              <div class="sparkline-container">
                <app-sparkline [data]="mockUtilization" [height]="40" color="var(--mat-sys-tertiary)" />
                <span class="trend-label">Avg: {{ averageUtilization }}%</span>
              </div>
            </div>

            <div class="detail-item full-width">
              <span class="label">Description</span>
              <span>{{ data.machine.description || 'No description provided.' }}</span>
            </div>
          </div>
        </mat-tab>

        <mat-tab label="Deck Layout">
          <div class="deck-view-container">
            @if (data.machine.plr_state) {
              <app-deck-visualizer [layoutData]="data.machine.plr_state" />
            } @else {
              <div class="no-data">
                <mat-icon>no_sim</mat-icon>
                <p>No deck state available</p>
              </div>
            }
          </div>
        </mat-tab>

        <mat-tab label="Technical">
          <div class="tech-details">
            <div class="detail-item">
              <span class="label">FQN (Driver)</span>
              <span class="p-mono">{{ data.machine.fqn || 'N/A' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">Connection Info</span>
              <pre *ngIf="data.machine.connection_info">{{ data.machine.connection_info | json }}</pre>
              <span *ngIf="!data.machine.connection_info">N/A</span>
            </div>
            <div class="detail-item">
              <span class="label">Simulation Override</span>
              <mat-chip [color]="data.machine.is_simulation_override ? 'accent' : 'primary'">
                {{ data.machine.is_simulation_override ? 'Enabled' : 'Disabled' }}
              </mat-chip>
            </div>
          </div>
        </mat-tab>
      </mat-tab-group>
    </mat-dialog-content>

    <mat-dialog-actions align="end">
      <button mat-button (click)="dialogRef.close()">Close</button>
      <button mat-button color="primary" [mat-dialog-close]="'edit'">
        <mat-icon>edit</mat-icon> Edit
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .title-container {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .machine-icon {
      font-size: 32px;
      width: 32px;
      height: 32px;
      color: var(--mat-sys-primary);
    }

    .title-text {
      display: flex;
      flex-direction: column;
      flex: 1;
    }

    .subtitle {
      font-size: 0.8rem;
      color: var(--mat-sys-on-surface-variant);
      font-weight: normal;
    }

    .details-content {
      min-width: 500px;
      min-height: 400px;
      padding-top: 16px;
    }

    .overview-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      padding: 16px;
    }

    .detail-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .full-width {
      grid-column: span 2;
    }

    .label {
      font-size: 0.75rem;
      color: var(--mat-sys-on-surface-variant);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .p-mono {
      font-family: monospace;
      background: var(--mat-sys-surface-container);
      padding: 2px 4px;
      border-radius: 4px;
      width: fit-content;
    }

    .deck-view-container {
      height: 350px;
      padding: 16px;
      background: var(--mat-sys-surface-container-low);
      border-radius: 8px;
    }

    .no-data {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: var(--mat-sys-on-surface-variant);
      opacity: 0.7;
    }

    .tech-details {
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    pre {
      background: var(--mat-sys-surface-container);
      padding: 12px;
      border-radius: 8px;
      margin: 0;
      white-space: pre-wrap;
      font-size: 0.85rem;
    }

    .sparkline-container {
      height: 40px;
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 8px 0;
    }

    .trend-label {
      font-size: 0.8em;
      color: var(--mat-sys-tertiary);
      font-weight: 500;
      white-space: nowrap;
    }
  `]
})
export class MachineDetailsDialogComponent {
  mockUtilization: number[] = [];
  averageUtilization = 0;

  constructor(
    public dialogRef: MatDialogRef<MachineDetailsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { machine: Machine }
  ) {
    this.generateMockData();
  }

  private generateMockData() {
    // Generate 24 points of data (hourly)
    this.mockUtilization = Array.from({ length: 24 }, () => Math.floor(Math.random() * 60) + 20); // 20-80% random
    const sum = this.mockUtilization.reduce((a, b) => a + b, 0);
    this.averageUtilization = Math.round(sum / this.mockUtilization.length);
  }
}
