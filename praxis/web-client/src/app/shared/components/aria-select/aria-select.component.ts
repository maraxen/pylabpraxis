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
  viewChild,
  viewChildren,
} from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { OverlayModule } from '@angular/cdk/overlay';
import { MatIconModule } from '@angular/material/icon';

export interface SelectOption {
  label: string;
  value: unknown;
  icon?: string;
  disabled?: boolean;
}

/**
 * ARIA-compliant single-select component using @angular/aria primitives.
 * Implements ControlValueAccessor for form integration.
 */
@Component({
  selector: 'app-aria-select',
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
  ],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => AriaSelectComponent),
      multi: true,
    },
  ],
  template: `
    <div ngCombobox class="aria-select-container" readonly>
      <div #origin class="aria-select-trigger">
        <span class="combobox-label">
          @if (displayIcon()) {
            <mat-icon class="selected-icon">{{ displayIcon() }}</mat-icon>
          }
          <span class="selected-text">{{ displayValue() }}</span>
        </span>
        <input
          [attr.aria-label]="label"
          [placeholder]="placeholder"
          ngComboboxInput
        />
        <mat-icon class="trigger-chevron">
          {{ combobox()?.expanded() ? 'expand_less' : 'expand_more' }}
        </mat-icon>
      </div>

      <ng-template ngComboboxPopupContainer>
        <ng-template
          [cdkConnectedOverlay]="{origin, usePopover: 'inline', matchWidth: true}"
          [cdkConnectedOverlayOpen]="true"
        >
          <div class="aria-select-panel">
            <div ngListbox>
              @for (option of options; track option.value) {
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
        min-width: 120px;
      }

      .aria-select-trigger {
        display: flex;
        position: relative;
        align-items: center;
      }

      .combobox-label {
        gap: 8px;
        left: 12px;
        display: flex;
        position: absolute;
        align-items: center;
        pointer-events: none;
      }

      [ngComboboxInput] {
        opacity: 0;
        border: none;
        cursor: pointer;
        height: 40px;
        padding: 0 40px 0 12px;
        width: 100%;
      }

      .trigger-chevron {
        right: 8px;
        position: absolute;
        pointer-events: none;
      }

      .option-check {
        font-size: 18px;
        margin-left: auto;
      }

      [ngOption]:not([aria-selected='true']) .option-check {
        display: none;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AriaSelectComponent implements ControlValueAccessor {
  @Input() label = '';
  @Input() options: SelectOption[] = [];
  @Input() disabled = false;
  @Input() placeholder = 'Select an option';

  /** Reference to the combobox directive */
  combobox = viewChild<Combobox<unknown>>(Combobox);
  /** Reference to the listbox */
  listbox = viewChild<Listbox<unknown>>(Listbox);
  /** All option elements */
  optionElements = viewChildren<Option<unknown>>(Option);

  // ControlValueAccessor callbacks
  private onChange: (value: unknown) => void = () => { };
  private onTouched: () => void = () => { };

  /** Computed display value from listbox state */
  displayValue = computed(() => {
    const values = this.listbox()?.values() || [];
    if (values.length === 0) {
      return this.placeholder;
    }
    const option = this.options.find((opt) => opt.value === values[0]);
    return option ? option.label : this.placeholder;
  });

  /** Computed display icon from listbox state */
  displayIcon = computed(() => {
    const values = this.listbox()?.values() || [];
    if (values.length === 0) {
      return '';
    }
    const option = this.options.find((opt) => opt.value === values[0]);
    return option?.icon || '';
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
      this.onChange(newValue);
      this.onTouched();
    });
  }

  // ControlValueAccessor implementation
  writeValue(value: unknown): void {
    // Set initial value on the listbox
    // The listbox will pick this up when it initializes
    if (this.listbox() && value != null) {
      this.listbox()?.values.set([value]);
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
