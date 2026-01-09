import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { MatListModule } from '@angular/material/list';
import { Router } from '@angular/router';
import { ProtocolDefinition } from '../../models/protocol.models';

@Component({
    selector: 'app-protocol-detail-dialog',
    standalone: true,
    imports: [
        CommonModule,
        MatDialogModule,
        MatButtonModule,
        MatIconModule,
        MatChipsModule,
        MatDividerModule,
        MatListModule
    ],
    template: `
    <div class="dialog-container">
      <div mat-dialog-title class="dialog-header">
        <div class="header-content">
          <div class="title-row">
            <mat-icon class="protocol-icon">science</mat-icon>
            <h2 class="protocol-name">{{ data.protocol.name }}</h2>
            <span class="spacer"></span>
            <button mat-icon-button mat-dialog-close>
              <mat-icon>close</mat-icon>
            </button>
          </div>
          <div class="metadata-chips">
            <span class="chip version">v{{ data.protocol.version }}</span>
            <span class="chip category" *ngIf="data.protocol.category">{{ data.protocol.category }}</span>
            <span class="chip type">{{ data.protocol.is_top_level ? 'Top Level' : 'Sub-Protocol' }}</span>
          </div>
        </div>
      </div>

      <mat-dialog-content class="dialog-content">
        <!-- Description Section -->
        <section class="info-section">
          <h3 class="section-title">Description</h3>
          <p class="description-text">{{ data.protocol.description || 'No description provided.' }}</p>
        </section>

        <mat-divider></mat-divider>

        <!-- Technical Information -->
        <section class="info-section grid-section">
           <div class="info-item">
             <span class="label">Accession ID</span>
             <span class="value font-mono">{{ data.protocol.accession_id }}</span>
           </div>
           <div class="info-item" *ngIf="data.protocol.fqn">
             <span class="label">FQN</span>
             <span class="value font-mono text-xs">{{ data.protocol.fqn }}</span>
           </div>
        </section>

        <mat-divider></mat-divider>

        <!-- Asset Requirements -->
        <section class="info-section">
          <h3 class="section-title flex items-center gap-2">
            <mat-icon>inventory_2</mat-icon>
            Asset Requirements
          </h3>
          <mat-list *ngIf="data.protocol.assets.length > 0; else noAssets">
            <mat-list-item *ngFor="let asset of data.protocol.assets">
              <mat-icon matListItemIcon>view_in_ar</mat-icon>
              <div matListItemTitle class="flex items-center gap-2">
                <span class="font-medium">{{ asset.name }}</span>
                <span class="chip optional" *ngIf="asset.optional">Optional</span>
              </div>
              <div matListItemLine class="text-xs opacity-70">{{ asset.fqn }}</div>
            </mat-list-item>
          </mat-list>
          <ng-template #noAssets>
            <p class="empty-state">No specific hardware assets required.</p>
          </ng-template>
        </section>

        <mat-divider></mat-divider>

        <!-- Parameters -->
        <section class="info-section">
          <h3 class="section-title flex items-center gap-2">
            <mat-icon>tune</mat-icon>
            Parameters
          </h3>
          <mat-list *ngIf="data.protocol.parameters.length > 0; else noParams">
            <mat-list-item *ngFor="let param of data.protocol.parameters">
              <mat-icon matListItemIcon>settings_input_component</mat-icon>
              <div matListItemTitle class="flex items-center gap-2">
                <span class="font-medium">{{ param.name }}</span>
                <span class="chip param-type">{{ param.type_hint }}</span>
              </div>
              <div matListItemLine class="text-xs opacity-70">{{ param.description || 'No description' }}</div>
              <div matListItemLine *ngIf="param.default_value_repr" class="text-xs italic">Default: {{ param.default_value_repr }}</div>
            </mat-list-item>
          </mat-list>
          <ng-template #noParams>
            <p class="empty-state">No parameters defined for this protocol.</p>
          </ng-template>
        </section>

        <!-- Simulation Result (If available) -->
        <ng-container *ngIf="data.protocol.simulation_result">
          <mat-divider></mat-divider>
          <section class="info-section">
            <h3 class="section-title flex items-center gap-2">
              <mat-icon>analytics</mat-icon>
              Simulation Status
            </h3>
            <div class="simulation-status" [class.passed]="data.protocol.simulation_result.passed" [class.failed]="!data.protocol.simulation_result.passed">
              <mat-icon>{{ data.protocol.simulation_result.passed ? 'check_circle' : 'error' }}</mat-icon>
              <span>{{ data.protocol.simulation_result.passed ? 'Simulation Passed' : 'Simulation Failed' }}</span>
            </div>
            <div *ngIf="data.protocol.simulation_result.violations.length > 0" class="violations-list">
              <div class="violation-item" *ngFor="let v of data.protocol.simulation_result.violations">
                 <mat-icon class="text-yellow-500">warning</mat-icon>
                 <span class="text-sm">{{ v['message'] || 'Unknown violation' }}</span>
              </div>
            </div>
          </section>
        </ng-container>
      </mat-dialog-content>

      <mat-dialog-actions align="end" class="dialog-actions">
        <button mat-button mat-dialog-close class="!rounded-xl !px-6">Close</button>
        <button mat-flat-button color="primary" class="!rounded-xl !px-6 !py-6 shadow-lg shadow-primary/20" (click)="runProtocol()">
          <mat-icon>play_arrow</mat-icon>
          Run Protocol
        </button>
      </mat-dialog-actions>
    </div>
  `,
    styles: [`
    .dialog-container {
      display: flex;
      flex-direction: column;
      max-height: 80vh;
      overflow: hidden;
      background: var(--theme-surface);
      color: var(--theme-text-primary);
    }

    .dialog-header {
      padding: 1.5rem 1.5rem 1rem;
      border-bottom: 1px solid var(--theme-border);
      background: var(--theme-surface-elevated);
      margin: 0 !important;
    }

    .header-content {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .title-row {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .protocol-icon {
      width: 32px;
      height: 32px;
      font-size: 32px;
      color: var(--primary-color);
    }

    .protocol-name {
      margin: 0;
      font-size: 1.5rem;
      font-weight: 700;
      line-height: 1.2;
    }

    .metadata-chips {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }

    .chip {
      padding: 0.25rem 0.6rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.025em;
    }

    .chip.version { background: var(--theme-surface-variant); color: var(--theme-text-secondary); }
    .chip.category { background: rgba(var(--primary-color-rgb), 0.1); color: var(--primary-color); border: 1px solid rgba(var(--primary-color-rgb), 0.2); }
    .chip.type { background: var(--theme-surface-variant); color: var(--theme-text-secondary); }
    .chip.optional { background: var(--theme-surface-variant); color: var(--theme-text-tertiary); font-size: 0.65rem; }
    .chip.param-type { background: var(--theme-surface-variant); color: var(--theme-text-tertiary); font-size: 0.65rem; margin-left: 0.5rem; }

    .dialog-content {
      padding: 1.5rem !important;
      overflow-y: auto;
    }

    .info-section {
      margin-bottom: 1.5rem;
      margin-top: 1.5rem;
    }

    .info-section:first-child { margin-top: 0; }
    .info-section:last-child { margin-bottom: 0; }

    .section-title {
      font-size: 0.9rem;
      font-weight: 700;
      color: var(--theme-text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 1rem;
    }

    .description-text {
      font-size: 1rem;
      line-height: 1.6;
      color: var(--theme-text-primary);
      margin: 0;
    }

    .grid-section {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.5rem;
    }

    .info-item {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    .label {
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--theme-text-tertiary);
      text-transform: uppercase;
    }

    .value {
      font-size: 0.9rem;
      font-weight: 500;
      color: var(--theme-text-primary);
    }

    .empty-state {
      font-style: italic;
      color: var(--theme-text-tertiary);
      font-size: 0.9rem;
    }

    .simulation-status {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem 1rem;
      border-radius: 0.75rem;
      font-weight: 600;
      margin-bottom: 1rem;
    }

    .simulation-status.passed { background: rgba(34, 197, 94, 0.1); color: rgb(34, 197, 94); }
    .simulation-status.failed { background: rgba(239, 68, 68, 0.1); color: rgb(239, 68, 68); }

    .violations-list {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .violation-item {
      display: flex;
      align-items: flex-start;
      gap: 0.5rem;
      padding: 0.5rem;
      background: var(--theme-surface-elevated);
      border-radius: 0.5rem;
    }

    .dialog-actions {
      padding: 1rem 1.5rem !important;
      border-top: 1px solid var(--theme-border);
      background: var(--theme-surface-elevated);
      margin: 0 !important;
    }

    .spacer { flex: 1; }

    /* Override Mat List styles */
    ::ng-deep .mat-mdc-list-item-title { font-weight: 600 !important; }
    ::ng-deep .mat-mdc-list-item { height: auto !important; padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; }
  `],
})
export class ProtocolDetailDialogComponent {
    private dialogRef = inject(MatDialogRef<ProtocolDetailDialogComponent>);
    public data = inject<{ protocol: ProtocolDefinition }>(MAT_DIALOG_DATA);
    private router = inject(Router);

    runProtocol() {
        this.dialogRef.close();
        this.router.navigate(['/app/run'], { queryParams: { protocolId: this.data.protocol.accession_id } });
    }
}
