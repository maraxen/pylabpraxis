/**
 * Well Selector Dialog Component
 *
 * A polished dialog for selecting wells from 96-well or 384-well plates.
 * Uses @angular/aria/grid for accessible keyboard navigation.
 *
 * Features:
 * - Row labels (A-H for 96, A-P for 384) - click to toggle entire row
 * - Column labels (1-12 for 96, 1-24 for 384) - click to toggle entire column
 * - Click-and-drag rectangular selection
 * - Quick actions: Select All, Clear All, Invert Selection
 * - Responsive sizing based on plate type
 * - ARIA-compliant grid for screen reader support
 */
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips';
import { Grid, GridRow, GridCell, GridCellWidget } from '@angular/aria/grid';

/**
 * Data passed to the dialog when opening.
 */
export interface WellSelectorDialogData {
  /** Plate type - determines grid dimensions */
  plateType: '96' | '384';
  /** Initial selection as array of well IDs (e.g., ["A1", "A2", "B1"]) */
  initialSelection: string[];
  /** Selection mode */
  mode: 'single' | 'multi';
  /** Optional title override */
  title?: string;
  /** Optional plate label */
  plateLabel?: string;
}

/**
 * Result returned when the dialog is closed.
 */
export interface WellSelectorDialogResult {
  /** Selected well IDs (e.g., ["A1", "A2", "B1"]) */
  wells: string[];
  /** Whether the user confirmed or cancelled */
  confirmed: boolean;
}

/**
 * Plate configuration derived from plate type.
 */
interface PlateConfig {
  rows: number;
  cols: number;
  cellSize: string;
  labelSize: string;
  showWellLabels: boolean;
}

const PLATE_CONFIGS: Record<'96' | '384', PlateConfig> = {
  '96': {
    rows: 8,
    cols: 12,
    cellSize: '36px',
    labelSize: '11px',
    showWellLabels: true,
  },
  '384': {
    rows: 16,
    cols: 24,
    cellSize: '20px',
    labelSize: '9px',
    showWellLabels: false, // Labels shown on hover only
  },
};

