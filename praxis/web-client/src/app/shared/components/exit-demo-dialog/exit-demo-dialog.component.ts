import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { OnboardingService } from '@core/services/onboarding.service';

@Component({
    selector: 'app-exit-demo-dialog',
    standalone: true,
    imports: [CommonModule, MatDialogModule, MatButtonModule],
    template: `
    <h2 mat-dialog-title>Tutorial Complete!</h2>
    <mat-dialog-content>
      <p class="mb-4">You have explored the key features of Praxis.</p>
      <p class="mb-4">You are currently in <strong>Demo Mode</strong> with sample data.</p>
      <p>Would you like to exit to an empty workspace to start fresh?</p>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="keep()">Keep Demo Mode</button>
      <button mat-raised-button color="primary" (click)="exit()">Exit Demo Mode</button>
    </mat-dialog-actions>
  `
})
export class ExitDemoDialogComponent {
    private dialogRef = inject(MatDialogRef<ExitDemoDialogComponent>);
    private onboarding = inject(OnboardingService);

    keep() {
        this.dialogRef.close();
    }

    exit() {
        this.onboarding.setDemoMode(false, true); // Updates state and reloads
        this.dialogRef.close();
    }
}
