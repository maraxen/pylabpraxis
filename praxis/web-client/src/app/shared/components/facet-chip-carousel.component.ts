import { Component, EventEmitter, Input, Output } from '@angular/core';

import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

export interface ChipOption {
  value: string | number;
  count: number;
  selected?: boolean;
}

@Component({
  selector: 'app-facet-chip-carousel',
  standalone: true,
  imports: [MatChipsModule, MatButtonModule, MatIconModule, MatTooltipModule],
  template: `
    <div class="facet-carousel">
      <div class="label-group">
        <span class="facet-label">{{ label }}:</span>
        @if (allowInvert) {
          <button
            mat-icon-button
            class="invert-btn"
            [class.active]="inverted"
            (click)="toggleInvert()"
            [matTooltip]="inverted ? 'Switch to Include' : 'Switch to Exclude'">
            <mat-icon>{{ inverted ? 'filter_alt_off' : 'filter_alt' }}</mat-icon>
          </button>
        }
      </div>
    
      <div class="chip-scroll-container" (mousedown)="startDrag($event)" (mouseleave)="stopDrag()" (mousemove)="onMouseMove($event)" (mouseup)="stopDrag()">
        <mat-chip-listbox [multiple]="multiple" (change)="onSelectionChange($event)">
          @for (option of options; track option.value) {
            <mat-chip-option
              [value]="option.value"
              [selected]="selectedValues.includes(option.value)"
              class="facet-chip"
              [class.inverted-mode]="inverted">
              {{ formatValue(option.value) }}
              <span class="chip-count">({{ option.count }})</span>
            </mat-chip-option>
          }
        </mat-chip-listbox>
      </div>
    </div>
    `,
  styles: [`
    :host { display: block; }
    
    .facet-carousel {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .label-group {
      display: flex;
      align-items: center;
      gap: 4px;
      min-width: 100px; /* Increased to accommodate button */
    }

    .facet-label {
      font-size: 12px;
      font-weight: 500;
      color: var(--mat-sys-on-surface-variant, #888);
      text-transform: capitalize;
    }

    .invert-btn {
      width: 24px;
      height: 24px;
      line-height: 24px;
      padding: 0;
      
      mat-icon { 
        font-size: 16px; 
        width: 16px; 
        height: 16px;
        color: var(--mat-sys-on-surface-variant);
      }

      &.active mat-icon {
        color: var(--mat-sys-error, #cf6679);
      }
    }

    .chip-scroll-container {
      flex: 1;
      overflow-x: auto;
      scrollbar-width: thin;
      cursor: grab;
      user-select: none;
      padding: 4px 0;

      &:active {
        cursor: grabbing;
      }

      /* Hide scrollbar for cleaner look */
      &::-webkit-scrollbar {
        height: 4px;
      }
      &::-webkit-scrollbar-track {
        background: transparent;
      }
      &::-webkit-scrollbar-thumb {
        background: var(--mat-sys-outline-variant, #444);
        border-radius: 2px;
      }
    }

    mat-chip-listbox {
      display: flex;
      flex-wrap: nowrap;
      gap: 6px;
    }

    .facet-chip {
      font-size: 12px;
      transition: transform 0.15s ease, background-color 0.2s ease;

      &:hover {
        transform: scale(1.02);
      }
      
      &.inverted-mode.mat-mdc-chip-selected {
         --mdc-chip-elevated-container-color: var(--mat-sys-error-container);
         --mdc-chip-label-text-color: var(--mat-sys-on-error-container);
      }
    }

    .chip-count {
      opacity: 0.7;
      font-size: 10px;
      margin-left: 2px;
    }
  `]
})
export class FacetChipCarouselComponent {
  @Input() label = '';
  @Input() options: ChipOption[] = [];
  @Input() selectedValues: (string | number)[] = [];
  @Input() multiple = true;
  @Input() allowInvert = false;
  @Input() inverted = false;

  @Output() selectionChange = new EventEmitter<(string | number)[]>();
  @Output() invertedChange = new EventEmitter<boolean>();

  private isDragging = false;
  private startX = 0;
  private scrollLeft = 0;

  formatValue(value: string | number): string {
    if (typeof value === 'number') {
      return value.toString();
    }
    // Convert snake_case to Title Case
    return value.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }

  onSelectionChange(event: any): void {
    const selected = event.value;
    // MatChipListbox returns a single value or array depending on multiple
    const values = Array.isArray(selected) ? selected : (selected ? [selected] : []);
    this.selectionChange.emit(values);
  }

  toggleInvert() {
    this.inverted = !this.inverted;
    this.invertedChange.emit(this.inverted);
  }

  startDrag(event: MouseEvent): void {
    const container = event.currentTarget as HTMLElement;
    this.isDragging = true;
    this.startX = event.pageX - container.offsetLeft;
    this.scrollLeft = container.scrollLeft;
  }

  stopDrag(): void {
    this.isDragging = false;
  }

  onMouseMove(event: MouseEvent): void {
    if (!this.isDragging) return;
    event.preventDefault();
    const container = event.currentTarget as HTMLElement;
    const x = event.pageX - container.offsetLeft;
    const walk = (x - this.startX) * 1.5;
    container.scrollLeft = this.scrollLeft - walk;
  }
}
