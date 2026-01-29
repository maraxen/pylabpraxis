import {
  ChangeDetectionStrategy,
  Component,
  Input,
  forwardRef,
  signal,
  computed,
  effect,
  untracked,
  ChangeDetectorRef,
  inject,
} from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatAutocompleteModule, MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import { MatInputModule } from '@angular/material/input';
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
 * Praxis Autocomplete Component
 * 
 * Replaces AriaAutocompleteComponent using MatAutocomplete.
 */
@Component({
  selector: 'app-praxis-autocomplete',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatAutocompleteModule,
    MatInputModule,
    MatFormFieldModule,
    MatIconModule,
    MatButtonModule,
  ],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => PraxisAutocompleteComponent),
      multi: true,
    },
  ],
  template: `
    <mat-form-field appearance="outline" class="praxis-select-field" subscriptSizing="dynamic">
      <mat-icon matPrefix class="search-icon">search</mat-icon>
      <input
        matInput
        [placeholder]="placeholder"
        [matAutocomplete]="auto"
        [ngModel]="query()"
        (ngModelChange)="onQueryChange($event)"
        [disabled]="disabled"
      />
      @if (query() && !disabled) {
        <button mat-icon-button matSuffix (click)="clearQuery($event)">
          <mat-icon>close</mat-icon>
        </button>
      }
      <mat-autocomplete #auto="matAutocomplete" [displayWith]="displayFn" (optionSelected)="onOptionSelected($event)" panelClass="praxis-select-panel">
        @for (option of filteredOptions(); track option.label) {
          <mat-option [value]="option.value" [disabled]="option.disabled">
            <div class="praxis-option-content">
              @if (option.icon) {
                <mat-icon class="option-icon">{{ option.icon }}</mat-icon>
              }
              <span class="option-label">{{ option.label }}</span>
            </div>
          </mat-option>
        }
        @if (filteredOptions().length === 0 && query()) {
          <mat-option disabled>No matches found</mat-option>
        }
      </mat-autocomplete>
    </mat-form-field>
  `,
  styleUrls: [], // Sourced from praxis-select.scss
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PraxisAutocompleteComponent implements ControlValueAccessor {
  @Input() label = '';
  @Input()
  set options(val: SelectOption[]) {
    this._options.set(val || []);
  }
  get options(): SelectOption[] {
    return this._options();
  }
  @Input() disabled = false;
  @Input() placeholder = 'Search...';

  private cdr = inject(ChangeDetectorRef);
  private _options = signal<SelectOption[]>([]);
  protected _currentValue = signal<unknown>(null);
  query = signal('');

  constructor() {
    // Sync query string whenever value or options change
    effect(() => {
      // We only want this effect to trigger when 'value' or 'options' change
      const val = this._currentValue();
      const opts = this._options();

      untracked(() => {
        if (val != null) {
          const match = opts.find(o => this.compareValues(o.value, val));
          if (match && this.query() !== match.label) {
            this.query.set(match.label);
            this.cdr.markForCheck();
          }
        } else if (this.query() !== '') {
          this.query.set('');
          this.cdr.markForCheck();
        }
      });
    });
  }

  // ControlValueAccessor callbacks
  private onChange: (value: unknown) => void = () => { };
  private onTouched: () => void = () => { };

  /** Filtered options based on query */
  filteredOptions = computed(() => {
    const q = this.query().toLowerCase();
    const opts = this._options();
    if (!q) return opts;
    return opts.filter((opt: SelectOption) =>
      opt.label.toLowerCase().includes(q)
    );
  });

  displayFn = (val: unknown): string => {
    if (val === null || val === undefined) return '';
    const match = this.options.find(o => this.compareValues(o.value, val));
    return match ? match.label : (typeof val === 'string' ? val : '');
  };

  onQueryChange(val: string): void {
    this.query.set(val);
    // If user clears input, we might want to clear selection or just filter.
    // Usually implies clearing selection if it doesn't match, but let's stick to standard autocomplete behavior
    // If strict selection is required, we can enforce it.
    // For now, valid selection happens onOptionSelected.
  }

  onOptionSelected(event: MatAutocompleteSelectedEvent): void {
    const val = event.option.value;
    this._currentValue.set(val);

    // Update Text
    const match = this.options.find(o => this.compareValues(o.value, val));
    if (match) {
      this.query.set(match.label);
    }

    this.onChange(val);
    this.onTouched();
    this.cdr.markForCheck();
  }

  clearQuery(event: Event): void {
    event.stopPropagation();
    this.query.set('');
    this._currentValue.set(null);
    this.onChange(null);
  }

  // ControlValueAccessor implementation
  writeValue(value: unknown): void {
    this._currentValue.set(value);

    // Attempt immediate sync - effect will also handle it when options arrive
    if (value != null) {
      const selectedOption = this.options.find((opt) => this.compareValues(opt.value, value));
      if (selectedOption) {
        this.query.set(selectedOption.label);
      }
    } else {
      this.query.set('');
    }
    this.cdr.markForCheck();
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

  compareValues(v1: unknown, v2: unknown): boolean {
    if (v1 === v2) return true;
    if (typeof v1 === 'object' && v1 !== null && typeof v2 === 'object' && v2 !== null) {
      const a = v1 as { accession_id?: string, id?: string | number };
      const b = v2 as { accession_id?: string, id?: string | number };
      // Check accession_id
      if (a.accession_id && b.accession_id) {
        return a.accession_id === b.accession_id;
      }
      // Check id
      if (a.id && b.id) {
        return a.id === b.id;
      }
    }
    return false;
  }
}
