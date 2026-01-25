import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';

import { Machine } from '../../../assets/models/asset.models';
import { PlaygroundAssetService } from '../../services/playground-asset.service';

@Component({
  selector: 'app-playground-machine-selector',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule
  ],
  template: `
    <div class="machine-selector-panel">
      <div class="panel-header">
        <h3>Available Machines</h3>
        <button mat-icon-button (click)="refreshMachines.emit()" matTooltip="Refresh machines">
          <mat-icon>refresh</mat-icon>
        </button>
      </div>
      
      <div *ngIf="availableMachines.length === 0" class="empty-machines">
        <mat-icon>precision_manufacturing</mat-icon>
        <p>No machines registered</p>
        <button mat-stroked-button (click)="assetService.openAssetWizard('MACHINE')">
          <mat-icon>add</mat-icon>
          Add Machine
        </button>
      </div>
      
      <div *ngIf="availableMachines.length > 0" class="machine-list">
        <div 
          *ngFor="let machine of availableMachines"
          class="machine-card" 
          [class.selected]="selectedMachine?.accession_id === machine.accession_id"
          (click)="selectMachine.emit(machine)">
          <div class="machine-icon">
            <mat-icon>{{ getMachineIcon(machine.machine_category || '') }}</mat-icon>
          </div>
          <div class="machine-info">
            <span class="machine-name">{{ machine.name }}</span>
            <span class="machine-category">{{ machine.machine_category || 'Machine' }}</span>
          </div>
          <div class="machine-status" [class]="(machine.status || 'offline').toLowerCase()">
            <span class="status-dot"></span>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .machine-selector-panel {
      width: 280px;
      min-width: 280px;
      border-right: 1px solid var(--mat-sys-outline-variant);
      background: var(--mat-sys-surface-container);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      border-bottom: 1px solid var(--mat-sys-outline-variant);
      background: var(--mat-sys-surface-container-high);
    }

    .panel-header h3 {
      margin: 0;
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--mat-sys-on-surface);
    }

    .machine-list {
      flex: 1;
      overflow-y: auto;
      padding: 8px;
    }

    .machine-card {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      border-radius: 8px;
      cursor: pointer;
      transition: background-color 0.15s ease, box-shadow 0.15s ease;
      margin-bottom: 4px;
      background: var(--mat-sys-surface);
      border: 1px solid transparent;
    }

    .machine-card:hover {
      background: var(--mat-sys-surface-container-highest);
    }

    .machine-card.selected {
      background: color-mix(in srgb, var(--mat-sys-primary) 12%, var(--mat-sys-surface));
      border-color: var(--mat-sys-primary);
    }

    .machine-icon {
      width: 40px;
      height: 40px;
      border-radius: 8px;
      background: var(--mat-sys-primary-container);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .machine-icon mat-icon {
      color: var(--mat-sys-on-primary-container);
    }

    .machine-info {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .machine-name {
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--mat-sys-on-surface);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .machine-category {
      font-size: 0.75rem;
      color: var(--mat-sys-on-surface-variant);
    }

    .machine-status {
      flex-shrink: 0;
    }

    .status-dot {
      display: block;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--mat-sys-outline);
    }

    .machine-status.idle .status-dot {
      background: var(--mat-sys-tertiary);
    }

    .machine-status.running .status-dot,
    .machine-status.connected .status-dot {
      background: var(--mat-sys-primary);
      animation: pulse 2s infinite;
    }

    .machine-status.error .status-dot {
      background: var(--mat-sys-error);
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }

    .empty-machines {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      padding: 24px;
      gap: 12px;
      color: var(--mat-sys-on-surface-variant);
      text-align: center;
    }

    .empty-machines mat-icon {
      font-size: 40px;
      width: 40px;
      height: 40px;
      opacity: 0.5;
    }

    .empty-machines p {
      margin: 0;
      font-size: 0.875rem;
    }
  `]
})
export class PlaygroundMachineSelectorComponent {
  @Input() availableMachines: Machine[] = [];
  @Input() selectedMachine: Machine | null = null;
  @Output() selectMachine = new EventEmitter<Machine>();
  @Output() refreshMachines = new EventEmitter<void>();

  public assetService = inject(PlaygroundAssetService);

  getMachineIcon(category: string): string {
    const iconMap: Record<string, string> = {
      'LiquidHandler': 'science',
      'PlateReader': 'visibility',
      'Shaker': 'vibration',
      'Centrifuge': 'loop',
      'Incubator': 'thermostat',
      'Other': 'precision_manufacturing'
    };
    return iconMap[category] || 'precision_manufacturing';
  }
}
