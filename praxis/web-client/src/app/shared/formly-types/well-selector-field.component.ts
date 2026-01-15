/**
 * Well Selector Field Component
 *
 * Formly field type that opens the Well Selector Dialog for well selection.
 * This provides a seamless integration with the protocol parameter configuration.
 *
 * Usage in FormlyFieldConfig:
 * {
 *   key: 'wells',
 *   type: 'well-selector',
 *   props: {
 *     label: 'Select Wells',
 *     plateType: '96',  // or '384'
 *     mode: 'multi',    // or 'single'
 *     plateLabel: 'Source Plate',
 *   }
 * }
 */
import {
  Component,
  ChangeDetectionStrategy,
  OnInit,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FieldType, FieldTypeConfig, FormlyModule } from '@ngx-formly/core';
import {
  WellSelectorDialogComponent,
  WellSelectorDialogData,
  WellSelectorDialogResult,
} from '../components/well-selector-dialog/well-selector-dialog.component';

@Component({
  selector: 'app-well-selector-field',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormlyModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatDialogModule,
    MatFormFieldModule,
  ],
  template: `
    <div class="well-selector-field-wrapper">
      @if (props.label) {
        <label class="field-label">
          {{ props.label }}
          @if (props.required) {
            <span class="required-indicator">*</span>
          }
        </label>
      }

      <div class="selection-display">
        @if (selectedWells().length === 0) {
          <span class="no-selection">No wells selected</span>
        } @else if (selectedWells().length <= 8) {
          <div class="chips-container">
            @for (well of selectedWells(); track well) {
              <mat-chip class="well-chip" highlighted>{{ well }}</mat-chip>
            }
          </div>
        } @else {
          <span class="selection-summary">
            {{ selectedWells().length }} wells selected
            <span class="sample-wells">({{ selectedWells().slice(0, 4).join(', ') }}...)</span>
          </span>
        }

        <button
          mat-stroked-button
          type="button"
          class="select-btn"
          (click)="openDialog()"
          [disabled]="props.disabled"
        >
          <mat-icon>grid_view</mat-icon>
          {{ selectedWells().length > 0 ? 'Edit Selection' : 'Select Wells' }}
        </button>
      </div>

      @if (props.description) {
        <div class="field-description">{{ props.description }}</div>
      }

      @if (showError) {
        <div class="field-error">
          <formly-validation-message [field]="field"></formly-validation-message>
        </div>
      }
    </div>
  `,
  styles: [`
    .well-selector-field-wrapper {
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

    .selection-display {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 12px;
      padding: 12px;
      background: var(--mat-sys-surface-container);
      border-radius: 8px;
      border: 1px solid var(--mat-sys-outline-variant);
    }

    .no-selection {
      color: var(--mat-sys-on-surface-variant);
      font-size: 14px;
      font-style: italic;
    }

    .chips-container {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      flex: 1;
    }

    .well-chip {
      font-size: 12px;
    }

    .selection-summary {
      flex: 1;
      font-size: 14px;
      font-weight: 500;
      color: var(--mat-sys-on-surface);
    }

    .sample-wells {
      font-weight: 400;
      color: var(--mat-sys-on-surface-variant);
    }

    .select-btn {
      margin-left: auto;
    }

    .select-btn mat-icon {
      margin-right: 4px;
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
export class WellSelectorFieldComponent extends FieldType<FieldTypeConfig> implements OnInit {
  private dialog = inject(MatDialog);

  /** Current selected wells from form control */
  selectedWells = signal<string[]>([]);

  /** Plate type from props */
  plateType = signal<'96' | '384'>('96');

  ngOnInit(): void {
    // Set plate type from props
    if (this.props['plateType']) {
      this.plateType.set(this.props['plateType'] as '96' | '384');
    }

    // Initialize from form control value
    const value = this.formControl.value;
    if (Array.isArray(value)) {
      this.selectedWells.set(value);
    }

    // Subscribe to form control value changes
    this.formControl.valueChanges.subscribe((value) => {
      if (Array.isArray(value)) {
        this.selectedWells.set(value);
      }
    });
  }

  /**
   * Open the well selector dialog.
   */
  openDialog(): void {
    const dialogData: WellSelectorDialogData = {
      plateType: this.plateType(),
      initialSelection: this.selectedWells(),
      mode: (this.props['mode'] as 'single' | 'multi') || 'multi',
      title: this.props['dialogTitle'],
      plateLabel: this.props['plateLabel'],
    };

    const dialogRef = this.dialog.open(WellSelectorDialogComponent, {
      data: dialogData,
      width: this.plateType() === '384' ? '800px' : '600px',
      maxWidth: '95vw',
      maxHeight: '90vh',
      panelClass: 'well-selector-dialog-panel',
    });

    dialogRef.afterClosed().subscribe((result: WellSelectorDialogResult | undefined) => {
      if (result?.confirmed) {
        this.formControl.setValue(result.wells);
        this.formControl.markAsTouched();
        this.formControl.markAsDirty();
      }
    });
  }
}
