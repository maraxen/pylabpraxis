import { Component, inject, OnInit } from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [
    MatCardModule,
    MatProgressSpinnerModule,
    MatIconModule
],
  template: `
    <div class="forgot-container">
      <div class="forgot-card">
        <div class="logo-section">
          <div class="logo-icon">
            <mat-icon class="lock-icon">lock_reset</mat-icon>
          </div>
          <h1 class="app-title">Reset Password</h1>
          <p class="app-subtitle">Redirecting to password reset...</p>
        </div>

        <mat-card class="glass-card">
          <mat-card-content>
            <div class="loading-content">
              <mat-spinner diameter="40"></mat-spinner>
              <p class="loading-text">Please wait...</p>
            </div>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      min-height: 100vh;
      width: 100%;
    }

    .forgot-container {
      min-height: 100vh;
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--theme-bg-gradient, linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%));
      padding: 2rem 1rem;
      box-sizing: border-box;
      position: relative;
      overflow: hidden;
    }

    .forgot-container::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle at 30% 20%, var(--aurora-primary, rgba(237, 122, 155, 0.15)) 0%, transparent 50%),
                  radial-gradient(circle at 70% 80%, var(--aurora-secondary, rgba(115, 169, 194, 0.15)) 0%, transparent 50%);
      animation: aurora 20s ease-in-out infinite alternate;
    }

    @keyframes aurora {
      0% { transform: translate(0, 0) rotate(0deg); }
      100% { transform: translate(-5%, 5%) rotate(10deg); }
    }

    .forgot-card {
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
      margin-bottom: 1.5rem;
      color: var(--theme-text-primary, white);
    }

    .logo-icon {
      width: 80px;
      height: 80px;
      margin: 0 auto 1rem;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, var(--primary-color, #ED7A9B) 0%, var(--tertiary-color, #73A9C2) 100%);
      border-radius: 24px;
      box-shadow: 0 8px 32px rgba(237, 122, 155, 0.3);
    }

    .logo-icon mat-icon {
      font-size: 40px;
      width: 40px;
      height: 40px;
      color: white;
    }

    .app-title {
      font-size: 1.75rem;
      font-weight: 700;
      margin: 0;
      color: var(--theme-text-primary, white);
    }

    .app-subtitle {
      font-size: 0.95rem;
      margin: 0.5rem 0 0 0;
      color: var(--theme-text-secondary, rgba(255, 255, 255, 0.7));
      font-weight: 400;
    }

    .glass-card {
      width: 100%;
      background: var(--glass-bg, rgba(255, 255, 255, 0.08)) !important;
      backdrop-filter: var(--glass-blur, blur(20px));
      -webkit-backdrop-filter: var(--glass-blur, blur(20px));
      border: var(--glass-border, 1px solid rgba(255, 255, 255, 0.1));
      border-radius: 24px !important;
      box-shadow: var(--glass-shadow, 0 8px 32px rgba(0, 0, 0, 0.3));
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
      color: var(--theme-text-secondary, rgba(255, 255, 255, 0.7));
      font-size: 1rem;
      margin: 0;
    }

    @media (max-width: 480px) {
      .forgot-container {
        padding: 1rem;
      }

      .logo-icon {
        width: 70px;
        height: 70px;
      }

      .logo-icon mat-icon {
        font-size: 36px;
        width: 36px;
        height: 36px;
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
export class ForgotPasswordComponent implements OnInit {
  ngOnInit() {
    // Redirect to Keycloak's password reset page
    // Keycloak handles password reset through its login page with reset action
    const keycloakUrl = environment.keycloak.url;
    const realm = environment.keycloak.realm;
    const clientId = environment.keycloak.clientId;
    const redirectUri = encodeURIComponent(window.location.origin + '/login');

    // Keycloak reset credentials URL
    const resetUrl = `${keycloakUrl}/realms/${realm}/login-actions/reset-credentials?client_id=${clientId}&redirect_uri=${redirectUri}`;

    window.location.href = resetUrl;
  }
}
