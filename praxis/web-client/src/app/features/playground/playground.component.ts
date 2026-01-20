import {
  Component,
  ElementRef,
  OnInit,
  OnDestroy,
  ViewChild,
  inject,
  effect,
  ChangeDetectorRef,
  signal,
  computed,
  AfterViewInit,
} from '@angular/core';
import { InteractionService } from '../../core/services/interaction.service';
import { AppStore } from '../../core/store/app.store';

import { FormsModule } from '@angular/forms';
import { DeckCatalogService } from '../run-protocol/services/deck-catalog.service';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatListModule } from '@angular/material/list';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatMenuModule } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ModeService } from '../../core/services/mode.service';
import { AssetService } from '../assets/services/asset.service';
import { Machine, Resource, MachineStatus } from '../assets/models/asset.models';
import { Subscription } from 'rxjs';
import { HardwareDiscoveryButtonComponent } from '@shared/components/hardware-discovery-button/hardware-discovery-button.component';

import { serial as polyfillSerial } from 'web-serial-polyfill';
import { SerialManagerService } from '../../core/services/serial-manager.service';
import { MatDialog } from '@angular/material/dialog';
import { AssetWizard } from '@shared/components/asset-wizard/asset-wizard';

import { MatTabsModule } from '@angular/material/tabs';
import { DirectControlComponent } from './components/direct-control/direct-control.component';
import { MachineRead } from '../../core/api-generated/models/MachineRead';

/**
 * Playground Component
 *
 * Replaces the xterm.js-based REPL with an embedded JupyterLite notebook.
 * Uses iframe embedding with URL parameters for configuration.
 */