@Component({
  selector: 'app-well-selector-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatDividerModule,
    MatChipsModule,
    Grid,
    GridRow,
    GridCell,
    GridCellWidget,
  ],
  template: `
    <div class="well-selector-dialog" [class.plate-384]="data.plateType === '384'">
      <!-- Header -->
      <h2 mat-dialog-title class="dialog-title">
        <mat-icon class="title-icon">grid_view</mat-icon>
        {{ data.title || 'Select Wells' }}
      </h2>

      <mat-dialog-content class="dialog-content">
        <!-- Plate Label -->
        @if (data.plateLabel) {
          <div class="plate-label">{{ data.plateLabel }}</div>
        }

        <!-- Toolbar -->
        <div class="toolbar">
          <button
            mat-stroked-button
            type="button"
            (click)="selectAll()"
            class="toolbar-btn"
          >
            <mat-icon>select_all</mat-icon>
            Select All
          </button>
          <button
            mat-stroked-button
            type="button"
            (click)="clearSelection()"
            [disabled]="selectedWellsSet().size === 0"
            class="toolbar-btn"
          >
            <mat-icon>deselect</mat-icon>
            Clear All
          </button>
          <button
            mat-stroked-button
            type="button"
            (click)="invertSelection()"
            class="toolbar-btn"
          >
            <mat-icon>flip</mat-icon>
            Invert
          </button>
          <span class="selection-count">
            <mat-icon class="count-icon">check_circle</mat-icon>
            {{ selectedWellsSet().size }} / {{ totalWells }} selected
          </span>
        </div>

        <!-- Plate Grid using ARIA Grid -->
        <div
          class="plate-container"
          (mouseup)="onMouseUp()"
          (mouseleave)="onMouseUp()"
        >
          <table
            ngGrid
            class="plate-grid"
            [style.--cell-size]="config.cellSize"
            [attr.aria-label]="'Well plate grid - ' + data.plateType + ' wells'"
          >
            <!-- Header Row with Column Labels -->
            <tr ngGridRow class="header-row">
              <td ngGridCell class="corner-cell"></td>
              @for (col of colLabels(); track col) {
                <td
                  ngGridCell
                  class="header-cell column-header"
                  [class.active]="isColumnFullySelected(col)"
                >
                  <button
                    ngGridCellWidget
                    type="button"
                    class="header-btn"
                    (click)="toggleColumn(col)"
                    [matTooltip]="'Toggle column ' + col"
                  >
                    {{ col }}
                  </button>
                </td>
              }
            </tr>

            <!-- Data Rows with Wells -->
            @for (row of rowLabels(); track row) {
              <tr ngGridRow class="plate-row">
                <!-- Row Header -->
                <td
                  ngGridCell
                  class="header-cell row-header"
                  [class.active]="isRowFullySelected(row)"
                >
                  <button
                    ngGridCellWidget
                    type="button"
                    class="header-btn"
                    (click)="toggleRow(row)"
                    [matTooltip]="'Toggle row ' + row"
                  >
                    {{ row }}
                  </button>
                </td>

                <!-- Wells -->
                @for (col of colLabels(); track col) {
                  @let wellId = row + col;
                  <td
                    ngGridCell
                    class="well-cell"
                    [class.selected]="isSelected(wellId)"
                    [class.in-drag]="isInDragRect(row, col)"
                    [class.dragging]="isDragging()"
                  >
                    <button
                      ngGridCellWidget
                      type="button"
                      class="well-btn"
                      [class.has-selection]="isSelected(wellId)"
                      (mousedown)="onMouseDown(wellId, row, col, $event)"
                      (mouseenter)="onMouseEnter(wellId, row, col)"
                      [attr.aria-pressed]="isSelected(wellId)"
                      [matTooltip]="wellId"
                      [matTooltipDisabled]="config.showWellLabels"
                    >
                      <span class="well-inner" [class.has-selection]="isSelected(wellId)">
                        @if (config.showWellLabels) {
                          <span class="well-label">{{ wellId }}</span>
                        }
                      </span>
                    </button>
                  </td>
                }
              </tr>
            }
          </table>
        </div>

        <!-- Selection Preview -->
        @if (selectedWellsSet().size > 0 && selectedWellsSet().size <= 24) {
          <div class="selection-preview">
            <span class="preview-label">Selected:</span>
            <div class="chips-container">
              @for (well of sortedSelection().slice(0, 24); track well) {
                <mat-chip
                  class="well-chip"
                  (removed)="removeWell(well)"
                  highlighted
                >
                  {{ well }}
                  <button matChipRemove>
                    <mat-icon>cancel</mat-icon>
                  </button>
                </mat-chip>
              }
              @if (selectedWellsSet().size > 24) {
                <span class="more-indicator">+{{ selectedWellsSet().size - 24 }} more</span>
              }
            </div>
          </div>
        }
      </mat-dialog-content>

      <mat-divider></mat-divider>

      <mat-dialog-actions align="end" class="dialog-actions">
        <button mat-button type="button" (click)="cancel()">
          Cancel
        </button>
        <button
          mat-flat-button
          color="primary"
          type="button"
          (click)="confirm()"
          [disabled]="data.mode === 'single' && selectedWellsSet().size !== 1"
        >
          <mat-icon>check</mat-icon>
          Confirm Selection
        </button>
      </mat-dialog-actions>
    </div>
  `,
  styles: [`
    .well-selector-dialog {
      display: flex;
      flex-direction: column;
      max-width: 100%;
      overflow: hidden;
    }

    .dialog-title {
      display: flex;
      align-items: center;
      gap: 12px;
      margin: 0;
      padding: 20px 24px 16px;
      font-size: 1.25rem;
      font-weight: 500;
      color: var(--mat-sys-on-surface);
    }

    .title-icon {
      color: var(--mat-sys-primary);
    }

    .dialog-content {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 0 24px;
      overflow: auto;
    }

    .plate-label {
      font-size: 14px;
      font-weight: 500;
      color: var(--mat-sys-on-surface-variant);
      text-align: center;
      padding: 4px 0;
    }

    .toolbar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      padding: 8px 0;
    }

    .toolbar-btn {
      font-size: 13px;
    }

    .toolbar-btn mat-icon {
      font-size: 18px;
      height: 18px;
      width: 18px;
      margin-right: 4px;
    }

    .selection-count {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-left: auto;
      padding: 6px 12px;
      background: var(--mat-sys-surface-container);
      border-radius: 16px;
      font-size: 13px;
      font-weight: 500;
      color: var(--mat-sys-on-surface-variant);
    }

    .count-icon {
      font-size: 16px;
      height: 16px;
      width: 16px;
      color: var(--mat-sys-primary);
    }

    .plate-container {
      display: flex;
      justify-content: center;
      padding: 16px 0;
      user-select: none;
      overflow: auto;
    }

    .plate-grid {
      border-spacing: 2px;
      border-collapse: separate;
      padding: 12px;
      background: var(--mat-sys-surface-container-low);
      border-radius: 12px;
      border: 1px solid var(--mat-sys-outline-variant);
    }

    .corner-cell {
      width: 32px;
      height: 28px;
    }

    .header-cell {
      padding: 0;
    }

    .header-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100%;
      background: none;
      border: none;
      font-weight: 600;
      font-size: var(--label-size, 11px);
      color: var(--mat-sys-on-surface-variant);
      cursor: pointer;
      border-radius: 4px;
      transition: all 0.15s ease;
      padding: 0;
    }

    .header-btn:hover {
      background: var(--mat-sys-primary-container);
      color: var(--mat-sys-on-primary-container);
    }

    .header-cell.active .header-btn {
      background: var(--mat-sys-primary);
      color: var(--mat-sys-on-primary);
    }

    .column-header {
      width: var(--cell-size, 36px);
      height: 28px;
    }

    .row-header {
      width: 32px;
      height: var(--cell-size, 36px);
    }

    .well-cell {
      width: var(--cell-size, 36px);
      height: var(--cell-size, 36px);
      padding: 0;
    }

    .well-btn {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      border-radius: 50%;
      border: 2px solid var(--mat-sys-outline-variant);
      background: var(--mat-sys-surface);
      transition: all 0.12s ease;
      position: relative;
      padding: 0;
      outline: none;
    }

    .well-btn:focus-visible {
      outline: 2px solid var(--mat-sys-primary);
      outline-offset: 2px;
    }

    .well-btn:hover:not(:disabled) {
      transform: scale(1.08);
      border-color: var(--mat-sys-primary);
      z-index: 2;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }

    .well-btn.has-selection {
      background: var(--mat-sys-primary-container);
      border-color: var(--mat-sys-primary);
    }

    .well-cell.in-drag .well-btn:not(.has-selection) {
      background: var(--mat-sys-secondary-container);
      border-color: var(--mat-sys-secondary);
      opacity: 0.8;
    }

    .well-inner {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;
    }

    .well-inner.has-selection {
      background: var(--mat-sys-primary);
      transform: scale(0.65);
    }

    .well-label {
      font-size: 9px;
      font-weight: 500;
      color: var(--mat-sys-on-surface-variant);
      pointer-events: none;
    }

    .well-btn.has-selection .well-label {
      color: var(--mat-sys-on-primary);
    }

    /* 384-well plate adjustments */
    .plate-384 .plate-grid {
      --label-size: 9px;
    }

    .plate-384 .corner-cell {
      width: 24px;
      height: 20px;
    }

    .plate-384 .row-header {
      width: 24px;
    }

    .plate-384 .column-header {
      height: 20px;
    }

    .plate-384 .well-btn:hover:not(:disabled) {
      transform: scale(1.15);
    }

    /* Selection Preview */
    .selection-preview {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      padding: 12px;
      background: var(--mat-sys-surface-container);
      border-radius: 8px;
      max-height: 120px;
      overflow-y: auto;
    }

    .preview-label {
      font-size: 13px;
      font-weight: 500;
      color: var(--mat-sys-on-surface-variant);
    }

    .chips-container {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }

    .well-chip {
      font-size: 11px;
      height: 26px;
      --mdc-chip-label-text-size: 11px;
      --mdc-chip-container-height: 26px;
    }

    .more-indicator {
      padding: 4px 8px;
      font-size: 12px;
      color: var(--mat-sys-on-surface-variant);
    }

    /* Dialog Actions */
    .dialog-actions {
      padding: 12px 24px 20px;
      gap: 8px;
    }

    .dialog-actions button mat-icon {
      margin-right: 4px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WellSelectorDialogComponent implements OnInit {
  private dialogRef = inject(MatDialogRef<WellSelectorDialogComponent>);
  public data = inject<WellSelectorDialogData>(MAT_DIALOG_DATA);

  /** Plate configuration */
  config: PlateConfig;

  /** Total number of wells */
  totalWells: number;

  /** Set of selected wells */
  protected readonly selectedWellsSet = signal(new Set<string>());

  /** Row labels computed from config */
  rowLabels = computed(() =>
    Array.from({ length: this.config.rows }, (_, i) =>
      String.fromCharCode(65 + i)
    )
  );

  /** Column labels computed from config */
  colLabels = computed(() =>
    Array.from({ length: this.config.cols }, (_, i) => (i + 1).toString())
  );

  /** Sorted selection for display */
  sortedSelection = computed(() => {
    const wells = Array.from(this.selectedWellsSet());
    return wells.sort((a, b) => {
      const aRow = a.match(/[A-Z]+/)?.[0] ?? '';
      const bRow = b.match(/[A-Z]+/)?.[0] ?? '';
      const aCol = parseInt(a.replace(/[A-Z]+/, ''), 10);
      const bCol = parseInt(b.replace(/[A-Z]+/, ''), 10);
      if (aRow !== bRow) return aRow.localeCompare(bRow);
      return aCol - bCol;
    });
  });

  /** Drag state signals */
  isDragging = signal(false);
  private dragStartRow = '';
  private dragStartCol = '';
  private dragEndRow = '';
  private dragEndCol = '';
  private dragAddMode = true;
  private selectionOnDragStart = new Set<string>();

  constructor() {
    this.config = PLATE_CONFIGS[this.data.plateType || '96'];
    this.totalWells = this.config.rows * this.config.cols;
  }

  ngOnInit(): void {
    // Initialize from initialSelection
    if (this.data.initialSelection?.length > 0) {
      this.selectedWellsSet.set(new Set(this.data.initialSelection));
    }
  }

  /** Check if a well is selected */
  isSelected(wellId: string): boolean {
    return this.selectedWellsSet().has(wellId);
  }

  /** Check if entire row is selected */
  isRowFullySelected(row: string): boolean {
    const cols = this.colLabels();
    return cols.every((col) => this.selectedWellsSet().has(`${row}${col}`));
  }

  /** Check if entire column is selected */
  isColumnFullySelected(col: string): boolean {
    const rows = this.rowLabels();
    return rows.every((row) => this.selectedWellsSet().has(`${row}${col}`));
  }

  /** Toggle entire row */
  toggleRow(row: string): void {
    const cols = this.colLabels();
    const isFullySelected = this.isRowFullySelected(row);
    const newSet = new Set(this.selectedWellsSet());

    cols.forEach((col) => {
      const wellId = `${row}${col}`;
      if (isFullySelected) {
        newSet.delete(wellId);
      } else {
        newSet.add(wellId);
      }
    });

    this.selectedWellsSet.set(newSet);
  }

  /** Toggle entire column */
  toggleColumn(col: string): void {
    const rows = this.rowLabels();
    const isFullySelected = this.isColumnFullySelected(col);
    const newSet = new Set(this.selectedWellsSet());

    rows.forEach((row) => {
      const wellId = `${row}${col}`;
      if (isFullySelected) {
        newSet.delete(wellId);
      } else {
        newSet.add(wellId);
      }
    });

    this.selectedWellsSet.set(newSet);
  }

  /** Select all wells */
  selectAll(): void {
    const newSet = new Set<string>();
    this.rowLabels().forEach((row) => {
      this.colLabels().forEach((col) => {
        newSet.add(`${row}${col}`);
      });
    });
    this.selectedWellsSet.set(newSet);
  }

  /** Clear all selections */
  clearSelection(): void {
    this.selectedWellsSet.set(new Set());
  }

  /** Invert selection */
  invertSelection(): void {
    const currentSet = this.selectedWellsSet();
    const newSet = new Set<string>();

    this.rowLabels().forEach((row) => {
      this.colLabels().forEach((col) => {
        const wellId = `${row}${col}`;
        if (!currentSet.has(wellId)) {
          newSet.add(wellId);
        }
      });
    });

    this.selectedWellsSet.set(newSet);
  }

  /** Remove a single well from selection */
  removeWell(wellId: string): void {
    const newSet = new Set(this.selectedWellsSet());
    newSet.delete(wellId);
    this.selectedWellsSet.set(newSet);
  }

  /** Handle mouse down for drag selection */
  onMouseDown(wellId: string, row: string, col: string, event: MouseEvent): void {
    if (event.button !== 0) return;
    event.preventDefault();

    this.isDragging.set(true);
    this.dragStartRow = row;
    this.dragStartCol = col;
    this.dragEndRow = row;
    this.dragEndCol = col;

    // Capture initial state
    this.selectionOnDragStart = new Set(this.selectedWellsSet());

    // Determine add/remove mode
    this.dragAddMode = !this.selectionOnDragStart.has(wellId);

    // Apply initial change
    this.applyDragSelection();
  }

  /** Handle mouse enter during drag */
  onMouseEnter(wellId: string, row: string, col: string): void {
    if (!this.isDragging()) return;

    this.dragEndRow = row;
    this.dragEndCol = col;

    // Update all wells in drag rectangle
    this.applyDragSelection();
  }

  /** Handle mouse up */
  onMouseUp(): void {
    this.isDragging.set(false);
  }

  /** Check if cell is in current drag rectangle */
  isInDragRect(row: string, col: string): boolean {
    if (!this.isDragging()) return false;

    const rowIdx = this.rowLabels().indexOf(row);
    const colIdx = this.colLabels().indexOf(col);
    const startRowIdx = this.rowLabels().indexOf(this.dragStartRow);
    const endRowIdx = this.rowLabels().indexOf(this.dragEndRow);
    const startColIdx = this.colLabels().indexOf(this.dragStartCol);
    const endColIdx = this.colLabels().indexOf(this.dragEndCol);

    const minRow = Math.min(startRowIdx, endRowIdx);
    const maxRow = Math.max(startRowIdx, endRowIdx);
    const minCol = Math.min(startColIdx, endColIdx);
    const maxCol = Math.max(startColIdx, endColIdx);

    return rowIdx >= minRow && rowIdx <= maxRow && colIdx >= minCol && colIdx <= maxCol;
  }

  /** Apply drag selection to all wells in rectangle */
  private applyDragSelection(): void {
    const rows = this.rowLabels();
    const cols = this.colLabels();
    const startRowIdx = rows.indexOf(this.dragStartRow);
    const endRowIdx = rows.indexOf(this.dragEndRow);
    const startColIdx = cols.indexOf(this.dragStartCol);
    const endColIdx = cols.indexOf(this.dragEndCol);

    const minRow = Math.min(startRowIdx, endRowIdx);
    const maxRow = Math.max(startRowIdx, endRowIdx);
    const minCol = Math.min(startColIdx, endColIdx);
    const maxCol = Math.max(startColIdx, endColIdx);

    // Always start from correct initial state
    const newSet = new Set(this.selectionOnDragStart);

    for (let r = minRow; r <= maxRow; r++) {
      for (let c = minCol; c <= maxCol; c++) {
        const wellId = `${rows[r]}${cols[c]}`;
        if (this.dragAddMode) {
          newSet.add(wellId);
        } else {
          newSet.delete(wellId);
        }
      }
    }

    this.selectedWellsSet.set(newSet);
  }

  /** Update a single well (not used in drag anymore but kept if needed) */
  private updateWell(wellId: string, select: boolean): void {
    const newSet = new Set(this.selectedWellsSet());
    if (select) {
      newSet.add(wellId);
    } else {
      newSet.delete(wellId);
    }
    this.selectedWellsSet.set(newSet);
  }

  /** Cancel and close dialog */
  cancel(): void {
    const result: WellSelectorDialogResult = {
      wells: [],
      confirmed: false,
    };
    this.dialogRef.close(result);
  }

  /** Confirm selection and close dialog */
  confirm(): void {
    const result: WellSelectorDialogResult = {
      wells: this.sortedSelection(),
      confirmed: true,
    };
    this.dialogRef.close(result);
  }
}
