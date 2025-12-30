import { Component, signal, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

@Component({
  selector: 'app-splash',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule
  ],
  template: `
    <div class="splash-container" [class.light-mode]="isLightTheme()">
      <!-- Theme toggle button -->
      <button
        mat-icon-button
        class="theme-toggle"
        (click)="toggleTheme()"
        [matTooltip]="isLightTheme() ? 'Switch to Dark Mode' : 'Switch to Light Mode'">
        <mat-icon>{{ isLightTheme() ? 'dark_mode' : 'light_mode' }}</mat-icon>
      </button>

      <!-- Animated background -->
      <div class="bg-gradient"></div>
      <div class="floating-orbs">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
      </div>

      <!-- Main content -->
      <div class="splash-content">
        <!-- Hero Section -->
        <section class="hero">
          <div class="logo-container">
            <div class="logo-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/>
              </svg>
            </div>
          </div>

          <h1 class="hero-title">
            <span class="title-gradient">Praxis</span>
          </h1>

          <p class="hero-subtitle">
            Next-Generation Laboratory Automation Platform
          </p>

          <p class="hero-description">
            Streamline your lab workflows with intelligent protocol execution,
            real-time monitoring, and seamless integration with PyLabRobot.
          </p>

          <div class="cta-buttons">
            <a mat-flat-button class="cta-primary" routerLink="/login">
              <mat-icon>login</mat-icon>
              Sign In
            </a>
            <a mat-stroked-button class="cta-secondary" routerLink="/register">
              <mat-icon>person_add</mat-icon>
              Create Account
            </a>
          </div>

          <a class="github-link" href="https://github.com/PyLabRobot/pylabrobot" target="_blank">
            <mat-icon>code</mat-icon>
            View on GitHub
          </a>
        </section>

        <!-- Features Section -->
        <section class="features">
          <div class="feature-card">
            <div class="feature-icon">
              <mat-icon>science</mat-icon>
            </div>
            <h3>Protocol Management</h3>
            <p>Upload, configure, and execute Python protocols with a visual interface</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <mat-icon>hub</mat-icon>
            </div>
            <h3>Device Integration</h3>
            <p>Connect liquid handlers, plate readers, and more through PyLabRobot</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <mat-icon>monitoring</mat-icon>
            </div>
            <h3>Real-Time Monitoring</h3>
            <p>Track execution progress with live status updates and logging</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <mat-icon>view_in_ar</mat-icon>
            </div>
            <h3>Deck Visualization</h3>
            <p>Interactive deck layouts showing labware positions and status</p>
          </div>
        </section>

        <!-- Footer -->
        <footer class="splash-footer">
          <p>Built with Angular & Material • Powered by PyLabRobot</p>
          <p class="version">v1.0.0</p>
        </footer>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      min-height: 100vh;
    }

    .splash-container {
      min-height: 100vh;
      position: relative;
      overflow: hidden;
      background: var(--theme-bg-gradient);
      transition: all 0.4s ease;
    }

    /* Theme Toggle Button */
    .theme-toggle {
      position: fixed;
      top: 1.5rem;
      right: 1.5rem;
      z-index: 100;
      background: var(--theme-surface) !important;
      border: 1px solid var(--theme-border) !important;
      color: var(--theme-text-primary) !important;
      transition: all 0.3s ease;
    }

    .theme-toggle:hover {
      background: var(--theme-surface-elevated) !important;
      transform: scale(1.1);
    }

    /* Animated Background */
    .bg-gradient {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background:
        radial-gradient(ellipse at 20% 20%, var(--aurora-primary) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, var(--aurora-secondary) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, var(--aurora-primary) 0%, transparent 70%);
      opacity: 0.5;
    }

    .floating-orbs {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      pointer-events: none;
    }

    .orb {
      position: absolute;
      border-radius: 50%;
      filter: blur(80px);
      opacity: 0.4;
      animation: float 20s ease-in-out infinite;
    }

    .orb-1 {
      width: 400px;
      height: 400px;
      background: var(--primary-color);
      top: -100px;
      left: -100px;
      animation-delay: 0s;
    }

    .orb-2 {
      width: 300px;
      height: 300px;
      background: var(--tertiary-color);
      bottom: -50px;
      right: -50px;
      animation-delay: -7s;
    }

    .orb-3 {
      width: 200px;
      height: 200px;
      background: linear-gradient(var(--primary-color), var(--tertiary-color));
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      animation-delay: -14s;
    }

    @keyframes float {
      0%, 100% { transform: translate(0, 0) scale(1); }
      33% { transform: translate(30px, -30px) scale(1.05); }
      66% { transform: translate(-20px, 20px) scale(0.95); }
    }

    /* Main Content */
    .splash-content {
      position: relative;
      z-index: 1;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      padding: 2rem;
    }

    /* Hero Section */
    .hero {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 4rem 1rem;
    }

    .logo-container {
      margin-bottom: 2rem;
    }

    .logo-icon {
      width: 100px;
      height: 100px;
      padding: 1.5rem;
      background: linear-gradient(135deg, var(--primary-color) 0%, var(--tertiary-color) 100%);
      border-radius: 32px;
      box-shadow: 0 20px 60px rgba(237, 122, 155, 0.3);
      animation: pulse 4s ease-in-out infinite;
    }

    .logo-icon svg {
      width: 100%;
      height: 100%;
      color: white;
    }

    @keyframes pulse {
      0%, 100% { transform: scale(1); box-shadow: 0 20px 60px rgba(237, 122, 155, 0.3); }
      50% { transform: scale(1.02); box-shadow: 0 25px 80px rgba(237, 122, 155, 0.4); }
    }

    .hero-title {
      font-size: clamp(2.5rem, 8vw, 5rem);
      font-weight: 800;
      margin: 0 0 1rem;
      line-height: 1.1;
    }

    .title-gradient {
      background: linear-gradient(135deg, var(--theme-text-primary) 0%, var(--theme-text-secondary) 50%, var(--primary-color) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .hero-subtitle {
      font-size: clamp(1.1rem, 3vw, 1.5rem);
      font-weight: 300;
      color: var(--theme-text-secondary);
      margin: 0 0 1.5rem;
      letter-spacing: 0.05em;
    }

    .hero-description {
      max-width: 600px;
      font-size: 1.1rem;
      font-weight: 400;
      color: var(--theme-text-tertiary);
      line-height: 1.7;
      margin: 0 0 2.5rem;
    }

    .cta-buttons {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      justify-content: center;
      margin-bottom: 1.5rem;
    }

    .cta-primary {
      padding: 1rem 2rem !important;
      font-size: 1rem !important;
      font-weight: 600;
      border-radius: 12px !important;
      background: linear-gradient(135deg, var(--primary-color) 0%, #d85a7f 100%) !important;
      color: white !important;
      box-shadow: 0 8px 30px rgba(237, 122, 155, 0.4);
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .cta-primary:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 40px rgba(237, 122, 155, 0.5);
    }

    .cta-secondary {
      padding: 1rem 2rem !important;
      font-size: 1rem !important;
      font-weight: 500;
      border-radius: 12px !important;
      border-color: var(--theme-border) !important;
      color: var(--theme-text-primary) !important;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.3s ease;
    }

    .cta-secondary:hover {
      background: var(--theme-surface) !important;
      border-color: var(--primary-color) !important;
    }

    .github-link {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      color: var(--theme-text-tertiary);
      text-decoration: none;
      font-size: 0.95rem;
      font-weight: 500;
      transition: all 0.3s ease;
    }

    .github-link:hover {
      color: var(--primary-color);
    }

    .github-link mat-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    /* Features Section */
    .features {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
      padding: 3rem 1rem;
      max-width: 1200px;
      margin: 0 auto;
      width: 100%;
    }

    .feature-card {
      background: var(--theme-surface);
      backdrop-filter: blur(10px);
      border: 1px solid var(--theme-border);
      border-radius: 20px;
      padding: 2rem;
      text-align: center;
      transition: all 0.3s ease;
    }

    .feature-card:hover {
      background: var(--theme-surface-elevated);
      transform: translateY(-4px);
      box-shadow: var(--glass-shadow);
    }

    .feature-icon {
      width: 60px;
      height: 60px;
      margin: 0 auto 1rem;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, var(--aurora-primary) 0%, var(--aurora-secondary) 100%);
      border-radius: 16px;
    }

    .feature-icon mat-icon {
      font-size: 28px;
      width: 28px;
      height: 28px;
      color: var(--primary-color);
    }

    .feature-card h3 {
      font-size: 1.2rem;
      font-weight: 600;
      color: var(--theme-text-primary);
      margin: 0 0 0.75rem;
    }

    .feature-card p {
      font-size: 0.95rem;
      font-weight: 400;
      color: var(--theme-text-tertiary);
      margin: 0;
      line-height: 1.6;
    }

    /* Footer */
    .splash-footer {
      text-align: center;
      padding: 2rem;
      color: var(--theme-text-tertiary);
      font-size: 0.9rem;
    }

    .splash-footer p {
      margin: 0;
    }

    .version {
      margin-top: 0.5rem !important;
      font-size: 0.8rem;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .splash-content {
        padding: 1rem;
      }

      .hero {
        padding: 2rem 1rem;
      }

      .logo-icon {
        width: 80px;
        height: 80px;
      }

      .features {
        grid-template-columns: 1fr;
        padding: 2rem 1rem;
      }

      .cta-buttons {
        flex-direction: column;
        width: 100%;
        max-width: 300px;
      }

      .cta-primary, .cta-secondary {
        width: 100%;
        justify-content: center;
      }

      .theme-toggle {
        top: 1rem;
        right: 1rem;
      }
    }
  `]
})
export class SplashComponent {
  isLightTheme = signal(false);

  constructor() {
    // Check localStorage for saved preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
      this.isLightTheme.set(true);
      document.body.classList.add('light-theme');
    }

    // Effect to update body class when theme changes
    effect(() => {
      if (this.isLightTheme()) {
        document.body.classList.add('light-theme');
        document.body.classList.remove('dark-theme');
      } else {
        document.body.classList.remove('light-theme');
        document.body.classList.add('dark-theme');
      }
    });
  }

  toggleTheme() {
    this.isLightTheme.update(v => !v);
    localStorage.setItem('theme', this.isLightTheme() ? 'light' : 'dark');
  }
}
