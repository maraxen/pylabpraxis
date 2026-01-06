import { Component, Input, ChangeDetectionStrategy, computed, signal } from '@angular/core';

import { MatIconModule } from '@angular/material/icon';
import { MatBadgeModule } from '@angular/material/badge';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MatListModule } from '@angular/material/list';
import { MatChipsModule } from '@angular/material/chips';
import { FailureMode, SimulationResult, ProtocolDefinition } from '@features/protocols/models/protocol.models';

export type SimulationStatus = 'ready' | 'warnings' | 'errors' | 'not_analyzed';

/**
 * Badge component that displays protocol simulation status and failure modes.
 * 
 * States:
 * - Ready (✅): No failure modes detected
 * - Warnings (⚠️ N issues): Some failure modes detected
 * - Not Analyzed (❓): Simulation hasn't run yet
 */
@Component({
    selector: 'app-protocol-warning-badge',
    standalone: true,
    imports: [
    MatIconModule,
    MatBadgeModule,
    MatTooltipModule,
    MatMenuModule,
    MatListModule,
    MatChipsModule
],
    template: `
    @switch (status()) {
      @case ('ready') {
        <span class="badge ready" [matTooltip]="'All simulation checks passed'">
          <mat-icon>check_circle</mat-icon>
          Ready
        </span>
      }
      @case ('warnings') {
        <span 
          class="badge warnings"
          [matMenuTriggerFor]="failureMenu"
          [matTooltip]="'Click to view issues'"
        >
          <mat-icon>warning</mat-icon>
          {{ failureModes().length }} issue{{ failureModes().length > 1 ? 's' : '' }}
        </span>
        
        <mat-menu #failureMenu="matMenu" class="failure-menu">
          <div class="menu-header" (click)="$event.stopPropagation()">
            <mat-icon color="warn">warning</mat-icon>
            <span>Detected Issues</span>
          </div>
          <mat-list dense>
            @for (failure of failureModes(); track $index) {
              <mat-list-item (click)="$event.stopPropagation()">
                <mat-icon matListItemIcon [class]="getSeverityClass(failure.severity)">
                  {{ getSeverityIcon(failure.severity) }}
                </mat-icon>
                <span matListItemTitle class="failure-title">{{ failure.failure_type }}</span>
                <span matListItemLine class="failure-message">{{ failure.message }}</span>
                @if (failure.suggested_fix) {
                  <span matListItemLine class="failure-fix">
                    <mat-icon class="fix-icon">lightbulb</mat-icon>
                    {{ failure.suggested_fix }}
                  </span>
                }
              </mat-list-item>
            }
          </mat-list>
        </mat-menu>
      }
      @case ('errors') {
        <span 
          class="badge errors"
          [matMenuTriggerFor]="failureMenu"
          [matTooltip]="'Critical issues detected - click to view'"
        >
          <mat-icon>error</mat-icon>
          {{ failureModes().length }} error{{ failureModes().length > 1 ? 's' : '' }}
        </span>
        
        <mat-menu #failureMenu="matMenu" class="failure-menu">
          <div class="menu-header error" (click)="$event.stopPropagation()">
            <mat-icon>error</mat-icon>
            <span>Critical Errors</span>
          </div>
          <mat-list dense>
            @for (failure of failureModes(); track $index) {
              <mat-list-item (click)="$event.stopPropagation()">
                <mat-icon matListItemIcon [class]="getSeverityClass(failure.severity)">
                  {{ getSeverityIcon(failure.severity) }}
                </mat-icon>
                <span matListItemTitle class="failure-title">{{ failure.failure_type }}</span>
                <span matListItemLine class="failure-message">{{ failure.message }}</span>
                @if (failure.suggested_fix) {
                  <span matListItemLine class="failure-fix">
                    <mat-icon class="fix-icon">lightbulb</mat-icon>
                    {{ failure.suggested_fix }}
                  </span>
                }
              </mat-list-item>
            }
          </mat-list>
        </mat-menu>
      }
      @case ('not_analyzed') {
        <span class="badge not-analyzed" [matTooltip]="'Protocol not yet analyzed'">
          <mat-icon>help_outline</mat-icon>
          Not analyzed
        </span>
      }
    }
  `,
    styles: [`
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 8px;
      border-radius: 16px;
      font-size: 0.75rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .badge mat-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
    }

    .badge.ready {
      background: rgba(34, 197, 94, 0.15);
      color: rgb(34, 197, 94);
    }

    .badge.warnings {
      background: rgba(245, 158, 11, 0.15);
      color: rgb(245, 158, 11);
    }

    .badge.warnings:hover {
      background: rgba(245, 158, 11, 0.25);
    }

    .badge.errors {
      background: rgba(239, 68, 68, 0.15);
      color: rgb(239, 68, 68);
    }

    .badge.errors:hover {
      background: rgba(239, 68, 68, 0.25);
    }

    .badge.not-analyzed {
      background: rgba(107, 114, 128, 0.15);
      color: rgb(107, 114, 128);
    }

    .menu-header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      font-weight: 500;
      border-bottom: 1px solid var(--mat-sys-outline-variant);
      color: rgb(245, 158, 11);
    }

    .menu-header.error {
      color: rgb(239, 68, 68);
    }

    .failure-title {
      font-weight: 500;
    }

    .failure-message {
      color: var(--mat-sys-on-surface-variant);
      font-size: 0.8rem;
    }

    .failure-fix {
      display: flex;
      align-items: center;
      gap: 4px;
      color: rgb(34, 197, 94);
      font-size: 0.75rem;
      font-style: italic;
    }

    .fix-icon {
      font-size: 14px;
      width: 14px;
      height: 14px;
    }

    .severity-error {
      color: rgb(239, 68, 68);
    }

    .severity-warning {
      color: rgb(245, 158, 11);
    }

    .severity-info {
      color: rgb(59, 130, 246);
    }

    ::ng-deep .failure-menu {
      max-width: 400px;
    }
  `],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProtocolWarningBadgeComponent {
    /**
     * The protocol definition containing simulation results.
     */
    @Input() protocol: ProtocolDefinition | null = null;

    /**
     * Computed failure modes from the protocol.
     */
    failureModes = computed(() => {
        if (!this.protocol) return [];
        return this.protocol.failure_modes ??
            this.protocol.simulation_result?.failure_modes ??
            [];
    });

    /**
     * Computed simulation status.
     */
    status = computed<SimulationStatus>(() => {
        if (!this.protocol) return 'not_analyzed';

        // Check if simulation has been run
        const hasSimulation = this.protocol.simulation_result ||
            this.protocol.failure_modes ||
            this.protocol.simulation_version;

        if (!hasSimulation) return 'not_analyzed';

        const failures = this.failureModes();
        if (failures.length === 0) return 'ready';

        // Check for any critical errors
        const hasErrors = failures.some(f => f.severity === 'error');
        return hasErrors ? 'errors' : 'warnings';
    });

    getSeverityIcon(severity: string): string {
        switch (severity) {
            case 'error': return 'error';
            case 'warning': return 'warning';
            case 'info': return 'info';
            default: return 'help_outline';
        }
    }

    getSeverityClass(severity: string): string {
        return `severity-${severity}`;
    }
}
