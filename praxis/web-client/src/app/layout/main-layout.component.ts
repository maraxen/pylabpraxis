import { Component, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
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
    StatusBarComponent
  ],
  template: `
    <mat-sidenav-container class="sidenav-container">
      <mat-sidenav
        #drawer
        class="sidenav"
        fixedInViewport
        [attr.role]="(isHandset() ? 'dialog' : 'navigation')"
        [mode]="(isHandset() ? 'over' : 'side')"
        [opened]="(store.sidebarOpen() || !isHandset())">

        <mat-toolbar>PyLabPraxis</mat-toolbar>

        <mat-nav-list>
          <a mat-list-item routerLink="/app/home" routerLinkActive="active-link">
            <mat-icon matListItemIcon>dashboard</mat-icon>
            <span matListItemTitle>Dashboard</span>
          </a>
          <a mat-list-item routerLink="/app/assets" routerLinkActive="active-link">
            <mat-icon matListItemIcon>science</mat-icon>
            <span matListItemTitle>Assets</span>
          </a>
          <a mat-list-item routerLink="/app/protocols" routerLinkActive="active-link">
             <mat-icon matListItemIcon>assignment</mat-icon>
             <span matListItemTitle>Protocols</span>
          </a>
          <a mat-list-item routerLink="/app/run" routerLinkActive="active-link">
             <mat-icon matListItemIcon>play_circle</mat-icon>
             <span matListItemTitle>Run Protocol</span>
          </a>
           <a mat-list-item routerLink="/app/visualizer" routerLinkActive="active-link">
             <mat-icon matListItemIcon>view_in_ar</mat-icon>
             <span matListItemTitle>Visualizer</span>
          </a>
           <a mat-list-item routerLink="/app/settings" routerLinkActive="active-link">
             <mat-icon matListItemIcon>settings</mat-icon>
             <span matListItemTitle>Settings</span>
          </a>
          <a mat-list-item routerLink="/app/stress-test" routerLinkActive="active-link">
             <mat-icon matListItemIcon>speed</mat-icon>
             <span matListItemTitle>Stress Test</span>
          </a>
        </mat-nav-list>
      </mat-sidenav>

      <mat-sidenav-content>
        <mat-toolbar color="primary">
          <button
            type="button"
            aria-label="Toggle sidenav"
            mat-icon-button
            (click)="store.toggleSidebar()">
            <mat-icon>menu</mat-icon>
          </button>
          <span>PyLabPraxis</span>
          <span class="spacer"></span>
          @if (store.auth().isAuthenticated) {
            <span class="text-sm mr-2">{{ store.auth().user?.username }}</span>
          }
          <button mat-icon-button (click)="toggleTheme()">
            <mat-icon>{{ store.theme() === 'dark' ? 'light_mode' : 'dark_mode' }}</mat-icon>
          </button>
          @if (store.auth().isAuthenticated) {
            <button mat-icon-button (click)="logout()" matTooltip="Logout">
              <mat-icon>logout</mat-icon>
            </button>
          }
        </mat-toolbar>

        <main class="content p-4">
          <router-outlet></router-outlet>
        </main>

        <app-status-bar></app-status-bar>

      </mat-sidenav-content>
    </mat-sidenav-container>
  `,
  styles: [`
    .sidenav-container {
      height: 100%;
    }
    .sidenav {
      width: 250px;
    }
    .mat-toolbar.mat-primary {
      position: sticky;
      top: 0;
      z-index: 1;
    }
    .spacer {
      flex: 1 1 auto;
    }
    .active-link {
        background-color: rgba(0, 0, 0, 0.05); /* or use theme color */
        border-right: 4px solid var(--mat-sys-primary);
    }
  `]
})
export class MainLayoutComponent {
  store = inject(AppStore);
  router = inject(Router);
  private breakpointObserver = inject(BreakpointObserver);

  isHandset = toSignal(this.breakpointObserver.observe(Breakpoints.Handset).pipe(map(result => result.matches)), { initialValue: false });

  toggleTheme() {
    const newTheme = this.store.theme() === 'dark' ? 'light' : 'dark';
    this.store.setTheme(newTheme);
    if (newTheme === 'dark') {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }
  }

  logout() {
    // Use Keycloak logout via AppStore
    this.store.logout();
  }
}