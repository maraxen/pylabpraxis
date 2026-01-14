import { Component, Inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MAT_BOTTOM_SHEET_DATA, MatBottomSheetRef } from '@angular/material/bottom-sheet';
import { PraxisMultiselectComponent } from '../praxis-multiselect/praxis-multiselect.component';
import { ViewControlsConfig, ViewControlsState } from './view-controls.types';

@Component({
    selector: 'app-view-controls-mobile-sheet',
    standalone: true,
    imports: [
        CommonModule,
        MatButtonModule,
        MatIconModule,
        MatDividerModule,
        PraxisMultiselectComponent,
    ],
    template: `
    <div class="mobile-filter-sheet">
      <div class="sheet-header">
        <h3>Filters</h3>
        <button mat-icon-button (click)="close()">
          <mat-icon>close</mat-icon>
        </button>
      </div>
      
      <mat-divider></mat-divider>

      <div class="sheet-content">
        @for (filter of data.config.filters; track filter.key) {
          <div class="filter-section">
            <label class="filter-label">{{ filter.label }}</label>
            <app-praxis-multiselect
              [options]="filter.options || []"
              [value]="localState().filters[filter.key] || []"
              (valueChange)="onFilterChange(filter.key, $event)"
            ></app-praxis-multiselect>
          </div>
        }
      </div>
      
      <div class="sheet-footer">
        <button mat-button (click)="clearAll()">Reset</button>
        <button mat-flat-button color="primary" (click)="apply()">
            Apply
        </button>
      </div>
    </div>
  `,
    styles: [`
    .mobile-filter-sheet {
      display: flex;
      flex-direction: column;
      max-height: 80vh;
      background: var(--theme-surface);
    }

    .sheet-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 16px;
      
      h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
      }
    }

    .sheet-content {
      padding: 16px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .filter-section {
      display: flex;
      flex-direction: column;
      gap: 8px;

      .filter-label {
        font-size: 14px;
        font-weight: 600;
        color: var(--theme-text-secondary);
      }
      
      app-praxis-multiselect {
        width: 100%;
      }
    }

    .sheet-footer {
      padding: 16px;
      display: flex;
      gap: 12px;
      border-top: 1px solid var(--theme-border);
      
      button {
        flex: 1;
      }
    }
  `]
})
export class ViewControlsMobileSheetComponent {
    localState = signal<ViewControlsState>({
        viewType: 'card',
        groupBy: null,
        filters: {},
        sortBy: '',
        sortOrder: 'asc',
        search: ''
    });

    constructor(
        @Inject(MAT_BOTTOM_SHEET_DATA) public data: { config: ViewControlsConfig, state: ViewControlsState },
        private bottomSheetRef: MatBottomSheetRef<ViewControlsMobileSheetComponent>
    ) {
        this.localState.set({ ...this.data.state });
    }

    onFilterChange(key: string, value: unknown[]) {
        this.localState.set({
            ...this.localState(),
            filters: {
                ...this.localState().filters,
                [key]: value
            }
        });
    }

    clearAll() {
        const clearedFilters: Record<string, unknown[]> = {};
        this.data.config.filters?.forEach(f => clearedFilters[f.key] = []);

        this.localState.set({
            ...this.localState(),
            filters: clearedFilters
        });
    }

    apply() {
        this.bottomSheetRef.dismiss(this.localState());
    }

    close() {
        this.bottomSheetRef.dismiss();
    }
}
