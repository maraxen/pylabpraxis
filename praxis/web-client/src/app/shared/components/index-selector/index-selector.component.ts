import {
  Component,
  Input,
  Output,
  EventEmitter,
  OnChanges,
  OnInit,
  OnDestroy,
  SimpleChanges,
  HostListener,
  ChangeDetectionStrategy,
  inject,
} from '@angular/core';
import { NgStyle } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Subscription } from 'rxjs';
import { LinkedSelectorService } from '../../services/linked-selector.service';

/**
 * Specification for an itemized resource grid.
 * Used to define the dimensions and layout of the selector.
 */
export interface ItemizedResourceSpec {
  /** Number of columns (e.g., 12 for 96-well plate) */
  itemsX: number;
  /** Number of rows (e.g., 8 for 96-well plate) */
  itemsY: number;
  /** Optional label for the resource (e.g., "Source Plate") */
  label?: string;
  /** Optional ID to link with other selectors */
  linkId?: string;
}

/**
 * Selection mode for the index selector.
 */
export type SelectionMode = 'single' | 'multiple' | 'range';

/**
 * A reusable component for visually selecting indices from an itemized resource grid.
 * Supports plates, tip racks, tube racks, and other gridded labware.
 *
 * Features:
 * - Click to select single index
 * - Click + drag for rectangular selection
 * - Shift+click to extend selection
 * - Ctrl/Cmd+click to toggle selection
 * - Outputs array of selected flat indices
 */
