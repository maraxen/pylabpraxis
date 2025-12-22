import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { ExecutionService } from '../../../features/run-protocol/services/execution.service';
import { AppStore } from '../../store/app.store';
import { ExecutionStatus } from '../../../features/run-protocol/models/execution.models';

@Component({
  selector: 'app-status-bar',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatProgressBarModule],
  template: `
    <div class="status-bar" [ngClass]="{'connected': isConnected(), 'disconnected': !isConnected()}">
      <div class="status-left">
        <mat-icon [fontIcon]="isConnected() ? 'cloud_done' : 'cloud_off'"></mat-icon>
        <span *ngIf="isConnected()">Connected</span>
        <span *ngIf="!isConnected()">Disconnected</span>
      </div>

      <div class="status-center" *ngIf="currentRun()">
        <ng-container [ngSwitch]="currentRun()?.status">
          <span *ngSwitchCase="'RUNNING'">
            <mat-icon fontIcon="play_arrow"></mat-icon> Protocol Running: {{ currentRun()?.protocolName }}
          </span>
          <span *ngSwitchCase="'PENDING'">
            <mat-icon fontIcon="hourglass_empty"></mat-icon> Protocol Pending: {{ currentRun()?.protocolName }}
          </span>
          <span *ngSwitchCase="'COMPLETED'">
            <mat-icon fontIcon="check_circle_outline"></mat-icon> Protocol Completed: {{ currentRun()?.protocolName }}
          </span>
          <span *ngSwitchCase="'FAILED'">
            <mat-icon fontIcon="error_outline"></mat-icon> Protocol Failed: {{ currentRun()?.protocolName }}
          </span>
          <span *ngSwitchCase="'CANCELLED'">
            <mat-icon fontIcon="cancel"></mat-icon> Protocol Cancelled: {{ currentRun()?.protocolName }}
          </span>
          <span *ngSwitchDefault>
            <mat-icon fontIcon="info_outline"></mat-icon> Status: {{ currentRun()?.status }}
          </span>
        </ng-container>
        <mat-progress-bar *ngIf="isRunning()" mode="determinate" [value]="currentRun()?.progress"></mat-progress-bar>
      </div>

      <div class="status-right">
        <!-- Add other global status indicators here -->
      </div>
    </div>
  `,
  styles: [`
    .status-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 4px 16px;
      font-size: 0.8em;
      color: white;
      transition: background-color 0.3s ease;
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      z-index: 1000; /* Ensure it's on top */
      height: 32px; /* Compact height */
    }
    .status-bar.connected {
      background-color: var(--mat-sys-color-primary); /* Primary color for connected */
    }
    .status-bar.disconnected {
      background-color: var(--mat-sys-color-error); /* Error color for disconnected */
    }
    .status-left, .status-right, .status-center {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .status-center {
      flex-grow: 1;
      justify-content: center;
    }
    mat-icon {
      font-size: 1.2em;
      height: 1.2em;
      width: 1.2em;
    }
    mat-progress-bar {
      width: 100px; /* Adjust as needed */
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class StatusBarComponent {
  readonly executionService = inject(ExecutionService);
  readonly appStore = inject(AppStore);

  readonly isConnected = this.executionService.isConnected;
  readonly currentRun = this.executionService.currentRun;
  readonly isLoading = this.appStore.isLoading; // Example, could be global or more specific

  readonly isRunning = () => this.currentRun()?.status === ExecutionStatus.RUNNING;
}
