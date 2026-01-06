import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { NgStyle } from '@angular/common';

// Define the type for the input data for better type safety.
export type PlateData = { [well: string]: number };

@Component({
  selector: 'app-plate-heatmap',
  standalone: true,
  imports: [NgStyle],
  templateUrl: './plate-heatmap.component.html',
  styleUrls: ['./plate-heatmap.component.scss'],
})
export class PlateHeatmapComponent implements OnChanges {
  // Input data for the heatmap. Expected format: { 'A1': 0.5, 'B2': 1.0, ... }
  @Input() data: PlateData = {};

  // Grid dimensions
  public readonly rows: string[] = Array.from({ length: 8 }, (_, i) => String.fromCharCode('A'.charCodeAt(0) + i)); // A-H
  public readonly columns: number[] = Array.from({ length: 12 }, (_, i) => i + 1); // 1-12

  // Internal representation of the plate data for easy access in the template.
  public plateGrid: (number | null)[][] = [];

  constructor() {
    this.updateGrid();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['data']) {
      this.updateGrid();
    }
  }

  /**
   * Updates the internal plateGrid based on the input data.
   */
  private updateGrid(): void {
    this.plateGrid = this.rows.map(row =>
      this.columns.map(col => {
        const wellId = `${row}${col}`;
        const value = this.data[wellId];
        return typeof value === 'number' && !isNaN(value) ? value : null;
      })
    );
  }

  /**
   * Calculates the background color for a well based on its value (0-1).
   * @param value The numerical value of the well.
   * @returns An HSLA color string.
   */
  public getWellColor(value: number | null): string {
    if (value === null || value < 0 || value > 1) {
      return 'hsla(0, 0%, 95%, 1)'; // Default color for empty or invalid wells
    }
    // Scale hue from blue (240) to red (0)
    const hue = 240 * (1 - value);
    return `hsla(${hue}, 100%, 50%, 1)`;
  }

  /**
   * Generates the tooltip text for a well.
   * @param row The row character (A-H).
   * @param col The column number (1-12).
   * @returns A string for the tooltip, e.g., "A1: 0.75".
   */
  public getTooltip(row: string, col: number): string {
    const wellId = `${row}${col}`;
    const value = this.data[wellId];
    const valueString = (typeof value === 'number' && !isNaN(value)) ? value.toFixed(2) : 'N/A';
    return `${wellId}: ${valueString}`;
  }
}
