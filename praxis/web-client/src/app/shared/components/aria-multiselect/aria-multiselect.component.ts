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
  EventEmitter,
  forwardRef,
  Input,
  Output,
  viewChild,
  viewChildren,
} from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { OverlayModule } from '@angular/cdk/overlay';
import { MatIconModule } from '@angular/material/icon';
import { FilterOption } from '../../services/filter-result.service';

/**
 * ARIA-compliant multiselect component using @angular/aria primitives.
 */
@Component({
  selector: 'app-aria-multiselect',
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
      useExisting: forwardRef(() => AriaMultiselectComponent),
      multi: true,
    },
  ],
  template: `
    <div ngCombobox class="aria-multiselect-container" readonly>
      <div #origin class="aria-multiselect-trigger">
        <span class="combobox-label">
          <span class="selected-text">{{ displayLabel() }}</span>
        </span>
        <input
          [attr.aria-label]="label"
          placeholder="Select items"
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
          <div class="aria-multiselect-panel">
            <div ngListbox [multi]="multiple">
              <!-- "All" option to clear selection -->
              <div
                ngOption
                [value]="null"
                label="All"
                class="aria-option"
                (click)="clearSelection()"
              >
                <mat-icon class="option-checkbox">
                  {{ !hasSelection() ? 'check_box' : 'check_box_outline_blank' }}
                </mat-icon>
                <span class="option-label">All</span>
              </div>

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
                  } @else if (multiple) {
                    <mat-icon class="option-checkbox">
                      {{ isSelected(option.value) ? 'check_box' : 'check_box_outline_blank' }}
                    </mat-icon>
                  }
                  <span class="option-label">{{ option.label }}</span>
                  @if (option.count !== undefined) {
                    <span class="option-count">({{ option.count }})</span>
                  }
                  @if (!multiple) {
                    <mat-icon class="option-check">check</mat-icon>
                  }
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
      }

      .aria-multiselect-trigger {
        display: flex;
        position: relative;
        align-items: center;
      }

      .combobox-label {
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
        height: 36px;
        padding: 0 36px 0 12px;
        width: 100%;
      }

      .trigger-chevron {
        right: 8px;
        position: absolute;
        pointer-events: none;
        font-size: 18px;
      }

      .option-count {
        font-size: 12px;
        opacity: 0.6;
        margin-left: 4px;
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
export class AriaMultiselectComponent implements ControlValueAccessor {
  @Input() label = '';
  @Input() options: FilterOption[] = [];
  @Input() disabled = false;
  @Input() multiple = false;

  /** Backward-compatible input for initial selection */
  @Input()
  set selectedValue(val: unknown) {
    this._pendingValue = val;
  }
  private _pendingValue: unknown = null;

  @Output() selectedValueChange = new EventEmitter<any>();
  /** Alias for backward compatibility with (selectionChange) binding */
  @Output() selectionChange = new EventEmitter<unknown>();

  /** Reference to the combobox directive */
  combobox = viewChild<Combobox<unknown>>(Combobox);
  /** Reference to the listbox */
  listbox = viewChild<Listbox<unknown>>(Listbox);
  /** All option elements */
  optionElements = viewChildren<Option<unknown>>(Option);

  // ControlValueAccessor callbacks
  private onChange: (value: unknown) => void = () => { };
  private onTouched: () => void = () => { };

  /** Computed display label */
  displayLabel = computed(() => {
    const values = this.listbox()?.values() || [];
    const filteredValues = values.filter((v) => v !== null);
    if (filteredValues.length === 0) {
      return this.label;
    }
    if (this.multiple) {
      return `${this.label} (${filteredValues.length})`;
    }
    const option = this.options.find((opt) => opt.value === filteredValues[0]);
    return option ? option.label : this.label;
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
      const filteredValues = values.filter((v) => v !== null);

      let emitValue: unknown;
      if (this.multiple) {
        emitValue = filteredValues;
      } else {
        emitValue = filteredValues.length > 0 ? filteredValues[0] : null;
      }

      this.onChange(emitValue);
      this.onTouched();
      this.selectedValueChange.emit(emitValue);
      this.selectionChange.emit(emitValue);
    });
  }

  hasSelection(): boolean {
    const values = this.listbox()?.values() || [];
    return values.filter((v) => v !== null).length > 0;
  }

  isSelected(value: unknown): boolean {
    const values = this.listbox()?.values() || [];
    return values.includes(value);
  }

  clearSelection(): void {
    this.listbox()?.values.set([]);
    this.combobox()?.close();
  }

  // ControlValueAccessor implementation
  writeValue(value: unknown): void {
    if (this.listbox() && value != null) {
      const valuesToSelect = this.multiple
        ? (Array.isArray(value) ? value : [value])
        : [value];
      this.listbox()?.values.set(valuesToSelect);
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
