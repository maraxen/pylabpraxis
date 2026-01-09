import {
  ChangeDetectionStrategy,
  Component,
  Input,
  forwardRef,
  signal,
  computed,
  Output,
  EventEmitter
} from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';

export interface SelectOption {
  label: string;
  value: unknown;
  icon?: string;
  disabled?: boolean;
}

/**
 * Praxis Select Component
 * 
 * Replaces the previous AriaSelectComponent with a standard Angular Material implementation
 * while preserving the custom aesthetic via CSS overrides in styles/praxis-select.scss.
 */
@Component({
  selector: 'app-praxis-select',
  standalone: true,
  imports: [
    CommonModule,
    MatSelectModule,
    MatFormFieldModule,
    MatIconModule
  ],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => PraxisSelectComponent),
      multi: true,
    },
  ],
  template: `
    <mat-form-field appearance="outline" class="praxis-select-field" subscriptSizing="dynamic">
      <!-- Custom Trigger to display icon + label selection -->
      <mat-select
        [placeholder]="placeholder"
        [disabled]="disabled"
        [value]="_currentValue()"
        (selectionChange)="onSelectionChange($event.value)"
        [compareWith]="compareValues"
        panelClass="praxis-select-panel"
      >
        <mat-select-trigger>
          <div class="praxis-select-trigger-content">
            @if (displayIcon()) {
              <mat-icon class="selected-icon">{{ displayIcon() }}</mat-icon>
            }
            <span class="selected-text">{{ displayValue() }}</span>
          </div>
        </mat-select-trigger>

        @for (option of options; track option.value) {
          <mat-option [value]="option.value" [disabled]="option.disabled">
            <div class="praxis-option-content">
              @if (option.icon) {
                <mat-icon class="option-icon">{{ option.icon }}</mat-icon>
              }
              <span class="option-label">{{ option.label }}</span>
            </div>
          </mat-option>
        }
      </mat-select>
    </mat-form-field>
  `,
  styleUrls: [], // Styles governed by global praxis-select.scss targetting classes
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PraxisSelectComponent implements ControlValueAccessor {
  @Input() label = '';
  @Input() options: SelectOption[] = [];
  @Input() disabled = false;
  @Input() placeholder = 'Select an option';
  @Input()
  set value(val: unknown) {
    this._currentValue.set(val);
  }
  @Output() valueChange = new EventEmitter<unknown>();
  @Output() selectionChange = new EventEmitter<unknown>();

  protected _currentValue = signal<unknown>(null);

  // ControlValueAccessor callbacks
  private onChange: (value: unknown) => void = () => { };
  private onTouched: () => void = () => { };

  /** Computed display value from signal state */
  displayValue = computed(() => {
    const val = this._currentValue();
    if (val === null || val === undefined) {
      return this.placeholder;
    }
    const option = this.options.find((opt) => this.compareValues(opt.value, val));
    return option ? option.label : this.placeholder;
  });

  /** Computed display icon from signal state */
  displayIcon = computed(() => {
    const val = this._currentValue();
    const option = this.options.find((opt) => this.compareValues(opt.value, val));
    return option?.icon || '';
  });

  onSelectionChange(value: unknown): void {
    this._currentValue.set(value);
    this.onChange(value);
    this.onTouched();
    this.valueChange.emit(value);
    this.selectionChange.emit(value);
  }

  // ControlValueAccessor implementation
  writeValue(value: unknown): void {
    this._currentValue.set(value);
  }

  registerOnChange(fn: (value: unknown) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }

  // Custom comparison for objects (e.g. {accession_id: ...})
  compareValues(v1: any, v2: any): boolean {
    if (v1 === v2) return true;
    if (typeof v1 === 'object' && v1 !== null && typeof v2 === 'object' && v2 !== null) {
      // Check specific known ID fields or generic equality
      return (v1.accession_id === v2.accession_id) || (v1.id === v2.id);
    }
    return false;
  }
}
