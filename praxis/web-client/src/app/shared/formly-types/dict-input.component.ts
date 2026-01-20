
import { Component, ChangeDetectionStrategy, OnInit, signal } from '@angular/core';
import { FieldType, FieldTypeConfig, FormlyModule } from '@ngx-formly/core';
import { ReactiveFormsModule, FormArray, FormGroup, FormControl, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';

@Component({
  selector: 'app-dict-input',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    FormlyModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
  ],
  template: `
    <div class="dict-container">
      @if (to.label) {
        <label class="field-label">
          {{ to.label }}
          @if (to.required) {
            <span class="required-indicator">*</span>
          }
        </label>
      }

      <div class="dict-items" [formGroup]="itemsForm">
        <ng-container formArrayName="items">
          @for (item of items.controls; track item; let i = $index) {
            <div class="dict-item" [formGroupName]="i">
              <mat-form-field class="key-field" appearance="outline" density="compact">
                <mat-label>Key</mat-label>
                <input matInput formControlName="key" placeholder="Key">
              </mat-form-field>

              <mat-form-field class="value-field" appearance="outline" density="compact">
                <mat-label>Value</mat-label>
                <input matInput formControlName="value" placeholder="Value">
              </mat-form-field>

              <button mat-icon-button color="warn" (click)="removeItem(i)" matTooltip="Remove Item">
                <mat-icon>delete</mat-icon>
              </button>
            </div>
          }
        </ng-container>
      </div>

      <div class="add-button">
        <button mat-stroked-button color="primary" (click)="addItem()">
          <mat-icon>add</mat-icon> Add Entry
        </button>
      </div>

      @if (to.description) {
        <div class="field-description">
          {{ to.description }}
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
    .dict-container {
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
    .dict-item {
      display: flex;
      gap: 8px;
      align-items: center;
      margin-bottom: 8px;
    }
    .key-field, .value-field {
      flex: 1;
    }
    .add-button {
      margin-top: 8px;
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
export class DictInputComponent extends FieldType<FieldTypeConfig> implements OnInit {
  itemsForm = new FormGroup({
    items: new FormArray<FormGroup>([])
  });

  get items() {
    return this.itemsForm.get('items') as FormArray<FormGroup>;
  }

  ngOnInit() {
    // Initialize from model value
    const value = this.formControl.value;
    if (value && typeof value === 'object') {
      Object.entries(value).forEach(([key, val]) => {
        this.addItem(key, val);
      });
    }

    // Subscribe to changes to update the main form control
    this.itemsForm.valueChanges.subscribe(val => {
      const result: Record<string, any> = {};
      val.items?.forEach((item: any) => {
        if (item.key) {
          // Attempt to parse value if it looks like a number
          let parsedValue = item.value;
          if (!isNaN(Number(item.value)) && item.value !== '') {
             parsedValue = Number(item.value);
          }
          result[item.key] = parsedValue;
        }
      });
      this.formControl.setValue(result);
      this.formControl.markAsDirty();
    });
  }

  addItem(key: string = '', value: any = '') {
    const group = new FormGroup({
      key: new FormControl(key, Validators.required),
      value: new FormControl(value, Validators.required)
    });
    this.items.push(group);
  }

  removeItem(index: number) {
    this.items.removeAt(index);
  }
}
