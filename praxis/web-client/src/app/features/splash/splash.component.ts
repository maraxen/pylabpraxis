import { Component, signal, effect, inject, computed } from '@angular/core';

import { Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { isBrowserModeEnv } from '../../core/services/mode.service';
import { AppStore } from '../../core/store/app.store';

@Component({
  selector: 'app-splash',
  standalone: true,
  imports: [
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
            <div class="logo-icon-container">
              <div class="logo-mark"></div>
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

    .logo-icon-container {
      width: 180px;
      height: 100px;
      padding: 1.5rem;
      background: var(--theme-surface);
      backdrop-filter: blur(10px);
      border: 1px solid var(--theme-border);
      border-radius: 32px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
      display: flex;
      align-items: center;
      justify-content: center;
      animation: pulse 4s ease-in-out infinite;
    }

    .logo-mark {
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, var(--primary-color) 0%, var(--tertiary-color) 100%);
      -webkit-mask: url("data:image/svg+xml,%3Csvg version='1.1' id='Layer_1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x='0px' y='0px' width='100%25' viewBox='355 55 315 320' enable-background='new 0 0 1024 544' xml:space='preserve'%3E%3Cpath fill='%23000000' d='M457.281006,317.309845 C472.602051,301.003693 490.885468,289.019226 508.817078,276.587738 C522.248413,267.276184 535.583191,257.841614 546.114136,245.101135 C555.523682,233.717361 561.449036,221.253204 557.488220,206.012863 C554.868408,195.932404 549.445618,187.434296 542.143372,180.083893 C536.727722,174.632553 530.759460,169.840576 524.647339,165.203201 C522.850647,163.839996 520.563965,162.905380 519.463501,160.139206 C527.944031,154.059570 536.445435,147.970306 544.939636,141.871078 C546.612915,140.669571 548.022583,141.233368 549.451965,142.374985 C569.399292,158.306992 585.755920,176.598831 590.775085,202.830429 C593.958008,219.464844 590.961121,234.909271 583.214355,249.663513 C573.248413,268.644409 557.512695,282.199005 540.555847,294.507599 C527.347595,304.095215 513.850159,313.283905 500.615753,322.836243 C492.211060,328.902649 484.699646,335.974731 478.276947,344.168793 C472.154938,351.979156 468.483490,360.799438 467.556549,370.642853 C467.241150,373.992096 466.097351,375.307220 462.677612,375.228088 C455.183441,375.054626 447.681915,375.140533 440.184235,375.210236 C437.373962,375.236389 435.020508,374.154266 432.711853,372.750122 C391.943420,347.955414 365.806152,312.879364 360.127930,264.919067 C356.303101,232.613235 364.293396,203.309128 389.654938,180.758850 C402.542664,169.299667 418.045532,163.744095 434.962219,161.670212 C455.593506,159.140945 474.478516,165.511887 493.015411,173.264969 C503.412476,177.613541 513.783875,180.424194 524.938965,176.541199 C526.284058,176.072983 527.630310,176.136108 528.764832,176.970398 C537.593201,183.462555 544.790344,191.296677 549.555542,202.023285 C539.020935,207.079025 528.514160,210.467163 517.319275,211.297195 C500.977020,212.508865 486.252136,206.489929 471.625671,200.389816 C459.876740,195.489807 447.802673,192.754700 435.101685,194.914551 C413.946136,198.512161 400.746643,211.514648 395.393402,231.699371 C387.202942,262.582062 396.478394,289.869019 415.211792,314.464478 C424.020782,326.029938 434.836456,335.146027 442.300446,338.546204 C446.704163,331.284180 451.198669,323.929352 457.281006,317.309845z'/%3E%3Cpath fill='%23000000' d='M604.101440,198.869415 C597.818176,197.400314 595.088989,193.728622 593.180054,187.806503 C590.234375,178.668427 585.135193,170.342926 578.535522,161.817368 C584.585449,160.137619 589.814819,161.324631 594.788635,162.209213 C633.516296,169.096878 658.837769,194.585068 665.211914,233.747559 C670.945801,268.976776 661.161438,300.616364 641.148621,329.481445 C628.701111,347.434998 612.384277,361.218872 593.867981,372.579254 C590.902039,374.398956 587.902466,375.273468 584.444397,375.211578 C577.450562,375.086334 570.453064,375.155457 563.457092,375.163849 C560.928894,375.166870 558.887146,374.847107 558.676208,371.540283 C557.616577,354.930847 548.650208,342.612274 536.739746,332.046143 C531.300110,327.220459 525.522888,322.775177 519.635010,317.940796 C522.579834,314.380676 526.480713,312.750366 529.697021,310.273956 C534.182129,306.820587 538.923645,303.695953 543.352417,300.175201 C546.072449,298.012848 548.164978,298.150970 550.792236,300.347992 C563.000549,310.557159 574.341614,321.496216 581.999573,335.708862 C582.542786,336.716980 582.964600,337.859406 584.370605,338.342407 C587.088135,338.008881 588.871765,335.814362 590.884949,334.214325 C618.126892,312.563141 633.523254,284.703094 633.516418,249.522003 C633.513245,232.845810 628.023682,217.811279 615.259705,206.152924 C612.017761,203.191803 608.196045,201.177383 604.101440,198.869415z'/%3E%3Cpath fill='%23000000' d='M507.403839,120.364090 C520.469727,111.378616 533.090027,102.387741 543.639587,90.910744 C551.769653,82.065918 558.232361,72.284454 559.022888,59.770985 C559.222961,56.603893 560.903198,55.600433 563.947998,55.652832 C571.773010,55.787491 579.604736,55.815937 587.428101,55.635883 C591.117859,55.550961 592.485535,56.933697 592.305359,60.605732 C591.529297,76.416580 585.762817,90.337318 576.697693,103.098885 C565.101440,119.423782 549.269897,131.060684 533.283569,142.534348 C522.469360,150.295868 511.105286,157.291855 500.838684,165.814636 C498.912231,167.413864 496.938538,168.243332 494.440186,167.106232 C484.719391,162.681885 474.603943,159.395248 464.274750,156.728485 C463.845123,156.617569 463.511536,156.134628 462.392670,155.218979 C475.659119,141.337006 491.666962,131.307312 507.403839,120.364090z'/%3E%3Cpath fill='%23000000' d='M490.830933,256.162598 C493.721344,258.697784 496.361237,260.984100 498.987823,263.285645 C501.442474,265.436493 504.597504,266.817230 506.653046,270.306122 C500.343994,274.655243 494.131683,279.004913 487.850159,283.252136 C478.446167,289.610474 478.514099,289.479126 469.992126,281.977295 C455.415497,269.145538 443.253540,254.664551 437.213348,235.784302 C434.118347,226.110001 433.689148,216.258362 434.844391,206.255661 C435.266479,202.600983 436.871002,200.710632 440.919739,200.626709 C449.193695,200.455200 457.115723,201.878952 464.882843,204.592224 C467.223938,205.410019 468.627777,206.548294 468.072845,209.293442 C465.230774,223.352554 471.201447,234.629227 479.721191,244.920395 C482.993500,248.873108 486.936981,252.270172 490.830933,256.162598z'/%3E%3Cpath fill='%23000000' d='M461.753265,117.246750 C446.309906,101.832626 436.321564,84.080307 434.044037,62.400234 C433.404419,56.312012 433.725586,55.718037 439.759552,55.698330 C447.251556,55.673870 454.744781,55.766140 462.235321,55.658920 C465.195801,55.616547 467.030029,56.444286 467.187408,59.727695 C467.789673,72.291931 474.401489,81.981178 482.432465,90.887375 C488.354858,97.455170 495.069122,103.184196 502.154907,108.479889 C503.709473,109.641731 505.636993,110.503304 506.365295,112.893867 C503.301514,116.347809 499.045258,118.359398 495.331085,121.062218 C492.641174,123.019661 489.849548,124.839699 487.073334,126.675751 C478.668884,132.234055 478.631317,132.262848 470.826813,125.605011 C467.790436,123.014748 464.933868,120.213661 461.753265,117.246750z'/%3E%3C/svg%3E") no-repeat center;
      mask: url("data:image/svg+xml,%3Csvg version='1.1' id='Layer_1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x='0px' y='0px' width='100%25' viewBox='355 55 315 320' enable-background='new 0 0 1024 544' xml:space='preserve'%3E%3Cpath fill='%23000000' d='M457.281006,317.309845 C472.602051,301.003693 490.885468,289.019226 508.817078,276.587738 C522.248413,267.276184 535.583191,257.841614 546.114136,245.101135 C555.523682,233.717361 561.449036,221.253204 557.488220,206.012863 C554.868408,195.932404 549.445618,187.434296 542.143372,180.083893 C536.727722,174.632553 530.759460,169.840576 524.647339,165.203201 C522.850647,163.839996 520.563965,162.905380 519.463501,160.139206 C527.944031,154.059570 536.445435,147.970306 544.939636,141.871078 C546.612915,140.669571 548.022583,141.233368 549.451965,142.374985 C569.399292,158.306992 585.755920,176.598831 590.775085,202.830429 C593.958008,219.464844 590.961121,234.909271 583.214355,249.663513 C573.248413,268.644409 557.512695,282.199005 540.555847,294.507599 C527.347595,304.095215 513.850159,313.283905 500.615753,322.836243 C492.211060,328.902649 484.699646,335.974731 478.276947,344.168793 C472.154938,351.979156 468.483490,360.799438 467.556549,370.642853 C467.241150,373.992096 466.097351,375.307220 462.677612,375.228088 C455.183441,375.054626 447.681915,375.140533 440.184235,375.210236 C437.373962,375.236389 435.020508,374.154266 432.711853,372.750122 C391.943420,347.955414 365.806152,312.879364 360.127930,264.919067 C356.303101,232.613235 364.293396,203.309128 389.654938,180.758850 C402.542664,169.299667 418.045532,163.744095 434.962219,161.670212 C455.593506,159.140945 474.478516,165.511887 493.015411,173.264969 C503.412476,177.613541 513.783875,180.424194 524.938965,176.541199 C526.284058,176.072983 527.630310,176.136108 528.764832,176.970398 C537.593201,183.462555 544.790344,191.296677 549.555542,202.023285 C539.020935,207.079025 528.514160,210.467163 517.319275,211.297195 C500.977020,212.508865 486.252136,206.489929 471.625671,200.389816 C459.876740,195.489807 447.802673,192.754700 435.101685,194.914551 C413.946136,198.512161 400.746643,211.514648 395.393402,231.699371 C387.202942,262.582062 396.478394,289.869019 415.211792,314.464478 C424.020782,326.029938 434.836456,335.146027 442.300446,338.546204 C446.704163,331.284180 451.198669,323.929352 457.281006,317.309845z'/%3E%3Cpath fill='%23000000' d='M604.101440,198.869415 C597.818176,197.400314 595.088989,193.728622 593.180054,187.806503 C590.234375,178.668427 585.135193,170.342926 578.535522,161.817368 C584.585449,160.137619 589.814819,161.324631 594.788635,162.209213 C633.516296,169.096878 658.837769,194.585068 665.211914,233.747559 C670.945801,268.976776 661.161438,300.616364 641.148621,329.481445 C628.701111,347.434998 612.384277,361.218872 593.867981,372.579254 C590.902039,374.398956 587.902466,375.273468 584.444397,375.211578 C577.450562,375.086334 570.453064,375.155457 563.457092,375.163849 C560.928894,375.166870 558.887146,374.847107 558.676208,371.540283 C557.616577,354.930847 548.650208,342.612274 536.739746,332.046143 C531.300110,327.220459 525.522888,322.775177 519.635010,317.940796 C522.579834,314.380676 526.480713,312.750366 529.697021,310.273956 C534.182129,306.820587 538.923645,303.695953 543.352417,300.175201 C546.072449,298.012848 548.164978,298.150970 550.792236,300.347992 C563.000549,310.557159 574.341614,321.496216 581.999573,335.708862 C582.542786,336.716980 582.964600,337.859406 584.370605,338.342407 C587.088135,338.008881 588.871765,335.814362 590.884949,334.214325 C618.126892,312.563141 633.523254,284.703094 633.516418,249.522003 C633.513245,232.845810 628.023682,217.811279 615.259705,206.152924 C612.017761,203.191803 608.196045,201.177383 604.101440,198.869415z'/%3E%3Cpath fill='%23000000' d='M507.403839,120.364090 C520.469727,111.378616 533.090027,102.387741 543.639587,90.910744 C551.769653,82.065918 558.232361,72.284454 559.022888,59.770985 C559.222961,56.603893 560.903198,55.600433 563.947998,55.652832 C571.773010,55.787491 579.604736,55.815937 587.428101,55.635883 C591.117859,55.550961 592.485535,56.933697 592.305359,60.605732 C591.529297,76.416580 585.762817,90.337318 576.697693,103.098885 C565.101440,119.423782 549.269897,131.060684 533.283569,142.534348 C522.469360,150.295868 511.105286,157.291855 500.838684,165.814636 C498.912231,167.413864 496.938538,168.243332 494.440186,167.106232 C484.719391,162.681885 474.603943,159.395248 464.274750,156.728485 C463.845123,156.617569 463.511536,156.134628 462.392670,155.218979 C475.659119,141.337006 491.666962,131.307312 507.403839,120.364090z'/%3E%3Cpath fill='%23000000' d='M490.830933,256.162598 C493.721344,258.697784 496.361237,260.984100 498.987823,263.285645 C501.442474,265.436493 504.597504,266.817230 506.653046,270.306122 C500.343994,274.655243 494.131683,279.004913 487.850159,283.252136 C478.446167,289.610474 478.514099,289.479126 469.992126,281.977295 C455.415497,269.145538 443.253540,254.664551 437.213348,235.784302 C434.118347,226.110001 433.689148,216.258362 434.844391,206.255661 C435.266479,202.600983 436.871002,200.710632 440.919739,200.626709 C449.193695,200.455200 457.115723,201.878952 464.882843,204.592224 C467.223938,205.410019 468.627777,206.548294 468.072845,209.293442 C465.230774,223.352554 471.201447,234.629227 479.721191,244.920395 C482.993500,248.873108 486.936981,252.270172 490.830933,256.162598z'/%3E%3Cpath fill='%23000000' d='M461.753265,117.246750 C446.309906,101.832626 436.321564,84.080307 434.044037,62.400234 C433.404419,56.312012 433.725586,55.718037 439.759552,55.698330 C447.251556,55.673870 454.744781,55.766140 462.235321,55.658920 C465.195801,55.616547 467.030029,56.444286 467.187408,59.727695 C467.789673,72.291931 474.401489,81.981178 482.432465,90.887375 C488.354858,97.455170 495.069122,103.184196 502.154907,108.479889 C503.709473,109.641731 505.636993,110.503304 506.365295,112.893867 C503.301514,116.347809 499.045258,118.359398 495.331085,121.062218 C492.641174,123.019661 489.849548,124.839699 487.073334,126.675751 C478.668884,132.234055 478.631317,132.262848 470.826813,125.605011 C467.790436,123.014748 464.933868,120.213661 461.753265,117.246750z'/%3E%3C/svg%3E") no-repeat center;
      mask-size: contain;
    }

    @keyframes pulse {
      0%, 100% { transform: scale(1); box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2); }
      50% { transform: scale(1.02); box-shadow: 0 25px 80px rgba(237, 122, 155, 0.2); }
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
  store = inject(AppStore);
  private router = inject(Router);
  isLightTheme = computed(() => this.store.theme() === 'light');

  constructor() {
    // Auto-redirect in browser mode or if already authenticated
    if (isBrowserModeEnv()) {
      // Use Angular Router to properly respect base href
      this.router.navigate(['/app/home']);
      return;
    }
  }

  toggleTheme() {
    const nextTheme = this.store.theme() === 'light' ? 'dark' : 'light';
    this.store.setTheme(nextTheme);
  }
}
