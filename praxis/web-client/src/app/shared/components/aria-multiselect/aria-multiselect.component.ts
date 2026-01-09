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
import { MatTooltipModule } from '@angular/material/tooltip';
import { FilterOption } from '../../services/filter-result.service';
import { CommonModule } from '@angular/common';

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
    MatTooltipModule,
    CommonModule
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

      <!-- Chips for partial selection -->
      @if (!isAllSelected() && selectedValues().length > 0) {
        <div class="selected-chips">
          @for (chip of visibleChips(); track chip.value) {
            <span class="selection-chip">
              <span class="chip-label">{{ chip.label }}</span>
            </span>
          }
          @if (overflowCount() > 0) {
            <span class="overflow-badge" [matTooltip]="overflowTooltip()">
              +{{ overflowCount() }}
            </span>
          }
        </div>
      }

      <ng-template ngComboboxPopupContainer>
        <ng-template
          [cdkConnectedOverlay]="{origin, usePopover: 'inline', matchWidth: true}"
          [cdkConnectedOverlayOpen]="true"
        >
          <div class="aria-multiselect-panel">
            <!-- Sticky Header -->
            <div class="panel-header">
              <button type="button" class="header-btn" (click)="selectAll($event)">
                Select All
              </button>
              <button type="button" class="header-btn" (click)="clearAll($event)">
                Clear All
              </button>
            </div>

            <div ngListbox [multi]="true">
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
                  @if (option.count !== undefined) {
                    <span class="option-count">({{ option.count }})</span>
                  }
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
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AriaMultiselectComponent implements ControlValueAccessor {
  @Input() label = '';
  @Input() options: FilterOption[] = [];
  @Input() disabled = false;
  @Input() placeholder = '';

  /** Backward-compatible input for initial selection */
  @Input()
  set selectedValue(val: unknown) {
    this._pendingValue = val;
  }
  private _pendingValue: unknown = null;
  private _initialized = false;

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

  /** Computed currently selected values */
  selectedValues = computed(() => {
    const values = this.listbox()?.values() || [];
    return values.filter((v) => v !== null);
  });

  /** Computed if all options are selected */
  isAllSelected = computed(() => {
    if (this.options.length === 0) return false;
    return this.selectedValues().length === this.options.length;
  });

  /** Computed display label */
  displayLabel = computed(() => {
    // If all selected or options not loaded yet
    if (this.isAllSelected() || (this.options.length > 0 && !this._initialized)) {
      return `All ${this.label}`;
    }

    const count = this.selectedValues().length;
    if (count === 0) {
      return this.placeholder || `None ${this.label}`;
    }

    return `${this.label} (${count})`;
  });

  /** Computed visible chips (max 2) */
  visibleChips = computed(() => {
    const values = this.selectedValues();
    return values.slice(0, 2).map((v) => {
      const opt = this.options.find((o) => o.value === v);
      return { value: v, label: opt?.label || String(v) };
    });
  });

  /** Computed overflow count */
  overflowCount = computed(() => Math.max(0, this.selectedValues().length - 2));

  /** Computed tooltip for overflow items */
  overflowTooltip = computed(() => {
    const values = this.selectedValues();
    return values
      .slice(2)
      .map((v) => {
        const opt = this.options.find((o) => o.value === v);
        return opt?.label || String(v);
      })
      .join(', ');
  });

  constructor(private elementRef: ElementRef) {
    // Scroll handling (standard boilerplate)
    afterRenderEffect(() => {
      const option = this.optionElements().find((opt) => opt.active());
      setTimeout(() => option?.element.scrollIntoView({ block: 'nearest' }), 50);
    });

    afterRenderEffect(() => {
      if (!this.combobox()?.expanded()) {
        setTimeout(() => this.listbox()?.element.scrollTo(0, 0), 150);
      }
    });

    // Default initialization: Select All (Full Array)
    afterRenderEffect(() => {
      if (this.options.length > 0 && !this._initialized && !this._pendingValue) {
        // Only auto-select all if no pending value from writeValue/Input
        const allValues = this.options.map(o => o.value);
        // Defer to next tick to ensure listbox is ready
        setTimeout(() => {
          if (this.listbox()) { // Safe check
            this.listbox()?.values.set(allValues);
            this._initialized = true;
          }
        });
      }
    });

    // Handle incoming input value (late binding)
    afterRenderEffect(() => {
      if (this._pendingValue !== null && this.listbox()) {
        const val = this._pendingValue;
        const valuesToSelect = Array.isArray(val) ? val : [val];
        this.listbox()?.values.set(valuesToSelect);
        this._pendingValue = null;
        this._initialized = true;
      }
    });

    // Watch for value changes and propagate to form
    afterRenderEffect(() => {
      const values = this.selectedValues();
      this.onChange(values);
      this.onTouched();
      this.selectedValueChange.emit(values);
      this.selectionChange.emit(values);
    });
  }

  selectAll(event: MouseEvent): void {
    event.stopPropagation();
    event.preventDefault(); // Prevent closing
    const allValues = this.options.map((o) => o.value);
    this.listbox()?.values.set(allValues);
  }

  clearAll(event: MouseEvent): void {
    event.stopPropagation();
    event.preventDefault(); // Prevent closing
    this.listbox()?.values.set([]);
  }

  // ControlValueAccessor implementation
  writeValue(value: unknown): void {
    if (this.listbox()) {
      const valuesToSelect = value != null
        ? (Array.isArray(value) ? value : [value])
        : [];
      this.listbox()?.values.set(valuesToSelect);
      this._initialized = true;
    } else {
      this._pendingValue = value;
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

