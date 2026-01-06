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
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { FormsModule } from '@angular/forms';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MaintenanceBadgeComponent } from '../maintenance-badge/maintenance-badge.component';
import { AppStore } from '../../../../core/store/app.store';
import { AssetService } from '../../services/asset.service';

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
    SparklineComponent,
    JsonPipe,
    MatSlideToggleModule,
    FormsModule,
    MatSnackBarModule,
    MaintenanceBadgeComponent
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
              @if (data.machine.connection_info) {
                <pre>{{ data.machine.connection_info | json }}</pre>
              }
              @if (!data.machine.connection_info) {
                <span>N/A</span>
              }
            </div>
            <div class="detail-item">
              <span class="label">Simulation Override</span>
              <mat-chip [color]="data.machine.is_simulation_override ? 'accent' : 'primary'">
                {{ data.machine.is_simulation_override ? 'Enabled' : 'Disabled' }}
              </mat-chip>
            </div>
          </div>
        </mat-tab>
    
        <mat-tab label="Maintenance">
          @if (store.maintenanceEnabled()) {
            <div class="maintenance-container">
              <div class="maintenance-header">
                <app-maintenance-badge [machine]="data.machine" [showLabel]="true" />
                <span class="spacer"></span>
                <mat-slide-toggle
                  [(ngModel)]="maintenanceEnabled"
                  color="primary">
                  Enable Maintenance Tracking
                </mat-slide-toggle>
              </div>
              @if (maintenanceEnabled) {
                <div class="config-section">
                  <h3>Schedule</h3>
                  <p class="hint">Edit the maintenance schedule JSON configuration.</p>
                  <textarea
                    class="json-editor"
                    [(ngModel)]="scheduleJsonString"
                    spellcheck="false">
                  </textarea>
                  <div class="actions">
                    <button mat-stroked-button (click)="resetSchedule()">Reset to Default</button>
                    <button mat-flat-button color="primary" (click)="saveMaintenanceSettings()" [disabled]="isSaving">
                      {{ isSaving ? 'Saving...' : 'Save Changes' }}
                    </button>
                  </div>
                </div>
              }
              @if (maintenanceEnabled) {
                <div class="history-section">
                  <h3>Recent History</h3>
                  <div class="history-list">
                    @for (entry of historyEntries; track entry) {
                      <div class="history-item">
                        <mat-icon class="text-green-500">check_circle</mat-icon>
                        <div class="history-details">
                          <span class="type">{{ entry.type | titlecase }}</span>
                          <span class="date">{{ entry.completed_at | date:'medium' }}</span>
                        </div>
                      </div>
                    }
                    @if (historyEntries.length === 0) {
                      <p class="no-history">No maintenance history recorded.</p>
                    }
                  </div>
                </div>
              }
              @if (!maintenanceEnabled) {
                <div class="disabled-msg">
                  <mat-icon>off</mat-icon>
                  <p>Maintenance tracking is disabled for this machine.</p>
                </div>
              }
            </div>
          } @else {
            <div class="global-disabled-msg">
              <mat-icon>settings_off</mat-icon>
              <h3>Maintenance Tracking Globally Disabled</h3>
              <p>Enable maintenance tracking in <span class="link" (click)="dialogRef.close()">Settings</span> to manage schedules.</p>
            </div>
          }
    
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
    .maintenance-container {
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .maintenance-header {
      display: flex;
      align-items: center;
      gap: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--mat-sys-outline-variant);
    }
    
    .spacer { flex: 1; }

    .config-section h3, .history-section h3 {
       margin: 0 0 8px 0;
       font-size: 1rem;
       font-weight: 500;
    }

    .hint {
       margin: 0 0 8px 0;
       font-size: 0.8rem;
       color: var(--mat-sys-on-surface-variant);
    }

    .json-editor {
      width: 100%;
      height: 200px;
      font-family: monospace;
      font-size: 13px;
      padding: 12px;
      background: var(--mat-sys-surface-container);
      border: 1px solid var(--mat-sys-outline-variant);
      border-radius: 8px;
      resize: vertical;
      color: var(--mat-sys-on-surface);
    }

    .actions {
       display: flex;
       justify-content: flex-end;
       gap: 8px;
       margin-top: 12px;
    }

    .disabled-msg, .global-disabled-msg {
       display: flex;
       flex-direction: column;
       align-items: center;
       justify-content: center;
       padding: 32px;
       color: var(--mat-sys-on-surface-variant);
       text-align: center;
       background: var(--mat-sys-surface-container-low);
       border-radius: 8px;
    }
    
    .history-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .history-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px;
        background: var(--mat-sys-surface-container);
        border-radius: 6px;
    }
    
    .history-details {
        display: flex;
        flex-direction: column;
    }
    
    .type { font-weight: 500; font-size: 0.9rem; }
    .date { font-size: 0.8rem; color: var(--mat-sys-on-surface-variant); }
    .no-history { font-style: italic; color: var(--mat-sys-outline); font-size: 0.9rem; }
  `]
})
export class MachineDetailsDialogComponent {
  store = inject(AppStore);
  private assetService = inject(AssetService);
  private snackBar = inject(MatSnackBar);

  mockUtilization: number[] = [];
  averageUtilization = 0;

  // Maintenance State
  maintenanceEnabled = true;
  scheduleJsonString = '';
  isSaving = false;
  historyEntries: any[] = [];

  constructor(
    public dialogRef: MatDialogRef<MachineDetailsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { machine: Machine }
  ) {
    this.generateMockData();
    this.initMaintenanceState();
  }

  private initMaintenanceState() {
    this.maintenanceEnabled = this.data.machine.maintenance_enabled ?? true;
    this.scheduleJsonString = JSON.stringify(this.data.machine.maintenance_schedule_json || {}, null, 2);

    const history = this.data.machine.last_maintenance_json || {};
    this.historyEntries = Object.values(history).sort((a: any, b: any) =>
      new Date(b.completed_at).getTime() - new Date(a.completed_at).getTime()
    );
  }

  resetSchedule() {
    // Determine default based on manufacturer/model or category if available
    // For now, reset to empty enabled schedule as we don't have access to defaults map here easily without importing
    // Ideally we would fetch default definition again. 
    // Simplified: Just keep current or provide a basic template.
    this.scheduleJsonString = JSON.stringify({
      intervals: [
        { type: 'yearly', interval_days: 365, description: 'Annual Inspection', required: true }
      ],
      enabled: true
    }, null, 2);
  }

  saveMaintenanceSettings() {
    try {
      const schedule = JSON.parse(this.scheduleJsonString);
      this.isSaving = true;

      this.assetService.updateMachine(this.data.machine.accession_id, {
        maintenance_enabled: this.maintenanceEnabled,
        maintenance_schedule_json: schedule
      }).subscribe({
        next: (updated) => {
          this.data.machine = updated; // Update local reference
          this.isSaving = false;
          this.snackBar.open('Maintenance settings saved', 'Close', { duration: 3000 });
          this.initMaintenanceState(); // Re-init to ensure consistency
        },
        error: (err) => {
          this.isSaving = false;
          console.error('Failed to save settings', err);
          this.snackBar.open('Error saving settings', 'Close', { duration: 3000 });
        }
      });
    } catch (e) {
      this.snackBar.open('Invalid JSON format', 'Close', { duration: 3000 });
    }
  }

  private generateMockData() {
    // Generate 24 points of data (hourly)
    this.mockUtilization = Array.from({ length: 24 }, () => Math.floor(Math.random() * 60) + 20); // 20-80% random
    const sum = this.mockUtilization.reduce((a, b) => a + b, 0);
    this.averageUtilization = Math.round(sum / this.mockUtilization.length);
  }
}
