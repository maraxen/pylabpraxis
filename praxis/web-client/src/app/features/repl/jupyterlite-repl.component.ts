import {
  Component,
  ElementRef,
  OnInit,
  OnDestroy,
  ViewChild,
  inject,
  effect,
  ChangeDetectorRef,
  SecurityContext,
} from '@angular/core';
import { AppStore } from '../../core/store/app.store';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ModeService } from '../../core/services/mode.service';
import { AssetService } from '../assets/services/asset.service';
import { Machine, Resource } from '../assets/models/asset.models';
import { Subscription } from 'rxjs';
import { HardwareDiscoveryButtonComponent } from '@shared/components/hardware-discovery-button/hardware-discovery-button.component';

/**
 * JupyterLite REPL Component
 *
 * Replaces the xterm.js-based REPL with an embedded JupyterLite notebook.
 * Uses iframe embedding with URL parameters for configuration.
 */
@Component({
  selector: 'app-jupyterlite-repl',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatSidenavModule,
    MatListModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    HardwareDiscoveryButtonComponent,
  ],
  template: `
    <div class="repl-container">
      <mat-drawer-container class="repl-drawer-container">
        <!-- Inventory Sidebar -->
        <mat-drawer
          #drawer
          mode="side"
          [(opened)]="isSidebarOpen"
          position="end"
          class="inventory-drawer"
        >
          <div class="drawer-header">
            <h3>Inventory</h3>
            <button
              mat-icon-button
              (click)="loadInventory()"
              matTooltip="Refresh Inventory"
            >
              <mat-icon>refresh</mat-icon>
            </button>
          </div>

          <div class="inventory-section">
            <h4>Machines</h4>
            <mat-list dense>
              @for (m of inventoryMachines; track m.accession_id) {
              <mat-list-item>
                <div class="inventory-item">
                  <span class="item-name">{{ m.name }}</span>
                  <button
                    mat-icon-button
                    (click)="insertAsset('machine', m)"
                    matTooltip="Insert variable name"
                    class="insert-btn"
                  >
                    <mat-icon>add_circle</mat-icon>
                  </button>
                </div>
              </mat-list-item>
              } @if (inventoryMachines.length === 0) {
              <div class="empty-state">No machines</div>
              }
            </mat-list>
          </div>

          <div class="inventory-section">
            <h4>Resources</h4>
            <mat-list dense>
              @for (r of inventoryResources.slice(0, 30); track r.accession_id) {
              <mat-list-item>
                <div class="inventory-item">
                  <span class="item-name">{{ r.name }}</span>
                  <button
                    mat-icon-button
                    (click)="insertAsset('resource', r)"
                    matTooltip="Insert variable name"
                    class="insert-btn"
                  >
                    <mat-icon>add_circle</mat-icon>
                  </button>
                </div>
              </mat-list-item>
              } @if (inventoryResources.length === 0) {
              <div class="empty-state">No resources</div>
              } @if (inventoryResources.length > 30) {
              <div class="empty-state">
                Showing first 30 of {{ inventoryResources.length }}
              </div>
              }
            </mat-list>
          </div>
        </mat-drawer>

        <!-- Main Content -->
        <mat-drawer-content class="repl-main-content">
          <mat-card class="repl-card">
            <!-- Menu Bar -->
            <div class="repl-header">
              <div class="header-title">
                <mat-icon>auto_stories</mat-icon>
                <h2>PyLabRobot Notebook ({{ modeLabel() }})</h2>
              </div>

              <div class="header-actions flex items-center gap-2">
                <app-hardware-discovery-button></app-hardware-discovery-button>
                <button
                  mat-icon-button
                  (click)="reloadNotebook()"
                  matTooltip="Restart Kernel (reload notebook)"
                >
                  <mat-icon>restart_alt</mat-icon>
                </button>
                <button
                  mat-icon-button
                  (click)="isSidebarOpen = !isSidebarOpen"
                  matTooltip="Toggle Inventory"
                >
                  <mat-icon>inventory_2</mat-icon>
                </button>
              </div>
            </div>

            <!-- JupyterLite iframe -->
            <div class="repl-notebook-wrapper">
              @if (isLoading) {
              <div class="loading-overlay">
                <mat-spinner diameter="48"></mat-spinner>
                <p>Loading JupyterLite...</p>
                <p class="loading-hint">This may take a moment on first load</p>
              </div>
              }
              <iframe
                #notebookFrame
                [src]="jupyterliteUrl"
                class="notebook-frame"
                (load)="onIframeLoad()"
                allow="cross-origin-isolated"
                sandbox="allow-scripts allow-same-origin allow-popups allow-forms allow-modals"
              ></iframe>
            </div>
          </mat-card>
        </mat-drawer-content>
      </mat-drawer-container>
    </div>
  `,
  styles: [
    `
      .repl-container {
        height: 100%;
        width: 100%;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
      }

      .repl-drawer-container {
        height: 100%;
        background: transparent;
      }

      .repl-main-content {
        padding: 16px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }

      .inventory-drawer {
        width: 280px;
        padding: 0;
        background: var(--mat-sys-surface-container);
        border-left: 1px solid var(--mat-sys-outline-variant);
      }

      .drawer-header {
        padding: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid var(--mat-sys-outline-variant);
      }

      .drawer-header h3 {
        margin: 0;
        font-size: 1rem;
        font-weight: 500;
      }

      .inventory-section {
        padding: 8px 16px;
      }

      .inventory-section h4 {
        margin: 8px 0 4px 0;
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--mat-sys-on-surface-variant);
        text-transform: uppercase;
      }

      .inventory-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
      }

      .item-name {
        font-family: monospace;
        font-size: 0.85rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        flex: 1;
      }

      .insert-btn {
        color: var(--mat-sys-primary);
      }

      .empty-state {
        padding: 16px;
        color: var(--mat-sys-on-surface-variant);
        text-align: center;
        font-style: italic;
      }

      .repl-card {
        height: 100%;
        display: flex;
        flex-direction: column;
        padding: 0;
        background: var(--mat-sys-surface-container);
        border: 1px solid var(--mat-sys-outline-variant);
        color: var(--mat-sys-on-surface);
        border-radius: 8px;
        overflow: hidden;
      }

      .repl-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 16px;
        background: var(--mat-sys-surface-container-high);
        border-bottom: 1px solid var(--mat-sys-outline-variant);
        flex-shrink: 0;
      }

      .header-title {
        display: flex;
        align-items: center;
        gap: 12px;
      }

      .repl-header mat-icon {
        color: var(--mat-sys-primary);
      }

      .repl-header h2 {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 500;
      }

      .header-actions {
        display: flex;
        gap: 8px;
      }

      .repl-notebook-wrapper {
        flex-grow: 1;
        overflow: hidden;
        position: relative;
        background: var(--mat-sys-surface-container-low);
      }

      .notebook-frame {
        width: 100%;
        height: 100%;
        border: none;
      }

      .loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: var(--mat-sys-surface-container);
        z-index: 10;
      }

      .loading-overlay p {
        margin-top: 16px;
        font-size: 1rem;
        color: var(--mat-sys-on-surface);
      }

      .loading-hint {
        font-size: 0.85rem !important;
        color: var(--mat-sys-on-surface-variant) !important;
      }
    `,
  ],
})
export class JupyterliteReplComponent implements OnInit, OnDestroy {
  @ViewChild('notebookFrame') notebookFrame!: ElementRef<HTMLIFrameElement>;

