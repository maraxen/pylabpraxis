import { Component, Input, ChangeDetectionStrategy, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatIconModule } from '@angular/material/icon';

export type AssetStatusType =
    | 'available'
    | 'reserved'
    | 'in_use'
    | 'depleted'
    | 'expired'
    | 'idle'
    | 'running'
    | 'error'
    | 'offline'
    | 'maintenance'
    | 'unknown';

interface StatusConfig {
    label: string;
    icon: string;
    cssClass: string;
    tooltip: string;
}

/**
 * Reusable status chip component with color + icon for accessibility.
 * Follows "Traffic Light + Shape Coding" pattern from CMMS research.
 */
@Component({
    selector: 'app-asset-status-chip',
    standalone: true,
    imports: [CommonModule, MatChipsModule, MatTooltipModule, MatIconModule],
    template: `
    <mat-chip
      [class]="config().cssClass"
      class="status-chip"
      [matTooltip]="config().tooltip"
      [disableRipple]="true"
    >
      <mat-icon class="status-icon">{{ config().icon }}</mat-icon>
      @if (showLabel) {
        <span class="status-label">{{ config().label }}</span>
      }
    </mat-chip>
  `,
    styles: [`
    .status-chip {
      --mdc-chip-container-height: 24px;
      font-size: 0.75rem;
      font-weight: 500;
    }

    .status-icon {
      font-size: 14px;
      width: 14px;
      height: 14px;
      margin-right: 4px;
    }

    .status-label {
      text-transform: capitalize;
    }

    /* Status-specific colors with icons for accessibility */
    .status-available {
      --mdc-chip-elevated-container-color: var(--sys-tertiary-container);
      --mdc-chip-label-text-color: var(--sys-on-tertiary-container);
    }

    .status-reserved {
      --mdc-chip-elevated-container-color: var(--sys-secondary-container);
      --mdc-chip-label-text-color: var(--sys-on-secondary-container);
    }

    .status-in_use, .status-running {
      --mdc-chip-elevated-container-color: var(--sys-primary-container);
      --mdc-chip-label-text-color: var(--sys-on-primary-container);
    }

    .status-idle {
      --mdc-chip-elevated-container-color: var(--sys-surface-container-high);
      --mdc-chip-label-text-color: var(--sys-on-surface);
    }

    .status-depleted, .status-expired, .status-error, .status-offline {
      --mdc-chip-elevated-container-color: var(--sys-error-container);
      --mdc-chip-label-text-color: var(--sys-on-error-container);
    }

    .status-maintenance {
      --mdc-chip-elevated-container-color: var(--sys-tertiary-container);
      --mdc-chip-label-text-color: var(--sys-on-tertiary-container);
    }

    .status-unknown {
      --mdc-chip-elevated-container-color: var(--sys-outline-variant);
      --mdc-chip-label-text-color: var(--sys-on-surface-variant);
    }
  `],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AssetStatusChipComponent {
    @Input({ required: true }) status!: AssetStatusType;
    @Input() showLabel = true;

    private readonly statusConfigs: Record<AssetStatusType, StatusConfig> = {
        available: {
            label: 'Available',
            icon: 'check_circle',
            cssClass: 'status-available',
            tooltip: 'Resource is available for use',
        },
        reserved: {
            label: 'Reserved',
            icon: 'schedule',
            cssClass: 'status-reserved',
            tooltip: 'Reserved for an upcoming protocol run',
        },
        in_use: {
            label: 'In Use',
            icon: 'play_circle',
            cssClass: 'status-in_use',
            tooltip: 'Currently being used in a protocol',
        },
        depleted: {
            label: 'Depleted',
            icon: 'remove_circle',
            cssClass: 'status-depleted',
            tooltip: 'Resource has been consumed/depleted',
        },
        expired: {
            label: 'Expired',
            icon: 'warning',
            cssClass: 'status-expired',
            tooltip: 'Resource has expired',
        },
        idle: {
            label: 'Idle',
            icon: 'pause_circle',
            cssClass: 'status-idle',
            tooltip: 'Machine is idle and ready',
        },
        running: {
            label: 'Running',
            icon: 'play_arrow',
            cssClass: 'status-running',
            tooltip: 'Machine is currently running a protocol',
        },
        error: {
            label: 'Error',
            icon: 'error',
            cssClass: 'status-error',
            tooltip: 'Machine has encountered an error',
        },
        offline: {
            label: 'Offline',
            icon: 'cloud_off',
            cssClass: 'status-offline',
            tooltip: 'Machine is offline or disconnected',
        },
        maintenance: {
            label: 'Maintenance',
            icon: 'build',
            cssClass: 'status-maintenance',
            tooltip: 'Machine is undergoing maintenance',
        },
        unknown: {
            label: 'Unknown',
            icon: 'help_outline',
            cssClass: 'status-unknown',
            tooltip: 'Status is unknown',
        },
    };

    config = computed(() => this.statusConfigs[this.status] || this.statusConfigs['unknown']);
}
