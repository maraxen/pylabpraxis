import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { AppStore } from '@core/store/app.store';
import { StatusBarComponent } from '@core/components/status-bar/status-bar.component';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { map } from 'rxjs/operators';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    StatusBarComponent
  ],
  template: `
    <div class="app-layout">
      <!-- Navigation Rail -->
      <nav class="nav-rail">
        <!-- Logo -->
        <div class="nav-logo">
          <mat-icon class="logo-icon">biotech</mat-icon>
        </div>

        <!-- Navigation Items -->
        <div class="nav-items">
          <a class="nav-item" routerLink="/app/home" routerLinkActive="active" matTooltip="Home" matTooltipPosition="right">
            <mat-icon>dashboard</mat-icon>
            <span class="nav-label">Home</span>
          </a>
          <a class="nav-item" routerLink="/app/assets" routerLinkActive="active" matTooltip="Assets" matTooltipPosition="right">
            <mat-icon>science</mat-icon>
            <span class="nav-label">Assets</span>
          </a>
          <a class="nav-item" routerLink="/app/protocols" routerLinkActive="active" matTooltip="Protocols" matTooltipPosition="right">
            <mat-icon>assignment</mat-icon>
            <span class="nav-label">Protocols</span>
          </a>
          <a class="nav-item" routerLink="/app/run" routerLinkActive="active" matTooltip="Run Protocol" matTooltipPosition="right">
            <mat-icon>play_circle</mat-icon>
            <span class="nav-label">Run</span>
          </a>
          <a class="nav-item" routerLink="/app/workcell" routerLinkActive="active" matTooltip="Workcell View" matTooltipPosition="right">
            <mat-icon>view_in_ar</mat-icon>
            <span class="nav-label">Workcell</span>
          </a>
          <a class="nav-item" routerLink="/app/playground" routerLinkActive="active" matTooltip="Playground" matTooltipPosition="right">
            <mat-icon>terminal</mat-icon>
            <span class="nav-label">Playground</span>
          </a>
          <a class="nav-item" routerLink="/app/data" routerLinkActive="active" matTooltip="Data Analysis" matTooltipPosition="right">
            <mat-icon>bar_chart</mat-icon>
            <span class="nav-label">Data</span>
          </a>
          <a class="nav-item" routerLink="/app/settings" routerLinkActive="active" matTooltip="Settings" matTooltipPosition="right">
            <mat-icon>settings</mat-icon>
            <span class="nav-label">Settings</span>
          </a>
        </div>

        <!-- Bottom Controls -->
        <div class="nav-controls">
          <!-- Simulation Mode Toggle -->
          <button
            class="nav-control-btn"
            [class.active]="store.simulationMode()"
            (click)="store.toggleSimulationMode()"
            matTooltip="{{ store.simulationMode() ? 'Simulation Mode ON' : 'LIVE Hardware Mode' }}"
            matTooltipPosition="right">
            <mat-icon>{{ store.simulationMode() ? 'science' : 'precision_manufacturing' }}</mat-icon>
            <span class="nav-label">{{ store.simulationMode() ? 'Sim' : 'Live' }}</span>
          </button>

          <!-- Theme Toggle -->
          <button
            class="nav-control-btn"
            (click)="cycleTheme()"
            matTooltip="Theme: {{ store.theme() | titlecase }}"
            matTooltipPosition="right">
            <mat-icon>{{ themeIcon() }}</mat-icon>
            <span class="nav-label">{{ store.theme() | titlecase }}</span>
          </button>

          <!-- Logout -->
          @if (store.auth().isAuthenticated) {
            <button
              class="nav-control-btn"
              (click)="logout()"
              matTooltip="Logout"
              matTooltipPosition="right">
              <mat-icon>logout</mat-icon>
              <span class="nav-label">Logout</span>
            </button>
          }
        </div>
      </nav>

      <!-- Main Content Area -->
      <div class="main-content-wrapper">
        <main class="main-content">
          <router-outlet></router-outlet>
        </main>
        <app-status-bar></app-status-bar>
      </div>
    </div>
  `,
  styles: [`
    .app-layout {
      display: flex;
      height: 100vh;
      width: 100vw;
      overflow: hidden;
    }

    /* Navigation Rail */
    .nav-rail {
      display: flex;
      flex-direction: column;
      width: 72px;
      min-width: 72px;
      background: var(--mat-sys-surface-container);
      border-right: 1px solid var(--mat-sys-outline-variant);
      padding: 8px 0;
      overflow: hidden;
      z-index: 50;
    }

    .nav-logo {
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 16px 0;
      margin-bottom: 8px;
    }

    .logo-icon {
      font-size: 32px;
      width: 32px;
      height: 32px;
      color: var(--mat-sys-primary);
      filter: drop-shadow(0 0 8px var(--mat-sys-primary-fixed-dim));
    }

    .nav-items {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding: 0 8px;
    }

    .nav-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 16px 0;
      border-radius: 16px;
      text-decoration: none;
      color: var(--mat-sys-on-surface-variant);
      transition: background 0.2s cubic-bezier(0.4, 0, 0.2, 1), transform 0.2s ease;
      cursor: pointer;
      border: 2px solid transparent;
    }

    .nav-item mat-icon {
      font-size: 24px;
      width: 24px;
      height: 24px;
      transition: transform 0.2s ease;
    }

    .nav-label {
      display: none;
    }

    .nav-item:hover {
      background: var(--mat-sys-surface-variant);
      transform: scale(1.02);
    }
    
    .nav-item:hover mat-icon {
      color: var(--mat-sys-primary);
    }

    .nav-item.active {
      background: var(--mat-sys-primary-container);
      color: var(--mat-sys-on-primary-container);
      border-width: 2px;
      border-color: var(--mat-sys-primary);
    }

    .nav-item.active mat-icon {
      color: var(--mat-sys-primary);
    }

    /* Bottom Controls */
    .nav-controls {
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding: 16px 8px;
      margin-top: auto;
      background: transparent;
    }

    .nav-control-btn {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 12px 0;
      border-radius: 12px;
      background: transparent;
      border: none;
      color: var(--mat-sys-on-surface-variant);
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .nav-control-btn mat-icon {
      font-size: 24px;
      width: 24px;
      height: 24px;
    }

    .nav-control-btn:hover {
      background: var(--mat-sys-surface-variant);
      color: var(--mat-sys-on-surface);
    }

    .nav-control-btn.active {
      background: var(--mat-sys-primary-container);
      color: var(--mat-sys-on-primary-container);
    }

    .nav-control-btn.active mat-icon {
      color: var(--mat-sys-primary);
    }

    /* Main Content */
    .main-content-wrapper {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      position: relative;
    }

    .main-content {
      flex: 1;
      overflow-y: auto;
      padding: 0; /* Remove padding here, components handle it */
      background: transparent; /* Allow body gradient to show */
    }

    /* Responsive - Collapse rail further on small screens */
    @media (max-width: 600px) {
      .nav-rail {
        width: 56px;
        min-width: 56px;
      }
    }

  `]
})
export class MainLayoutComponent {
  store = inject(AppStore);
  router = inject(Router);
  private breakpointObserver = inject(BreakpointObserver);

  isHandset = toSignal(
    this.breakpointObserver.observe(Breakpoints.Handset).pipe(map(result => result.matches)),
    { initialValue: false }
  );

  themeIcon() {
    switch (this.store.theme()) {
      case 'light': return 'light_mode';
      case 'dark': return 'dark_mode';
      case 'system': return 'brightness_auto';
      default: return 'brightness_auto';
    }
  }

  cycleTheme() {
    const themes: Array<'light' | 'dark' | 'system'> = ['light', 'dark', 'system'];
    const currentIndex = themes.indexOf(this.store.theme());
    const nextIndex = (currentIndex + 1) % themes.length;
    this.store.setTheme(themes[nextIndex]);
  }

  logout() {
    this.store.logout();
  }
}