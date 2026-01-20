import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';

@Component({
  selector: 'app-interaction-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatInputModule,
    MatFormFieldModule
  ],
  template: `
    <h2 mat-dialog-title>Interaction Required</h2>
    <mat-dialog-content>
      <div *ngIf="data.interaction_type === 'pause'">
        <p>{{ data.payload.message }}</p>
      </div>

      <div *ngIf="data.interaction_type === 'confirm'">
        <p>{{ data.payload.message }}</p>
      </div>

      <div *ngIf="data.interaction_type === 'input'">
        <p>{{ data.payload.prompt }}</p>
        <mat-form-field appearance="fill" class="full-width">
          <mat-label>Input</mat-label>
          <input matInput [(ngModel)]="inputValue">
        </mat-form-field>
      </div>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <ng-container [ngSwitch]="data.interaction_type">
        <button mat-button *ngSwitchCase="'pause'" (click)="dialogRef.close(true)">Resume</button>
        
        <ng-container *ngSwitchCase="'confirm'">
          <button mat-button (click)="dialogRef.close(false)">No</button>
          <button mat-raised-button color="primary" (click)="dialogRef.close(true)">Yes</button>
        </ng-container>

        <button mat-raised-button color="primary" *ngSwitchCase="'input'" (click)="dialogRef.close(inputValue)">Submit</button>
      </ng-container>
    </mat-dialog-actions>
  `,
  styles: [`
    .full-width {
      width: 100%;
    }
    mat-dialog-content {
      min-width: 300px;
    }
  `]
})
export class InteractionDialogComponent {
  inputValue: string = '';

  constructor(
    public dialogRef: MatDialogRef<InteractionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { interaction_type: string, payload: any }
  ) {}
}
