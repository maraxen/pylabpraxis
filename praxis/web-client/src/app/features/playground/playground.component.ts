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
} from '@angular/core';
import { AppStore } from '../../core/store/app.store';

import { FormsModule } from '@angular/forms';

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
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ModeService } from '../../core/services/mode.service';
import { AssetService } from '../assets/services/asset.service';
import { Machine, Resource, MachineStatus } from '../assets/models/asset.models';
import { Subscription } from 'rxjs';
import { HardwareDiscoveryButtonComponent } from '@shared/components/hardware-discovery-button/hardware-discovery-button.component';

import { serial as polyfillSerial } from 'web-serial-polyfill';
import { SerialManagerService } from '../../core/services/serial-manager.service';
import { MatDialog } from '@angular/material/dialog';
import { InventoryDialogComponent, InventoryItem } from './components/inventory-dialog/inventory-dialog.component';

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
    HardwareDiscoveryButtonComponent,

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
              <h2>Playground Notebook ({{ modeLabel() }})</h2>
            </div>
            
            <div class="header-actions flex items-center gap-2">
              <app-hardware-discovery-button></app-hardware-discovery-button>
              <button 
                mat-icon-button 
                (click)="reloadNotebook()"
                matTooltip="Restart Kernel (reload notebook)">
                <mat-icon>restart_alt</mat-icon>
              </button>
              <button 
                mat-icon-button 
                (click)="openInventory()"
                matTooltip="Open Inventory Dialog"
                color="primary">
                <mat-icon>inventory_2</mat-icon>
              </button>
            </div>
          </div>

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
          </div>
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

      .inventory-area {
        height: 100%;
        min-width: 0; /* Allow shrinking */
        display: flex;
        flex-direction: column;
      }

      .resize-handle {
        width: 16px;
        height: 100%;
        cursor: col-resize;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        z-index: 10;
        
        /* Visual indicator */
        &::after {
          content: '';
          width: 4px;
          height: 48px;
          background-color: var(--mat-sys-outline-variant);
          border-radius: 2px;
        }

        &:hover::after {
          background-color: var(--mat-sys-primary);
        }
      }

      .repl-card, .inventory-card {
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

      .repl-header, .inventory-header {
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

      .repl-header h2, .inventory-header h3 {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .repl-notebook-wrapper, .inventory-content {
        flex-grow: 1;
        /* overflow: hidden;  <-- REMOVE THIS. Let the iframe verify its own scroll area. */
        position: relative;
        background: var(--mat-sys-surface-container-low);
      }

      .inventory-content {
        overflow-y: auto;
        padding: 0;
      }

      .notebook-frame {
        width: 100%;
        height: 100%;
        border: none;
      }

      .filter-section {
        padding: 12px 16px;
        border-bottom: 1px solid var(--mat-sys-outline-variant);
        display: flex;
        flex-direction: column;
        gap: 8px;
        background: var(--mat-sys-surface);
      }

      .search-field {
        width: 100%;
        margin-bottom: 0;
      }

      :host ::ng-deep .search-field {
        .mat-mdc-form-field-subscript-wrapper { display: none; }
        .mat-mdc-text-field-wrapper { height: 40px; }
        .mat-mdc-form-field-flex { height: 40px; }
      }

      .category-btn {
        width: 100%;
        justify-content: space-between;
      }

      .inventory-section {
        padding: 8px 0;
      }

      .inventory-section h4 {
        padding: 0 16px;
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 8px 0 8px 0;
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--mat-sys-on-surface-variant);
        text-transform: uppercase;
      }

      .inventory-section h4 mat-icon {
        font-size: 16px;
        width: 16px;
        height: 16px;
      }

      .inventory-list {
        display: flex;
        flex-direction: column;
      }

      .inventory-item-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 4px 8px 4px 16px;
        border-bottom: 1px solid var(--mat-sys-outline-variant);
        
        &:last-child {
          border-bottom: none;
        }

        &:hover {
          background-color: var(--mat-sys-surface-container-high);
        }
      }

      .item-info {
        display: flex;
        flex-direction: column;
        flex: 1;
        min-width: 0;
        gap: 4px;
      }

      .item-name {
        font-family: monospace;
        font-size: 0.85rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .item-badges {
        display: flex;
        gap: 4px;
      }

      .badge {
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 4px;
        text-transform: uppercase;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 2px;
      }
      
      .badge.in-use {
        background-color: var(--mat-sys-error-container);
        color: var(--mat-sys-on-error-container);
        
        mat-icon {
          font-size: 10px;
          height: 10px;
          width: 10px;
        }
      }

      .badge.simulated {
        background-color: var(--mat-sys-secondary-container);
        color: var(--mat-sys-on-secondary-container);
      }

      .resource-icon {
        font-size: 14px;
        width: 14px;
        height: 14px;
        color: var(--mat-sys-primary);
        display: inline-block;
        margin-right: 4px;
        vertical-align: middle;
      }

      .insert-btn {
        color: var(--mat-sys-primary);
        transform: scale(0.9);
      }

      .empty-state-small {
        padding: 16px;
        text-align: center;
        color: var(--mat-sys-on-surface-variant);
        font-style: italic;
        font-size: 0.85rem;
      }



      .truncation-notice {
        padding: 8px 16px;
        text-align: center;
        font-size: 0.75rem;
        color: var(--mat-sys-on-surface-variant);
        font-style: italic;
      }
      
      .selected {
        background-color: var(--mat-sys-secondary-container);
        color: var(--mat-sys-on-secondary-container);
      }
    `,
  ],
})
export class PlaygroundComponent implements OnInit, OnDestroy {
  @ViewChild('notebookFrame') notebookFrame!: ElementRef<HTMLIFrameElement>;

  private modeService = inject(ModeService);
  private store = inject(AppStore);
  private snackBar = inject(MatSnackBar);
  private cdr = inject(ChangeDetectorRef);
  private assetService = inject(AssetService);
  private sanitizer = inject(DomSanitizer);
  private dialog = inject(MatDialog);

  // Serial Manager for main-thread I/O (Phase B)
  private serialManager = inject(SerialManagerService);

  modeLabel = computed(() => this.modeService.modeLabel());

  // JupyterLite Iframe Configuration
  jupyterliteUrl: SafeResourceUrl | undefined;
  currentTheme = 'light';

  private subscription = new Subscription();

  // Ready signal handshake
  private replChannel: BroadcastChannel | null = null;

  constructor() {
    effect(() => {
      const theme = this.store.theme();
      this.updateJupyterliteTheme(theme);
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
    // buildJupyterliteUrl is called by updateJupyterliteTheme initially via effect
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
      if (event.data?.type === 'praxis:ready') {
        console.log('[REPL] Received kernel ready signal');
      }
    };
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
    // Clean up ready signal channel
    if (this.replChannel) {
      this.replChannel.close();
      this.replChannel = null;
    }
  }

  openInventory() {
    const dialogRef = this.dialog.open(InventoryDialogComponent, {
      width: '900px',
      height: 'auto',
      maxHeight: '90vh',
      panelClass: 'praxis-dialog-no-padding'
    });

    dialogRef.afterClosed().subscribe((result: InventoryItem[] | undefined) => {
      if (result && result.length > 0) {
        this.insertMultipleAssets(result);
      }
    });
  }

  async insertMultipleAssets(items: InventoryItem[]) {
    for (const item of items) {
      await this.insertAsset(
        item.type,
        item.asset,
        item.variableName,
        item.backend
      );
    }
  }

  // Helper for AssetService (kept for reference or if we need to reload dialog data via service, though dialog handles it)
  // loadInventory removed as Dialog manages its own data.
  /* Helper methods for Code Generation */

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
    this.cdr.detectChanges();
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
      '            print(f"DEBUG Code:\\n{code}")',
      '            exec(code, globals())',
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
      '    _praxis_channel.postMessage({"type": "praxis:ready"})',
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
    const baseBootstrap = this.generateBootstrapCode();

    // Attempt to fetch shims once and cache them
    const shims = ['web_serial_shim.py', 'web_usb_shim.py'];
    let shimInjections = '\n# Injected Shims\n';

    for (const shim of shims) {
      try {
        const response = await fetch(`/assets/shims/${shim}`);
        if (response.ok) {
          const code = await response.text();
          shimInjections += `\n# --- ${shim} ---\n${code}\n`;
        }
      } catch (e) {
        console.warn(`[REPL] Failed to pre-load shim: ${shim}`, e);
        // Fallback to runtime fetch in Python if pre-load fails
        shimInjections += `import pyodide.http\nexec(await (await pyodide.http.pyfetch('/assets/shims/${shim}')).string())\n`;
      }
    }

    return baseBootstrap + shimInjections;
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
    if (iframe && (iframe.contentDocument?.body?.childNodes?.length ?? 0) > 0) {
      console.log('[REPL] Iframe content detected');

      // Inject fetch interceptor to suppress 404s for virtual filesystem lookups
      try {
        const script = iframe.contentWindow?.document.createElement('script');
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
          iframe.contentWindow?.document.head.appendChild(script);
          console.log('[REPL] Fetch interceptor injected into iframe');
        }
      } catch (e) {
        console.warn('[REPL] Could not inject interceptor (likely cross-origin):', e);
      }
    } else {
      console.warn('[REPL] Iframe load event fired but no content detected');
    }
  }

  /**
   * Reload the notebook (restart kernel)
   */
  reloadNotebook() {
    // Force iframe reload by momentarily clearing URL or just rebuilding
    this.jupyterliteUrl = undefined; // Force DOM cleanup
    this.cdr.detectChanges();

    setTimeout(() => {
      this.buildJupyterliteUrl();
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
  private generateMachineCode(machine: Machine, variableName?: string, backendOverride?: string): string {
    const varName = variableName || this.assetToVarName(machine);
    const category = machine.machine_category?.toLowerCase() || 'machine';
    const plrBackendFqn = machine.plr_definition?.fqn || machine.connection_info?.['plr_backend'];

    // Override simulation if backendOverride ('simulated') is passed
    // Or if default is simulated
    const isSimulated = backendOverride === 'simulated' || machine.is_simulation_override;

    // Get FQNs from definition
    const frontendFqn = machine.plr_definition?.frontend_fqn;
    const backendFqn = plrBackendFqn;

    // If we have both FQNs, generate clean code using them
    if (frontendFqn && backendFqn) {
      const frontendClass = frontendFqn.split('.').pop()!;
      const frontendModule = frontendFqn.substring(0, frontendFqn.lastIndexOf('.'));
      const backendClass = backendFqn.split('.').pop()!;
      const backendModule = backendFqn.substring(0, backendFqn.lastIndexOf('.'));

      if (isSimulated) {
        if (frontendClass === 'LiquidHandler') {
          return [
            `# Machine: ${machine.name} (simulation mode)`,
            `from ${frontendModule} import ${frontendClass}`,
            `from pylabrobot.liquid_handling.backends.simulation import SimulatorBackend`,
            `${varName} = ${frontendClass}(backend=SimulatorBackend())`,
            `await ${varName}.setup()`,
            `print(f"Created: {${varName}} (simulation mode)")`,
          ].join('\n');
        }
        return [
          `# Machine: ${machine.name} (simulation mode)`,
          `# Note: Simulation not available for ${frontendClass}`,
          `from ${frontendModule} import ${frontendClass}`,
          `from ${backendModule} import ${backendClass}`,
          `${varName}_backend = ${backendClass}()`,
          `${varName} = ${frontendClass}(backend=${varName}_backend)`,
          `# await ${varName}.setup()  # Uncomment when connected to hardware`,
          `print(f"Created: {${varName}} (backend initialized, setup skipped)")`,
        ].join('\n');
      }

      // Physical hardware
      if (frontendClass === 'PlateReader') {
        return [
          `# Machine: ${machine.name}`,
          `from ${frontendModule} import ${frontendClass}`,
          `from ${backendModule} import ${backendClass}`,
          `${varName}_backend = ${backendClass}()`,
          `# Force-inject WebSerial (browser shim) into backend io`,
          `${varName}_backend.io = WebSerial(baudrate=125000)`,
          `${varName} = ${frontendClass}(name="${machine.name}", backend=${varName}_backend, size_x=1, size_y=1, size_z=1)`,
          ``,
          `# Auto-start connection`,
          `import asyncio`,
          `print("⏳ Initializing ${machine.name}...")`,
          `async def _auto_setup_${varName}():`,
          `    try:`,
          `        await ${varName}.setup()`,
          `        print("✅ ${machine.name} connected and ready!")`,
          `    except Exception as e:`,
          `        print(f"❌ Setup failed: {e}")`,
          ``,
          `asyncio.create_task(_auto_setup_${varName}())`,
        ].join('\n');
      }

      return [
        `# Machine: ${machine.name}`,
        `from ${frontendModule} import ${frontendClass}`,
        `from ${backendModule} import ${backendClass}`,
        `${varName}_backend = ${backendClass}()`,
        `${varName} = ${frontendClass}(backend=${varName}_backend)`,
        `await ${varName}.setup()`,
        `print(f"Created: {${varName}}")`,
      ].join('\n');
    }

    // Fallback: category-based logic
    if (category === 'liquid_handler' || category === 'liquidhandler') {
      if (isSimulated) {
        return [
          `# Machine: ${machine.name} (simulation mode)`,
          `from pylabrobot.liquid_handling import LiquidHandler`,
          `from pylabrobot.liquid_handling.backends.simulation import SimulatorBackend`,
          `${varName} = LiquidHandler(backend=SimulatorBackend())`,
          `print(f"Created: {${varName}} (simulation mode)")`,
          `print("Use variable: ${varName}")`,
          `print("Call 'await ${varName}.setup()' to initialize")`
        ].join('\n');
      } else {
        const backendClass = plrBackendFqn?.split('.').pop() || 'STAR';
        const backendModule = plrBackendFqn?.replace(`.${backendClass}`, '') || 'pylabrobot.liquid_handling.backends.hamilton';
        return [
          `# Machine: ${machine.name} (physical hardware)`,
          `from pylabrobot.liquid_handling import LiquidHandler`,
          `from ${backendModule} import ${backendClass}`,
          `${varName}_backend = ${backendClass}()`,
          `${varName} = LiquidHandler(backend=${varName}_backend)`,
          `print(f"Created: {${varName}} with ${backendClass} backend")`,
          `print("Use variable: ${varName}")`,
          `print("Call 'await ${varName}.setup()' to connect to hardware")`
        ].join('\n');
      }
    } else if (category === 'plate_reader' || category === 'platereader' || category === 'platereaderbackend') {
      const backendClass = plrBackendFqn?.split('.').pop() || 'CLARIOstarBackend';
      const backendModule = plrBackendFqn?.replace(`.${backendClass}`, '') || 'pylabrobot.plate_reading.clario_star_backend';
      return [
        `# Machine: ${machine.name}`,
        `from pylabrobot.plate_reading import PlateReader`,
        `from ${backendModule} import ${backendClass}`,
        `${varName}_backend = ${backendClass}()`,
        `# Force-inject WebSerial (browser shim) into backend io`,
        `${varName}_backend.io = WebSerial(baudrate=125000)`,
        `${varName} = PlateReader(name="${machine.name}", backend=${varName}_backend, size_x=1, size_y=1, size_z=1)`,
        ``,
        `# Auto-start connection`,
        `import asyncio`,
        `print("⏳ Initializing ${machine.name}...")`,
        `async def _auto_setup_${varName}():`,
        `    try:`,
        `        await ${varName}.setup()`,
        `        print("✅ ${machine.name} connected and ready!")`,
        `    except Exception as e:`,
        `        print(f"❌ Setup failed: {e}")`,
        ``,
        `asyncio.create_task(_auto_setup_${varName}())`
      ].join('\n');
    } else {
      return [
        `# Machine: ${machine.name}`,
        `# Category: ${category}`,
        `# FQN: ${plrBackendFqn || 'unknown'}`,
        `print("Warning: Could not determine specific frontend for category '${category}'")`,
        `print("Machine '${machine.name}' has been skipped or needs manual setup.")`
      ].join('\n');
    }
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
    backendOverride?: string
  ) {
    const varName = variableName || this.assetToVarName(asset);

    // If implementing physical machine, check prior authorization
    if (type === 'machine') {
      const machine = asset as Machine;
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
      code = this.generateMachineCode(asset as Machine, varName, backendOverride);
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
}
