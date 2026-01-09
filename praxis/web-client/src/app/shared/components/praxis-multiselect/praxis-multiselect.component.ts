import {
  ChangeDetectionStrategy,
  Component,
  Input,
  Output,
  EventEmitter,
  forwardRef,
  signal,
  computed,
  ViewChild,
} from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { MatSelect, MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CommonModule } from '@angular/common';
import { FilterOption } from '../../services/filter-result.service';

/**
 * Praxis Multiselect Component
 * 
 * Replaces AriaMultiselectComponent using MatSelect with multiple selection enabled.
 * Preserves the "Chip" display logic for selected items.
 */
@Component({
  selector: 'app-praxis-multiselect',
  standalone: true,
  imports: [
    CommonModule,
    MatSelectModule,
    MatFormFieldModule,
    MatIconModule,
    MatTooltipModule
  ],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => PraxisMultiselectComponent),
      multi: true,
    },
  ],
  template: `
    <div class="praxis-multiselect-container">
      <mat-form-field appearance="outline" class="praxis-select-field" subscriptSizing="dynamic">
        <mat-select
          #select
          [placeholder]="placeholder || label"
          [disabled]="disabled"
          multiple
          [value]="_currentValues()"
          (selectionChange)="onSelectionChange($event.value)"
          [compareWith]="compareValues"
          panelClass="praxis-select-panel"
        >
          <mat-select-trigger>
            <span class="trigger-label">{{ label || placeholder }}</span>
          </mat-select-trigger>
          
          <!-- Option to Select All (Optional, can be added if needed) -->

          @for (option of options; track option.value) {
            <mat-option [value]="option.value" [disabled]="option.disabled">
              <div class="praxis-option-content">
                @if (option.icon) {
                  <mat-icon class="option-icon">{{ option.icon }}</mat-icon>
                }
                <span class="option-label">{{ option.label }}</span>
                @if (option.count !== undefined) {
                  <span class="option-count">({{ option.count }})</span>
                }
              </div>
            </mat-option>
          }
        </mat-select>
      </mat-form-field>

      <div class="praxis-chip-grid">
        @if (_currentValues().length > 0) {
          @for (val of _currentValues(); track val) {
            <span class="selection-chip">
              <span class="chip-label">{{ getOptionLabel(val) }}</span>
              <mat-icon class="remove-icon" (click)="removeValue(val, $event)">close</mat-icon>
            </span>
          }
        } @else {
          <span class="chip-none">None</span>
        }
      </div>
    </div>
  `,
  styleUrls: [], // Sourced from praxis-select.scss
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PraxisMultiselectComponent implements ControlValueAccessor {
  @Input() label = '';
  @Input() options: FilterOption[] = [];
  @Input() disabled = false;
  @Input() placeholder = '';

  /** Backward-compatible input for initial selection */
  set selectedValue(val: unknown) {
    const values = val != null ? (Array.isArray(val) ? val : [val]) : [];
    this._currentValues.set(values);
  }

  @Input()
  set value(val: unknown) {
    const values = val != null ? (Array.isArray(val) ? val : [val]) : [];
    this._currentValues.set(values);
  }

  @Output() valueChange = new EventEmitter<unknown[]>();

  @Output() selectedValueChange = new EventEmitter<unknown[]>();
  @Output() selectionChange = new EventEmitter<unknown>();

  @ViewChild('select') matSelect!: MatSelect;

  protected _currentValues = signal<unknown[]>([]);

  // ControlValueAccessor callbacks
  private onChange: (value: unknown[]) => void = () => { };
  private onTouched: () => void = () => { };

  /** Computed visible chips (max 2) */
  visibleValues = computed(() => {
    return this._currentValues().slice(0, 2);
  });

  /** Computed overflow count */
  overflowCount = computed(() => Math.max(0, this._currentValues().length - 2));

  /** Computed tooltip for overflow items */
  overflowTooltip = computed(() => {
    return this._currentValues()
      .slice(2)
      .map((v) => this.getOptionLabel(v))
      .join(', ');
  });

  onSelectionChange(values: unknown[]): void {
    this._currentValues.set(values);
    this.onChange(values);
    this.onTouched();
    this.selectedValueChange.emit(values);
    this.valueChange.emit(values);
    this.selectionChange.emit(values);
  }

  getOptionLabel(value: unknown): string {
    const option = this.options.find((opt) => this.compareValues(opt.value, value));
    return option ? option.label : String(value);
  }

  // ControlValueAccessor implementation
  writeValue(value: unknown): void {
    const values = value != null ? (Array.isArray(value) ? value : [value]) : [];
    this._currentValues.set(values);
  }

  registerOnChange(fn: (value: unknown[]) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }

  compareValues(v1: any, v2: any): boolean {
    if (v1 === v2) return true;
    if (typeof v1 === 'object' && v1 !== null && typeof v2 === 'object' && v2 !== null) {
      return (v1.accession_id === v2.accession_id) || (v1.id === v2.id);
    }
    return false;
  }

  /**
   * Clears all selected values
   * Public API potentially used by parents
   */
  clearAll(event?: Event): void {
    event?.stopPropagation();
    this.onSelectionChange([]);
  }

  removeValue(valueToRemove: unknown, event: Event): void {
    event.stopPropagation();
    const current = this._currentValues();
    const newValues = current.filter(v => !this.compareValues(v, valueToRemove));
    this.onSelectionChange(newValues);
  }
}
