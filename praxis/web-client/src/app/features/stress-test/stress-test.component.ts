import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { FormsModule } from '@angular/forms';
import { MachinesService } from '@core/api-generated/services/MachinesService';
import { ApiWrapperService } from '@core/services/api-wrapper.service';
import { firstValueFrom } from 'rxjs';

@Component({
  selector: 'app-stress-test',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressBarModule,
    FormsModule
  ],
  template: `
    <div class="container p-4">
      <mat-card>
        <mat-card-header>
          <mat-card-title>Frontend Stress Tester</mat-card-title>
          <mat-card-subtitle>Generate load from the browser</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content class="flex flex-col gap-4 mt-4">
          <div class="flex gap-4">
            <mat-form-field>
              <mat-label>Concurrent Requests</mat-label>
              <input matInput type="number" [(ngModel)]="concurrency" min="1" max="100">
            </mat-form-field>
            <mat-form-field>
              <mat-label>Total Requests</mat-label>
              <input matInput type="number" [(ngModel)]="totalRequests" min="1" max="10000">
            </mat-form-field>
          </div>

          <div class="actions">
            <button mat-raised-button color="primary" (click)="startTest()" [disabled]="isRunning()">
              {{ isRunning() ? 'Running...' : 'Start Stress Test' }}
            </button>
          </div>

          @if (isRunning()) {
            <mat-progress-bar mode="determinate" [value]="progress()"></mat-progress-bar>
            <p>Progress: {{ completed() }} / {{ totalRequests }}</p>
          }

          @if (results()) {
            <div class="results mt-4 p-4 bg-gray-100 rounded">
              <h3 class="font-bold">Results</h3>
              <p>Time Taken: {{ results()?.timeTaken }}ms</p>
              <p>Requests/Sec: {{ results()?.rps }}</p>
              <p>Errors: {{ results()?.errors }}</p>
              <p>Avg Latency: {{ results()?.avgLatency | number:'1.0-2' }}ms</p>
            </div>
          }
        </mat-card-content>
      </mat-card>
    </div>
  `
})
export class StressTestComponent {
  private apiWrapper = inject(ApiWrapperService);

  concurrency = 10;
  totalRequests = 100;

  isRunning = signal(false);
  progress = signal(0);
  completed = signal(0);
  results = signal<{ timeTaken: number, rps: number, errors: number, avgLatency: number } | null>(null);

  async startTest() {
    this.isRunning.set(true);
    this.completed.set(0);
    this.progress.set(0);
    this.results.set(null);

    const startTime = Date.now();
    let errors = 0;
    const latencies: number[] = [];

    const batchSize = this.concurrency;
    const batches = Math.ceil(this.totalRequests / batchSize);

    for (let i = 0; i < batches; i++) {
      const promises = [];
      const currentBatchSize = Math.min(batchSize, this.totalRequests - (i * batchSize));

      for (let j = 0; j < currentBatchSize; j++) {
        const reqStart = Date.now();
        // Hit the machines endpoint as it's a simple GET
        promises.push(
          firstValueFrom(this.apiWrapper.wrap(MachinesService.getMultiApiV1MachinesGet()))
            .then(() => {
              latencies.push(Date.now() - reqStart);
            })
            .catch(() => {
              errors++;
            })
        );
      }

      await Promise.all(promises);
      const currentCompleted = Math.min((i + 1) * batchSize, this.totalRequests);
      this.completed.set(currentCompleted);
      this.progress.set((currentCompleted / this.totalRequests) * 100);
    }

    const endTime = Date.now();
    const timeTaken = endTime - startTime;
    const avgLatency = latencies.reduce((a, b) => a + b, 0) / latencies.length || 0;

    this.results.set({
      timeTaken,
      rps: (this.totalRequests / (timeTaken / 1000)),
      errors,
      avgLatency
    });
    this.isRunning.set(false);
  }
}
