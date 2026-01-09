import {
  Component,
  Input,
  Output,
  EventEmitter,
  ChangeDetectionStrategy,
  signal,
  computed,
  viewChild,
  viewChildren,
  afterRenderEffect,
  ElementRef,
} from '@angular/core';
import {
  Combobox,
  ComboboxInput,
  ComboboxPopup,
} from '@angular/aria/combobox';
import { Listbox, Option } from '@angular/aria/listbox';
import { OverlayModule } from '@angular/cdk/overlay';
import { MatIconModule } from '@angular/material/icon';
import { FilterOption } from '../../services/filter-result.service';

/**
 * ARIA-compliant multiselect component using @angular/aria primitives.
 * Replaces the custom FilterChipComponent with standardized accessibility patterns.
 *
 * Features:
 * - Full keyboard navigation (Arrow keys, Enter, Escape)
 * - Screen reader support with proper ARIA attributes
 * - Single and multiple selection modes
 * - CDK Overlay for### 1. New ARIA Components

- **`AriaSelectComponent`**: Single-select component with Material Design 3 styling. Fixed selection bug by removing `selectionMode="explicit"`.
- **`AriaMultiselectComponent`**: Multi-select dropdown. Fixed selection bug and standardized styling.
- **`AriaAutocompleteComponent`**: New component for searchable database lookups (Protocol, Run, Inventory). Supports query filtering and keyboard navigation.
 */
