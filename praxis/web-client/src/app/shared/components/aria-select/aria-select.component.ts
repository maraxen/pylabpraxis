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
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { OverlayModule, CdkConnectedOverlay } from '@angular/cdk/overlay';
import { MatIconModule } from '@angular/material/icon';

export interface SelectOption {
    label: string;
    value: any;
    icon?: string;
    disabled?: boolean;
}

/**
 * ARIA-compliant single-select component using @angular/aria primitives.
 * Implements ControlValueAccessor for form integration.
 *
 * Features:
 * - Full keyboard navigation (Arrow keys, Enter, Escape)
 * - Screen reader support with proper ARIA attributes
 * - CDK Overlay for proper popup positioning
 * - Theme integration with Material Design 3 tokens
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
    <div
      class="select-container"
      ngCombobox
      #combobox="ngCombobox"
      [disabled]="disabled"
    >
      <!-- Trigger Button -->
      <button
        type="button"
        class="select-trigger"
        [class.expanded]="combobox.expanded()"
        [class.disabled]="disabled"
        [class.has-value]="hasValue()"
        cdkOverlayOrigin
        #trigger="cdkOverlayOrigin"
        (click)="combobox.expanded() ? combobox.close() : combobox.open()"
        [attr.aria-expanded]="combobox.expanded()"
        [attr.aria-label]="label"
        [attr.aria-disabled]="disabled"
      >
        @if (displayIcon()) {
          <mat-icon class="trigger-icon">{{ displayIcon() }}</mat-icon>
        }
        <span class="trigger-text">{{ displayValue() }}</span>
        <mat-icon class="trigger-chevron">
          {{ combobox.expanded() ? 'expand_less' : 'expand_more' }}
        </mat-icon>
      </button>

      <!-- Hidden input for ARIA combobox pattern -->
      <input
        type="text"
        ngComboboxInput
        class="visually-hidden"
        [attr.aria-label]="label"
        readonly
      />

      <!-- Dropdown popup via CDK Overlay -->
      <ng-template
        cdkConnectedOverlay
        [cdkConnectedOverlayOrigin]="trigger"
        [cdkConnectedOverlayOpen]="combobox.expanded()"
        [cdkConnectedOverlayWidth]="triggerWidth()"
        [cdkConnectedOverlayPanelClass]="'aria-select-panel'"
        [cdkConnectedOverlayPositions]="positions"
        (detach)="combobox.close()"
      >
        <div
          ngComboboxPopup
          class="select-popup"
          ngListbox
          [multi]="false"
          [(values)]="selectedValues"
          (valuesChange)="onValueChange($event)"
          orientation="vertical"
          selectionMode="explicit"
        >
          @for (option of options; track option.value) {
            <div
              ngOption
              [value]="option.value"
              [label]="option.label"
              [disabled]="option.disabled ?? false"
              class="select-option"
              [class.selected]="isSelected(option.value)"
              [class.disabled]="option.disabled"
            >
              @if (option.icon) {
                <mat-icon class="option-icon">{{ option.icon }}</mat-icon>
              }
              <span class="option-label">{{ option.label }}</span>
            </div>
          }
        </div>
      </ng-template>
    </div>
  `,
    styles: [
        `
      :host {
        display: inline-block;
        min-width: 120px;
      }

      .select-container {
        position: relative;
        width: 100%;
      }

      .select-trigger {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        height: 40px;
        padding: 0 12px;
        border-radius: 4px;
        border: 1px solid var(--mat-sys-outline);
        background-color: transparent;
        color: var(--mat-sys-on-surface);
        cursor: pointer;
        transition: all 0.2s ease;
        user-select: none;
        font-size: 14px;
        font-family: inherit;
        gap: 8px;

        &:hover:not(.disabled) {
          border-color: var(--mat-sys-on-surface);
        }

        &:focus {
          outline: 2px solid var(--mat-sys-primary);
          outline-offset: 2px;
        }

        &.expanded {
          border-color: var(--mat-sys-primary);
        }

        &.disabled {
          cursor: not-allowed;
          opacity: 0.5;
          background-color: var(--mat-sys-surface-variant);
        }
      }

      .trigger-icon {
        font-size: 20px;
        width: 20px;
        height: 20px;
        color: var(--mat-sys-on-surface-variant);
      }

      .trigger-text {
        flex: 1;
        text-align: left;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .trigger-chevron {
        font-size: 20px;
        width: 20px;
        height: 20px;
        color: var(--mat-sys-on-surface-variant);
        flex-shrink: 0;
      }

      .visually-hidden {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
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
    combobox = viewChild<Combobox<any>>(Combobox);
    /** Reference to the listbox */
    listbox = viewChild<Listbox<any>>(Listbox);
    /** All option elements */
    optionElements = viewChildren<Option<any>>(Option);

    /** Internal selected values signal (array of 1 for single select) */
    selectedValues = signal<any[]>([]);

    /** Overlay positions */
    positions = [
        { originX: 'start' as const, originY: 'bottom' as const, overlayX: 'start' as const, overlayY: 'top' as const },
        { originX: 'start' as const, originY: 'top' as const, overlayX: 'start' as const, overlayY: 'bottom' as const },
    ];

    /** Trigger element width for overlay sizing */
    triggerWidth = signal(200);

    // ControlValueAccessor callbacks
    private onChange: (value: any) => void = () => { };
    private onTouched: () => void = () => { };

    /** Computed display value */
    displayValue = computed(() => {
        const values = this.selectedValues();
        if (values.length === 0) {
            return this.placeholder;
        }
        const option = this.options.find((opt) => opt.value === values[0]);
        return option ? option.label : this.placeholder;
    });

    /** Computed display icon */
    displayIcon = computed(() => {
        const values = this.selectedValues();
        if (values.length === 0) {
            return '';
        }
        const option = this.options.find((opt) => opt.value === values[0]);
        return option?.icon || '';
    });

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
            const triggerEl = this.elementRef.nativeElement.querySelector('.select-trigger');
            if (triggerEl) {
                this.triggerWidth.set(triggerEl.offsetWidth);
            }
        });
    }

    hasValue(): boolean {
        return this.selectedValues().length > 0;
    }

    isSelected(value: any): boolean {
        return this.selectedValues().includes(value);
    }

    onValueChange(values: any[]): void {
        const newValue = values.length > 0 ? values[0] : null;
        this.onChange(newValue);
        this.onTouched();
        // Auto-close on selection for single select
        this.combobox()?.close();
    }

    // ControlValueAccessor implementation
    writeValue(value: any): void {
        this.selectedValues.set(value != null ? [value] : []);
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
