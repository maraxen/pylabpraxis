import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';

import { RunHistoryService } from '../services/run-history.service';
import { RunDetail } from '../models/monitor.models';

/**
 * Displays detailed information about a single protocol run.
 */
@Component({
    selector: 'app-run-detail',
    standalone: true,
    imports: [
        CommonModule,
        RouterLink,
        MatCardModule,
        MatIconModule,
        MatButtonModule,
        MatProgressSpinnerModule,
        MatChipsModule,
        MatDividerModule,
    ],
    template: `
    <div class="p-6 max-w-screen-xl mx-auto">
      <!-- Header -->
      <div class="flex items-center gap-4 mb-6">
        <button mat-icon-button (click)="goBack()" aria-label="Go back">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <div class="flex-1">
          <h1 class="text-2xl font-bold text-sys-text-primary">
            @if (run()) {
              {{ run()?.protocol_name || run()?.name || 'Run Details' }}
            } @else {
              Run Details
            }
          </h1>
          <p class="text-sys-text-secondary">{{ runId }}</p>
        </div>
      </div>

      @if (isLoading()) {
        <div class="flex justify-center py-12">
          <mat-spinner diameter="48"></mat-spinner>
        </div>
      } @else if (!run()) {
        <div class="empty-state text-center py-12 text-sys-text-tertiary">
          <mat-icon class="!w-16 !h-16 !text-[64px] opacity-30 mb-4">error_outline</mat-icon>
          <p class="text-lg">Run not found</p>
          <a mat-button routerLink="/app/monitor" class="mt-4">
            <mat-icon>arrow_back</mat-icon>
            Back to Monitor
          </a>
        </div>
      } @else {
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Main Info Card -->
          <mat-card class="lg:col-span-2 detail-card">
            <mat-card-header>
              <mat-card-title>Run Information</mat-card-title>
            </mat-card-header>
            <mat-card-content class="pt-4">
              <!-- Status -->
              <div class="info-row">
                <span class="info-label">Status</span>
                <div class="flex items-center gap-2">
                  <mat-icon [class]="runHistoryService.getStatusColor(run()!.status)" class="!w-5 !h-5 !text-[20px]">
                    {{ runHistoryService.getStatusIcon(run()!.status) }}
                  </mat-icon>
                  <span class="font-semibold">{{ run()!.status }}</span>
                </div>
              </div>
              <mat-divider></mat-divider>

              <!-- Times -->
              <div class="info-row">
                <span class="info-label">Created</span>
                <span>{{ formatDateTime(run()!.created_at) }}</span>
              </div>
              @if (run()!.start_time) {
                <div class="info-row">
                  <span class="info-label">Started</span>
                  <span>{{ formatDateTime(run()!.start_time) }}</span>
                </div>
              }
              @if (run()!.end_time) {
                <div class="info-row">
                  <span class="info-label">Completed</span>
                  <span>{{ formatDateTime(run()!.end_time) }}</span>
                </div>
              }
              @if (run()!.duration_ms) {
                <div class="info-row">
                  <span class="info-label">Duration</span>
                  <span>{{ runHistoryService.formatDuration(run()!.duration_ms) }}</span>
                </div>
              }
              <mat-divider></mat-divider>

              <!-- Parameters -->
              @if (run()!.input_parameters_json && hasKeys(run()!.input_parameters_json)) {
                <div class="mt-4">
                  <h3 class="font-semibold text-sys-text-primary mb-2">Input Parameters</h3>
                  <pre class="bg-surface-container p-3 rounded-lg text-sm overflow-x-auto">{{ formatJson(run()!.input_parameters_json) }}</pre>
                </div>
              }
            </mat-card-content>
          </mat-card>

          <!-- Sidebar -->
          <div class="space-y-4">
            <!-- Actions Card -->
            <mat-card class="detail-card">
              <mat-card-header>
                <mat-card-title>Actions</mat-card-title>
              </mat-card-header>
              <mat-card-content class="pt-4 space-y-2">
                <button mat-stroked-button class="w-full" disabled>
                  <mat-icon>replay</mat-icon>
                  Re-run Protocol
                </button>
                <button mat-stroked-button class="w-full" disabled>
                  <mat-icon>download</mat-icon>
                  Export Logs
                </button>
              </mat-card-content>
            </mat-card>

            <!-- Output Data Card-->
            @if (run()!.output_data_json && hasKeys(run()!.output_data_json)) {
              <mat-card class="detail-card">
                <mat-card-header>
                  <mat-card-title>Output Data</mat-card-title>
                </mat-card-header>
                <mat-card-content class="pt-4">
                  <pre class="bg-surface-container p-3 rounded-lg text-sm overflow-x-auto max-h-64">{{ formatJson(run()!.output_data_json) }}</pre>
                </mat-card-content>
              </mat-card>
            }
          </div>
        </div>

        <!-- Logs Section -->
        @if (run()!.logs && run()!.logs!.length > 0) {
          <mat-card class="detail-card mt-6">
            <mat-card-header>
              <mat-card-title>Execution Logs</mat-card-title>
            </mat-card-header>
            <mat-card-content class="pt-4">
              <div class="bg-[#1e1e1e] text-green-400 p-4 rounded-lg font-mono text-sm max-h-96 overflow-y-auto">
                @for (log of run()!.logs; track $index) {
                  <div class="log-line">{{ log }}</div>
                }
              </div>
            </mat-card-content>
          </mat-card>
        }
      }
    </div>
  `,
    styles: [`
    .detail-card {
      background: var(--mat-sys-surface-container-low);
      border: 1px solid var(--mat-sys-outline-variant);
    }
    .info-row {
      display: flex;
      justify-content: space-between;
      padding: 12px 0;
    }
    .info-label {
      color: var(--mat-sys-on-surface-variant);
      font-weight: 500;
    }
    .log-line {
      padding: 2px 0;
      white-space: pre-wrap;
      word-break: break-all;
    }
    pre {
      margin: 0;
      font-family: 'Fira Code', 'Monaco', monospace;
    }
  `],
})
export class RunDetailComponent implements OnInit {
    private readonly route = inject(ActivatedRoute);
    private readonly location = inject(Location);
    readonly runHistoryService = inject(RunHistoryService);

    readonly run = signal<RunDetail | null>(null);
    readonly isLoading = signal(true);
    runId = '';

    ngOnInit(): void {
        this.runId = this.route.snapshot.paramMap.get('id') || '';
        if (this.runId) {
            this.loadRunDetail();
        } else {
            this.isLoading.set(false);
        }
    }

    loadRunDetail(): void {
        this.isLoading.set(true);
        this.runHistoryService.getRunDetail(this.runId).subscribe({
            next: (detail) => {
                this.run.set(detail);
                this.isLoading.set(false);
            },
            error: (err) => {
                console.error('[RunDetail] Error loading run:', err);
                this.isLoading.set(false);
            },
        });
    }

    goBack(): void {
        this.location.back();
    }

    formatDateTime(isoDate?: string): string {
        if (!isoDate) return '-';
        try {
            return new Date(isoDate).toLocaleString();
        } catch {
            return isoDate;
        }
    }

    formatJson(obj?: Record<string, unknown>): string {
        if (!obj) return '';
        return JSON.stringify(obj, null, 2);
    }

    hasKeys(obj?: Record<string, unknown>): boolean {
        return !!obj && Object.keys(obj).length > 0;
    }
}
