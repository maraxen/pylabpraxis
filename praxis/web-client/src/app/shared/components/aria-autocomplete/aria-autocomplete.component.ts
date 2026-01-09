import {
  Combobox,
  ComboboxInput,
  ComboboxPopup,
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
  value: any;
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
    <div
      class="autocomplete-container"
      ngCombobox
      #combobox="ngCombobox"
      [disabled]="disabled"
    >
      <div class="input-wrapper" [class.expanded]="combobox.expanded()">
        <mat-icon class="search-icon">search</mat-icon>
        
        <input
          type="text"
          ngComboboxInput
          class="autocomplete-input"
          [placeholder]="placeholder"
          [attr.aria-label]="label"
          [(ngModel)]="query"
          cdkOverlayOrigin
          #trigger="cdkOverlayOrigin"
        />

        @if (query()) {
          <mat-icon class="clear-icon" (click)="clearQuery($event)">close</mat-icon>
        }

        <mat-icon class="trigger-chevron" (click)="toggle($event)">
          {{ combobox.expanded() ? 'expand_less' : 'expand_more' }}
        </mat-icon>
      </div>

      <!-- Dropdown popup via CDK Overlay -->
      <ng-template
        cdkConnectedOverlay
        [cdkConnectedOverlayOrigin]="trigger"
        [cdkConnectedOverlayOpen]="combobox.expanded()"
        [cdkConnectedOverlayWidth]="triggerWidth()"
        [cdkConnectedOverlayPanelClass]="'aria-autocomplete-panel'"
        [cdkConnectedOverlayPositions]="positions"
        (detach)="combobox.close()"
      >
        <div
          ngComboboxPopup
          ngListbox
          class="select-popup"
          [multi]="false"
          [(values)]="selectedValues"
          (valuesChange)="onValueChange($event)"
          orientation="vertical"
        >
          @for (option of filteredOptions(); track option.label) {
            <div
              ngOption
              [value]="option.value"
              [label]="option.label"
              [disabled]="option.disabled ?? false"
              class="select-option"
              [class.selected]="isSelected(option.value)"
            >
              @if (option.icon) {
                <mat-icon class="option-icon">{{ option.icon }}</mat-icon>
              }
              <span class="option-label">{{ option.label }}</span>
            </div>
          } @empty {
            <div class="no-results">No matches found</div>
          }
        </div>
      </ng-template>
    </div>
  `,
  styles: [
    `
      :host {
        display: inline-block;
        width: 100%;
      }

      .autocomplete-container {
        position: relative;
        width: 100%;
      }

      .input-wrapper {
        display: flex;
        align-items: center;
        width: 100%;
        height: 48px;
        padding: 0 12px;
        border-radius: 8px;
        border: 1px solid var(--mat-sys-outline);
        background-color: var(--mat-sys-surface-container);
        transition: all 0.2s ease;
        gap: 8px;

        &:hover {
          border-color: var(--mat-sys-on-surface);
        }

        &:focus-within, &.expanded {
          border-color: var(--mat-sys-primary);
          box-shadow: 0 0 0 1px var(--mat-sys-primary);
        }
      }

      .search-icon {
        color: var(--mat-sys-on-surface-variant);
        font-size: 20px;
        width: 20px;
        height: 20px;
        flex-shrink: 0;
      }

      .autocomplete-input {
        flex: 1;
        min-width: 0;
        border: none;
        background: transparent;
        color: var(--mat-sys-on-surface);
        font-size: 14px;
        font-family: inherit;
        outline: none;
        height: 100%;

        &::placeholder {
          color: var(--mat-sys-on-surface-variant);
          opacity: 0.7;
        }
      }

      .clear-icon, .trigger-chevron {
        color: var(--mat-sys-on-surface-variant);
        font-size: 20px;
        width: 20px;
        height: 20px;
        cursor: pointer;
        flex-shrink: 0;
        &:hover { color: var(--mat-sys-on-surface); }
      }

      .select-popup {
        background: var(--mat-sys-surface-container);
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        max-height: 300px;
        overflow: hidden;
      }

      .listbox-container {
        max-height: 300px;
        overflow-y: auto;
        padding: 4px 0;
      }

      .select-option {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 16px;
        cursor: pointer;
        color: var(--mat-sys-on-surface);
        font-size: 14px;

        &:hover, &[data-active="true"] {
          background: var(--mat-sys-surface-container-high);
        }

        &.selected {
          background: color-mix(in srgb, var(--mat-sys-primary) 12%, transparent);
          color: var(--mat-sys-primary);
        }
      }

      .option-icon {
        font-size: 18px;
        width: 18px;
        height: 18px;
        color: var(--mat-sys-primary);
      }

      .no-results {
        padding: 12px 16px;
        color: var(--mat-sys-on-surface-variant);
        font-size: 14px;
        font-style: italic;
      }
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
  combobox = viewChild<Combobox<any>>(Combobox);
  /** Reference to the listbox */
  listbox = viewChild<Listbox<any>>(Listbox);
  /** All option elements */
  optionElements = viewChildren<Option<any>>(Option);

  /** Internal query signal */
  query = signal('');

  /** Internal selected values signal */
  selectedValues = signal<any[]>([]);

  /** Overlay positions */
  positions = [
    { originX: 'start' as const, originY: 'bottom' as const, overlayX: 'start' as const, overlayY: 'top' as const },
    { originX: 'start' as const, originY: 'top' as const, overlayX: 'start' as const, overlayY: 'bottom' as const },
  ];

  /** Trigger element width for overlay sizing */
  triggerWidth = signal(300);

  /** Filtered options based on query */
  filteredOptions = computed(() => {
    const q = this.query().toLowerCase();
    if (!q) return this.options;
    return this.options.filter(opt =>
      opt.label.toLowerCase().includes(q)
    );
  });

  // ControlValueAccessor callbacks
  private onChange: (value: any) => void = () => { };
  private onTouched: () => void = () => { };

  constructor(private elementRef: ElementRef) {
    // Scroll to active option when it changes
    afterRenderEffect(() => {
      const option = this.optionElements().find((opt) => opt.active());
      setTimeout(() => option?.element.scrollIntoView({ block: 'nearest' }), 50);
    });

    // Reset scroll when closed
    afterRenderEffect(() => {
      if (!this.combobox()?.expanded()) {
        setTimeout(() => this.listbox()?.element.scrollTo(0, 0), 150);
      }
    });

    // Update trigger width when rendered
    afterRenderEffect(() => {
      const wrapper = this.elementRef.nativeElement.querySelector('.input-wrapper');
      if (wrapper) {
        this.triggerWidth.set(wrapper.offsetWidth);
      }
    });
  }

  toggle(event: MouseEvent) {
    event.stopPropagation();
    event.preventDefault();
    if (this.combobox()?.expanded()) {
      this.combobox()?.close();
    } else {
      this.combobox()?.open();
    }
  }

  clearQuery(event: MouseEvent) {
    event.stopPropagation();
    event.preventDefault();
    this.query.set('');
    this.selectedValues.set([]);
    this.onChange(null);
  }

  isSelected(value: any): boolean {
    // Compare by accession_id if value is an object
    const selected = this.selectedValues();
    if (selected.length === 0) return false;
    const selectedVal = selected[0];
    if (value?.accession_id && selectedVal?.accession_id) {
      return value.accession_id === selectedVal.accession_id;
    }
    return selectedVal === value;
  }

  onValueChange(values: any[]): void {
    const newValue = values.length > 0 ? values[0] : null;
    this.onChange(newValue);
    this.onTouched();

    // Update query to match selected label
    const selectedOption = this.options.find(opt => {
      if (opt.value?.accession_id && newValue?.accession_id) {
        return opt.value.accession_id === newValue.accession_id;
      }
      return opt.value === newValue;
    });
    if (selectedOption) {
      this.query.set(selectedOption.label);
    }

    this.combobox()?.close();
  }

  // ControlValueAccessor implementation
  writeValue(value: any): void {
    this.selectedValues.set(value != null ? [value] : []);
    const selectedOption = this.options.find(opt => {
      if (opt.value?.accession_id && value?.accession_id) {
        return opt.value.accession_id === value.accession_id;
      }
      return opt.value === value;
    });
    if (selectedOption) {
      this.query.set(selectedOption.label);
    } else {
      this.query.set('');
    }
  }

  registerOnChange(fn: (value: any) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }
}
