
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatExpansionModule } from '@angular/material/expansion';
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
    MatListModule,
    MatSlideToggleModule,
    MatExpansionModule
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

        <!-- Features -->
        <mat-card class="glass-panel">
          <mat-card-header>
            <mat-icon mat-card-avatar class="text-accent scale-125">extension</mat-icon>
            <mat-card-title>Features</mat-card-title>
            <mat-card-subtitle>Enable or disable optional capabilities</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content class="pt-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-medium">Maintenance Tracking</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">Track asset maintenance schedules and alerts</p>
              </div>
              <mat-slide-toggle 
                [checked]="store.maintenanceEnabled()" 
                (change)="store.setMaintenanceEnabled($event.checked)"
                color="primary">
              </mat-slide-toggle>
            </div>
          </mat-card-content>
        </mat-card>

        <!-- Remote Hardware Access -->
        <mat-card class="glass-panel">
          <mat-card-header>
            <mat-icon mat-card-avatar class="text-warning scale-125">lan</mat-icon>
            <mat-card-title>Remote Hardware Access</mat-card-title>
            <mat-card-subtitle>Connect local hardware to cloud execution</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content class="pt-4">
            <p class="mb-4 text-sm opacity-80">
              To expose local lab equipment to cloud-based protocol execution:
            </p>
            <mat-list>
              <mat-list-item>
                <mat-icon matListItemIcon class="text-primary">download</mat-icon>
                <span matListItemTitle>1. Install the Praxis Agent</span>
                <code matListItemLine class="font-mono text-xs bg-surface-container px-2 py-0.5 rounded">pip install praxis-agent</code>
              </mat-list-item>
              <mat-list-item>
                <mat-icon matListItemIcon class="text-primary">terminal</mat-icon>
                <span matListItemTitle>2. Run with your API token</span>
                <code matListItemLine class="font-mono text-xs bg-surface-container px-2 py-0.5 rounded">praxis-agent --token YOUR_TOKEN</code>
              </mat-list-item>
              <mat-list-item>
                <mat-icon matListItemIcon class="text-primary">check_circle</mat-icon>
                <span matListItemTitle>3. Devices appear in discovery</span>
                <span matListItemLine class="text-sm opacity-70">Local hardware is now accessible remotely</span>
              </mat-list-item>
            </mat-list>
            <mat-expansion-panel class="mt-4">
              <mat-expansion-panel-header>
                <mat-panel-title>
                  <mat-icon class="mr-2 text-sm">info</mat-icon>
                  Alternative: ngrok tunneling
                </mat-panel-title>
              </mat-expansion-panel-header>
              <div class="p-4 space-y-2">
                <p class="text-sm">For direct serial port forwarding:</p>
                <code class="block bg-surface-container p-2 rounded font-mono text-xs">ngrok tcp 9600 --region=us</code>
                <p class="text-xs opacity-70 mt-2">
                  Configure the tunnel URL in machine connection settings.
                </p>
              </div>
            </mat-expansion-panel>
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
