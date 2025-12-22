
import { Component, inject, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { RouterLink } from '@angular/router';
import { ExecutionService } from '../services/execution.service';
import { ExecutionStatus } from '../models/execution.models';

@Component({
  selector: 'app-live-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatProgressBarModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    RouterLink
  ],
  template: `
    <div class="p-6">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold">Execution Monitor</h1>
        <div class="flex items-center gap-2">
          <span class="text-sm" [class.text-green-600]="executionService.isConnected()" [class.text-gray-400]="!executionService.isConnected()">
            <mat-icon class="text-sm">{{ executionService.isConnected() ? 'wifi' : 'wifi_off' }}</mat-icon>
            {{ executionService.isConnected() ? 'Connected' : 'Disconnected' }}
          </span>
        </div>
      </div>

      @if (executionService.currentRun(); as run) {
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Status Card -->
          <mat-card class="glass-panel">
            <mat-card-header>
              <mat-card-title>{{ run.protocolName }}</mat-card-title>
              <mat-card-subtitle>Run ID: {{ run.runId }}</mat-card-subtitle>
            </mat-card-header>
            <mat-card-content class="pt-4">
              <div class="flex items-center gap-2 mb-4">
                <mat-chip-set>
                  <mat-chip [highlighted]="run.status === ExecutionStatus.RUNNING"
                            [class.bg-green-100]="run.status === ExecutionStatus.COMPLETED"
                            [class.bg-red-100]="run.status === ExecutionStatus.FAILED">
                    {{ run.status | uppercase }}
                  </mat-chip>
                </mat-chip-set>
              </div>

              <div class="mb-4">
                <p class="text-sm text-gray-600 mb-1">Progress: {{ run.progress }}%</p>
                <mat-progress-bar mode="determinate" [value]="run.progress"></mat-progress-bar>
              </div>

              <p *ngIf="run.currentStep" class="text-sm">
                <span class="text-gray-500">Current Step:</span> {{ run.currentStep }}
              </p>
            </mat-card-content>
            <mat-card-actions>
              <button mat-button color="warn" (click)="stopRun()"
                      [disabled]="run.status !== ExecutionStatus.RUNNING">
                <mat-icon>stop</mat-icon> Stop
              </button>
            </mat-card-actions>
          </mat-card>

          <!-- Log Output -->
          <mat-card class="glass-panel lg:col-span-2">
            <mat-card-header>
              <mat-card-title>Execution Log</mat-card-title>
            </mat-card-header>
            <mat-card-content class="pt-4">
              <div class="bg-gray-900 text-green-400 font-mono text-sm p-4 rounded-lg h-64 overflow-y-auto">
                @for (log of run.logs; track $index) {
                  <div class="mb-1">{{ log }}</div>
                }
                @empty {
                  <div class="text-gray-500">Waiting for log output...</div>
                }
              </div>
            </mat-card-content>
          </mat-card>
        </div>

        <!-- Actions -->
        <div class="mt-6 flex gap-2" *ngIf="run.status === ExecutionStatus.COMPLETED || run.status === ExecutionStatus.FAILED">
          <button mat-flat-button color="primary" routerLink="/run">
            <mat-icon>replay</mat-icon> Run Another
          </button>
          <button mat-stroked-button routerLink="/home">
            <mat-icon>home</mat-icon> Dashboard
          </button>
        </div>
      } @else {
        <mat-card class="glass-panel text-center py-12">
          <mat-icon class="text-6xl text-gray-300 mb-4">play_disabled</mat-icon>
          <p class="text-gray-500">No active execution</p>
          <button mat-flat-button color="primary" routerLink="/run" class="mt-4">
            Start New Run
          </button>
        </mat-card>
      }
    </div>
  `
})
export class LiveDashboardComponent implements OnDestroy {
  executionService = inject(ExecutionService);
  ExecutionStatus = ExecutionStatus;

  stopRun() {
    this.executionService.stopRun().subscribe();
  }

  ngOnDestroy() {
    // Don't clear run on destroy - allow continued monitoring
  }
}
