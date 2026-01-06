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
  signal,
  computed,
} from '@angular/core';
import { AppStore } from '../../core/store/app.store';

import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ModeService } from '../../core/services/mode.service';
import { AssetService } from '../assets/services/asset.service';
import { Machine, Resource } from '../assets/models/asset.models';
import { Subscription } from 'rxjs';
import { HardwareDiscoveryButtonComponent } from '@shared/components/hardware-discovery-button/hardware-discovery-button.component';
import { getResourceCategoryIcon, getMachineCategoryIcon } from '@shared/constants/asset-icons';

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
    FormsModule,
    RouterLink,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatSidenavModule,
    MatListModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    HardwareDiscoveryButtonComponent
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

          <!-- Search and Filters -->
          <div class="filter-section">
            <mat-form-field appearance="outline" class="search-field">
              <mat-icon matPrefix>search</mat-icon>
              <input
                matInput
                placeholder="Search inventory..."
                [(ngModel)]="searchTerm"
                (ngModelChange)="onSearchChange($event)"
              />
              @if (searchTerm()) {
                <button
                  matSuffix
                  mat-icon-button
                  aria-label="Clear"
                  (click)="clearSearch()"
                >
                  <mat-icon>close</mat-icon>
                </button>
              }
            </mat-form-field>

            <!-- Category Filter Chips -->
            @if (allCategories().length > 0) {
              <div class="category-chips">
                <mat-chip-listbox
                  [(ngModel)]="selectedCategory"
                  (change)="onCategoryChange()"
                  aria-label="Filter by category"
                >
                  <mat-chip-option [value]="null">All</mat-chip-option>
                  @for (cat of allCategories(); track cat) {
                    <mat-chip-option [value]="cat">
                      <mat-icon class="chip-icon">{{ getCategoryIcon(cat) }}</mat-icon>
                      {{ cat }}
                    </mat-chip-option>
                  }
                </mat-chip-listbox>
              </div>
            }
          </div>

          <!-- Machines Section -->
          <div class="inventory-section">
            <h4>
              <mat-icon>precision_manufacturing</mat-icon>
              Machines ({{ filteredMachines().length }})
            </h4>
            <mat-list dense>
              @for (m of filteredMachines(); track m.accession_id) {
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
              }
              @if (filteredMachines().length === 0) {
                <div class="empty-state">
                  @if (inventoryMachines().length === 0) {
                    <p>No machines in inventory</p>
                    <a routerLink="/app/assets" class="add-link">
                      <mat-icon>add</mat-icon>
                      Add from Assets
                    </a>
                  } @else {
                    <p>No machines match your filters</p>
                  }
                </div>
              }
            </mat-list>
          </div>

          <!-- Resources Section -->
          <div class="inventory-section">
            <h4>
              <mat-icon>category</mat-icon>
              Resources ({{ filteredResources().length }})
            </h4>
            <mat-list dense>
              @for (r of filteredResources().slice(0, 50); track r.accession_id) {
                <mat-list-item>
                  <div class="inventory-item">
                    <mat-icon class="resource-icon">{{ getCategoryIcon(getResourceCategory(r)) }}</mat-icon>
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
              }
              @if (filteredResources().length === 0) {
                <div class="empty-state">
                  @if (inventoryResources().length === 0) {
                    <p>No resources in inventory</p>
                    <a routerLink="/app/assets" class="add-link">
                      <mat-icon>add</mat-icon>
                      Add from Assets
                    </a>
                  } @else {
                    <p>No resources match your filters</p>
                  }
                </div>
              }
              @if (filteredResources().length > 50) {
                <div class="truncation-notice">
                  Showing first 50 of {{ filteredResources().length }}
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
            <div class="repl-notebook-wrapper" data-tour-id="repl-notebook">
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
        width: 300px;
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

      /* Filter Section */
      .filter-section {
        padding: 12px 16px;
        border-bottom: 1px solid var(--mat-sys-outline-variant);
      }

      .search-field {
        width: 100%;
      }

      :host ::ng-deep .search-field {
        .mat-mdc-form-field-subscript-wrapper { display: none; }
        .mat-mdc-text-field-wrapper { height: 40px; }
        .mat-mdc-form-field-flex { height: 40px; }
        .mat-mdc-form-field-icon-prefix { padding: 8px 0 0 8px; }
      }

      .category-chips {
        margin-top: 8px;
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
      }

      :host ::ng-deep .category-chips {
        mat-chip-listbox {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
        }
        .mat-mdc-chip {
          --mdc-chip-container-height: 28px;
          font-size: 0.75rem;
        }
        .chip-icon {
          font-size: 14px;
          width: 14px;
          height: 14px;
          margin-right: 4px;
        }
      }

      .inventory-section {
        padding: 8px 16px;
      }

      .inventory-section h4 {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 8px 0 4px 0;
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

      .inventory-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        gap: 8px;
      }

      .resource-icon {
        font-size: 16px;
        width: 16px;
        height: 16px;
        color: var(--mat-sys-primary);
        flex-shrink: 0;
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
        flex-shrink: 0;
      }

      .empty-state {
        padding: 16px;
        color: var(--mat-sys-on-surface-variant);
        text-align: center;
      }

      .empty-state p {
        margin: 0 0 8px 0;
        font-style: italic;
      }

      .add-link {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        color: var(--mat-sys-primary);
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 500;
      }

      .add-link:hover {
        text-decoration: underline;
      }

      .add-link mat-icon {
        font-size: 16px;
        width: 16px;
        height: 16px;
      }

      .truncation-notice {
        padding: 8px 16px;
        color: var(--mat-sys-on-surface-variant);
        text-align: center;
        font-size: 0.75rem;
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

  // Inventory - using signals for reactivity
  inventoryMachines = signal<Machine[]>([]);
  inventoryResources = signal<Resource[]>([]);
  isSidebarOpen = true;

  // Filter state
  searchTerm = signal<string>('');
  selectedCategory = signal<string | null>(null);

  // Computed filtered lists
  filteredMachines = computed(() => {
    const search = this.searchTerm().toLowerCase();
    const category = this.selectedCategory();
    let machines = this.inventoryMachines();

    if (search) {
      machines = machines.filter(m =>
        m.name.toLowerCase().includes(search) ||
        m.machine_category?.toLowerCase().includes(search)
      );
    }

    if (category) {
      machines = machines.filter(m => m.machine_category === category);
    }

    return machines;
  });

  filteredResources = computed(() => {
    const search = this.searchTerm().toLowerCase();
    const category = this.selectedCategory();
    let resources = this.inventoryResources();

    if (search) {
      resources = resources.filter(r =>
        r.name.toLowerCase().includes(search) ||
        this.getResourceCategory(r)?.toLowerCase().includes(search) ||
        r.fqn?.toLowerCase().includes(search)
      );
    }

    if (category) {
      resources = resources.filter(r => this.getResourceCategory(r) === category);
    }

    return resources;
  });

  // All unique categories for filter chips
  allCategories = computed(() => {
    const resourceCats = this.inventoryResources()
      .map(r => this.getResourceCategory(r))
      .filter((c): c is string => !!c);
    const machineCats = this.inventoryMachines()
      .map(m => m.machine_category)
      .filter((c): c is string => !!c);

    const uniqueCats = [...new Set([...resourceCats, ...machineCats])];
    return uniqueCats.sort();
  });

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
   * Handle search input change
   */
  onSearchChange(value: string): void {
    this.searchTerm.set(value);
  }

  /**
   * Clear search input
   */
  clearSearch(): void {
    this.searchTerm.set('');
  }

  /**
   * Handle category filter change
   */
  onCategoryChange(): void {
    // The signal is already updated via ngModel binding
    // This method exists for any additional side effects if needed
  }

  /**
   * Get category from a resource (via plr_definition or asset_type)
   */
  getResourceCategory(resource: Resource): string {
    // Try to extract from plr_definition.plr_category or fall back to asset_type
    return resource.plr_definition?.plr_category || resource.asset_type || '';
  }

  /**
   * Get icon for a category
   */
  getCategoryIcon(category: string): string {
    // Try resource icon first, then machine icon
    const icon = getResourceCategoryIcon(category);
    if (icon !== 'inventory_2') return icon;
    return getMachineCategoryIcon(category);
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
        this.inventoryMachines.set(machines);
      })
    );
    this.subscription.add(
      this.assetService.getResources().subscribe((resources) => {
        this.inventoryResources.set(resources);
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

