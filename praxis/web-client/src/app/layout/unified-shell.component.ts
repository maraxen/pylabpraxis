import { Component, inject, signal, computed, effect, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet, RouterLink, RouterLinkActive, NavigationEnd } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { AppStore } from '@core/store/app.store';
import { ModeService } from '@core/services/mode.service';
import { BreadcrumbComponent } from '@core/components/breadcrumb/breadcrumb.component';
import { ExecutionService } from '@features/run-protocol/services/execution.service';
import { ExecutionStatus } from '@features/run-protocol/models/execution.models';
import { filter } from 'rxjs/operators';
import { toSignal } from '@angular/core/rxjs-interop';
import { CommandRegistryService } from '@core/services/command-registry.service';
import { HardwareDiscoveryService } from '@core/services/hardware-discovery.service';
import { HardwareDiscoveryDialogComponent } from '@shared/components/hardware-discovery-dialog/hardware-discovery-dialog.component';
import { OnboardingService } from '@core/services/onboarding.service';
import { TutorialService } from '@core/services/tutorial.service';
import { WelcomeDialogComponent } from '@shared/components/welcome-dialog/welcome-dialog.component';

@Component({
  selector: 'app-unified-shell',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatIconModule,
    MatTooltipModule,
    MatTooltipModule,
    MatButtonModule,
    BreadcrumbComponent
  ],
  template: `
    <div class="shell-layout">
      <!-- Thin Sidebar Rail -->
      <nav class="sidebar-rail">
        <!-- Logo / Home -->
        <a class="nav-item logo-item" [routerLink]="modeService.isBrowserMode() ? '/app/home' : (store.auth().isAuthenticated ? '/app/home' : '/')" matTooltip="Home" matTooltipPosition="right">
          <div class="logo-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/>
            </svg>
          </div>
        </a>

        <div class="nav-divider"></div>

        <!-- Action -->
        <a class="nav-item" data-tour-id="nav-run" routerLink="/app/run" routerLinkActive="active" matTooltip="Run Protocol" matTooltipPosition="right">
          <mat-icon>play_circle</mat-icon>
          <span class="nav-label">Run</span>
        </a>
        <a class="nav-item" data-tour-id="nav-monitor" routerLink="/app/monitor" routerLinkActive="active" matTooltip="Execution Monitor" matTooltipPosition="right">
          <mat-icon>monitor_heart</mat-icon>
          <span class="nav-label">Monitor</span>
        </a>

        <div class="nav-divider"></div>

        <!-- Management -->
        <a class="nav-item" data-tour-id="nav-assets" routerLink="/app/assets" routerLinkActive="active" matTooltip="Assets" matTooltipPosition="right">
          <mat-icon>precision_manufacturing</mat-icon>
          <span class="nav-label">Assets</span>
        </a>
        <a class="nav-item" data-tour-id="nav-protocols" routerLink="/app/protocols" routerLinkActive="active" matTooltip="Protocols" matTooltipPosition="right">
          <mat-icon>science</mat-icon>
          <span class="nav-label">Protocols</span>
        </a>

        <div class="nav-divider"></div>

        <!-- Views -->
        <a class="nav-item" data-tour-id="nav-visualizer" routerLink="/app/visualizer" routerLinkActive="active" matTooltip="Deck Visualizer" matTooltipPosition="right">
          <mat-icon>view_in_ar</mat-icon>
          <span class="nav-label">Deck</span>
        </a>
        <a class="nav-item" data-tour-id="nav-data" routerLink="/app/data" routerLinkActive="active" matTooltip="Data Analysis" matTooltipPosition="right">
          <mat-icon>bar_chart</mat-icon>
          <span class="nav-label">Data</span>
        </a>

        <div class="nav-divider"></div>

        <!-- Knowledge -->
        <a class="nav-item" routerLink="/docs" routerLinkActive="active" matTooltip="Documentation" matTooltipPosition="right">
          <mat-icon>menu_book</mat-icon>
          <span class="nav-label">Docs</span>
        </a>

        <!-- Tools -->
        <a class="nav-item" data-tour-id="nav-repl" routerLink="/app/repl" routerLinkActive="active" matTooltip="REPL" matTooltipPosition="right">
          <mat-icon>terminal</mat-icon>
          <span class="nav-label">REPL</span>
        </a>

        <div class="spacer"></div>

        <!-- System -->
        <a class="nav-item" data-tour-id="nav-settings" routerLink="/app/settings" routerLinkActive="active" matTooltip="Settings" matTooltipPosition="right">
          <mat-icon>settings</mat-icon>
          <span class="nav-label">Settings</span>
        </a>

        <div class="nav-divider"></div>


        <button
          class="nav-item control-btn theme-toggle"
          data-tour-id="theme-toggle"
          (click)="cycleTheme()"
          [matTooltip]="'Theme: ' + (store.theme() | titlecase)"
          matTooltipPosition="right">
          <mat-icon>{{ themeIcon() }}</mat-icon>
          <span class="nav-label small">{{ store.theme() }}</span>
        </button>

        <div 
          class="mode-badge" 
          data-tour-id="status-indicator"
          [class]="systemStatus().color"
          [matTooltip]="systemStatus().message" 
          matTooltipPosition="right">
          <mat-icon>{{ systemStatus().icon }}</mat-icon>
          <span class="nav-label">{{ modeService.modeLabel() }}</span>
        </div>

        @if (store.auth().isAuthenticated) {
          <button
            class="nav-item control-btn"
            (click)="logout()"
            matTooltip="Logout"
            matTooltipPosition="right">
            <mat-icon>logout</mat-icon>
            <span class="nav-label">Logout</span>
          </button>
        } @else if (!modeService.isBrowserMode()) {
          <a
            class="nav-item"
            routerLink="/login"
            matTooltip="Sign In"
            matTooltipPosition="right">
            <mat-icon>login</mat-icon>
            <span class="nav-label">Login</span>
          </a>
        }
      </nav>

      <!-- Main Content -->
      <div class="main-wrapper">
        <header class="px-6 py-4 flex items-center border-b border-[var(--mat-sys-outline-variant)] bg-[var(--mat-sys-surface)]">
            <app-breadcrumb></app-breadcrumb>
        </header>
        <main class="main-content">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>
  `,
  styles: [`
    .shell-layout {
      display: flex;
      height: 100vh;
      width: 100vw;
      overflow: hidden;
      background: var(--theme-bg-gradient);
    }

    /* Sidebar Rail */
    .sidebar-rail {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 80px;
      min-width: 80px;
      background: var(--mat-sys-surface-container);
      border-right: 1px solid var(--mat-sys-outline-variant);
      z-index: 100;
      padding: 12px 0;
      gap: 4px;
    }

    .nav-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 64px;
      height: 56px;
      border-radius: 12px;
      margin: 2px 0;
      color: var(--mat-sys-on-surface-variant);
      text-decoration: none;
      transition: all 0.2s ease;
      cursor: pointer;
      border: none;
      background: transparent;
      gap: 2px;
    }

    .nav-item:hover {
      background: var(--mat-sys-surface-variant);
      color: var(--mat-sys-on-surface);
    }

    .nav-item.active {
      background: var(--mat-sys-primary-container);
      color: var(--mat-sys-on-primary-container);
    }

    .nav-item mat-icon {
      font-size: 24px;
      width: 24px;
      height: 24px;
    }

    .nav-label {
      font-size: 10px;
      font-weight: 500;
      letter-spacing: 0.3px;
      text-transform: uppercase;
      opacity: 0.8;
    }

    .nav-item.active .nav-label {
      opacity: 1;
      font-weight: 700;
    }

    /* Logo */
    .logo-item {
      margin-bottom: 8px;
      opacity: 1 !important;
      height: 48px; /* Restore simpler height for logo */
    }

    .logo-icon {
      width: 40px;
      height: 40px;
      padding: 6px;
      background: linear-gradient(135deg, var(--primary-color) 0%, #d85a7f 100%);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(237, 122, 155, 0.3);
    }

    .logo-icon svg {
      width: 100%;
      height: 100%;
      color: white;
    }

    /* Divider */
    .nav-divider {
      width: 40px;
      height: 1px;
      background: var(--mat-sys-outline-variant);
      margin: 4px 0;
    }

    /* Spacer */
    .spacer {
      flex: 1;
    }

    /* Control Buttons */
    .control-btn {
      color: var(--mat-sys-on-surface-variant);
    }

    /* Mode Badge */
    .mode-badge {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 64px;
      height: 56px;
      border-radius: 12px;
      margin: 2px 0;
      background: var(--mat-sys-surface-container-high);
      border: 1px solid var(--mat-sys-outline-variant);
      color: var(--mat-sys-on-surface-variant);
      gap: 2px;
    }

    .mode-badge.good {
      background: rgba(76, 175, 80, 0.15);
      border-color: #4caf50;
      color: #4caf50;
    }

    .mode-badge.attention {
      background: rgba(255, 152, 0, 0.15);
      border-color: #ff9800;
      color: #ff9800;
    }

    .mode-badge.problem {
      background: rgba(244, 67, 54, 0.15);
      border-color: #f44336;
      color: #f44336;
    }

    .theme-toggle {
      height: 48px;
    }

    .nav-label.small {
      font-size: 8px;
      opacity: 0.6;
    }

    .mode-badge mat-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .mode-badge .nav-label {
      font-size: 9px;
      font-weight: 600;
      text-transform: uppercase;
    }

    /* Main Content */
    .main-wrapper {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      min-width: 0;
    }

    .main-content {
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .sidebar-rail {
        width: 64px;
        min-width: 64px;
      }
      
      .nav-item {
        width: 52px;
        height: 52px;
      }

      .nav-label {
        font-size: 9px;
      }

      .nav-divider {
        width: 32px;
      }
    }
  `]
})
export class UnifiedShellComponent implements OnInit {
  store = inject(AppStore);
  router = inject(Router);
  modeService = inject(ModeService);
  executionService = inject(ExecutionService);
  private commandRegistry = inject(CommandRegistryService);
  private hardwareDiscovery = inject(HardwareDiscoveryService);
  private dialog = inject(MatDialog);
  private onboarding = inject(OnboardingService);
  private tutorial = inject(TutorialService);

