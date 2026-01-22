import { Component, inject, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { AppStore } from '@core/store/app.store';
import { ModeService } from '@core/services/mode.service';
import { ExecutionService } from '@features/run-protocol/services/execution.service';
import { ExecutionStatus } from '@features/run-protocol/models/execution.models';
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
    MatButtonModule
  ],
  template: `
    <div class="shell-layout">
      <!-- Thin Sidebar Rail -->
      <nav class="sidebar-rail">
        <!-- Logo / Home -->
        <a class="nav-item logo-item" [routerLink]="modeService.isBrowserMode() ? '/app/home' : (store.auth().isAuthenticated ? '/app/home' : '/')" matTooltip="Home" matTooltipPosition="right">
          <div class="logo-container">
            <div class="logo-image"></div>
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
        <a class="nav-item" data-tour-id="nav-workcell" routerLink="/app/workcell" routerLinkActive="active" matTooltip="Workcell View" matTooltipPosition="right">
          <mat-icon>view_in_ar</mat-icon>
          <span class="nav-label">Workcell</span>
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
        <a class="nav-item" data-tour-id="nav-playground" routerLink="/app/playground" routerLinkActive="active" matTooltip="Playground" matTooltipPosition="right">
          <mat-icon>terminal</mat-icon>
          <span class="nav-label">Playground</span>
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

        @if (store.auth().isAuthenticated && !modeService.isBrowserMode()) {
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
        <main class="main-content">
          <router-outlet></router-outlet>
        </main>

        <footer class="app-footer">
            <a href="https://github.com/maraxen/praxis" target="_blank" class="footer-link" matTooltip="GitHub Repository">
                <mat-icon>code</mat-icon>
            </a>
            <a href="https://github.com/maraxen/praxis" target="_blank" class="footer-link" matTooltip="Star on GitHub">
                <mat-icon>star_border</mat-icon>
            </a>
            <a href="https://github.com/maraxen/praxis/issues/new" target="_blank" class="footer-link" matTooltip="Raise an Issue">
                <mat-icon>bug_report</mat-icon>
            </a>
            <div class="footer-divider"></div>
            <a href="https://labautomation.io" target="_blank" class="footer-link" matTooltip="LabAutomation.io">
                <mat-icon>forum</mat-icon>
            </a>
            <a href="https://pylabrobot.org" target="_blank" class="footer-link" matTooltip="PyLabRobot.org">
                <mat-icon>biotech</mat-icon>
            </a>
        </footer>
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
      width: 5rem;
      min-width: 5rem;
      background: var(--mat-sys-surface-container);
      border-right: 1px solid var(--mat-sys-outline-variant);
      z-index: 100;
      padding: 0.75rem 0;
      gap: 0.25rem;
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

    /* Gradient Hover & Active State for Icons */
    .nav-item:hover mat-icon,
    .nav-item.active mat-icon {
      background: linear-gradient(135deg, var(--primary-color) 0%, var(--tertiary-color) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .nav-item mat-icon {
      font-size: 24px;
      width: 24px;
      height: 24px;
    }

    .nav-label {
      display: none; /* Hidden in rail mode - rely on tooltips */
    }

    /* Logo */
    .logo-item {
      margin-bottom: 8px;
      opacity: 1 !important;
      height: 48px; /* Restore simpler height for logo */
    }

    .logo-container {
      width: 80px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: none;
      border: none;
      outline: none;
      transition: all 0.3s ease;
    }

    .logo-item:hover .logo-container {
      transform: scale(1.05);
    }

    .logo-item:hover {
        background: none !important;
    }

    .logo-image {
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, var(--primary-color) 0%, var(--tertiary-color) 100%);
      -webkit-mask: url("data:image/svg+xml,%3Csvg version='1.1' id='Layer_1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x='0px' y='0px' width='100%25' viewBox='355 55 315 320' enable-background='new 0 0 1024 544' xml:space='preserve'%3E%3Cpath fill='%23000000' d='M457.281006,317.309845 C472.602051,301.003693 490.885468,289.019226 508.817078,276.587738 C522.248413,267.276184 535.583191,257.841614 546.114136,245.101135 C555.523682,233.717361 561.449036,221.253204 557.488220,206.012863 C554.868408,195.932404 549.445618,187.434296 542.143372,180.083893 C536.727722,174.632553 530.759460,169.840576 524.647339,165.203201 C522.850647,163.839996 520.563965,162.905380 519.463501,160.139206 C527.944031,154.059570 536.445435,147.970306 544.939636,141.871078 C546.612915,140.669571 548.022583,141.233368 549.451965,142.374985 C569.399292,158.306992 585.755920,176.598831 590.775085,202.830429 C593.958008,219.464844 590.961121,234.909271 583.214355,249.663513 C573.248413,268.644409 557.512695,282.199005 540.555847,294.507599 C527.347595,304.095215 513.850159,313.283905 500.615753,322.836243 C492.211060,328.902649 484.699646,335.974731 478.276947,344.168793 C472.154938,351.979156 468.483490,360.799438 467.556549,370.642853 C467.241150,373.992096 466.097351,375.307220 462.677612,375.228088 C455.183441,375.054626 447.681915,375.140533 440.184235,375.210236 C437.373962,375.236389 435.020508,374.154266 432.711853,372.750122 C391.943420,347.955414 365.806152,312.879364 360.127930,264.919067 C356.303101,232.613235 364.293396,203.309128 389.654938,180.758850 C402.542664,169.299667 418.045532,163.744095 434.962219,161.670212 C455.593506,159.140945 474.478516,165.511887 493.015411,173.264969 C503.412476,177.613541 513.783875,180.424194 524.938965,176.541199 C526.284058,176.072983 527.630310,176.136108 528.764832,176.970398 C537.593201,183.462555 544.790344,191.296677 549.555542,202.023285 C539.020935,207.079025 528.514160,210.467163 517.319275,211.297195 C500.977020,212.508865 486.252136,206.489929 471.625671,200.389816 C459.876740,195.489807 447.802673,192.754700 435.101685,194.914551 C413.946136,198.512161 400.746643,211.514648 395.393402,231.699371 C387.202942,262.582062 396.478394,289.869019 415.211792,314.464478 C424.020782,326.029938 434.836456,335.146027 442.300446,338.546204 C446.704163,331.284180 451.198669,323.929352 457.281006,317.309845z'/%3E%3Cpath fill='%23000000' d='M604.101440,198.869415 C597.818176,197.400314 595.088989,193.728622 593.180054,187.806503 C590.234375,178.668427 585.135193,170.342926 578.535522,161.817368 C584.585449,160.137619 589.814819,161.324631 594.788635,162.209213 C633.516296,169.096878 658.837769,194.585068 665.211914,233.747559 C670.945801,268.976776 661.161438,300.616364 641.148621,329.481445 C628.701111,347.434998 612.384277,361.218872 593.867981,372.579254 C590.902039,374.398956 587.902466,375.273468 584.444397,375.211578 C577.450562,375.086334 570.453064,375.155457 563.457092,375.163849 C560.928894,375.166870 558.887146,374.847107 558.676208,371.540283 C557.616577,354.930847 548.650208,342.612274 536.739746,332.046143 C531.300110,327.220459 525.522888,322.775177 519.635010,317.940796 C522.579834,314.380676 526.480713,312.750366 529.697021,310.273956 C534.182129,306.820587 538.923645,303.695953 543.352417,300.175201 C546.072449,298.012848 548.164978,298.150970 550.792236,300.347992 C563.000549,310.557159 574.341614,321.496216 581.999573,335.708862 C582.542786,336.716980 582.964600,337.859406 584.370605,338.342407 C587.088135,338.008881 588.871765,335.814362 590.884949,334.214325 C618.126892,312.563141 633.523254,284.703094 633.516418,249.522003 C633.513245,232.845810 628.023682,217.811279 615.259705,206.152924 C612.017761,203.191803 608.196045,201.177383 604.101440,198.869415z'/%3E%3Cpath fill='%23000000' d='M507.403839,120.364090 C520.469727,111.378616 533.090027,102.387741 543.639587,90.910744 C551.769653,82.065918 558.232361,72.284454 559.022888,59.770985 C559.222961,56.603893 560.903198,55.600433 563.947998,55.652832 C571.773010,55.787491 579.604736,55.815937 587.428101,55.635883 C591.117859,55.550961 592.485535,56.933697 592.305359,60.605732 C591.529297,76.416580 585.762817,90.337318 576.697693,103.098885 C565.101440,119.423782 549.269897,131.060684 533.283569,142.534348 C522.469360,150.295868 511.105286,157.291855 500.838684,165.814636 C498.912231,167.413864 496.938538,168.243332 494.440186,167.106232 C484.719391,162.681885 474.603943,159.395248 464.274750,156.728485 C463.845123,156.617569 463.511536,156.134628 462.392670,155.218979 C475.659119,141.337006 491.666962,131.307312 507.403839,120.364090z'/%3E%3Cpath fill='%23000000' d='M490.830933,256.162598 C493.721344,258.697784 496.361237,260.984100 498.987823,263.285645 C501.442474,265.436493 504.597504,266.817230 506.653046,270.306122 C500.343994,274.655243 494.131683,279.004913 487.850159,283.252136 C478.446167,289.610474 478.514099,289.479126 469.992126,281.977295 C455.415497,269.145538 443.253540,254.664551 437.213348,235.784302 C434.118347,226.110001 433.689148,216.258362 434.844391,206.255661 C435.266479,202.600983 436.871002,200.710632 440.919739,200.626709 C449.193695,200.455200 457.115723,201.878952 464.882843,204.592224 C467.223938,205.410019 468.627777,206.548294 468.072845,209.293442 C465.230774,223.352554 471.201447,234.629227 479.721191,244.920395 C482.993500,248.873108 486.936981,252.270172 490.830933,256.162598z'/%3E%3Cpath fill='%23000000' d='M461.753265,117.246750 C446.309906,101.832626 436.321564,84.080307 434.044037,62.400234 C433.404419,56.312012 433.725586,55.718037 439.759552,55.698330 C447.251556,55.673870 454.744781,55.766140 462.235321,55.658920 C465.195801,55.616547 467.030029,56.444286 467.187408,59.727695 C467.789673,72.291931 474.401489,81.981178 482.432465,90.887375 C488.354858,97.455170 495.069122,103.184196 502.154907,108.479889 C503.709473,109.641731 505.636993,110.503304 506.365295,112.893867 C503.301514,116.347809 499.045258,118.359398 495.331085,121.062218 C492.641174,123.019661 489.849548,124.839699 487.073334,126.675751 C478.668884,132.234055 478.631317,132.262848 470.826813,125.605011 C467.790436,123.014748 464.933868,120.213661 461.753265,117.246750z'/%3E%3C/svg%3E") no-repeat center;
      mask: url("data:image/svg+xml,%3Csvg version='1.1' id='Layer_1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x='0px' y='0px' width='100%25' viewBox='355 55 315 320' enable-background='new 0 0 1024 544' xml:space='preserve'%3E%3Cpath fill='%23000000' d='M457.281006,317.309845 C472.602051,301.003693 490.885468,289.019226 508.817078,276.587738 C522.248413,267.276184 535.583191,257.841614 546.114136,245.101135 C555.523682,233.717361 561.449036,221.253204 557.488220,206.012863 C554.868408,195.932404 549.445618,187.434296 542.143372,180.083893 C536.727722,174.632553 530.759460,169.840576 524.647339,165.203201 C522.850647,163.839996 520.563965,162.905380 519.463501,160.139206 C527.944031,154.059570 536.445435,147.970306 544.939636,141.871078 C546.612915,140.669571 548.022583,141.233368 549.451965,142.374985 C569.399292,158.306992 585.755920,176.598831 590.775085,202.830429 C593.958008,219.464844 590.961121,234.909271 583.214355,249.663513 C573.248413,268.644409 557.512695,282.199005 540.555847,294.507599 C527.347595,304.095215 513.850159,313.283905 500.615753,322.836243 C492.211060,328.902649 484.699646,335.974731 478.276947,344.168793 C472.154938,351.979156 468.483490,360.799438 467.556549,370.642853 C467.241150,373.992096 466.097351,375.307220 462.677612,375.228088 C455.183441,375.054626 447.681915,375.140533 440.184235,375.210236 C437.373962,375.236389 435.020508,374.154266 432.711853,372.750122 C391.943420,347.955414 365.806152,312.879364 360.127930,264.919067 C356.303101,232.613235 364.293396,203.309128 389.654938,180.758850 C402.542664,169.299667 418.045532,163.744095 434.962219,161.670212 C455.593506,159.140945 474.478516,165.511887 493.015411,173.264969 C503.412476,177.613541 513.783875,180.424194 524.938965,176.541199 C526.284058,176.072983 527.630310,176.136108 528.764832,176.970398 C537.593201,183.462555 544.790344,191.296677 549.555542,202.023285 C539.020935,207.079025 528.514160,210.467163 517.319275,211.297195 C500.977020,212.508865 486.252136,206.489929 471.625671,200.389816 C459.876740,195.489807 447.802673,192.754700 435.101685,194.914551 C413.946136,198.512161 400.746643,211.514648 395.393402,231.699371 C387.202942,262.582062 396.478394,289.869019 415.211792,314.464478 C424.020782,326.029938 434.836456,335.146027 442.300446,338.546204 C446.704163,331.284180 451.198669,323.929352 457.281006,317.309845z'/%3E%3Cpath fill='%23000000' d='M604.101440,198.869415 C597.818176,197.400314 595.088989,193.728622 593.180054,187.806503 C590.234375,178.668427 585.135193,170.342926 578.535522,161.817368 C584.585449,160.137619 589.814819,161.324631 594.788635,162.209213 C633.516296,169.096878 658.837769,194.585068 665.211914,233.747559 C670.945801,268.976776 661.161438,300.616364 641.148621,329.481445 C628.701111,347.434998 612.384277,361.218872 593.867981,372.579254 C590.902039,374.398956 587.902466,375.273468 584.444397,375.211578 C577.450562,375.086334 570.453064,375.155457 563.457092,375.163849 C560.928894,375.166870 558.887146,374.847107 558.676208,371.540283 C557.616577,354.930847 548.650208,342.612274 536.739746,332.046143 C531.300110,327.220459 525.522888,322.775177 519.635010,317.940796 C522.579834,314.380676 526.480713,312.750366 529.697021,310.273956 C534.182129,306.820587 538.923645,303.695953 543.352417,300.175201 C546.072449,298.012848 548.164978,298.150970 550.792236,300.347992 C563.000549,310.557159 574.341614,321.496216 581.999573,335.708862 C582.542786,336.716980 582.964600,337.859406 584.370605,338.342407 C587.088135,338.008881 588.871765,335.814362 590.884949,334.214325 C618.126892,312.563141 633.523254,284.703094 633.516418,249.522003 C633.513245,232.845810 628.023682,217.811279 615.259705,206.152924 C612.017761,203.191803 608.196045,201.177383 604.101440,198.869415z'/%3E%3Cpath fill='%23000000' d='M507.403839,120.364090 C520.469727,111.378616 533.090027,102.387741 543.639587,90.910744 C551.769653,82.065918 558.232361,72.284454 559.022888,59.770985 C559.222961,56.603893 560.903198,55.600433 563.947998,55.652832 C571.773010,55.787491 579.604736,55.815937 587.428101,55.635883 C591.117859,55.550961 592.485535,56.933697 592.305359,60.605732 C591.529297,76.416580 585.762817,90.337318 576.697693,103.098885 C565.101440,119.423782 549.269897,131.060684 533.283569,142.534348 C522.469360,150.295868 511.105286,157.291855 500.838684,165.814636 C498.912231,167.413864 496.938538,168.243332 494.440186,167.106232 C484.719391,162.681885 474.603943,159.395248 464.274750,156.728485 C463.845123,156.617569 463.511536,156.134628 462.392670,155.218979 C475.659119,141.337006 491.666962,131.307312 507.403839,120.364090z'/%3E%3Cpath fill='%23000000' d='M490.830933,256.162598 C493.721344,258.697784 496.361237,260.984100 498.987823,263.285645 C501.442474,265.436493 504.597504,266.817230 506.653046,270.306122 C500.343994,274.655243 494.131683,279.004913 487.850159,283.252136 C478.446167,289.610474 478.514099,289.479126 469.992126,281.977295 C455.415497,269.145538 443.253540,254.664551 437.213348,235.784302 C434.118347,226.110001 433.689148,216.258362 434.844391,206.255661 C435.266479,202.600983 436.871002,200.710632 440.919739,200.626709 C449.193695,200.455200 457.115723,201.878952 464.882843,204.592224 C467.223938,205.410019 468.627777,206.548294 468.072845,209.293442 C465.230774,223.352554 471.201447,234.629227 479.721191,244.920395 C482.993500,248.873108 486.936981,252.270172 490.830933,256.162598z'/%3E%3Cpath fill='%23000000' d='M461.753265,117.246750 C446.309906,101.832626 436.321564,84.080307 434.044037,62.400234 C433.404419,56.312012 433.725586,55.718037 439.759552,55.698330 C447.251556,55.673870 454.744781,55.766140 462.235321,55.658920 C465.195801,55.616547 467.030029,56.444286 467.187408,59.727695 C467.789673,72.291931 474.401489,81.981178 482.432465,90.887375 C488.354858,97.455170 495.069122,103.184196 502.154907,108.479889 C503.709473,109.641731 505.636993,110.503304 506.365295,112.893867 C503.301514,116.347809 499.045258,118.359398 495.331085,121.062218 C492.641174,123.019661 489.849548,124.839699 487.073334,126.675751 C478.668884,132.234055 478.631317,132.262848 470.826813,125.605011 C467.790436,123.014748 464.933868,120.213661 461.753265,117.246750z'/%3E%3C/svg%3E") no-repeat center;
      mask-size: contain;
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
      background: var(--mat-sys-success-container);
      border-color: var(--status-success);
      color: var(--status-success);
    }

    .mode-badge.attention {
      background: var(--mat-sys-warning-container);
      border-color: var(--status-warning);
      color: var(--status-warning);
    }

    .mode-badge.problem {
      background: var(--mat-sys-error-container);
      border-color: var(--status-error);
      color: var(--status-error);
    }

    .theme-toggle {
      height: 48px;
    }

    .mode-badge mat-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

  /* Main Content */
    .main-wrapper {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      min-width: 0;
      position: relative; /* For stacking context if needed */
    }

    .main-content {
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      /* Add padding if needed, or rely on child components */
    }

    /* Footer */
    .app-footer {
        height: 2rem;
        min-height: 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        background: var(--mat-sys-surface-container);
        border-top: 1px solid var(--mat-sys-outline-variant);
        padding: 0 1rem;
        z-index: 10;
        font-size: 0.75rem;
    }

    .footer-link {
        color: var(--mat-sys-on-surface-variant);
        opacity: 0.5;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        width: 1.5rem;
        height: 1.5rem;
        border-radius: 50%;
    }

    .footer-link:hover {
        opacity: 1;
        background: var(--mat-sys-surface-variant);
        color: var(--mat-sys-primary);
    }

    .footer-link mat-icon {
        font-size: 1rem;
        width: 1rem;
        height: 1rem;
    }

    .footer-divider {
        width: 1px;
        height: 1rem;
        background: var(--mat-sys-outline-variant);
        opacity: 0.5;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .sidebar-rail {
        width: 4rem;
        min-width: 4rem;
      }
      
      .nav-item {
        width: 3.25rem;
        height: 3.25rem;
      }

      .nav-label {
        font-size: 0.55rem;
      }

      .nav-divider {
        width: 2rem;
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
