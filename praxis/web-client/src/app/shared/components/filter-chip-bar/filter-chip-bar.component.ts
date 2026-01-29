import { Component, ChangeDetectionStrategy, Input, Output, EventEmitter, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ActiveFilter } from '../view-controls/view-controls.types';

/** Flattened chip representing a single filter value */
export interface FilterChip<T = unknown> {
    filterId: string;
    filterLabel: string;
    value: T;
    displayValue: string;
    icon: string;
}

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
    <div class="filter-chip-bar" [class.has-filters]="chips().length > 0">
      @if (chips().length > 0) {
        <span class="active-label">Active:</span>
        <div class="chips-scroll-container">
          @for (chip of chips(); track chip.filterId + '-' + chip.displayValue) {
            <div class="filter-chip"
                 [matTooltip]="chip.filterLabel + ': ' + chip.displayValue"
                 matTooltipPosition="above">
              <mat-icon class="filter-icon">{{ chip.icon }}</mat-icon>
              <span class="chip-label">{{ chip.displayValue }}</span>
              <mat-icon class="chip-remove" (click)="onRemoveValue(chip)">close</mat-icon>
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
        background: var(--theme-surface-subtle, rgba(0,0,0,0.02));
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
      gap: 6px;
      overflow-x: auto;
      flex: 1;
      padding-bottom: 2px;

      &::-webkit-scrollbar {
        height: 4px;
      }
      &::-webkit-scrollbar-thumb {
        background-color: var(--mat-sys-outline-variant);
        border-radius: 4px;
      }
    }

    .filter-chip {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      height: 24px;
      padding: 2px 6px;
      background: var(--mat-sys-surface-container-high);
      border: 1px solid var(--mat-sys-outline-variant);
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
      white-space: nowrap;
      animation: slideIn 0.15s ease;
      user-select: none;
      transition: all 0.15s ease;
      flex-shrink: 0;

      &:hover {
        border-color: var(--primary-color);
        background: var(--mat-sys-surface-container-highest);
      }

      .filter-icon {
        font-size: 14px;
        width: 14px;
        height: 14px;
        color: var(--primary-color);
        flex-shrink: 0;
      }

      .chip-label {
        // Gradient text styling matching praxis-select
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        max-width: 120px;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .chip-remove {
        font-size: 14px;
        width: 14px;
        height: 14px;
        cursor: pointer;
        color: var(--theme-text-secondary);
        opacity: 0.6;
        flex-shrink: 0;
        transition: all 0.15s ease;

        &:hover {
          opacity: 1;
          color: var(--mat-sys-error);
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
      flex-shrink: 0;

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
      from { transform: translateX(-8px); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class FilterChipBarComponent<T> {
    private _filters = signal<ActiveFilter<T>[]>([]);

    @Input() set filters(value: ActiveFilter<T>[]) {
        this._filters.set(value || []);
    }

    /** Emits { filterId, value } when a specific value is removed */
    @Output() removeValue = new EventEmitter<{ filterId: string; value: T }>();

    /** Emits filterId when the entire filter group should be removed (legacy support) */
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
        'priority': 'priority_high',
        'vendor': 'store',
        'manufacturer': 'factory',
        'plr_category': 'science'
    };

    /** Flatten filters into individual chips - one per value */
    chips = computed<FilterChip<T>[]>(() => {
        const result: FilterChip<T>[] = [];

        for (const filter of this._filters()) {
            const icon = this.getIcon(filter.filterId);

            for (const value of filter.values) {
                result.push({
                    filterId: filter.filterId,
                    filterLabel: filter.label,
                    value: value,
                    displayValue: String(value),
                    icon
                });
            }
        }

        return result;
    });

    private getIcon(filterId: string): string {
        const key = filterId.toLowerCase();

        // Check exact match
        if (this.iconMap[key]) return this.iconMap[key];

        // Check partial match (e.g. 'machine_type' -> 'precision_manufacturing')
        for (const [k, v] of Object.entries(this.iconMap)) {
            if (key.includes(k)) return v;
        }

        return 'filter_alt'; // Default icon
    }

    onRemoveValue(chip: FilterChip): void {
        this.removeValue.emit({ filterId: chip.filterId, value: chip.value as T });
    }

    onClearAll(): void {
        this.clearAll.emit();
    }
}
