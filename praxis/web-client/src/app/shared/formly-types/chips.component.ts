import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { FieldType, FieldTypeConfig, FormlyModule } from '@ngx-formly/core';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { Observable, of, isObservable } from 'rxjs';

@Component({
  selector: 'app-chips-type',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatChipsModule,
    MatIconModule,
    FormlyModule
  ],
  template: `
    <div class="chips-container">
      @if (to.label) {
        <label>{{ to.label }}</label>
      }
      <mat-chip-listbox [multiple]="to['multiple']" [formControl]="formControl" [selectable]="true">
        @for (option of options$ | async; track option) {
          <mat-chip-option [value]="option.value">
            {{ option.label }}
          </mat-chip-option>
        }
      </mat-chip-listbox>
    </div>
    `,
  styles: [`
    .chips-container {
      margin-bottom: 16px;
    }
    label {
      display: block;
      margin-bottom: 8px;
      font-weight: 500;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChipsTypeComponent extends FieldType<FieldTypeConfig> {
  get options$(): Observable<any[]> {
    const options = this.to.options;
    if (isObservable(options)) {
      return options as Observable<any[]>;
    }
    return of(Array.isArray(options) ? options : []);
  }
}