  constructor() {
    this.registerCommands();
  }

  ngOnInit() {
    // Check if we need to show welcome dialog
    if (this.onboarding.shouldShowWelcome()) {
      this.dialog.open(WelcomeDialogComponent, {
        width: '600px',
        disableClose: true,
        autoFocus: false
      });
    } else if (localStorage.getItem('praxis_pending_tutorial') === 'true') {
      // Pending tutorial start after reload
      localStorage.removeItem('praxis_pending_tutorial');
      // Small delay to ensure UI is largely rendered
      setTimeout(() => this.tutorial.start(), 1000);
    }
  }

  private registerCommands() {
    this.commandRegistry.registerCommand({
      id: 'hardware.discover',
      label: 'Discover Hardware',
      description: 'Scan for connected devices (Serial/USB)',
      icon: 'usb',
      category: 'Hardware',
      action: () => {
        this.dialog.open(HardwareDiscoveryDialogComponent, {
          width: '800px',
          maxHeight: '90vh'
        });
        if (!this.hardwareDiscovery.isDiscovering()) {
          this.hardwareDiscovery.discoverAll();
        }
      }
    });
  }

  readonly systemStatus = computed(() => {
    const isBrowser = this.modeService.isBrowserMode();
    const isConnected = this.executionService.isConnected();
    const run = this.executionService.currentRun();
    const mode = this.modeService.modeLabel();

    // Problem State: Disconnected (non-browser) or run failed
    if ((!isBrowser && !isConnected && (mode === 'Production' || mode === 'Lite')) || run?.status === ExecutionStatus.FAILED) {
      return {
        color: 'problem',
        icon: 'error_outline',
        message: run?.status === ExecutionStatus.FAILED ? `Run Failed: ${run.protocolName}` : 'System Disconnected'
      };
    }

    // Attention State: Running, pending or cancelled
    if (run?.status === ExecutionStatus.RUNNING || run?.status === ExecutionStatus.PENDING || run?.status === ExecutionStatus.CANCELLED) {
      return {
        color: 'attention',
        icon: run.status === ExecutionStatus.RUNNING ? 'running_with_errors' : 'hourglass_empty',
        message: `Protocol ${run.status}: ${run.protocolName}`
      };
    }

    // Good State: Everything else
    return {
      color: 'good',
      icon: isBrowser ? 'cloud_done' : 'check_circle_outline',
      message: `System Ready - ${mode} Mode`
    };
  });

  // Check if current route is in /app/*
  isInApp(): boolean {
    return this.router.url.startsWith('/app');
  }

  themeIcon(): string {
    switch (this.store.theme()) {
      case 'light': return 'light_mode';
      case 'dark': return 'dark_mode';
      case 'system': return 'brightness_auto';
      default: return 'brightness_auto';
    }
  }

  cycleTheme(): void {
    const themes: Array<'light' | 'dark' | 'system'> = ['light', 'dark', 'system'];
    const currentIndex = themes.indexOf(this.store.theme());
    const nextIndex = (currentIndex + 1) % themes.length;
    this.store.setTheme(themes[nextIndex]);
  }

  logout(): void {
    this.store.logout();
  }
}