@Component({
  selector: 'app-aria-multiselect',
  standalone: true,
  imports: [
    Combobox,
    ComboboxInput,
    ComboboxPopup,
    Listbox,
    Option,
    OverlayModule,
    MatIconModule,
  ],
  template: `
    <div class="multiselect-container" ngCombobox #combobox="ngCombobox" [disabled]="disabled">
      <!-- Trigger Button styled as chip -->
      <button
        type="button"
        class="multiselect-trigger"
        [class.active]="hasSelection()"
        [class.disabled]="disabled"
        cdkOverlayOrigin
        #trigger="cdkOverlayOrigin"
        (click)="combobox.expanded() ? combobox.close() : combobox.open()"
        [attr.aria-expanded]="combobox.expanded()"
        [attr.aria-label]="label"
        [attr.aria-disabled]="disabled"
      >
        <span class="trigger-text">{{ displayLabel() }}</span>
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
        [cdkConnectedOverlayPanelClass]="'aria-multiselect-panel'"
        [cdkConnectedOverlayPositions]="positions"
        (detach)="combobox.close()"
      >
        <div
          ngComboboxPopup
          ngListbox
          class="multiselect-popup"
          [multi]="multiple"
          [(values)]="selectedValues"
          (valuesChange)="onValuesChange($event)"
          orientation="vertical"
        >
          <!-- "All" option to clear selection -->
          <div
            ngOption
            [value]="null"
            label="All"
            class="multiselect-option"
            [class.selected]="!hasSelection()"
            (click)="clearSelection()"
          >
            @if (multiple) {
              <mat-icon class="option-checkbox">
                {{ !hasSelection() ? 'check_box' : 'check_box_outline_blank' }}
              </mat-icon>
            }
            <span class="option-label">All</span>
          </div>

          <!-- Dynamic options -->
          @for (option of options; track option.value) {
            <div
              ngOption
              [value]="option.value"
              [label]="option.label"
              [disabled]="option.disabled ?? false"
              class="multiselect-option"
              [class.selected]="isSelected(option.value)"
              [class.disabled]="option.disabled"
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
      }

      .multiselect-container {
        position: relative;
      }

      .multiselect-trigger {
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 32px;
        padding: 0 12px;
        border-radius: 16px;
        border: 1px solid var(--theme-border, var(--mat-sys-outline));
        background-color: transparent;
        color: var(--theme-text-primary, var(--mat-sys-on-surface));
        cursor: pointer;
        transition: all 0.2s ease;
        user-select: none;
        font-size: 13px;
        font-weight: 500;
        max-width: 250px;
        font-family: inherit;
        gap: 4px;

        &:hover:not(.disabled):not(.active) {
          background-color: var(--theme-surface-elevated, var(--mat-sys-surface-container-high));
          border-color: var(--theme-text-secondary, var(--mat-sys-outline));
        }

        &.active {
          background-color: var(--primary-color, var(--mat-sys-primary));
          border-color: var(--primary-color, var(--mat-sys-primary));
          color: var(--mat-sys-on-primary, #2b151a);

          .trigger-chevron {
            opacity: 1;
          }

          &:hover:not(.disabled) {
            filter: brightness(1.1);
          }
        }

        &.disabled {
          cursor: not-allowed;
          border: 1px dashed var(--theme-border, var(--mat-sys-outline));
          background-color: var(--theme-surface, var(--mat-sys-surface));
          opacity: 0.5;
        }
      }

      .trigger-text {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .trigger-chevron {
        font-size: 18px;
        width: 18px;
        height: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0.7;
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
export class AriaMultiselectComponent {
  // TODO(mdc-migration): The following lines are a workaround for a bug in MDC.
  // - [x] **Build Pass**: Production build verification confirms all templates are valid.
  // - [x] **Unit Tests**: Created tests for `AriaAutocompleteComponent` covering filtering and `ControlValueAccessor`.
  // - [x] **Grep Audit**: Confirmed `mat-select` is completely removed from the `app` source code.
  @Input() label = '';
  @Input() options: FilterOption[] = [];
  @Input() disabled = false;
  @Input() multiple = false;

  /** Reference to the combobox directive */
  combobox = viewChild<Combobox<any>>(Combobox);
  /** Reference to the listbox */
  listbox = viewChild<Listbox<any>>(Listbox);
  /** All option elements */
  optionElements = viewChildren<Option<any>>(Option);

  // Support both single value and array for backward compatibility
  @Input()
  set selectedValue(val: any | any[]) {
    if (this.multiple) {
      this.selectedValues.set(Array.isArray(val) ? val : val != null ? [val] : []);
    } else {
      this.selectedValues.set(val != null ? [val] : []);
    }
  }

  @Output() selectedValueChange = new EventEmitter<any>();

  // Internal state as signal for ARIA listbox
  selectedValues = signal<any[]>([]);

  /** Overlay positions */
  positions = [
    { originX: 'start' as const, originY: 'bottom' as const, overlayX: 'start' as const, overlayY: 'top' as const },
    { originX: 'start' as const, originY: 'top' as const, overlayX: 'start' as const, overlayY: 'bottom' as const },
  ];

  /** Trigger element width for overlay sizing */
  triggerWidth = signal(180);

  // Computed display label
  displayLabel = computed(() => this.label);

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
      const triggerEl = this.elementRef.nativeElement.querySelector('.multiselect-trigger');
      if (triggerEl) {
        this.triggerWidth.set(Math.max(triggerEl.offsetWidth, 180));
      }
    });
  }

  hasSelection(): boolean {
    return this.selectedValues().length > 0;
  }

  isSelected(value: any): boolean {
    return this.selectedValues().includes(value);
  }

  onValuesChange(values: any[]): void {
    // Filter out null (the "All" option)
    const filtered = values.filter((v) => v !== null);

    if (this.multiple) {
      this.selectedValueChange.emit(filtered);
      // Keep dropdown open for multi-select
    } else {
      // Single select: emit the last selected value or null
      this.selectedValueChange.emit(filtered.length > 0 ? filtered[filtered.length - 1] : null);
      // Close dropdown for single-select after selection
      this.combobox()?.close();
    }
  }

  clearSelection(): void {
    this.selectedValues.set([]);
    this.selectedValueChange.emit(this.multiple ? [] : null);
    // Close dropdown after clearing
    this.combobox()?.close();
  }
}
