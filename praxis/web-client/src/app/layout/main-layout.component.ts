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
          <a class="nav-item" routerLink="/app/home" routerLinkActive="active">
            <mat-icon>dashboard</mat-icon>
            <span class="nav-label">Home</span>
          </a>
          <a class="nav-item" routerLink="/app/assets" routerLinkActive="active">
            <mat-icon>science</mat-icon>
            <span class="nav-label">Assets</span>
          </a>
          <a class="nav-item" routerLink="/app/protocols" routerLinkActive="active">
            <mat-icon>assignment</mat-icon>
            <span class="nav-label">Protocols</span>
          </a>
          <a class="nav-item" routerLink="/app/run" routerLinkActive="active">
            <mat-icon>play_circle</mat-icon>
            <span class="nav-label">Run</span>
          </a>
          <a class="nav-item" routerLink="/app/visualizer" routerLinkActive="active">
            <mat-icon>view_in_ar</mat-icon>
            <span class="nav-label">Deck</span>
          </a>
          <a class="nav-item" routerLink="/app/data" routerLinkActive="active">
            <mat-icon>bar_chart</mat-icon>
            <span class="nav-label">Data</span>
          </a>
          <a class="nav-item" routerLink="/app/settings" routerLinkActive="active">
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
      background: rgba(30, 30, 45, 0.6); /* Semi-transparent dark */
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-right: 1px solid rgba(255, 255, 255, 0.08);
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
      color: var(--primary-color);
      filter: drop-shadow(0 0 8px rgba(237, 122, 155, 0.4));
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
      padding: 12px 0;
      border-radius: 16px;
      text-decoration: none;
      color: rgba(255, 255, 255, 0.5);
      transition: all 0.2s ease;
      cursor: pointer;
      border: 1px solid transparent;
    }

    .nav-item mat-icon {
      font-size: 24px;
      width: 24px;
      height: 24px;
      margin-bottom: 4px;
      transition: transform 0.2s ease;
    }

    .nav-label {
      font-size: 11px;
      font-weight: 500;
      text-align: center;
      line-height: 1.2;
    }

    .nav-item:hover {
      background: rgba(255, 255, 255, 0.08);
      color: white;
      transform: translateY(-1px);
    }
    
    .nav-item:hover mat-icon {
      transform: scale(1.1);
      color: var(--primary-color);
    }

    .nav-item.active {
      background: rgba(237, 122, 155, 0.15); /* Primary low opacity */
      color: white;
      border-color: rgba(237, 122, 155, 0.3);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .nav-item.active mat-icon {
      color: var(--primary-color);
    }

    /* Bottom Controls */
    .nav-controls {
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding: 8px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      margin-top: auto;
      background: rgba(0, 0, 0, 0.1);
    }

    .nav-control-btn {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 8px 0;
      border-radius: 12px;
      background: transparent;
      border: none;
      color: rgba(255, 255, 255, 0.5);
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .nav-control-btn mat-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
      margin-bottom: 2px;
    }

    .nav-control-btn .nav-label {
      font-size: 10px;
    }

    .nav-control-btn:hover {
      background: rgba(255, 255, 255, 0.08);
      color: white;
    }

    .nav-control-btn.active {
      background: rgba(237, 122, 155, 0.15);
      color: white;
    }

    .nav-control-btn.active mat-icon {
      color: var(--primary-color);
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

      .nav-label {
        display: none;
      }

      .nav-item {
        padding: 16px 0;
      }

      .nav-control-btn {
        padding: 12px 0;
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