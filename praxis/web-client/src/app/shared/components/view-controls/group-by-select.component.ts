import { Component, Input, Output, EventEmitter, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { SelectOption } from './view-controls.types';

@Component({
    selector: 'app-group-by-select',
    standalone: true,
    imports: [CommonModule, MatFormFieldModule, MatSelectModule, MatIconModule],
    template: `
    <mat-form-field appearance="outline" class="group-by-field" subscriptSizing="dynamic">
      <mat-label>Group By</mat-label>
      <mat-select [value]="value" (selectionChange)="valueChange.emit($event.value)">
        <mat-option [value]="null">None</mat-option>
        @for (option of options; track option.value) {
          <mat-option [value]="option.value" [disabled]="option.disabled">
            <div class="option-content">
              @if (option.icon) {
                <mat-icon>{{ option.icon }}</mat-icon>
              }
              <span>{{ option.label }}</span>
            </div>
          </mat-option>
        }
      </mat-select>
    </mat-form-field>
  `,
    styles: [`
    .group-by-field {
      width: 160px;
      /* Style overrides to match theme and size */
      ::ng-deep {
        .mat-mdc-text-field-wrapper {
          height: 32px !important;
          padding: 0 8px !important;
          background-color: transparent !important;
        }
        .mat-mdc-form-field-flex {
          height: 32px !important;
          align-items: center !important;
        }
        .mat-mdc-form-field-infix {
          padding: 0 !important;
          min-height: auto !important;
          width: auto !important;
          display: flex;
          align-items: center;
        }
        .mat-mdc-select-value {
          font-size: 13px;
        }
        .mat-mdc-form-field-label-wrapper {
          top: -8px;
        }
      }
    }
    .option-content {
      display: flex;
      align-items: center;
      gap: 8px;
      mat-icon {
        font-size: 18px;
        width: 18px;
        height: 18px;
      }
    }
  `],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class GroupBySelectComponent {
    @Input() value: string | null = null;
    @Input() options: SelectOption[] = [];
    @Output() valueChange = new EventEmitter<string | null>();
}
