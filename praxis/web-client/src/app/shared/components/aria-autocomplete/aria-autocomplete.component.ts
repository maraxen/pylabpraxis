import {
  Combobox,
  ComboboxInput,
  ComboboxPopup,
  ComboboxPopupContainer,
} from '@angular/aria/combobox';
import { Listbox, Option } from '@angular/aria/listbox';
import {
  afterRenderEffect,
  ChangeDetectionStrategy,
  Component,
  computed,
  ElementRef,
  forwardRef,
  Input,
  signal,
  viewChild,
  viewChildren,
} from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, FormsModule } from '@angular/forms';
import { OverlayModule } from '@angular/cdk/overlay';
import { MatIconModule } from '@angular/material/icon';

export interface SelectOption {
  label: string;
  value: unknown;
  icon?: string;
  disabled?: boolean;
}

/**
 * ARIA-compliant autocomplete component using @angular/aria primitives.
 * Provides a searchable input field with a filtered dropdown.
 */
@Component({
  selector: 'app-aria-autocomplete',
  standalone: true,
  imports: [
    Combobox,
    ComboboxInput,
    ComboboxPopup,
    ComboboxPopupContainer,
    Listbox,
    Option,
    OverlayModule,
    MatIconModule,
    FormsModule,
  ],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => AriaAutocompleteComponent),
      multi: true,
    },
  ],
  template: `
    <div ngCombobox class="aria-autocomplete-container" filterMode="auto-select">
      <div #origin class="input-wrapper">
        <mat-icon class="search-icon">search</mat-icon>
        <input
          [attr.aria-label]="label"
          [placeholder]="placeholder"
          [(ngModel)]="query"
          ngComboboxInput
        />
        @if (query()) {
          <mat-icon class="clear-icon" (click)="clearQuery($event)">close</mat-icon>
        }
      </div>

      <ng-template ngComboboxPopupContainer>
        <ng-template
          [cdkConnectedOverlay]="{origin, usePopover: 'inline', matchWidth: true}"
          [cdkConnectedOverlayOpen]="true"
        >
          <div class="aria-autocomplete-panel">
            @if (filteredOptions().length === 0) {
              <div class="no-results">No matches found</div>
            }
            <div ngListbox>
              @for (option of filteredOptions(); track option.label) {
                <div
                  ngOption
                  [value]="option.value"
                  [label]="option.label"
                  [disabled]="option.disabled ?? false"
                  class="aria-option"
                >
                  @if (option.icon) {
                    <mat-icon class="option-icon">{{ option.icon }}</mat-icon>
                  }
                  <span class="option-label">{{ option.label }}</span>
                  <mat-icon class="option-check">check</mat-icon>
                </div>
              }
            </div>
          </div>
        </ng-template>
      </ng-template>
    </div>
  `,
  styles: [
    `
      :host {
        display: inline-block;
        width: 100%;
      }
      
      // Additional specific styles not covered by shared SCSS can remain here if needed
      // Currently all styles are moved to aria-select.scss
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AriaAutocompleteComponent implements ControlValueAccessor {
  @Input() label = '';
  @Input() options: SelectOption[] = [];
  @Input() disabled = false;
  @Input() placeholder = 'Search...';

  /** Reference to the combobox directive */
  combobox = viewChild<Combobox<unknown>>(Combobox);
  /** Reference to the listbox */
  listbox = viewChild<Listbox<unknown>>(Listbox);
  /** All option elements */
  optionElements = viewChildren<Option<unknown>>(Option);

  /** Query signal for filtering */
  query = signal('');

  // ControlValueAccessor callbacks
  private onChange: (value: unknown) => void = () => { };
  private onTouched: () => void = () => { };

  /** Filtered options based on query */
  filteredOptions = computed(() => {
    const q = this.query().toLowerCase();
    if (!q) return this.options;
    return this.options.filter((opt) =>
      opt.label.toLowerCase().includes(q)
    );
  });

  constructor(private elementRef: ElementRef) {
    // Scrolls to active option when it changes
    afterRenderEffect(() => {
      const option = this.optionElements().find((opt) => opt.active());
      setTimeout(() => option?.element.scrollIntoView({ block: 'nearest' }), 50);
    });

    // Resets listbox scroll when closed
    afterRenderEffect(() => {
      if (!this.combobox()?.expanded()) {
        setTimeout(() => this.listbox()?.element.scrollTo(0, 0), 150);
      }
    });

    // Watch for value changes and propagate to form
    afterRenderEffect(() => {
      const values = this.listbox()?.values() || [];
      const newValue = values.length > 0 ? values[0] : null;

      // Update query to match selected label
      if (newValue) {
        const selectedOption = this.options.find((opt) => {
          if (typeof opt.value === 'object' && opt.value !== null &&
            typeof newValue === 'object' && newValue !== null) {
            return (opt.value as { accession_id?: string }).accession_id ===
              (newValue as { accession_id?: string }).accession_id;
          }
          return opt.value === newValue;
        });
        if (selectedOption) {
          this.query.set(selectedOption.label);
        }
      }

      this.onChange(newValue);
      this.onTouched();
    });
  }

  clearQuery(event: MouseEvent): void {
    event.stopPropagation();
    event.preventDefault();
    this.query.set('');
    // Clear selection
    this.listbox()?.values.set([]);
    this.onChange(null);
  }

  // ControlValueAccessor implementation
  writeValue(value: unknown): void {
    if (value != null) {
      const selectedOption = this.options.find((opt) => {
        if (typeof opt.value === 'object' && opt.value !== null &&
          typeof value === 'object' && value !== null) {
          return (opt.value as { accession_id?: string }).accession_id ===
            (value as { accession_id?: string }).accession_id;
        }
        return opt.value === value;
      });
      if (selectedOption) {
        this.query.set(selectedOption.label);
      }
    } else {
      this.query.set('');
    }
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
}