  private modeService = inject(ModeService);
  private store = inject(AppStore);
  private snackBar = inject(MatSnackBar);
  private cdr = inject(ChangeDetectorRef);
  private assetService = inject(AssetService);
  private sanitizer = inject(DomSanitizer);

  private subscription = new Subscription();

  // Inventory
  inventoryMachines: Machine[] = [];
  inventoryResources: Resource[] = [];
  isSidebarOpen = true;

  // Loading state
  isLoading = true;

  // JupyterLite URL
  jupyterliteUrl: SafeResourceUrl = '';
  private currentTheme = 'light';

  modeLabel = this.modeService.modeLabel;

  constructor() {
    // Sync theme changes
    effect(() => {
      const theme = this.store.theme();
      this.updateJupyterliteTheme(theme);
    });
  }

  ngOnInit() {
    this.buildJupyterliteUrl();
    this.loadInventory();
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  /**
   * Build the JupyterLite URL with configuration parameters
   */
  private buildJupyterliteUrl() {
    const theme = this.store.theme();
    const isDark =
      theme === 'dark' ||
      (theme === 'system' &&
        window.matchMedia('(prefers-color-scheme: dark)').matches);

    this.currentTheme = isDark ? 'dark' : 'light';

    // Build bootstrap code for asset preloading
    const bootstrapCode = this.generateBootstrapCode();

    // JupyterLite REPL URL with parameters
    const baseUrl = './assets/jupyterlite/repl/index.html';
    const params = new URLSearchParams({
      kernel: 'python',
      toolbar: '1',
      theme: isDark ? 'JupyterLab Dark' : 'JupyterLab Light',
    });

    // Add bootstrap code if we have assets
    if (bootstrapCode) {
      params.set('code', bootstrapCode);
    }

    const fullUrl = `${baseUrl}?${params.toString()}`;
    this.jupyterliteUrl = this.sanitizer.bypassSecurityTrustResourceUrl(fullUrl);
  }

  /**
   * Update theme when app theme changes
   */
  private updateJupyterliteTheme(theme: string) {
    const isDark =
      theme === 'dark' ||
      (theme === 'system' &&
        window.matchMedia('(prefers-color-scheme: dark)').matches);

    const newTheme = isDark ? 'dark' : 'light';

    // Only reload if theme actually changed
    if (this.currentTheme !== newTheme) {
      this.currentTheme = newTheme;
      this.buildJupyterliteUrl();
    }
  }

  /**
   * Generate Python bootstrap code for asset preloading
   */
  private generateBootstrapCode(): string {
    // Generate code to install local pylabrobot wheel and load browser I/O shims
    const lines = [
      '# PyLabRobot Interactive Notebook',
      '# Installing pylabrobot from local wheel...',
      'import micropip',
      "await micropip.install('/assets/wheels/pylabrobot-0.1.6-py3-none-any.whl')",
      '',
      '# Load WebSerial/WebUSB shims for browser I/O',
      'import pyodide.http',
      "shim_code = await (await pyodide.http.pyfetch('/assets/shims/web_serial_shim.py')).string()",
      'exec(shim_code)',
      "usb_code = await (await pyodide.http.pyfetch('/assets/shims/web_usb_shim.py')).string()",
      'exec(usb_code)',
      '',
      '# Patch pylabrobot.io to use browser shims',
      'import pylabrobot.io.serial as _ser',
      'import pylabrobot.io.usb as _usb',
      '_ser.Serial = WebSerial',
      '_usb.USB = WebUSB',
      '',
      '# Import pylabrobot',
      'import pylabrobot',
      'from pylabrobot.resources import *',
      'print("✓ pylabrobot loaded with browser I/O shims!")',
      'print(f"  Version: {pylabrobot.__version__}")',
      'print("Use the Inventory sidebar to insert asset variables.")',
    ];

    return lines.join('\n');
  }

  /**
   * Generate a Python-safe variable name from an asset
   */
  private assetToVarName(asset: { name: string; accession_id: string }): string {
    // Convert name to snake_case and add UUID prefix
    const desc = asset.name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_|_$/g, '');
    const prefix = asset.accession_id.slice(0, 6);
    return `${desc}_${prefix}`;
  }