@Component({
  selector: 'app-index-selector',
  standalone: true,
  imports: [NgStyle, FormsModule, MatButtonModule, MatIconModule, MatTooltipModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="index-selector-container" [class.disabled]="disabled">
      <!-- Label if provided -->
      @if (spec.label) {
        <div class="selector-header">
          <span class="selector-label">{{ spec.label }}</span>
          <span class="selection-summary">{{ getSelectionSummary() }}</span>
        </div>
      }
    
      <!-- Toolbar -->
      <div class="selector-toolbar">
        <button
          mat-icon-button
          (click)="selectAll()"
          [disabled]="disabled"
          matTooltip="Select All"
          >
          <mat-icon>select_all</mat-icon>
        </button>
        <button
          mat-icon-button
          (click)="clearSelection(); emitSelection()"
          [disabled]="disabled"
          matTooltip="Clear Selection"
          >
          <mat-icon>deselect</mat-icon>
        </button>
      </div>
    
      <!-- Grid container with headers -->
      <div class="grid-container" [ngStyle]="getGridStyle()">
        <!-- Column Headers -->
        @if (showColumnLabels) {
          @for (col of columns; track col; let i = $index) {
            <div
              class="column-header"
              [style.grid-column]="i + 2"
              (click)="selectColumn(i)"
              >
              {{ col }}
            </div>
          }
        }
    
        <!-- Row Headers -->
        @if (showRowLabels) {
          @for (row of rows; track row; let i = $index) {
            <div
              class="row-header"
              [style.grid-row]="i + 2"
              (click)="selectRow(i)"
              >
              {{ row }}
            </div>
          }
        }
    
        <!-- Main Grid -->
        <div class="main-grid" [ngStyle]="getInnerGridStyle()">
          @for (row of rows; track row; let rowIdx = $index) {
            <div class="grid-row">
              @for (col of columns; track col; let colIdx = $index) {
                <div
                  class="cell"
                  [class.selected]="selectionGrid[rowIdx]?.[colIdx]"
                  [class.in-drag]="isInDragRect(rowIdx, colIdx)"
                  [class.disabled]="disabled"
                  [title]="getWellId(rowIdx, colIdx)"
                  (click)="onCellClick(rowIdx, colIdx, $event)"
                  (mousedown)="onCellMouseDown(rowIdx, colIdx, $event)"
                  (mouseenter)="onCellMouseEnter(rowIdx, colIdx)"
                ></div>
              }
            </div>
          }
        </div>
      </div>
    
      <!-- Selection info footer -->
      @if (!spec.label) {
        <div class="selector-footer">
          <span class="selection-summary">{{ getSelectionSummary() }}</span>
        </div>
      }
    </div>
    `,
  styles: [`
    :host {
      display: block;
      font-family: var(--mat-font-family, Roboto, sans-serif);
      --selector-primary: var(--mat-primary-color, #3f51b5);
      --selector-selected-bg: var(--mat-primary-color, #3f51b5);
      --selector-selected-fg: white;
      --selector-hover-bg: rgba(63, 81, 181, 0.2);
      --selector-drag-bg: rgba(63, 81, 181, 0.3);
      --selector-border: #e0e0e0;
    }

    .index-selector-container {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .index-selector-container.disabled {
      opacity: 0.6;
      pointer-events: none;
    }

    .selector-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 4px 8px;
    }

    .selector-label {
      font-weight: 500;
      font-size: 14px;
      color: var(--mat-on-surface-variant);
    }

    .selection-summary {
      font-size: 12px;
      color: var(--mat-on-surface-variant, #666);
    }

    .selector-toolbar {
      display: flex;
      gap: 4px;
      margin-bottom: 4px;
    }

    .selector-toolbar button {
      opacity: 0.8;
    }

    .selector-toolbar button:hover {
      opacity: 1;
    }

    .grid-container {
      display: grid;
      gap: 2px;
      padding: 4px;
      background: var(--mat-surface, #fafafa);
      border-radius: 8px;
      border: 1px solid var(--selector-border);
      user-select: none;
    }

    .column-header,
    .row-header {
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      font-weight: 600;
      color: var(--mat-on-surface-variant, #666);
      cursor: pointer;
      transition: background-color 0.15s ease;
      border-radius: 4px;
    }

    .column-header:hover,
    .row-header:hover {
      background: var(--selector-hover-bg);
    }

    .column-header {
      grid-row: 1;
    }

    .row-header {
      grid-column: 1;
    }

    .main-grid {
      display: grid;
      gap: 2px;
      background: var(--mat-surface-container, #fff);
      border-radius: 4px;
      overflow: hidden;
    }

    .grid-row {
      display: contents;
    }

    .cell {
      width: 100%;
      height: 100%;
      min-width: 16px;
      min-height: 16px;
      background: var(--mat-surface-container-high, #f5f5f5);
      border: 1px solid var(--selector-border);
      border-radius: 50%;
      cursor: pointer;
      transition:
        background-color 0.1s ease,
        transform 0.1s ease,
        border-color 0.1s ease;
    }

    .cell:hover:not(.disabled) {
      transform: scale(1.1);
      border-color: var(--selector-primary);
      z-index: 1;
    }

    .cell.selected {
      background: var(--selector-selected-bg);
      border-color: var(--selector-selected-bg);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    .cell.selected:hover:not(.disabled) {
      background: var(--selector-selected-bg);
      filter: brightness(1.1);
    }

    .cell.in-drag:not(.selected) {
      background: var(--selector-drag-bg);
      border-color: var(--selector-primary);
    }

    .cell.disabled {
      cursor: not-allowed;
      opacity: 0.5;
    }

    .selector-footer {
      padding: 4px 8px;
      text-align: center;
    }
  `],
})
export class IndexSelectorComponent implements OnChanges, OnInit, OnDestroy {
  private linkedSelectorService = inject(LinkedSelectorService);
  private linkSubscription?: Subscription;
  private readonly instanceId = `index - selector - ${Math.random().toString(36).substring(2, 9)}`;

  /** Grid specification defining columns and rows */
  @Input() spec: ItemizedResourceSpec = { itemsX: 12, itemsY: 8 };

  /** Currently selected indices (flat indices) */
  @Input() selectedIndices: number[] = [];

  /** Selection mode: single, multiple, or range */
  @Input() mode: SelectionMode = 'multiple';

  /** Whether the selector is disabled */
  @Input() disabled = false;

  /** Optional highlight color for selected cells */
  @Input() selectionColor = 'var(--mat-primary-color, #3f51b5)';

  /** Whether to show row labels (A, B, C...) */
  @Input() showRowLabels = true;

  /** Whether to show column labels (1, 2, 3...) */
  @Input() showColumnLabels = true;

  /** Emits when selection changes */
  @Output() selectionChange = new EventEmitter<number[]>();

  /** Emits the alphanumeric well IDs (e.g., ['A1', 'A2', 'B1']) */
  @Output() wellIdsChange = new EventEmitter<string[]>();

  // Internal state
  rows: string[] = [];
  columns: number[] = [];
  selectionGrid: boolean[][] = [];

  // Drag selection state
  private isDragging = false;
  private dragStartRow = -1;
  private dragStartCol = -1;
  private dragEndRow = -1;
  private dragEndCol = -1;
  private dragAddMode = true; // true = select, false = deselect

  // Track last clicked cell for shift+click
  private lastClickedRow = -1;
  private lastClickedCol = -1;

  constructor() {
    this.initializeGrid();
  }

  ngOnInit(): void {
    // Register with linked selector service if linkId is provided
    if (this.spec.linkId) {
      this.linkedSelectorService.registerSelector(this.spec.linkId, this.instanceId);

      // Subscribe to selection changes from linked selectors
      this.linkSubscription = this.linkedSelectorService
        .getSelection$(this.spec.linkId, this.instanceId)
        .subscribe(indices => {
          this.selectedIndices = indices;
          this.syncGridFromIndices();
        });
    }
  }

  ngOnDestroy(): void {
    // Unregister from linked selector service
    if (this.spec.linkId) {
      this.linkedSelectorService.unregisterSelector(this.spec.linkId, this.instanceId);
    }
    this.linkSubscription?.unsubscribe();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['spec']) {
      this.initializeGrid();

      // Re-register if linkId changed
      if (changes['spec'].previousValue?.linkId !== changes['spec'].currentValue?.linkId) {
        const prevLinkId = changes['spec'].previousValue?.linkId;
        if (prevLinkId) {
          this.linkedSelectorService.unregisterSelector(prevLinkId, this.instanceId);
          this.linkSubscription?.unsubscribe();
        }

        const newLinkId = changes['spec'].currentValue?.linkId;
        if (newLinkId) {
          this.linkedSelectorService.registerSelector(newLinkId, this.instanceId);
          this.linkSubscription = this.linkedSelectorService
            .getSelection$(newLinkId, this.instanceId)
            .subscribe(indices => {
              this.selectedIndices = indices;
              this.syncGridFromIndices();
            });
        }
      }
    }
    if (changes['selectedIndices']) {
      this.syncGridFromIndices();
    }
  }

  /**
   * Initialize the grid based on the spec.
   */
  private initializeGrid(): void {
    const { itemsX, itemsY } = this.spec;

    // Generate row labels (A, B, C, ... for up to 26 rows, then AA, AB, etc.)
    this.rows = Array.from({ length: itemsY }, (_, i) => this.indexToRowLabel(i));

    // Generate column labels (1, 2, 3, ...)
    this.columns = Array.from({ length: itemsX }, (_, i) => i + 1);

    // Initialize selection grid
    this.selectionGrid = Array.from({ length: itemsY }, () =>
      Array.from({ length: itemsX }, () => false)
    );

    // Sync existing selection
    this.syncGridFromIndices();
  }

  /**
   * Convert row index to label (0 -> A, 1 -> B, ..., 25 -> Z, 26 -> AA)
   */
  private indexToRowLabel(index: number): string {
    if (index < 26) {
      return String.fromCharCode('A'.charCodeAt(0) + index);
    }
    // For larger grids (>26 rows)
    const first = Math.floor(index / 26) - 1;
    const second = index % 26;
    return String.fromCharCode('A'.charCodeAt(0) + first) +
      String.fromCharCode('A'.charCodeAt(0) + second);
  }

  /**
   * Sync the selection grid from the input indices array.
   */
  private syncGridFromIndices(): void {
    const { itemsX, itemsY } = this.spec;

    // Clear grid
    for (let r = 0; r < itemsY; r++) {
      for (let c = 0; c < itemsX; c++) {
        if (this.selectionGrid[r]) {
          this.selectionGrid[r][c] = false;
        }
      }
    }

    // Set selected cells
    for (const flatIndex of this.selectedIndices) {
      const row = Math.floor(flatIndex / itemsX);
      const col = flatIndex % itemsX;
      if (row >= 0 && row < itemsY && col >= 0 && col < itemsX) {
        if (this.selectionGrid[row]) {
          this.selectionGrid[row][col] = true;
        }
      }
    }
  }

  /**
   * Convert row and column to flat index.
   */
  private toFlatIndex(row: number, col: number): number {
    return row * this.spec.itemsX + col;
  }

  /**
   * Get the well ID string (e.g., "A1") for a row and column.
   */
  getWellId(row: number, col: number): string {
    return `${this.rows[row]}${this.columns[col]}`;
  }

  /**
   * Handle cell click.
   */
  onCellClick(row: number, col: number, event: MouseEvent): void {
    if (this.disabled) return;

    event.preventDefault();

    if (this.mode === 'single') {
      // Single selection mode - clear all and select one
      this.clearSelection();
      this.selectionGrid[row][col] = true;
    } else if (event.shiftKey && this.lastClickedRow >= 0) {
      // Shift+click: select range from last clicked to current
      this.selectRange(this.lastClickedRow, this.lastClickedCol, row, col);
    } else if (event.ctrlKey || event.metaKey) {
      // Ctrl/Cmd+click: toggle selection
      this.selectionGrid[row][col] = !this.selectionGrid[row][col];
    } else {
      // Regular click in multiple mode
      if (!this.isDragging) {
        // Clear previous selection and start new
        this.clearSelection();
        this.selectionGrid[row][col] = true;
      }
    }

    this.lastClickedRow = row;
    this.lastClickedCol = col;
    this.emitSelection();
  }

  /**
   * Handle mouse down for drag selection.
   */
  onCellMouseDown(row: number, col: number, event: MouseEvent): void {
    if (this.disabled || event.button !== 0) return;

    this.isDragging = true;
    this.dragStartRow = row;
    this.dragStartCol = col;
    this.dragEndRow = row;
    this.dragEndCol = col;

    // Determine if we're adding or removing based on the cell state
    this.dragAddMode = !this.selectionGrid[row][col];

    event.preventDefault();
  }

  /**
   * Handle mouse enter during drag.
   */
  onCellMouseEnter(row: number, col: number): void {
    if (!this.isDragging || this.disabled) return;

    this.dragEndRow = row;
    this.dragEndCol = col;

    // Update visual feedback during drag
    this.updateDragSelection();
  }

  /**
   * Handle global mouse up to end drag.
   */
  @HostListener('document:mouseup', ['$event'])
  onMouseUp(_event: MouseEvent): void {
    if (!this.isDragging) return;

    // Finalize drag selection
    this.finalizeDragSelection();
    this.isDragging = false;
    this.emitSelection();
  }

  /**
   * Update selection during drag (visual feedback).
   */
  private updateDragSelection(): void {
    // This method can be used to show drag preview
    // Currently handled by CSS highlighting
  }

  /**
   * Finalize the drag selection.
   */
  private finalizeDragSelection(): void {
    const minRow = Math.min(this.dragStartRow, this.dragEndRow);
    const maxRow = Math.max(this.dragStartRow, this.dragEndRow);
    const minCol = Math.min(this.dragStartCol, this.dragEndCol);
    const maxCol = Math.max(this.dragStartCol, this.dragEndCol);

    for (let r = minRow; r <= maxRow; r++) {
      for (let c = minCol; c <= maxCol; c++) {
        this.selectionGrid[r][c] = this.dragAddMode;
      }
    }
  }

  /**
   * Select a range of cells between two corners.
   */
  private selectRange(
    startRow: number,
    startCol: number,
    endRow: number,
    endCol: number
  ): void {
    const minRow = Math.min(startRow, endRow);
    const maxRow = Math.max(startRow, endRow);
    const minCol = Math.min(startCol, endCol);
    const maxCol = Math.max(startCol, endCol);

    for (let r = minRow; r <= maxRow; r++) {
      for (let c = minCol; c <= maxCol; c++) {
        this.selectionGrid[r][c] = true;
      }
    }
  }

  /**
   * Clear all selections.
   */
  clearSelection(): void {
    for (let r = 0; r < this.spec.itemsY; r++) {
      for (let c = 0; c < this.spec.itemsX; c++) {
        if (this.selectionGrid[r]) {
          this.selectionGrid[r][c] = false;
        }
      }
    }
  }

  /**
   * Select all cells.
   */
  selectAll(): void {
    if (this.disabled) return;

    for (let r = 0; r < this.spec.itemsY; r++) {
      for (let c = 0; c < this.spec.itemsX; c++) {
        if (this.selectionGrid[r]) {
          this.selectionGrid[r][c] = true;
        }
      }
    }
    this.emitSelection();
  }

  /**
   * Select a row.
   */
  selectRow(row: number): void {
    if (this.disabled) return;

    for (let c = 0; c < this.spec.itemsX; c++) {
      this.selectionGrid[row][c] = true;
    }
    this.emitSelection();
  }

  /**
   * Select a column.
   */
  selectColumn(col: number): void {
    if (this.disabled) return;

    for (let r = 0; r < this.spec.itemsY; r++) {
      this.selectionGrid[r][col] = true;
    }
    this.emitSelection();
  }

  /**
   * Check if a cell is in the current drag rectangle.
   */
  isInDragRect(row: number, col: number): boolean {
    if (!this.isDragging) return false;

    const minRow = Math.min(this.dragStartRow, this.dragEndRow);
    const maxRow = Math.max(this.dragStartRow, this.dragEndRow);
    const minCol = Math.min(this.dragStartCol, this.dragEndCol);
    const maxCol = Math.max(this.dragStartCol, this.dragEndCol);

    return row >= minRow && row <= maxRow && col >= minCol && col <= maxCol;
  }

  /**
   * Emit the current selection.
   */
  emitSelection(): void {
    const indices: number[] = [];
    const wellIds: string[] = [];

    for (let r = 0; r < this.spec.itemsY; r++) {
      for (let c = 0; c < this.spec.itemsX; c++) {
        if (this.selectionGrid[r]?.[c]) {
          indices.push(this.toFlatIndex(r, c));
          wellIds.push(this.getWellId(r, c));
        }
      }
    }

    // Sort indices to maintain consistent order
    indices.sort((a, b) => a - b);
    wellIds.sort((a, b) => {
      // Sort by row first, then column
      const aRow = a.match(/[A-Z]+/)?.[0] ?? '';
      const bRow = b.match(/[A-Z]+/)?.[0] ?? '';
      const aCol = parseInt(a.replace(/[A-Z]+/, ''), 10);
      const bCol = parseInt(b.replace(/[A-Z]+/, ''), 10);

      if (aRow !== bRow) return aRow.localeCompare(bRow);
      return aCol - bCol;
    });

    this.selectionChange.emit(indices);
    this.wellIdsChange.emit(wellIds);

    // Broadcast to linked selectors
    if (this.spec.linkId) {
      this.linkedSelectorService.updateSelection(this.spec.linkId, this.instanceId, indices);
    }
  }

  /**
   * Get the selection summary text.
   */
  getSelectionSummary(): string {
    const count = this.selectedIndices.length;
    if (count === 0) return 'No selection';
    if (count === 1) return `1 position selected`;
    return `${count} positions selected`;
  }

  /**
   * Get grid style based on spec.
   */
  getGridStyle(): { [key: string]: string } {
    const colWidth = Math.min(40, Math.max(20, 400 / this.spec.itemsX));
    const rowHeight = Math.min(40, Math.max(20, 320 / this.spec.itemsY));

    return {
      'grid-template-columns': `30px repeat(${this.spec.itemsX}, ${colWidth}px)`,
      'grid-template-rows': `30px repeat(${this.spec.itemsY}, ${rowHeight}px)`,
    };
  }

  /**
   * Get inner grid style.
   */
  getInnerGridStyle(): { [key: string]: string } {
    return {
      'grid-template-columns': `repeat(${this.spec.itemsX}, 1fr)`,
      'grid-template-rows': `repeat(${this.spec.itemsY}, 1fr)`,
      'grid-column': `2 / span ${this.spec.itemsX}`,
      'grid-row': `2 / span ${this.spec.itemsY}`,
    };
  }
}