@Component({
  selector: 'app-playground',
  standalone: true,
  imports: [
    FormsModule,

    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatListModule,
    MatSnackBarModule,
    MatFormFieldModule,
    MatInputModule,
    MatMenuModule,
    MatDividerModule,
    MatSelectModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    HardwareDiscoveryButtonComponent,
    DirectControlComponent,
  ],
  template: `
    <div class="repl-container">
      <!-- Main Notebook Area -->
      <div class="notebook-area">
        <mat-card class="repl-card">
          <!-- Menu Bar -->
          <div class="repl-header">
            <div class="header-title">
              <mat-icon>auto_stories</mat-icon>
              <h2>Playground ({{ modeLabel() }})</h2>
            </div>
            
            <div class="header-actions flex items-center gap-2">
              <app-hardware-discovery-button></app-hardware-discovery-button>
              <button 
                mat-icon-button 
                (click)="reloadNotebook()"
                matTooltip="Restart Kernel (reload notebook)"
                aria-label="Restart Kernel (reload notebook)">
                <mat-icon>restart_alt</mat-icon>
              </button>
              <button 
                mat-icon-button 
                (click)="openInventory()"
                matTooltip="Open Inventory Dialog"
                aria-label="Open Inventory Dialog"
                color="primary">
                <mat-icon>inventory_2</mat-icon>
              </button>
            </div>
          </div>

          <mat-tab-group class="repl-tabs" [selectedIndex]="selectedTabIndex()" (selectedIndexChange)="selectedTabIndex.set($event)">
            <mat-tab label="REPL Notebook">
              <ng-template matTabContent>
                <!-- JupyterLite iframe -->
                <div class="repl-notebook-wrapper" data-tour-id="repl-notebook">

                  @if (jupyterliteUrl) {
                    <iframe
                      #notebookFrame
                      [src]="jupyterliteUrl"
                      class="notebook-frame"
                      (load)="onIframeLoad()"
                      allow="cross-origin-isolated; usb; serial"
                      sandbox="allow-scripts allow-same-origin allow-popups allow-forms allow-modals"
                    ></iframe>
                  }

                  @if (isLoading()) {
                    <div class="loading-overlay">
                      <div class="loading-content">
                        <mat-spinner diameter="48"></mat-spinner>
                        <p>Initializing Pyodide Environment...</p>
                        @if (loadingError()) {
                          <button mat-flat-button color="warn" (click)="reloadNotebook()">
                            <mat-icon>refresh</mat-icon>
                            Retry Loading
                          </button>
                        }
                      </div>
                    </div>
                  }
                </div>
              </ng-template>
            </mat-tab>
            
            <mat-tab label="Direct Control">
              <ng-template matTabContent>
                <div class="direct-control-wrapper">
                  @if (selectedMachine()) {
                    <app-direct-control 
                      [machine]="$any(selectedMachine())"
                      (executeCommand)="onExecuteCommand($event)">
                    </app-direct-control>
                  } @else {
                    <div class="empty-state">
                      <mat-icon>settings_remote</mat-icon>
                      <p>No machine selected. Use the Inventory to select or create a machine.</p>
                      <button mat-stroked-button (click)="openInventory()">
                        <mat-icon>inventory_2</mat-icon>
                        Open Inventory
                      </button>
                    </div>
                  }
                </div>
              </ng-template>
            </mat-tab>
          </mat-tab-group>
        </mat-card>
      </div>
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
        overflow: hidden;
        padding: 16px;
        gap: 0; 
      }

      .notebook-area {
        height: 100%;
        min-width: 0; /* Allow shrinking */
        display: flex;
        flex-direction: column;
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
        height: 56px;
        box-sizing: border-box;
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
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .repl-tabs {
        flex: 1;
        display: flex;
        flex-direction: column;
        min-height: 0;
      }

      :host ::ng-deep .repl-tabs {
        .mat-mdc-tab-body-wrapper {
          flex: 1;
        }
      }

      .repl-notebook-wrapper {
        height: 100%;
        position: relative;
        background: var(--mat-sys-surface-container-low);
      }

      .direct-control-wrapper {
        height: 100%;
        padding: 24px;
        overflow-y: auto;
        background: var(--mat-sys-surface-container-low);
      }

      .notebook-frame {
        width: 100%;
        height: 100%;
        border: none;
      }

      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        gap: 16px;
        color: var(--mat-sys-on-surface-variant);
        text-align: center;
      }

      .empty-state mat-icon {
        font-size: 48px;
        width: 48px;
        height: 48px;
      }

      .loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--mat-sys-surface-container-low);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 100;
        transition: opacity 0.5s ease-out;
      }

      .loading-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
        color: var(--mat-sys-on-surface-variant);
      }

      .loading-content p {
        margin: 0;
        font-weight: 500;
        letter-spacing: 0.02em;
      }
    `,
  ],
})
export class PlaygroundComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('notebookFrame') notebookFrame!: ElementRef<HTMLIFrameElement>;

  private modeService = inject(ModeService);
  private store = inject(AppStore);
  private snackBar = inject(MatSnackBar);
  private cdr = inject(ChangeDetectorRef);
  private assetService = inject(AssetService);
  private deckService = inject(DeckCatalogService);
  private sanitizer = inject(DomSanitizer);
  private dialog = inject(MatDialog);
  private interactionService = inject(InteractionService);

  // Serial Manager for main-thread I/O (Phase B)
  private serialManager = inject(SerialManagerService);

  modeLabel = computed(() => this.modeService.modeLabel());

  // JupyterLite Iframe Configuration
  jupyterliteUrl: SafeResourceUrl | undefined;
  currentTheme = '';
  isLoading = signal(true);
  loadingError = signal(false);
  private loadingTimeout: ReturnType<typeof setTimeout> | undefined;
  private viewInitialized = false;

  private subscription = new Subscription();

  // Selected machine for Direct Control
  selectedMachine = signal<Machine | null>(null);
  selectedTabIndex = signal(0);

  // Ready signal handshake
  private replChannel: BroadcastChannel | null = null;

  constructor() {
    effect(() => {
      const theme = this.store.theme();
      // Only update if view is initialized to avoid early DOM mounting issues
      if (this.viewInitialized) {
        this.updateJupyterliteTheme(theme);
      }
    });
    // Initialize WebSerial Polyfill if WebUSB is available
    if (typeof navigator !== 'undefined' && 'usb' in navigator) {
      try {
        (window as any).polyfillSerial = polyfillSerial; // Expose the serial API interface
        console.log('[REPL] WebSerial Polyfill loaded and exposed as window.polyfillSerial');
      } catch (e) {
        console.warn('[REPL] Failed to load WebSerial polyfill', e);
      }
    }

    // SerialManager is auto-initialized and listening for BroadcastChannel messages
    console.log('[REPL] SerialManager ready for main-thread serial I/O');
  }

  ngOnInit() {
    this.setupReadyListener();
  }

  ngAfterViewInit() {
    this.viewInitialized = true;
    // Trigger initial load now that view is ready
    this.updateJupyterliteTheme(this.store.theme());
    this.cdr.detectChanges();
  }

  /**
   * Set up the BroadcastChannel listener for the ready signal.
   * This must be done early (before iframe load) to avoid race conditions.
   */
  private setupReadyListener() {
    if (this.replChannel) {
      this.replChannel.close();
    }

    // Set up BroadcastChannel listener for ready signal from Pyodide kernel
    this.replChannel = new BroadcastChannel('praxis_repl');
    this.replChannel.onmessage = (event) => {
      const data = event.data;
      if (data?.type === 'praxis:ready') {
        console.log('[REPL] Received kernel ready signal');
        this.isLoading.set(false);
        if (this.loadingTimeout) {
          clearTimeout(this.loadingTimeout);
          this.loadingTimeout = undefined;
        }
        this.cdr.detectChanges();
      } else if (data?.type === 'USER_INTERACTION') {
        this.handleUserInteraction(data);
      }
    };
  }

  /**
   * Handle USER_INTERACTION requests from the REPL channel and show UI dialogs
   */
  private async handleUserInteraction(payload: any) {
    const result = await this.interactionService.handleInteraction({
      interaction_type: payload.interaction_type,
      payload: payload.payload
    });

    if (this.replChannel) {
      this.replChannel.postMessage({
        type: 'praxis:interaction_response',
        id: payload.id,
        value: result
      });
    }
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
    // Clean up ready signal channel
    if (this.replChannel) {
      this.replChannel.close();
      this.replChannel = null;
    }
    if (this.loadingTimeout) {
      clearTimeout(this.loadingTimeout);
    }
  }

  openInventory() {
    const dialogRef = this.dialog.open(AssetWizard, {
      width: '1200px',
      minWidth: '500px',
      height: 'auto',
      minHeight: '400px',
      maxHeight: '90vh',
      panelClass: 'praxis-dialog-no-padding'
    });

    dialogRef.afterClosed().subscribe((result: any) => {
      if (result && typeof result === 'object') {
        const type = result.asset_type === 'MACHINE' ? 'machine' : 'resource';
        this.insertAsset(type, result);
      }
    });
  }

  // Helper for AssetService (kept for reference or if we need to reload dialog data via service, though dialog handles it)
  // loadInventory removed as Dialog manages its own data.
  /* Helper methods for Code Generation */

  /**
   * Helper to determine if dark mode is active based on body class or store
   */
  private getIsDarkMode(): boolean {
    // Single source of truth for the UI is the class on document.body
    return document.body.classList.contains('dark-theme');
  }

  /**
   * Build the JupyterLite URL with configuration parameters
   */
  private async buildJupyterliteUrl() {
    if (this.loadingTimeout) {
      clearTimeout(this.loadingTimeout);
    }

    this.isLoading.set(true);
    this.loadingError.set(false);
    this.jupyterliteUrl = undefined;
    this.cdr.detectChanges();

    const isDark = this.getIsDarkMode();
    this.currentTheme = isDark ? 'dark' : 'light';

    // Build bootstrap code for asset preloading
    const bootstrapCode = await this.getOptimizedBootstrap();

    console.log('[REPL] Building JupyterLite URL. Calculated isDark:', isDark, 'Effective Theme Class:', this.currentTheme);

    // JupyterLite REPL URL with parameters
    const baseUrl = './assets/jupyterlite/repl/index.html';
    const params = new URLSearchParams({
      kernel: 'python',
      toolbar: '1',
      theme: isDark ? 'JupyterLab Dark' : 'JupyterLab Light',
    });

    console.log('[REPL] Generated Params:', params.toString());

    // Add bootstrap code if we have assets
    if (bootstrapCode) {
      params.set('code', bootstrapCode);
    }

    const fullUrl = `${baseUrl}?${params.toString()}`;
    this.jupyterliteUrl = this.sanitizer.bypassSecurityTrustResourceUrl(fullUrl);

    // Set a timeout to show error/retry if iframe load is slow
    this.loadingTimeout = setTimeout(() => {
      if (this.isLoading()) {
        console.warn('[REPL] Loading timeout reached - forcing overlay close');
        this.isLoading.set(false);
        this.cdr.detectChanges();
      }
    }, 15000); // 15 second fallback

    this.cdr.detectChanges();
  }

  /**
   * Update theme when app theme changes
   */
  private async updateJupyterliteTheme(_: string) {
    const isDark = this.getIsDarkMode();
    const newTheme = isDark ? 'dark' : 'light';

    // Only reload if theme actually changed
    if (this.currentTheme !== newTheme) {
      console.log('[REPL] Theme changed from', this.currentTheme, 'to', newTheme, '- rebuilding URL');
      this.currentTheme = newTheme;
      await this.buildJupyterliteUrl();
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
      '# Ensure WebSerial and WebUSB are in builtins for all cells',
      'import builtins',
      'if "WebSerial" in globals():',
      '    builtins.WebSerial = WebSerial',
      'if "WebUSB" in globals():',
      '    builtins.WebUSB = WebUSB',
      '',
      '# Mock pylibftdi (not supported in browser/Pyodide)',
      'import sys',
      'from unittest.mock import MagicMock',
      'sys.modules["pylibftdi"] = MagicMock()',
      '',
      '# Load WebSerial/WebUSB shims for browser I/O',
      '# Note: These are pre-loaded to avoid extra network requests',
      'try:',
      '    import pyodide_js',
      '    from pyodide.ffi import to_js',
      'except ImportError:',
      '    pass',
      '',
      '# Shims will be injected directly via code to avoid 404s',
      '# Patching is done in the bootstrap below',
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
      '',
      '# Message listener for asset injection via BroadcastChannel',
      '# We use BroadcastChannel because it works across Window/Worker contexts',
      'import js',
      'import json',
      '',
      'def _praxis_message_handler(event):',
      '    try:',
      '        data = event.data',
      '        # Convert JsProxy to dict if needed',
      '        if hasattr(data, "to_py"):',
      '            data = data.to_py()',
      '        ',
      '        if isinstance(data, dict) and data.get("type") == "praxis:execute":',
      '            code = data.get("code", "")',
      '            print(f"Executing injected code...")',
      '            exec(code, globals())',
      '        elif isinstance(data, dict) and data.get("type") == "praxis:interaction_response":',
      '            try:',
      '                import web_bridge',
      '                web_bridge.handle_interaction_response(data.get("id"), data.get("value"))',
      '            except ImportError:',
      '                print("! web_bridge not found for interaction response")',
      '    except Exception as e:',
      '        import traceback',
      '        print(f"Error executing injected code: {e}")',
      '        print(traceback.format_exc())',
      '',
      '# Setup BroadcastChannel',
      'try:',
      '    if hasattr(js, "BroadcastChannel"):',
      '        # Try .new() first (Pyodide convention)',
      '        if hasattr(js.BroadcastChannel, "new"):',
      '            _praxis_channel = js.BroadcastChannel.new("praxis_repl")',
      '        else:',
      '            # Fallback to direct constructor',
      '            _praxis_channel = js.BroadcastChannel("praxis_repl")',
      '        ',
      '        _praxis_channel.onmessage = _praxis_message_handler',
      '        print("✓ Asset injection ready (channel created)")',
      '    else:',
      '        print("! BroadcastChannel not available")',
      'except Exception as e:',
      '    print(f"! Failed to setup injection channel: {e}")',
      '',
      'print("✓ pylabrobot loaded with browser I/O shims!")',
      'print(f"  Version: {pylabrobot.__version__}")',
      'print("Use the Inventory button to insert asset variables.")',
      '',
      '# Send ready signal to Angular host',
      'try:',
      '    # Must convert dict to JS Object for structured clone in BroadcastChannel',
      '    from pyodide.ffi import to_js',
      '    ready_msg = to_js({"type": "praxis:ready"}, dict_converter=js.Object.fromEntries)',
      '    _praxis_channel.postMessage(ready_msg)',
      '    print("✓ Ready signal sent")',
      'except Exception as e:',
      '    print(f"! Ready signal failed: {e}")',
    ];

    return lines.join('\n');
  }

  /**
   * Enhanced bootstrap that includes shims directly or uses more efficient fetching
   */
  private async getOptimizedBootstrap(): Promise<string> {
    // We cannot inline the shims because they are too large for the URL parameters (causes 431 error).
    // Instead, we generate Python code to fetch and execute them from within the kernel.
    const shims = ['web_serial_shim.py', 'web_usb_shim.py'];
    let shimInjections = '# --- Browser Hardware Shims --- \n';
    shimInjections += 'import pyodide.http\n';

    for (const shim of shims) {
      // Generate Python code to fetch and exec
      shimInjections += `
print("PylibPraxis: Loading ${shim}...")
try:
    _shim_code = await (await pyodide.http.pyfetch('/assets/shims/${shim}')).string()
    exec(_shim_code, globals())
    print("PylibPraxis: Loaded ${shim}")
except Exception as e:
    print(f"PylibPraxis: Failed to load ${shim}: {e}")
`;
    }

    // Load web_bridge.py as a module
    shimInjections += `
print("PylibPraxis: Loading web_bridge.py...")
try:
    _bridge_code = await (await pyodide.http.pyfetch('/assets/python/web_bridge.py')).string()
    with open('web_bridge.py', 'w') as f:
        f.write(_bridge_code)
    print("PylibPraxis: Loaded web_bridge.py")
except Exception as e:
    print(f"PylibPraxis: Failed to load web_bridge.py: {e}")

# Load praxis package
import os
if not os.path.exists('praxis'):
    os.makedirs('praxis')
    
for _p_file in ['__init__.py', 'interactive.py']:
    try:
        print(f"PylibPraxis: Loading praxis/{_p_file}...")
        _p_code = await (await pyodide.http.pyfetch(f'/assets/python/praxis/{_p_file}')).string()
        with open(f'praxis/{_p_file}', 'w') as f:
            f.write(_p_code)
        print(f"PylibPraxis: Loaded praxis/{_p_file}")
    except Exception as e:
        print(f"PylibPraxis: Failed to load praxis/{_p_file}: {e}")
`;

    const baseBootstrap = this.generateBootstrapCode();
    return shimInjections + '\n' + baseBootstrap;
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
    console.log('[REPL] Iframe loaded event fired');

    // Check if iframe has actual content
    const iframe = this.notebookFrame?.nativeElement;
    // We try to access contentDocument. If it fails (cross-origin) or is empty/about:blank, likely failed or just initialized.
    let hasContent = false;
    try {
      hasContent = (iframe?.contentDocument?.body?.childNodes?.length ?? 0) > 0;
    } catch (e) {
      console.warn('[REPL] Cannot access iframe content (possibly 431 error or cross-origin):', e);
      hasContent = false;
    }

    if (hasContent) {
      console.log('[REPL] Iframe content detected');
      // Success case - but we wait for 'ready' signal to clear isLoading for the user.
      // However, if we don't get 'ready' signal, we rely on timeout.
      // We do NOT clear isLoading here immediately because the kernel is still booting.

      // Inject fetch interceptor to suppress 404s for virtual filesystem lookups
      try {
        const script = iframe!.contentWindow?.document.createElement('script');
        if (script) {
          script.textContent = `
            (function() {
              const originalFetch = window.fetch;
              window.fetch = function(input, init) {
                const url = typeof input === 'string' ? input : (input instanceof URL ? input.href : input.url);
                // Suppress network requests for pylabrobot modules that are already in VFS
                if (url.includes('pylabrobot') && (url.endsWith('.py') || url.endsWith('.so') || url.includes('/__init__.py'))) {
                  // We could return a fake response here, but Pyodide might need a real network 404 
                  // to move to the next finder. However, we can log it gracefully.
                }
                return originalFetch(input, init);
              };
            })();
          `;
          iframe!.contentWindow?.document.head.appendChild(script);
          console.log('[REPL] Fetch interceptor injected into iframe');
        }
      } catch (e) {
        console.warn('[REPL] Could not inject interceptor (likely cross-origin):', e);
      }
    } else {
      console.warn('[REPL] Iframe load event fired but no content detected (or access denied)');
      // If we loaded blank/error page (like 431), we should probably fail.
      // But 'about:blank' also fires load.
      // Let's assume if it's a 431 error page, it has SOME content but maybe not what we expect?
      // Actually, if it's 431, the browser shows an error page.

      // If we clear isLoading here, we hide the spinner and show the error page (white screen or browser error).
      // If we don't clear it, the timeout will eventually catch it.
      // Let's rely on the timeout to show "Retry" if the kernel doesn't say "Ready".
    }
  }

  /**
   * Reload the notebook (restart kernel)
   */
  reloadNotebook() {
    // Force iframe reload by momentarily clearing URL or just rebuilding
    this.jupyterliteUrl = undefined; // Force DOM cleanup
    this.cdr.detectChanges();

    setTimeout(async () => {
      await this.buildJupyterliteUrl();
      this.cdr.detectChanges();
    }, 100);
  }

  /**
   * Generate Python code to instantiate a resource
   */
  private generateResourceCode(resource: Resource, variableName?: string): string {
    const varName = variableName || this.assetToVarName(resource);
    const fqn = resource.fqn || resource.plr_definition?.fqn;

    if (!fqn) {
      // Fallback: just create a comment with the name
      return `# Resource: ${resource.name} (no FQN available)`;
    }

    const parts = fqn.split('.');
    const className = parts[parts.length - 1];

    const lines = [
      `# Resource: ${resource.name}`,
      `from pylabrobot.resources import ${className}`,
      `${varName} = ${className}(name="${varName}")`,
      `print(f"Created: {${varName}}")`
    ];

    return lines.join('\n');
  }

  /**
   * Generate Python code to instantiate a machine.
   */
  private async generateMachineCode(machine: Machine, variableName?: string, deckConfigId?: string): Promise<string> {
    const varName = variableName || this.assetToVarName(machine);
    
    // Extract FQNs
    const frontendFqn = machine.plr_definition?.frontend_fqn || machine.frontend_definition?.fqn;
    const backendFqn = machine.plr_definition?.fqn || machine.backend_definition?.fqn || machine.simulation_backend_name;
    const isSimulated = !!(machine.is_simulation_override || machine.simulation_backend_name);

    if (!frontendFqn) {
      return `# Machine: ${machine.name} (Missing Frontend FQN)`;
    }

    const frontendClass = frontendFqn.split('.').pop()!;
    const frontendModule = frontendFqn.substring(0, frontendFqn.lastIndexOf('.'));

    const config = {
      backend_fqn: backendFqn || 'pylabrobot.liquid_handling.backends.simulation.SimulatorBackend',
      port_id: machine.connection_info?.['address'] || machine.connection_info?.['port_id'] || '',
      is_simulated: isSimulated,
      baudrate: machine.connection_info?.['baudrate'] || 9600
    };

    const lines = [
      `# Machine: ${machine.name}`,
      `from web_bridge import create_configured_backend`,
      `from ${frontendModule} import ${frontendClass}`,
      ``,
      `config = ${JSON.stringify(config, null, 2)}`,
      `backend = create_configured_backend(config)`,
      `${varName} = ${frontendClass}(backend=backend)`,
      `await ${varName}.setup()`,
      `print(f"Created: {${varName}}")`
    ];

    return lines.join('\n');
  }

  /**
   * Check if a machine is currently in use by a protocol run
   */
  isMachineInUse(machine: Machine): boolean {
    // Check if machine has an active protocol run
    return machine.status === MachineStatus.RUNNING;
  }

  /**
   * Insert asset into the notebook by generating and executing Python code
   */
  async insertAsset(
    type: 'machine' | 'resource',
    asset: Machine | Resource,
    variableName?: string,
    deckConfigId?: string
  ) {
    const varName = variableName || this.assetToVarName(asset);

    // If implementing physical machine, check prior authorization
    if (type === 'machine') {
      const machine = asset as Machine;
      this.selectedMachine.set(machine);
      // If it's a physical machine (not simulated)
      if (!machine.is_simulation_override) {
        try {
          // We might want to check ports here, but for now assuming user knows what they are doing
          // or logic is handled elsewhere.
        } catch (err) {
          console.error('Failed to check hardware permissions:', err);
        }
      }
    }

    // Generate appropriate Python code
    let code: string;
    if (type === 'machine') {
      code = await this.generateMachineCode(asset as Machine, varName, deckConfigId);
    } else {
      code = this.generateResourceCode(asset as Resource, varName);
    }

    // Send code via BroadcastChannel
    try {
      const channel = new BroadcastChannel('praxis_repl');
      channel.postMessage({
        type: 'praxis:execute',
        code: code
      });
      setTimeout(() => channel.close(), 100);

      this.snackBar.open(`Inserted ${varName}`, 'OK', { duration: 2000 });
    } catch (e) {
      console.error('Failed to send asset to REPL:', e);
      // Fallback: copy code to clipboard
      navigator.clipboard.writeText(code).then(() => {
        this.snackBar.open(`Code copied to clipboard (BroadcastChannel failed)`, 'OK', {
          duration: 2000,
        });
      });
    }
  }

  /**
   * Handle executeCommand from DirectControlComponent
   */
  async onExecuteCommand(event: { machineName: string, methodName: string, args: any }) {
    const { machineName, methodName, args } = event;
    
    // Convert machine name to safe variable name (same logic as insertAsset)
    const asset = this.selectedMachine();
    if (!asset) return;
    
    const varName = this.assetToVarName(asset);
    
    // Construct Python code: await machine_name.method_name(arg1=val1, arg2=val2)
    const argList = Object.entries(args)
      .map(([key, val]) => {
        const valStr = typeof val === 'string' ? `"${val}"` : val;
        return `${key}=${valStr}`;
      })
      .join(', ');
    
    const code = `await ${varName}.${methodName}(${argList})`;
    
    console.log('[REPL] Executing direct command:', code);

    // Send code via BroadcastChannel
    try {
      const channel = new BroadcastChannel('praxis_repl');
      channel.postMessage({
        type: 'praxis:execute',
        code: code
      });
      setTimeout(() => channel.close(), 100);

      this.snackBar.open(`Executing ${methodName}...`, 'OK', { duration: 2000 });
    } catch (e) {
      console.error('Failed to send command to REPL:', e);
      this.snackBar.open(`Failed to send command`, 'OK', { duration: 3000 });
    }
  }
}