  /**
   * Handle iframe load event
   */
  onIframeLoad() {
    // Wait a bit for JupyterLite to fully initialize
    setTimeout(() => {
      this.isLoading = false;
      this.cdr.detectChanges();
    }, 2000);
  }

  /**
   * Reload the notebook (restart kernel)
   */
  reloadNotebook() {
    this.isLoading = true;
    this.buildJupyterliteUrl();
    this.cdr.detectChanges();
  }

  /**
   * Load inventory from asset service
   */
  loadInventory() {
    this.subscription.add(
      this.assetService.getMachines().subscribe((machines) => {
        this.inventoryMachines = machines;
      })
    );
    this.subscription.add(
      this.assetService.getResources().subscribe((resources) => {
        this.inventoryResources = resources;
      })
    );
  }

  /**
   * Insert asset variable name into the notebook
   */
  insertAsset(type: 'machine' | 'resource', asset: Machine | Resource) {
    const varName = this.assetToVarName(asset);

    // Try to send code to JupyterLite via postMessage
    // Note: JupyterLite REPL supports receiving code via postMessage
    if (this.notebookFrame?.nativeElement?.contentWindow) {
      try {
        // JupyterLite uses a specific message format
        this.notebookFrame.nativeElement.contentWindow.postMessage(
          {
            type: 'from-host-editor',
            content: varName,
          },
          '*'
        );
        this.snackBar.open(`Inserted ${varName}`, 'OK', { duration: 2000 });
      } catch (e) {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(varName).then(() => {
          this.snackBar.open(`Copied "${varName}" to clipboard`, 'OK', {
            duration: 2000,
          });
        });
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(varName).then(() => {
        this.snackBar.open(`Copied "${varName}" to clipboard`, 'OK', {
          duration: 2000,
        });
      });
    }
  }
}
