
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { AppStore } from '../../../core/store/app.store';

type Theme = 'light' | 'dark' | 'system';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonToggleModule,
    MatIconModule,
    MatListModule
  ],
  template: `
    <div class="p-6">
      <h1 class="text-3xl font-bold mb-6">Settings</h1>

      <div class="max-w-3xl space-y-6">
        <!-- Appearance -->
        <mat-card class="glass-panel">
          <mat-card-header>
            <mat-icon mat-card-avatar class="text-primary scale-125">palette</mat-icon>
            <mat-card-title>Appearance</mat-card-title>
            <mat-card-subtitle>Customize application look and feel</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content class="pt-4">
             <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
               <div>
                 <h3 class="font-medium">Theme</h3>
                 <p class="text-sm text-gray-500 dark:text-gray-400">Select your preferred color theme</p>
               </div>

               <mat-button-toggle-group [value]="store.theme()" (change)="setTheme($event.value)" appearance="legacy">
                 <mat-button-toggle value="light">
                    <mat-icon class="mr-1">light_mode</mat-icon> Light
                 </mat-button-toggle>
                 <mat-button-toggle value="system">
                    <mat-icon class="mr-1">brightness_auto</mat-icon> System
                 </mat-button-toggle>
                 <mat-button-toggle value="dark">
                    <mat-icon class="mr-1">dark_mode</mat-icon> Dark
                 </mat-button-toggle>
               </mat-button-toggle-group>
             </div>
          </mat-card-content>
        </mat-card>

        <!-- System Info / About -->
        <mat-card class="glass-panel">
          <mat-card-header>
            <mat-icon mat-card-avatar class="text-secondary scale-125">info</mat-icon>
            <mat-card-title>About</mat-card-title>
             <mat-card-subtitle>System Information</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content class="pt-4">
             <mat-list>
                <mat-list-item>
                    <span matListItemTitle>Version</span>
                    <span matListItemLine>0.1.0-alpha</span>
                </mat-list-item>
                <mat-list-item>
                    <span matListItemTitle>Frontend Framework</span>
                    <span matListItemLine>Angular v21.0.2</span>
                </mat-list-item>
                 <mat-list-item>
                    <span matListItemTitle>Backend API</span>
                    <span matListItemLine>/api/v1 (FastAPI)</span>
                </mat-list-item>
             </mat-list>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    mat-icon {
        vertical-align: middle;
    }
  `]
})
export class SettingsComponent {
  store = inject(AppStore);

  setTheme(theme: Theme) {
    this.store.setTheme(theme);
  }
}
