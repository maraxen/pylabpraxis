import { Component, ChangeDetectionStrategy, OnInit, inject, signal, computed } from '@angular/core';

import { ReactiveFormsModule } from '@angular/forms';
import { FieldType, FieldTypeConfig, FormlyModule } from '@ngx-formly/core';
import {
    IndexSelectorComponent,
    ItemizedResourceSpec,
    SelectionMode,
} from '../components/index-selector/index-selector.component';

/**
 * Formly field type wrapper for IndexSelectorComponent.
 * Enables visual grid selection for itemized resources (wells, tips, tubes).
 *
 * Usage in FormlyFieldConfig:
 * {
 *   key: 'source_wells',
 *   type: 'index-selector',
 *   props: {
 *     label: 'Source Wells',
 *     itemsX: 12,
 *     itemsY: 8,
 *     mode: 'multiple',
 *     linkedTo: 'dest_wells',
 *   }
 * }
 */
@Component({
    selector: 'app-index-selector-field',
    standalone: true,
    imports: [
    ReactiveFormsModule,
    FormlyModule,
    IndexSelectorComponent
],
    template: `
    <div class="index-selector-field-wrapper">
      @if (props.label) {
        <label class="field-label">
          {{ props.label }}
          @if (props.required) {
            <span class="required-indicator">*</span>
          }
        </label>
      }
    
      <app-index-selector
        [spec]="resourceSpec()"
        [selectedIndices]="selectedIndices()"
        [mode]="selectionMode()"
        [disabled]="props.disabled || false"
        (selectionChange)="onSelectionChange($event)"
        (wellIdsChange)="onWellIdsChange($event)"
      ></app-index-selector>
    
      @if (props.description) {
        <div class="field-description">
          {{ props.description }}
        </div>
      }
    
      @if (showError) {
        <div class="field-error">
          <formly-validation-message [field]="field"></formly-validation-message>
        </div>
      }
    </div>
    `,
    styles: [`
    .index-selector-field-wrapper {
      margin-bottom: 16px;
    }

    .field-label {
      display: block;
      font-weight: 500;
      margin-bottom: 8px;
      color: var(--mat-on-surface, #333);
    }

    .required-indicator {
      color: var(--mat-error, var(--status-error));
      margin-left: 4px;
    }

    .field-description {
      font-size: 0.85em;
      color: var(--mat-on-surface-variant, #666);
      margin-top: 8px;
    }

    .field-error {
      color: var(--mat-error, var(--status-error));
      font-size: 0.85em;
      margin-top: 4px;
    }
  `],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IndexSelectorFieldComponent extends FieldType<FieldTypeConfig> implements OnInit {
    /** Resource specification computed from props */
    resourceSpec = signal<ItemizedResourceSpec>({ itemsX: 12, itemsY: 8 });

    /** Current selected indices from form control */
    selectedIndices = signal<number[]>([]);

    /** Selection mode from props */
    selectionMode = signal<SelectionMode>('multiple');

    ngOnInit(): void {
        // Build spec from props
        this.resourceSpec.set({
            itemsX: this.props['itemsX'] || 12,
            itemsY: this.props['itemsY'] || 8,
            label: this.props['label'],
            linkId: this.props['linkedTo'],
        });

        // Set mode from props
        if (this.props['mode']) {
            this.selectionMode.set(this.props['mode'] as SelectionMode);
        }

        // Initialize from form control value
        const value = this.formControl.value;
        if (Array.isArray(value)) {
            this.selectedIndices.set(value);
        }

        // Subscribe to form control value changes
        this.formControl.valueChanges.subscribe(value => {
            if (Array.isArray(value)) {
                this.selectedIndices.set(value);
            }
        });
    }

    /**
     * Handle selection changes from the index selector.
     */
    onSelectionChange(indices: number[]): void {
        this.formControl.setValue(indices);
        this.formControl.markAsTouched();
        this.formControl.markAsDirty();
    }

    /**
     * Handle well ID changes - can be used for display purposes.
     */
    onWellIdsChange(wellIds: string[]): void {
        // Store well IDs in a separate property if needed
        // This can be useful for display or debugging
    }
}
