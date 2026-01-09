import { Component, inject } from '@angular/core';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-add-asset-choice-dialog',
  standalone: true,
  imports: [
    MatDialogModule,
    MatButtonModule,
    MatIconModule
  ],
  template: `
    <h2 mat-dialog-title>Add New Asset</h2>
    <mat-dialog-content>
      <p class="text-sys-text-secondary mb-4">What would you like to add?</p>
      <div class="grid grid-cols-2 gap-4">
        <button
          mat-stroked-button
          class="choice-card !flex !flex-col !items-center !gap-2 !p-6 !h-auto hover:!bg-primary/5 hover:!border-primary transition-all"
          (click)="select('machine')"
        >
          <mat-icon class="!w-12 !h-12 !text-[48px] text-primary">precision_manufacturing</mat-icon>
          <span class="font-semibold text-lg">Machine</span>
          <span class="text-xs text-sys-text-secondary text-center">Robots, liquid handlers, etc.</span>
        </button>
        <button
          mat-stroked-button
          class="choice-card !flex !flex-col !items-center !gap-2 !p-6 !h-auto hover:!bg-primary/5 hover:!border-primary transition-all"
          (click)="select('resource')"
        >
          <mat-icon class="!w-12 !h-12 !text-[48px] text-primary">science</mat-icon>
          <span class="font-semibold text-lg">Resource</span>
          <span class="text-xs text-sys-text-secondary text-center">Plates, tips, labware</span>
        </button>
      </div>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
    </mat-dialog-actions>
  `,
  styles: [`
    mat-dialog-content {
      padding: 20px 24px;
      min-width: 400px;
    }

    .choice-card {
      border-radius: 12px;
    }
  `]
})
export class AddAssetChoiceDialogComponent {
  private dialogRef = inject(MatDialogRef<AddAssetChoiceDialogComponent>);

  select(type: 'machine' | 'resource') {
    this.dialogRef.close(type);
  }
}
