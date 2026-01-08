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
import { MatListModule } from '@angular/material/list';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
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
import { getResourceCategoryIcon, getMachineCategoryIcon } from '@shared/constants/asset-icons';
import { serial as polyfillSerial } from 'web-serial-polyfill';
import { SerialManagerService } from '../../core/services/serial-manager.service';

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
    MatListModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatFormFieldModule,
    MatInputModule,
    MatMenuModule,
    MatDividerModule,
    MatSelectModule,
    MatChipsModule,
    HardwareDiscoveryButtonComponent
  ],
  template: `
    <div class="repl-container" [style.grid-template-columns]="gridTemplateColumns()">
      <!-- Main Notebook Area -->
      <div class="notebook-area">
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
                matTooltip="Restart Kernel (reload notebook)">
                <mat-icon>restart_alt</mat-icon>
              </button>
              <button 
                mat-icon-button 
                (click)="toggleInventory()"
                [matTooltip]="isInventoryOpen() ? 'Close Inventory' : 'Open Inventory'"
                [color]="isInventoryOpen() ? 'primary' : ''">
                <mat-icon>{{ isInventoryOpen() ? 'inventory_2' : 'inventory_2' }}</mat-icon>
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

      <!-- Resize Handle -->
      @if (isInventoryOpen()) {
        <div 
          class="resize-handle"
          (mousedown)="startResize($event)"
        ></div>
      }

      <!-- Inventory Sidebar -->
      @if (isInventoryOpen()) {
        <div class="inventory-area">
          <mat-card class="inventory-card">
            <div class="inventory-header">
              <h3>Inventory</h3>
              <button 
                mat-icon-button 
                (click)="loadInventory()" 
                matTooltip="Refresh Inventory">
                <mat-icon>refresh</mat-icon>
              </button>
              <button 
                mat-icon-button 
                (click)="toggleInventory()" 
                matTooltip="Close Inventory">
                <mat-icon>close</mat-icon>
              </button>
            </div>

            <!-- Search and Filters -->
            <div class="filter-section">
              <mat-form-field appearance="outline" class="search-field praxis-search-field">
                <mat-icon matPrefix>search</mat-icon>
                <input 
                  matInput 
                  placeholder="Search inventory..." 
                  [ngModel]="searchTerm()"
                  (ngModelChange)="onSearchChange($event)"
                >
                @if (searchTerm()) {
                  <button matSuffix mat-icon-button aria-label="Clear" (click)="clearSearch()">
                    <mat-icon>close</mat-icon>
                  </button>
                }
              </mat-form-field>

              <!-- Category Dropdown Filter -->
              <div class="category-filter">
                <button mat-stroked-button [matMenuTriggerFor]="categoryMenu" class="category-btn">
                  <mat-icon>{{ selectedCategory() ? getCategoryIcon(selectedCategory()!) : 'category' }}</mat-icon>
                  {{ selectedCategory() || 'All Categories' }}
                  <mat-icon iconPositionEnd>arrow_drop_down</mat-icon>
                </button>
                <mat-menu #categoryMenu="matMenu">
                  <button mat-menu-item (click)="selectCategory(null)" [class.selected]="!selectedCategory()">
                    <mat-icon>category</mat-icon>
                    <span>All Categories</span>
                  </button>
                  <mat-divider></mat-divider>
                  @for (cat of allCategories(); track cat) {
                    <button mat-menu-item (click)="selectCategory(cat)" [class.selected]="selectedCategory() === cat">
                      <mat-icon>{{ getCategoryIcon(cat) }}</mat-icon>
                      <span>{{ cat }}</span>
                    </button>
                  }
                </mat-menu>
              </div>
            </div>

            <div class="inventory-content">
              <!-- Machines Section -->
              <div class="inventory-section">
                <h4>
                  <mat-icon>precision_manufacturing</mat-icon> 
                  Machines ({{ filteredMachines().length }})
                </h4>
                <div class="inventory-list">
                  @for (m of filteredMachines(); track m.accession_id) {
                    <div class="inventory-item-row">
                      <div class="item-info">
                        <span class="item-name" [matTooltip]="m.name">{{ m.name }}</span>
                        <div class="item-badges">
                          @if (isMachineInUse(m)) {
                            <span class="badge in-use" matTooltip="Currently in use by protocol execution">
                              <mat-icon>play_circle</mat-icon> In Use
                            </span>
                          }
                          @if (m.is_simulation_override) {
                            <span class="badge simulated" matTooltip="Simulation Mode">Sim</span>
                          }
                        </div>
                      </div>
                      <button 
                        mat-icon-button 
                        (click)="insertAsset('machine', m)"
                        matTooltip="Insert into notebook"
                        class="insert-btn">
                        <mat-icon>add_circle</mat-icon>
                      </button>
                    </div>
                  }
                  @if (filteredMachines().length === 0) {
                    <div class="empty-state-small">
                      No machines found
                    </div>
                  }
                </div>
              </div>

              <!-- Resources Section -->
              <div class="inventory-section">
                <h4>
                  <mat-icon>category</mat-icon> 
                  Resources ({{ filteredResources().length }})
                </h4>
                <div class="inventory-list">
                  @for (r of filteredResources().slice(0, 50); track r.accession_id) {
                    <div class="inventory-item-row">
                      <div class="item-info">
                        <mat-icon class="resource-icon">{{ getCategoryIcon(getResourceCategory(r)) }}</mat-icon>
                        <span class="item-name" [matTooltip]="r.name">{{ r.name }}</span>
                      </div>
                      <button 
                        mat-icon-button 
                        (click)="insertAsset('resource', r)"
                        matTooltip="Insert into notebook"
                        class="insert-btn">
                        <mat-icon>add_circle</mat-icon>
                      </button>
                    </div>
                  }
                  @if (filteredResources().length === 0) {
                    <div class="empty-state-small">
                      No resources found
                    </div>
                  }
                  @if (filteredResources().length > 50) {
                    <div class="truncation-notice">
                      Showing first 50 of {{ filteredResources().length }}
                    </div>
                  }
                </div>
              </div>
            </div>
          </mat-card>
        </div>
      }
    </div>
  `,
  styles: [
    `
      .repl-container {
        height: 100%;
        width: 100%;
        box-sizing: border-box;
        display: grid;
        /* Default columns: notebook, handle (if open), inventory (if open) */
        /* Set dynamically via style binding */
        /* overflow: hidden; Removed to allow iframe internal scrolling if needed, though usually iframe handles it. 
           Actually, we want the container to be rigid and the iframe to scroll internally. 
           Let's keep overflow hidden on container but ensure wrapper allows content. */
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
export class JupyterliteReplComponent implements OnInit, OnDestroy {
  @ViewChild('notebookFrame') notebookFrame!: ElementRef<HTMLIFrameElement>;

  private modeService = inject(ModeService);
  private store = inject(AppStore);
  private snackBar = inject(MatSnackBar);
  private cdr = inject(ChangeDetectorRef);
  private assetService = inject(AssetService);
  private sanitizer = inject(DomSanitizer);

  // Serial Manager for main-thread I/O (Phase B)
  private serialManager = inject(SerialManagerService);

  modeLabel = computed(() => this.modeService.modeLabel());

  // JupyterLite Iframe Configuration
  jupyterliteUrl: SafeResourceUrl | undefined;
  currentTheme = 'light';
  isLoading = true;

  private subscription = new Subscription();

  // Inventory state
  inventoryMachines = signal<Machine[]>([]);
  inventoryResources = signal<Resource[]>([]);
  isInventoryOpen = signal(false);

  // Resizable panel state
  inventoryWidth = signal(300);
  isResizing = signal(false);

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
    this.loadInventory();
    // buildJupyterliteUrl is called by updateJupyterliteTheme initially via effect
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  // Computed grid columns
  gridTemplateColumns = computed(() => {
    if (!this.isInventoryOpen()) {
      return '1fr 0px 0px'; // Notebook takes full width
    }
    // Notebook | Handle | Inventory
    return `1fr 16px ${this.inventoryWidth()}px`;
  });

  // Filter state
  searchTerm = signal<string>('');
  selectedCategory = signal<string | null>(null);

  allCategories = computed(() => {
    const machines = this.inventoryMachines();
    const resources = this.inventoryResources();
    const categories = new Set<string>();

    machines.forEach(m => {
      if (m.machine_category) categories.add(m.machine_category);
    });
    resources.forEach(r => {
      const cat = this.getResourceCategory(r);
      if (cat) categories.add(cat);
    });

    return Array.from(categories).sort();
  });

  filteredMachines = computed(() => {
    const machines = this.inventoryMachines();
    const search = this.searchTerm().toLowerCase();
    const category = this.selectedCategory();

    return machines.filter(m => {
      const matchesSearch = !search || m.name.toLowerCase().includes(search);
      const matchesCategory = !category || m.machine_category === category;
      return matchesSearch && matchesCategory;
    });
  });

  filteredResources = computed(() => {
    const resources = this.inventoryResources();
    const search = this.searchTerm().toLowerCase();
    const category = this.selectedCategory();

    return resources.filter(r => {
      const matchesSearch = !search || r.name.toLowerCase().includes(search);
      const matchesCategory = !category || this.getResourceCategory(r) === category;
      return matchesSearch && matchesCategory;
    });
  });

  // Resize handling
  private startX = 0;
  private startWidth = 0;
  private resizeListener: ((e: MouseEvent) => void) | null = null;
  private upListener: (() => void) | null = null;

  startResize(event: MouseEvent) {
    event.preventDefault();
    this.isResizing.set(true);
    this.startX = event.clientX;
    this.startWidth = this.inventoryWidth();

    // Add global listeners
    this.resizeListener = (e: MouseEvent) => this.handleResize(e);
    this.upListener = () => this.stopResize();

    document.addEventListener('mousemove', this.resizeListener);
    document.addEventListener('mouseup', this.upListener);

    // Add overlay to iframe to prevent it swallowing mouse events
    const overlay = document.createElement('div');
    overlay.id = 'resize-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100vw';
    overlay.style.height = '100vh';
    overlay.style.zIndex = '9999';
    overlay.style.cursor = 'col-resize';
    document.body.appendChild(overlay);
  }

  handleResize(event: MouseEvent) {
    if (!this.isResizing()) return;

    // Calculate new width (dragging left increases width)
    const delta = this.startX - event.clientX;
    let newWidth = this.startWidth + delta;

    // Constrain width
    const minWidth = 250;
    const maxWidth = 500;
    newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));

    this.inventoryWidth.set(newWidth);
  }

  stopResize() {
    this.isResizing.set(false);

    if (this.resizeListener) {
      document.removeEventListener('mousemove', this.resizeListener);
      this.resizeListener = null;
    }
    if (this.upListener) {
      document.removeEventListener('mouseup', this.upListener);
      this.upListener = null;
    }

    const overlay = document.getElementById('resize-overlay');
    if (overlay) {
      overlay.remove();
    }
  }

  /**
   * Toggle inventory sidebar
   */
  toggleInventory() {
    this.isInventoryOpen.update(v => !v);
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
   * Select a category filter
   */
  selectCategory(category: string | null): void {
    this.selectedCategory.set(category);
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
      `shim_code = await (await pyodide.http.pyfetch('/assets/shims/web_serial_shim.py?t=${Date.now()}')).string()`,
      'exec(shim_code)',
      `usb_code = await (await pyodide.http.pyfetch('/assets/shims/web_usb_shim.py?t=${Date.now()}')).string()`,
      'exec(usb_code)',
      '',
      '# Mock pylibftdi (not supported in browser/Pyodide)',
      'import sys',
      'from unittest.mock import MagicMock',
      'sys.modules["pylibftdi"] = MagicMock()',
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
      '        _praxis_channel = js.BroadcastChannel.new("praxis_repl")',
      '        _praxis_channel.onmessage = _praxis_message_handler',
      '        print("✓ Asset injection ready")',
      '    else:',
      '        print("! BroadcastChannel not available")',
      'except Exception as e:',
      '    print(f"! Failed to setup injection channel: {e}")',
      '',
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
  /**
   * Handle iframe load event
   */
  onIframeLoad() {
    // Check if iframe has actual content
    const iframe = this.notebookFrame?.nativeElement;
    if (iframe && (iframe.contentDocument?.body?.childNodes?.length ?? 0) > 0) {
      // Wait a bit for JupyterLite to fully initialize
      setTimeout(() => {
        this.isLoading = false;
        this.cdr.detectChanges();
      }, 3000); // Increased timeout to be safe
    }
  }

  /**
   * Reload the notebook (restart kernel)
   */
  reloadNotebook() {
    this.isLoading = true;
    // Force iframe reload by momentarily clearing URL or just rebuilding
    this.jupyterliteUrl = undefined; // Force DOM cleanup
    this.cdr.detectChanges();

    setTimeout(() => {
      this.buildJupyterliteUrl();
      this.cdr.detectChanges();
    }, 100);
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
   * Generate Python code to instantiate a resource
   */
  private generateResourceCode(resource: Resource): string {
    const varName = this.assetToVarName(resource);
    const fqn = resource.fqn || resource.plr_definition?.fqn;

    if (!fqn) {
      // Fallback: just create a comment with the name
      return `# Resource: ${resource.name} (no FQN available)`;
    }

    // Extract module and class name from FQN
    // e.g., "pylabrobot.resources.corning.Cor_96_wellplate_360ul_Fb"
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
   * Uses the machine's actual backend FQN if available; falls back to simulation.
   */
  private generateMachineCode(machine: Machine): string {
    const varName = this.assetToVarName(machine);
    const category = machine.machine_category?.toLowerCase() || 'machine';
    // plr_definition.fqn contains the PLR backend class FQN (e.g., pylabrobot.plate_reading.clario_star_backend.CLARIOstarBackend)
    // machine.fqn is the instance FQN (e.g., machines.user.clariostar_abc123) - NOT the PLR class
    // TEMPORARY PATCH: Look for plr_backend in connection_info (added by sqlite.service for CLARIOstar testing)
    // Long term fix: use plr_definition.fqn populated from database sync
    const plrBackendFqn = machine.plr_definition?.fqn || machine.connection_info?.['plr_backend'];
    const isSimulated = machine.is_simulation_override;

    // Get FQNs from definition
    const frontendFqn = machine.plr_definition?.frontend_fqn;
    // backendFqn alias for consistency in new block
    const backendFqn = plrBackendFqn;

    // If we have both FQNs, generate clean code using them
    if (frontendFqn && backendFqn) {
      const frontendClass = frontendFqn.split('.').pop()!;
      const frontendModule = frontendFqn.substring(0, frontendFqn.lastIndexOf('.'));
      const backendClass = backendFqn.split('.').pop()!;
      const backendModule = backendFqn.substring(0, backendFqn.lastIndexOf('.'));

      if (isSimulated) {
        // For simulated, use SimulatorBackend (liquid handlers only for now)
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
        // Generic simulation fallback
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

      // Physical hardware with known frontend FQN
      // Special handling for PlateReader - injects WebSerial shim
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

      // Generic physical hardware
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

    // Fallback: category-based logic for legacy data without frontend_fqn
    // Generate code based on machine category
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
        // Physical liquid handler - extract backend class from FQN
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
        `# Note: Shim uses auto-discovery to find the port authorized by the UI`,
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
      // Generic machine - just create a comment
      return [
        `# Machine: ${machine.name}`,
        `# Category: ${category}`,
        `# FQN: ${plrBackendFqn || 'unknown'}`,
        `print("Warning: Could not determine specific frontend for category '${category}'")`,
        `print("Machine '${machine.name}' has been skipped or needs manual setup.")`,
        `# Note: Generic machine instantiation not yet supported`,
        `# Please instantiate manually using pylabrobot APIs`
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
  async insertAsset(type: 'machine' | 'resource', asset: Machine | Resource) {
    const varName = this.assetToVarName(asset);

    // If implementing physical machine, check prior authorization
    if (type === 'machine') {
      const machine = asset as Machine;
      // If it's a physical machine (not simulated)
      if (!machine.is_simulation_override) {
        try {
          // Check if we have any authorized ports
          // 1. Native WebSerial
          const nativePorts = await (navigator as any).serial?.getPorts() || [];
          console.log(`[DEBUG] Native Serial Ports: ${nativePorts.length}`);

          // 2. Check Raw WebUSB (The Source of Truth)
          const usbDevices = await (navigator as any).usb?.getDevices() || [];
          console.log(`[DEBUG] Raw WebUSB Devices (Permissions Granted): ${usbDevices.length}`);
          usbDevices.forEach((d: any, i: number) => {
            console.log(`   [${i}] VID: 0x${d.vendorId.toString(16)} | PID: 0x${d.productId.toString(16)} | Class: ${d.deviceClass}`);
          });

          // 3. Polyfill (WebUSB)
          const polyfill = (window as any).polyfillSerial;
          const polyfillPorts = polyfill ? await polyfill.getPorts() : [];
          console.log(`[DEBUG] Polyfill Mapped Ports: ${polyfillPorts.length}`);

          const ports = [...nativePorts, ...polyfillPorts];

          console.log(`[REPL] Checking authorized ports for ${machine.name}... Found: ${ports.length}`);
          if (ports.length > 0) {
            ports.forEach((p: any, i: number) => {
              const info = p.getInfo();
              console.log(`[REPL] Port ${i}: VID=${info.usbVendorId}, PID=${info.usbProductId}`);
            });
          }

          if (ports.length === 0) {
            console.warn('[REPL] No authorized ports found in UI context. Python shim might fail.');
            this.snackBar.open('Warning: No authorized device detected. Setup might fail.', 'OK', { duration: 5000 });
            // DO NOT RETURN. Let the code generate.
          }

          // Proceed to generate code regardless of port check...
          const backend = machine.connection_info ? (machine.connection_info['backend'] || machine.connection_info['plr_backend']) : null;
        } catch (err) {
          console.error('Failed to check hardware permissions:', err);
          // Proceed anyway? Or fail? Fail is safer.
          // In Pyodide environment, navigator.serial might not exist outside secure context, but we are in browser.
        }
      }
    }

    // Generate appropriate Python code
    let code: string;
    if (type === 'machine') {
      code = this.generateMachineCode(asset as Machine);
    } else {
      code = this.generateResourceCode(asset as Resource);
    }

    // Send code via BroadcastChannel
    try {
      const channel = new BroadcastChannel('praxis_repl');
      channel.postMessage({
        type: 'praxis:execute',
        code: code
      });
      // Close channel after sending to avoid leaks (it's lightweight to create)
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

