import { Component, computed, input, inject } from '@angular/core';

import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Machine } from '../../models/asset.models';
import { calculateMaintenanceStatus, calculateNextDueDate } from '../../utils/maintenance.utils';
import { AppStore } from '@core/store/app.store';

export type MaintenanceStatus = 'ok' | 'warning' | 'overdue' | 'disabled';

@Component({
  selector: 'app-maintenance-badge',
  standalone: true,
  imports: [MatIconModule, MatTooltipModule],
  template: `
    @if (status() !== 'disabled') {
      <div 
        class="badge" 
        [class]="status()"
        [matTooltip]="tooltipText()">
        <mat-icon class="icon">{{ icon() }}</mat-icon>
        @if (showLabel()) {
          <span class="label">{{ labelText() }}</span>
        }
      </div>
    }
  `,
  styles: [`
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 500;
      line-height: 16px;
      border: 1px solid transparent;
      user-select: none;
      transition: all 0.2s;
    }

    .icon {
      font-size: 14px;
      width: 14px;
      height: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    /* Status Colors */
    .ok {
      background-color: rgba(34, 197, 94, 0.1);
      color: rgb(21, 128, 61);
      border-color: rgba(34, 197, 94, 0.2);
    }

    .warning {
      background-color: rgba(234, 179, 8, 0.1);
      color: rgb(161, 98, 7);
      border-color: rgba(234, 179, 8, 0.2);
    }

    .overdue {
      background-color: rgba(239, 68, 68, 0.1);
      color: rgb(185, 28, 28);
      border-color: rgba(239, 68, 68, 0.2);
    }
  `]
})
export class MaintenanceBadgeComponent {
  store = inject(AppStore);
  machine = input.required<Machine>();
  showLabel = input<boolean>(false);

  status = computed((): MaintenanceStatus => {
    if (!this.store.maintenanceEnabled()) return 'disabled';
    return calculateMaintenanceStatus(this.machine());
  });

  icon = computed(() => {
    switch (this.status()) {
      case 'ok': return 'check_circle';
      case 'warning': return 'schedule';
      case 'overdue': return 'error';
      default: return 'build';
    }
  });

  labelText = computed(() => {
    switch (this.status()) {
      case 'ok': return 'Maintained';
      case 'warning': return 'Due Soon';
      case 'overdue': return 'Overdue';
      default: return '';
    }
  });

  tooltipText = computed(() => {
    const nextDue = calculateNextDueDate(this.machine());
    if (!nextDue) return 'Maintenance tracking disabled';

    const days = Math.ceil((nextDue.getTime() - Date.now()) / (1000 * 60 * 60 * 24));

    if (days < 0) return `Maintenance overdue by ${Math.abs(days)} days`;
    if (days === 0) return 'Maintenance due today';
    return `Maintenance due in ${days} days`;
  });
}
