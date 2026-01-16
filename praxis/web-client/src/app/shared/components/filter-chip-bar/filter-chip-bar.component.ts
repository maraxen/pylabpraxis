import { Component, ChangeDetectionStrategy, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ActiveFilter } from '../view-controls/view-controls.types';

@Component({
    selector: 'app-filter-chip-bar',
    standalone: true,
    imports: [
        CommonModule,
        MatIconModule,
        MatButtonModule,
        MatTooltipModule
    ],
    template: `
    <div class="filter-chip-bar" [class.has-filters]="filters.length > 0">
      @if (filters.length > 0) {
        <span class="active-label">Active:</span>
        <div class="chips-scroll-container">
          @for (filter of filters; track filter.filterId) {
            <div class="filter-chip" 
                 [matTooltip]="filter.displayText"
                 matTooltipPosition="above">
              <mat-icon class="filter-icon">{{ getIcon(filter.filterId) }}</mat-icon>
              <span class="chip-content">{{ getShortLabel(filter) }}</span>
              <button mat-icon-button class="chip-remove" (click)="onRemove(filter.filterId)">
                <mat-icon>close</mat-icon>
              </button>
            </div>
          }
          <button mat-button class="clear-all-link" (click)="onClearAll()">Clear all</button>
        </div>
      }
    </div>
  `,
    styles: [`
    :host {
      display: block;
    }

    .filter-chip-bar {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 4px 8px;
      border-radius: 8px;
      min-height: 32px;
      
      &.has-filters {
        background: var(--theme-surface-subtle);
        animation: fadeIn 0.2s ease;
      }
    }

    .active-label {
      font-size: 0.6875rem;
      font-weight: 700;
      text-transform: uppercase;
      color: var(--theme-text-secondary);
      letter-spacing: 0.03125rem;
      flex-shrink: 0;
    }

    .chips-scroll-container {
      display: flex;
      align-items: center;
      gap: 8px;
      overflow-x: auto;
      flex: 1;
      padding-bottom: 2px; // for scrollbar offset
      
      &::-webkit-scrollbar {
        height: 0;
      }
    }

    .filter-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      height: 26px;
      padding: 0 4px 0 8px;
      background: var(--theme-surface-elevated);
      border: 1px solid var(--theme-border);
      border-radius: 13px;
      font-size: 0.75rem;
      color: var(--theme-text-primary);
      white-space: nowrap;
      animation: slideIn 0.2s ease;
      user-select: none;
      transition: all 0.2s ease;

      &:hover {
        border-color: var(--primary-color);
        background: var(--theme-surface-container-high);
      }

      .filter-icon {
        font-size: 14px;
        width: 14px;
        height: 14px;
        color: var(--theme-text-tertiary);
      }

      .chip-content {
        font-weight: 500;
        max-width: 150px;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .chip-remove {
        width: 18px;
        height: 18px;
        line-height: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        
        .mat-icon {
          font-size: 14px;
          width: 14px;
          height: 14px;
        }

        color: var(--theme-text-secondary);
        &:hover {
          color: var(--mat-sys-error);
          background: rgba(var(--mat-sys-error-rgb), 0.1);
        }
      }
    }

    .clear-all-link {
      height: 1.5rem;
      padding: 0 0.5rem;
      font-size: 0.6875rem;
      color: var(--primary-color);
      font-weight: 600;
      min-width: auto;
      
      &:hover {
        text-decoration: underline;
        background: transparent;
      }
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    @keyframes slideIn {
      from { transform: translateX(-10px); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class FilterChipBarComponent {
    @Input() filters: ActiveFilter[] = [];
    @Output() remove = new EventEmitter<string>();
    @Output() clearAll = new EventEmitter<void>();

    // Icon mapping for known filter types
    private iconMap: Record<string, string> = {
        'machine': 'precision_manufacturing',
        'resource': 'inventory_2',
        'status': 'flag',
        'type': 'category',
        'category': 'category',
        'date': 'calendar_today',
        'user': 'person',
        'tag': 'label',
        'priority': 'priority_high'
    };

    getIcon(filterId: string): string {
        const key = filterId.toLowerCase();
        // Check exact match
        if (this.iconMap[key]) return this.iconMap[key];

        // Check partial match (e.g. 'machine_type' -> 'precision_manufacturing')
        for (const [k, v] of Object.entries(this.iconMap)) {
            if (key.includes(k)) return v;
        }

        return 'filter_alt'; // Default icon
    }

    getShortLabel(filter: ActiveFilter): string {
        // If values are displayed, just show values, otherwise show label: values
        // We want a compact representation
        const values = filter.values.join(', ');
        if (values.length > 20) {
            return `${filter.label}: ${values.substring(0, 18)}...`;
        }
        return `${filter.label}: ${values}`;
    }

    onRemove(filterId: string) {
        this.remove.emit(filterId);
    }

    onClearAll() {
        this.clearAll.emit();
    }
}
