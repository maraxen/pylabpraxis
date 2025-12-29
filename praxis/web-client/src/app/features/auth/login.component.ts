
import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { KeycloakService } from '../../core/auth/keycloak.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatCardModule,
    MatProgressSpinnerModule
  ],
  template: `
    <div class="login-container">
      <div class="login-card">
        <div class="logo-section">
          <div class="logo-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/>
            </svg>
          </div>
          <h1 class="app-title">PyLabPraxis</h1>
          <p class="app-subtitle">Laboratory Automation Platform</p>
        </div>

        <mat-card class="glass-card">
          <mat-card-content>
            <div class="loading-content" *ngIf="loading && !error">
              <mat-spinner diameter="40"></mat-spinner>
              <p class="loading-text">Redirecting to login...</p>
            </div>

            <div class="error-content" *ngIf="error" style="text-align: center; color: #ff6b6b;">
              <p>{{ error }}</p>
              <button mat-button (click)="retryLogin()" style="color: white; border: 1px solid white; padding: 0.5rem 1rem; margin-top: 1rem; cursor: pointer; background: transparent; border-radius: 4px;">
                Retry Login
              </button>
            </div>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      height: 100vh;
      width: 100%;
    }

    .login-container {
      min-height: 100vh;
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      padding: 1rem;
      box-sizing: border-box;
      position: relative;
      overflow: hidden;
    }

    .login-container::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle at 30% 20%, rgba(237, 122, 155, 0.15) 0%, transparent 50%),
                  radial-gradient(circle at 70% 80%, rgba(115, 169, 194, 0.15) 0%, transparent 50%);
      animation: aurora 20s ease-in-out infinite alternate;
    }

    @keyframes aurora {
      0% { transform: translate(0, 0) rotate(0deg); }
      100% { transform: translate(-5%, 5%) rotate(10deg); }
    }

    .login-card {
      position: relative;
      z-index: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100%;
      max-width: 420px;
    }

    .logo-section {
      text-align: center;
      margin-bottom: 2rem;
      color: white;
    }

    .logo-icon {
      width: 80px;
      height: 80px;
      margin: 0 auto 1rem;
      padding: 1rem;
      background: linear-gradient(135deg, var(--primary-color, #ED7A9B) 0%, var(--tertiary-color, #73A9C2) 100%);
      border-radius: 24px;
      box-shadow: 0 8px 32px rgba(237, 122, 155, 0.3);
    }

    .logo-icon svg {
      width: 100%;
      height: 100%;
      color: white;
    }

    .app-title {
      font-size: 2rem;
      font-weight: 700;
      margin: 0;
      background: linear-gradient(90deg, #fff 0%, rgba(255,255,255,0.8) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .app-subtitle {
      font-size: 0.95rem;
      margin: 0.5rem 0 0 0;
      color: rgba(255, 255, 255, 0.7);
      font-weight: 400;
    }

    .glass-card {
      width: 100%;
      background: rgba(255, 255, 255, 0.08) !important;
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 24px !important;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .glass-card mat-card-content {
      padding: 2rem !important;
    }

    .loading-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1.5rem;
      padding: 2rem 0;
    }

    .loading-text {
      color: rgba(255, 255, 255, 0.7);
      font-size: 1rem;
      margin: 0;
    }

    @media (max-width: 480px) {
      .login-container {
        padding: 1rem;
      }

      .logo-icon {
        width: 60px;
        height: 60px;
      }

      .app-title {
        font-size: 1.5rem;
      }

      .glass-card mat-card-content {
        padding: 1.5rem !important;
      }
    }
  `]
})
export class LoginComponent implements OnInit {
  private keycloakService = inject(KeycloakService);

  error = '';
  loading = true;

  // Check if we're in demo mode
  private isDemoMode = ((window as any).__DEMO_MODE__) ||
    ((environment as any).demo === true);

  async ngOnInit() {
    // Demo mode: redirect directly to home without auth
    if (this.isDemoMode) {
      console.log('[Demo Mode] Bypassing login, redirecting to home');
      window.location.href = '/pylabpraxis/app/home';
      return;
    }

    this.loading = true;
    try {
      // If already authenticated, redirect to home
      if (this.keycloakService.isAuthenticated()) {
        window.location.href = '/app/home';
        return;
      }

      // Small delay to ensure init is complete and prevent instant redirect loop if broken
      await new Promise(resolve => setTimeout(resolve, 500));

      // Redirect to Keycloak login
      await this.keycloakService.login();
    } catch (err: any) {
      console.error('Login failed:', err);
      this.error = err?.message || 'Failed to initialize login';
      this.loading = false;
    }
  }

  retryLogin() {
    this.error = '';
    this.ngOnInit();
  }
}
