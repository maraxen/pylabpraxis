import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';

@Component({
    selector: 'app-parameter-viewer',
    standalone: true,
    imports: [CommonModule, MatIconModule, MatDividerModule, MatTooltipModule],
    template: `
    <div class="parameter-viewer">
      @if (parameters() && hasKeys(parameters())) {
        <div class="parameter-grid">
          @for (item of flattenParameters(parameters()); track item.path) {
            <div class="parameter-item" [style.padding-left.px]="item.level * 16">
              <div class="parameter-content">
                <span class="parameter-key" [class.parent]="item.isParent">
                  {{ item.key }}
                </span>
                @if (!item.isParent) {
                  <span class="parameter-value" [ngClass]="getValueClass(item.value)">
                    {{ formatValue(item.value) }}
                  </span>
                }
              </div>
              @if (item.isParent) {
                <mat-divider class="parent-divider"></mat-divider>
              }
            </div>
          }
        </div>
      } @else {
        <div class="empty-params">
          <mat-icon>info_outline</mat-icon>
          <span>No parameters provided</span>
        </div>
      }
    </div>
  `,
    styles: [`
    .parameter-viewer {
      background: var(--sys-surface-container-low);
      border-radius: 8px;
      overflow: hidden;
    }

    .parameter-grid {
      display: flex;
      flex-direction: column;
    }

    .parameter-item {
      padding: 8px 16px;
      border-bottom: 1px solid var(--sys-outline-variant);
      transition: background-color 0.2s;
    }

    .parameter-item:last-child {
      border-bottom: none;
    }

    .parameter-item:hover:not(:has(.parent)) {
      background-color: var(--sys-surface-container-high);
    }

    .parameter-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }

    .parameter-key {
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--sys-on-surface-variant);
      font-family: 'Inter', sans-serif;
    }

    .parameter-key.parent {
      color: var(--sys-primary);
      text-transform: uppercase;
      font-size: 0.75rem;
      letter-spacing: 0.05em;
      font-weight: 700;
      padding-top: 8px;
    }

    .parent-divider {
      margin-top: 4px;
      border-color: var(--sys-primary-container);
      opacity: 0.5;
    }

    .parameter-value {
      font-size: 0.875rem;
      font-family: 'Fira Code', monospace;
      font-weight: 600;
      word-break: break-all;
      text-align: right;
    }

    .value-number { color: var(--sys-primary); }
    .value-boolean { color: var(--sys-tertiary); }
    .value-string { color: var(--sys-on-surface); }
    .value-null { color: var(--sys-outline); font-style: italic; }

    .empty-params {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 16px;
      color: var(--sys-on-surface-variant);
      font-style: italic;
      font-size: 0.875rem;
    }

    .empty-params mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
    }
  `]
})
export class ParameterViewerComponent {
    parameters = input<Record<string, any> | null | undefined>(null);

    hasKeys(obj: any): boolean {
        return !!obj && Object.keys(obj).length > 0;
    }

    flattenParameters(obj: any, prefix = '', level = 0): Array<{ key: string, value: any, path: string, level: number, isParent: boolean }> {
        let result: Array<any> = [];
        const keys = Object.keys(obj || {});

        for (const key of keys) {
            const val = obj[key];
            const path = prefix ? `${prefix}.${key}` : key;
            const isObject = typeof val === 'object' && val !== null && !Array.isArray(val);

            if (isObject) {
                result.push({ key, value: null, path, level, isParent: true });
                result = [...result, ...this.flattenParameters(val, path, level + 1)];
            } else {
                result.push({ key, value: val, path, level, isParent: false });
            }
        }

        return result;
    }

    formatValue(value: any): string {
        if (value === null || value === undefined) return 'null';
        if (Array.isArray(value)) return `[ ${value.join(', ')} ]`;
        return String(value);
    }

    getValueClass(value: any): string {
        if (value === null || value === undefined) return 'value-null';
        if (typeof value === 'number') return 'value-number';
        if (typeof value === 'boolean') return 'value-boolean';
        return 'value-string';
    }
}
