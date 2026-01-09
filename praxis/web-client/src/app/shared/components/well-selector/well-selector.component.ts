import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Input,
  OnChanges,
  Output,
  SimpleChanges,
  computed,
  signal,
} from '@angular/core';
import { NgClass } from '@angular/common';
import { Grid, GridRow, GridCell, GridCellWidget } from '@angular/aria/grid';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

@Component({
  selector: 'app-well-selector',
  standalone: true,
  imports: [
    Grid,
    GridRow,
    GridCell,
    GridCellWidget,
    NgClass,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
  ],
  template: `
    <div class="well-selector-container">
      <div class="controls">
        <button
          mat-stroked-button
          type="button"
          (click)="clearSelection()"
          [disabled]="selectedWellsSet().size === 0"
        >
          Clear Selection
        </button>
        <button mat-stroked-button type="button" (click)="invertSelection()">
          Invert Selection
        </button>
      </div>

      <!-- ARIA Grid -->
      <div
        grid
        [attr.aria-label]="'Well Selector'"
        class="plate-grid"
        [style.--cols]="cols"
      >
        <!-- Header Row (Column Labels) -->
        <div gridRow class="header-row">
          <div gridCell class="corner-cell"></div>
          @for (col of colLabels(); track col) {
            <div gridCell class="header-cell column-label">{{ col }}</div>
          }
        </div>

        @for (row of rowLabels(); track row) {
          <div gridRow class="plate-row">
            <!-- Row Label -->
            <div gridCell class="header-cell row-label">{{ row }}</div>

            @for (col of colLabels(); track col) {
              @let wellId = row + col;
              <div
                gridCell
                class="well-cell"
                [class.selected]="isSelected(wellId)"
                [class.dragging]="isDragging"
                (mousedown)="onMouseDown(wellId, $event)"
                (mouseenter)="onMouseEnter(wellId)"
              >
                <div gridCellWidget>
                  <div
                    class="well-circle"
                    [matTooltip]="wellId"
                    [class.has-selection]="isSelected(wellId)"
                  ></div>
                </div>
              </div>
            }
          </div>
        }
      </div>
    </div>
  `,
  styles: [`
    .well-selector-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 16px;
      background-color: var(--mat-sys-surface);
      border-radius: 8px;
    }

    .controls {
      display: flex;
      gap: 8px;
      justify-content: flex-end;
    }

    .plate-grid {
      display: grid;
      /* 1 for row label + cols columns. --cols is passed from inline style */
      grid-template-columns: 32px repeat(var(--cols, 12), 1fr);
      gap: 4px;
      user-select: none;
      padding: 8px;
      background-color: var(--mat-sys-surface-container-low);
      border-radius: 8px;
    }

    /* Ensure grid roles don't break CSS Grid layout */
    div[gridRow] {
      display: contents;
    }

    .header-cell {
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 500;
      color: var(--mat-sys-on-surface-variant);
      font-size: 13px;
      min-height: 32px;
    }

    .well-cell {
      position: relative;
      aspect-ratio: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      border-radius: 50%;
      border: 1px solid var(--mat-sys-outline-variant);
      background-color: var(--mat-sys-surface);
      transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
      outline: none;

      &:hover {
        background-color: var(--mat-sys-surface-container-high);
        border-color: var(--mat-sys-outline);
        transform: scale(1.05);
        z-index: 1;
      }

      &.dragging:hover {
        transform: none; /* Reduce movement during drag */
      }

      &.selected {
        background-color: var(--mat-sys-primary-container);
        border-color: var(--mat-sys-primary);

        .well-circle.has-selection {
          background-color: var(--mat-sys-primary);
          transform: scale(0.6);
        }
      }

      /* Focus styles for keyboard accessibility */
      &:focus-visible {
        outline: 2px solid var(--mat-sys-primary);
        outline-offset: 2px;
        z-index: 2;
      }
    }

    .well-circle {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); /* Smooth animation */
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    '(window:mouseup)': 'onMouseUp()',
    '(mouseleave)': 'onMouseUp()',
  },
})
export class WellSelectorComponent implements OnChanges {
  @Input() rows = 8;
  @Input() cols = 12;
  @Input() selectedWells: string[] = [];
  @Output() selectionChange = new EventEmitter<string[]>();

  protected readonly selectedWellsSet = signal(new Set<string>());

  readonly rowLabels = computed(() =>
    Array.from({ length: this.rows }, (_, i) => String.fromCharCode(65 + i))
  );

  readonly colLabels = computed(() =>
    Array.from({ length: this.cols }, (_, i) => i + 1)
  );

  isDragging = false;
  private startState = false;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['selectedWells']) {
      this.selectedWellsSet.set(new Set(this.selectedWells || []));
    }
  }

  isSelected(well: string): boolean {
    return this.selectedWellsSet().has(well);
  }

  onMouseDown(well: string, event: MouseEvent): void {
    if (event.button !== 0) return;
    event.preventDefault();

    this.isDragging = true;
    const currentSet = this.selectedWellsSet();
    this.startState = !currentSet.has(well);
    this.updateWell(well, this.startState);
  }

  onMouseEnter(well: string): void {
    if (this.isDragging) {
      this.updateWell(well, this.startState);
    }
  }

  onMouseUp(): void {
    this.isDragging = false;
  }

  private updateWell(well: string, select: boolean): void {
    const currentSet = new Set(this.selectedWellsSet());
    if (select) {
      if (!currentSet.has(well)) {
        currentSet.add(well);
        this.emitChange(currentSet);
      }
    } else {
      if (currentSet.has(well)) {
        currentSet.delete(well);
        this.emitChange(currentSet);
      }
    }
  }

  clearSelection(): void {
    if (this.selectedWellsSet().size > 0) {
      this.emitChange(new Set());
    }
  }

  invertSelection(): void {
    const newSet = new Set<string>();
    const currentSet = this.selectedWellsSet();

    for (const r of this.rowLabels()) {
      for (const c of this.colLabels()) {
        const well = `${r}${c}`;
        if (!currentSet.has(well)) {
          newSet.add(well);
        }
      }
    }
    this.emitChange(newSet);
  }

  private emitChange(set: Set<string>): void {
    this.selectedWellsSet.set(set);
    this.selectionChange.emit(Array.from(set));
  }
}
