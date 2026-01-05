import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { FormsModule } from '@angular/forms';
import { OnboardingService } from '@core/services/onboarding.service';
import { ModeService } from '@core/services/mode.service';
import { TutorialService } from '@core/services/tutorial.service';

@Component({
    selector: 'app-welcome-dialog',
    standalone: true,
    imports: [CommonModule, MatDialogModule, MatButtonModule, MatSlideToggleModule, FormsModule],
    template: `
    <h2 mat-dialog-title>Welcome to Praxis</h2>
    <mat-dialog-content class="prose max-w-none">
      <p class="mb-4">Praxis is your modern lab automation platform.</p>
      <p class="mb-6">Would you like a quick tour of the key features?</p>
      
      <div class="demo-toggle-container p-4 bg-gray-50 rounded-lg border border-gray-200 mb-2">
        <mat-slide-toggle
            color="primary"
            [(ngModel)]="isDemoMode"
            (change)="toggleDemoMode()">
            Enable Demo Mode (Recommended)
        </mat-slide-toggle>
        <p class="text-xs text-gray-500 mt-2 ml-2 leading-relaxed">
            Demo mode populates the app with sample data so you can explore safely without connecting hardware.
        </p>
      </div>
      
      @if (needsReload) {
        <p class="text-xs text-amber-600 font-medium mt-2 flex items-center gap-1">
          <span class="material-icons text-[16px]">info</span> App will reload to apply mode change.
        </p>
      }
    </mat-dialog-content>
    <mat-dialog-actions align="end" class="gap-2">
      <button mat-button (click)="skip()">Skip for Now</button>
      <button mat-raised-button color="primary" (click)="startTutorial()">Start Tutorial</button>
    </mat-dialog-actions>
  `,
    styles: [`
    .demo-toggle-container {
        display: flex;
        flex-direction: column;
    }
  `]
})
export class WelcomeDialogComponent {
    private dialogRef = inject(MatDialogRef<WelcomeDialogComponent>);
    private onboarding = inject(OnboardingService);
    private modeService = inject(ModeService);
    private tutorial = inject(TutorialService);

    // Initialize with current preference
    isDemoMode = this.onboarding.isDemoModeEnabled();

    // Track if current active mode differs from preference
    get needsReload(): boolean {
        return this.isDemoMode !== this.modeService.isDemoMode();
    }

    toggleDemoMode() {
        // Set preference but don't reload yet
        this.onboarding.setDemoMode(this.isDemoMode, false);
    }

    startTutorial() {
        this.onboarding.markOnboardingComplete();

        if (this.needsReload) {
            // If we need to reload to apply demo mode, persist "pending intent"
            localStorage.setItem('praxis_pending_tutorial', 'true');
            window.location.reload();
        } else {
            this.dialogRef.close();
            this.tutorial.start();
        }
    }

    skip() {
        this.onboarding.markOnboardingComplete();
        this.onboarding.setDemoMode(this.isDemoMode, this.needsReload); // Reload if needed
        if (!this.needsReload) {
            this.dialogRef.close();
        }
    }
}
