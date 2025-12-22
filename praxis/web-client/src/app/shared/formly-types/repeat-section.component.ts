import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FieldArrayType, FormlyModule } from '@ngx-formly/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-repeat-section',
  standalone: true,
  imports: [
    CommonModule,
    FormlyModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule
  ],
  template: `
    <div class="repeat-container">
      <div *ngFor="let field of field.fieldGroup; let i = index" class="repeat-item">
        <mat-card class="repeat-card">
          <mat-card-content>
            <formly-field [field]="field"></formly-field>
          </mat-card-content>
          <mat-card-actions align="end">
            <button mat-icon-button color="warn" (click)="remove(i)" matTooltip="Remove Item">
              <mat-icon>delete</mat-icon>
            </button>
          </mat-card-actions>
        </mat-card>
      </div>
      <div class="add-button">
        <button mat-stroked-button color="primary" (click)="add()">
          <mat-icon>add</mat-icon> {{ to['addText'] || 'Add Item' }}
        </button>
      </div>
    </div>
  `,
  styles: [`
    .repeat-container {
      margin-top: 8px;
    }
    .repeat-item {
      margin-bottom: 8px;
    }
    .add-button {
      margin-top: 8px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RepeatTypeComponent extends FieldArrayType {}
