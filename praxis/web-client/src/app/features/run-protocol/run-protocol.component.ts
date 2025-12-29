import { Component, ChangeDetectionStrategy, inject, signal, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatStepperModule } from '@angular/material/stepper';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatBadgeModule } from '@angular/material/badge';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { finalize } from 'rxjs/operators';

import { ProtocolDefinition } from '@features/protocols/models/protocol.models';
import { ProtocolService } from '@features/protocols/services/protocol.service';
import { ExecutionService } from './services/execution.service';
import { ParameterConfigComponent } from './components/parameter-config/parameter-config.component';
import { ProtocolCardComponent } from './components/protocol-card/protocol-card.component';
import { ProtocolCardSkeletonComponent } from './components/protocol-card/protocol-card-skeleton.component';
import { DeckVisualizerComponent } from './components/deck-visualizer/deck-visualizer.component';
import { AppStore } from '@core/store/app.store';
import { DeckGeneratorService } from './services/deck-generator.service';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { GuidedSetupComponent } from './components/guided-setup/guided-setup.component';

const RECENTS_KEY = 'pylabpraxis_recent_protocols';
const MAX_RECENTS = 5;

interface FilterOption {
  value: string;
  count: number;
  selected: boolean;
}

interface FilterCategory {
  key: string;
  label: string;
  options: FilterOption[];
  expanded: boolean;
}

@Component({
  selector: 'app-run-protocol',
  standalone: true,
  imports: [
    CommonModule,
    MatStepperModule,
    MatButtonModule,
    MatIconModule,
    FormsModule,
    ReactiveFormsModule,
    RouterLink,
    MatFormFieldModule,
    MatInputModule,
    MatExpansionModule,
    MatCheckboxModule,
    MatBadgeModule,
    MatProgressSpinnerModule,
    MatSlideToggleModule,
    ParameterConfigComponent,
    ProtocolCardComponent,
    ProtocolCardSkeletonComponent,
    DeckVisualizerComponent,
  ],
  template: `
    <div class="run-protocol-container">
      <mat-stepper [linear]="true" #stepper>
        <!-- Step 1: Select Protocol -->
        <mat-step [stepControl]="protocolFormGroup" label="Select Protocol">
          <form [formGroup]="protocolFormGroup">
            @if (selectedProtocol()) {
              <div class="selected-protocol-banner">
                <mat-icon>check_circle</mat-icon>
                <div class="banner-content">
                  <h3>{{ selectedProtocol()?.name }}</h3>
                  <p>{{ selectedProtocol()?.description }}</p>
                  <button mat-raised-button color="primary"
                    [disabled]="!configuredAssets() || isStartingRun() || executionService.isRunning()"
                    (click)="startRun()">
                  <mat-icon>play_arrow</mat-icon> Run Protocol
                </button>
                </div>
                <div class="actions" [class.pulse-action]="!configuredAssets()">
                  <button mat-stroked-button color="primary" (click)="openGuidedSetup()">
                    <mat-icon>settings_suggest</mat-icon> Configure Deck
                  </button>
                </div>
                <button mat-button (click)="clearProtocol()">
                  <mat-icon>close</mat-icon> Change
                </button>
              </div>
            } @else {
              <div class="protocol-selection-view">
                <!-- Header -->
                <div class="selection-header">
                  <h2>Select a Protocol</h2>
                  <button mat-stroked-button routerLink="/app/protocols">
                    <mat-icon>library_books</mat-icon> Go to Library
                  </button>
                </div>

                <!-- Recents Section -->
                @if (isLoading() || recentProtocols().length > 0) {
                  <section class="recents-section">
                    <h3><mat-icon>history</mat-icon> Jump Back In</h3>
                    <div class="recents-carousel">
                      @if (isLoading()) {
                        @for (i of [1, 2, 3]; track i) {
                          <app-protocol-card-skeleton [compact]="true" />
                        }
                      } @else {
                        @for (protocol of recentProtocols(); track protocol.accession_id) {
                          <app-protocol-card
                            [protocol]="protocol"
                            [compact]="true"
                            (select)="selectProtocol($event)"
                          />
                        }
                      }
                    </div>
                  </section>
                }

                <!-- Main Protocol List -->
                <section class="all-protocols-section">
                  <h3><mat-icon>folder_open</mat-icon> All Protocols</h3>
                  <div class="protocols-layout">
                    <!-- Sidebar Filters -->
                    <aside class="filters-sidebar">
                      <!-- Search -->
                      <mat-form-field appearance="outline" class="search-field">
                        <mat-label>Search Protocols</mat-label>
                        <input matInput [value]="searchQuery()" (input)="onSearchChange($event)" placeholder="e.g. dilution, transfer">
                        <mat-icon matPrefix>search</mat-icon>
                        @if (searchQuery()) {
                          <button matSuffix mat-icon-button (click)="clearSearch()">
                            <mat-icon>close</mat-icon>
                          </button>
                        }
                      </mat-form-field>

                      <!-- Filter Panels -->
                      <mat-accordion>
                        @for (category of filterCategories(); track category.key) {
                          <mat-expansion-panel [expanded]="category.expanded">
                            <mat-expansion-panel-header>
                              <mat-panel-title>
                                {{ category.label }}
                                @if (getSelectedCount(category) > 0) {
                                  <span class="filter-badge">{{ getSelectedCount(category) }}</span>
                                }
                              </mat-panel-title>
                            </mat-expansion-panel-header>
                            <div class="filter-options">
                              @for (option of category.options; track option.value) {
                                <mat-checkbox
                                  [checked]="option.selected"
                                  (change)="toggleFilter(category.key, option.value)"
                                >
                                  {{ option.value }} <span class="count">({{ option.count }})</span>
                                </mat-checkbox>
                              }
                            </div>
                          </mat-expansion-panel>
                        }
                      </mat-accordion>
                    </aside>

                    <!-- Protocol Grid -->
                    <div class="protocols-grid">
                      @if (isLoading()) {
                        @for (i of [1, 2, 3, 4, 5, 6]; track i) {
                          <app-protocol-card-skeleton />
                        }
                      } @else if (filteredProtocols().length === 0) {
                        <div class="empty-state">
                          <mat-icon>search_off</mat-icon>
                          <h4>No protocols found</h4>
                          <p>Try adjusting your search or filters.</p>
                        </div>
                      } @else {
                        @for (protocol of filteredProtocols(); track protocol.accession_id) {
                          <app-protocol-card
                            [protocol]="protocol"
                            (select)="selectProtocol($event)"
                          />
                        }
                      }
                    </div>
                  </div>
                </section>
              </div>
            }
            <div class="actions">
              <button mat-button matStepperNext [disabled]="!selectedProtocol()">Next</button>
            </div>
          </form>
        </mat-step>

        <!-- Step 2: Configure Parameters -->
        <mat-step [stepControl]="parametersFormGroup" label="Configure Parameters">
          <form [formGroup]="parametersFormGroup">
            <app-parameter-config
              [protocol]="selectedProtocol()"
              [formGroup]="parametersFormGroup">
            </app-parameter-config>
            <div class="actions">
              <button mat-button matStepperPrevious>Back</button>
              <button mat-button matStepperNext>Next</button>
            </div>
          </form>
        </mat-step>

        <!-- Step 3: Deck Configuration -->
        <mat-step label="Deck Configuration">
          <div class="deck-config-step">
            <app-deck-visualizer [layoutData]="deckData()"></app-deck-visualizer>
            
            <div class="deck-info">
              <h3><mat-icon>info</mat-icon> Pre-Run Deck Check</h3>
              <p>Ensure resources are placed correctly as shown on the left.</p>
              
              <div class="deck-status" [class.ready]="!!configuredAssets()">
                 <mat-icon>{{ configuredAssets() ? 'check_circle' : 'warning' }}</mat-icon>
                 <span>{{ configuredAssets() ? 'Deck Configured' : 'Configuration Required' }}</span>
              </div>

              <div class="actions" [class.pulse-action]="!configuredAssets()">
                  <button mat-stroked-button color="primary" (click)="openGuidedSetup()">
                    <mat-icon>settings_suggest</mat-icon> Configure Deck
                  </button>
              </div>
            </div>
          </div>
          <div class="actions">
            <button mat-button matStepperPrevious>Back</button>
            <button mat-button matStepperNext>Next</button>
          </div>
        </mat-step>

        <!-- Step 4: Review & Run -->
        <mat-step label="Review & Run">
          <h3>Ready to Run</h3>
          <p>Protocol: {{ selectedProtocol()?.name }}</p>
          <p>Parameters Configured: {{ parametersFormGroup.valid ? 'Yes' : 'No' }}</p>
          <div class="actions">
            <button mat-button matStepperPrevious>Back</button>
            <button mat-raised-button color="primary" (click)="startRun()" [disabled]="isStartingRun()">
              <mat-icon *ngIf="!isStartingRun()">play_arrow</mat-icon>
              <mat-spinner *ngIf="isStartingRun()" diameter="20" class="button-spinner"></mat-spinner>
              {{ isStartingRun() ? 'Starting...' : 'Start Execution' }}
            </button>
          </div>
        </mat-step>
      </mat-stepper>
    </div>
  `,
  styles: [`
    .run-protocol-container {
      padding: 24px;
      height: 100%;
      overflow-y: auto;
    }
    .actions {
      margin-top: 24px;
      display: flex;
      gap: 8px;
    }
    .button-spinner {
      margin-right: 8px;
    }

    /* Deck Config Step */
    .deck-config-step {
      display: grid;
      grid-template-columns: 1fr 300px;
      gap: 24px;
      margin-bottom: 24px;
      min-height: 400px;
    }
    .deck-info {
        flex: 0 0 300px;
        padding: 24px;
        background: var(--sys-surface-container-high);
        border-radius: 12px;
    }

    .deck-status {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 16px 0;
        padding: 12px;
        border-radius: 8px;
        background: var(--sys-error-container);
        color: var(--sys-on-error-container);
        font-weight: 500;
    }

    .deck-status.ready {
        background: var(--sys-primary-container);
        color: var(--sys-on-primary-container);
    }
    
    .actions {
        margin-top: 16px;
    }

    @keyframes subtle-pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(var(--sys-primary-rgb), 0.7); }
        50% { transform: scale(1.02); box-shadow: 0 0 0 6px rgba(var(--sys-primary-rgb), 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(var(--sys-primary-rgb), 0); }
    }

    .pulse-action button {
        animation: subtle-pulse 2s infinite;
    }
    .deck-info h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 0;
    }
    .resource-summary {
      margin-top: 24px;
    }
    .resource-summary ul {
      margin: 8px 0;
      padding-left: 20px;
    }
    .resource-summary li {
      margin-bottom: 4px;
      font-size: 0.9em;
      color: var(--sys-on-surface-variant);
    }

    /* Selected Protocol Banner */
    .selected-protocol-banner {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 16px 24px;
      background: var(--sys-primary-container);
      color: var(--sys-on-primary-container);
      border-radius: 12px;
      margin-bottom: 16px;
    }
    .selected-protocol-banner mat-icon {
      font-size: 32px;
      width: 32px;
      height: 32px;
      color: var(--sys-primary);
    }
    .selected-protocol-banner .banner-content {
      flex: 1;
    }
    .selected-protocol-banner h3 {
      margin: 0;
    }
    .selected-protocol-banner p {
      margin: 4px 0 0;
      opacity: 0.8;
    }

    /* Selection View */
    .protocol-selection-view {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    .selection-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .selection-header h2 {
      margin: 0;
    }

    /* Recents Section */
    .recents-section h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 16px;
    }
    .recents-carousel {
      display: flex;
      gap: 16px;
      overflow-x: auto;
      padding-bottom: 8px;
    }

    /* All Protocols Section */
    .all-protocols-section h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 16px;
    }
    .protocols-layout {
      display: grid;
      grid-template-columns: 280px 1fr;
      gap: 24px;
    }

    /* Filters Sidebar */
    .filters-sidebar {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .search-field {
      width: 100%;
    }
    .filter-options {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .filter-options .count {
      opacity: 0.6;
      font-size: 0.85em;
    }
    .filter-badge {
      background: var(--sys-primary);
      color: var(--sys-on-primary);
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.75em;
      margin-left: 8px;
    }

    /* Protocol Grid */
    .protocols-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 16px;
    }

    /* Empty State */
    .empty-state {
      grid-column: 1 / -1;
      text-align: center;
      padding: 48px;
      color: var(--sys-on-surface-variant);
    }
    .empty-state mat-icon {
      font-size: 64px;
      width: 64px;
      height: 64px;
      opacity: 0.5;
    }
    .empty-state h4 {
      margin: 16px 0 8px;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .protocols-layout {
        grid-template-columns: 1fr;
      }
      .filters-sidebar {
        order: -1;
      }
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RunProtocolComponent implements OnInit {
  private _formBuilder = inject(FormBuilder);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private protocolService = inject(ProtocolService);
  private executionService = inject(ExecutionService);
  private deckGenerator = inject(DeckGeneratorService);
  private dialog = inject(MatDialog);

  protocolFormGroup = this._formBuilder.group({ protocolId: [''] });
  parametersFormGroup = this._formBuilder.group({});

  // Signals
  protocols = signal<ProtocolDefinition[]>([]);
  selectedProtocol = signal<ProtocolDefinition | null>(null);
  isLoading = signal(true);
  isStartingRun = signal(false);
  searchQuery = signal('');
  activeFilters = signal<Record<string, Set<string>>>({});
  configuredAssets = signal<Record<string, any> | null>(null);

  // Computed Deck Data
  deckData = computed(() => {
    const protocol = this.selectedProtocol();
    if (!protocol) return null;
    return this.deckGenerator.generateDeckForProtocol(protocol, this.configuredAssets() || undefined);
  });

  // Inject global store for simulation mode
  store = inject(AppStore);

  openGuidedSetup() {
    const protocol = this.selectedProtocol();
    if (!protocol) return;

    const dialogRef = this.dialog.open(GuidedSetupComponent, {
      data: { protocol },
      width: '600px',
      disableClose: true
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result && result.assetMap) {
        this.configuredAssets.set(result.assetMap);
      }
    });
  }

  // Computed
  recentProtocols = computed(() => {
    const recentIds = this.getRecentIds();
    const allProtocols = this.protocols();
    return recentIds
      .map(id => allProtocols.find(p => p.accession_id === id))
      .filter((p): p is ProtocolDefinition => p !== undefined);
  });

  filterCategories = computed<FilterCategory[]>(() => {
    const allProtocols = this.protocols();
    const active = this.activeFilters();

    // Build category filter
    const categoryMap = new Map<string, number>();
    allProtocols.forEach(p => {
      const cat = p.category || 'Uncategorized';
      categoryMap.set(cat, (categoryMap.get(cat) || 0) + 1);
    });

    const categoryOptions: FilterOption[] = Array.from(categoryMap.entries())
      .map(([value, count]) => ({
        value,
        count,
        selected: active['category']?.has(value) || false,
      }))
      .sort((a, b) => b.count - a.count);

    // Build is_top_level filter
    const topLevelCount = allProtocols.filter(p => p.is_top_level).length;
    const subCount = allProtocols.length - topLevelCount;
    const typeOptions: FilterOption[] = [
      { value: 'Top Level', count: topLevelCount, selected: active['type']?.has('Top Level') || false },
      { value: 'Sub-Protocol', count: subCount, selected: active['type']?.has('Sub-Protocol') || false },
    ].filter(o => o.count > 0);

    return [
      { key: 'category', label: 'Category', options: categoryOptions, expanded: true },
      { key: 'type', label: 'Type', options: typeOptions, expanded: false },
    ].filter(c => c.options.length > 0);
  });

  filteredProtocols = computed(() => {
    let result = this.protocols();
    const query = this.searchQuery().toLowerCase().trim();
    const active = this.activeFilters();

    // Apply search filter
    if (query) {
      result = result.filter(p =>
        p.name.toLowerCase().includes(query) ||
        (p.description?.toLowerCase().includes(query)) ||
        (p.category?.toLowerCase().includes(query))
      );
    }

    // Apply category filter
    if (active['category']?.size) {
      result = result.filter(p => active['category'].has(p.category || 'Uncategorized'));
    }

    // Apply type filter
    if (active['type']?.size) {
      result = result.filter(p => {
        const isTop = active['type'].has('Top Level') && p.is_top_level;
        const isSub = active['type'].has('Sub-Protocol') && !p.is_top_level;
        return isTop || isSub;
      });
    }

    return result;
  });

  ngOnInit() {
    this.loadProtocols();

    // Check for pre-selected protocol from query params
    this.route.queryParams.subscribe(params => {
      const protocolId = params['protocolId'];
      if (protocolId && this.protocols().length > 0) {
        this.loadProtocolById(protocolId);
      }
    });
  }

  loadProtocols() {
    this.protocolService.getProtocols().pipe(
      finalize(() => this.isLoading.set(false))
    ).subscribe({
      next: (protocols) => {
        this.protocols.set(protocols);
        // Check for pre-selected from query
        const protocolId = this.route.snapshot.queryParams['protocolId'];
        if (protocolId) {
          this.loadProtocolById(protocolId);
        }
      },
      error: (err) => console.error('Failed to load protocols', err)
    });
  }

  loadProtocolById(id: string) {
    const found = this.protocols().find(p => p.accession_id === id);
    if (found) {
      this.selectProtocol(found);
    }
  }

  selectProtocol(protocol: ProtocolDefinition) {
    this.selectedProtocol.set(protocol);
    this.configuredAssets.set(null); // Reset deck config
    this.parametersFormGroup = this._formBuilder.group({});

    // Create form controls for parameters
    if (protocol.parameters) {
      // This block's content was not provided in the instruction,
      // so it remains empty as per the instruction's snippet.
    }
    this.protocolFormGroup.patchValue({ protocolId: protocol.accession_id });
    this.addToRecents(protocol.accession_id);
  }

  clearProtocol() {
    this.selectedProtocol.set(null);
    this.protocolFormGroup.reset();
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { protocolId: null },
      queryParamsHandling: 'merge'
    });
  }

  // Recents Management
  private getRecentIds(): string[] {
    try {
      const stored = localStorage.getItem(RECENTS_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  private addToRecents(id: string) {
    const recents = this.getRecentIds().filter(r => r !== id);
    recents.unshift(id);
    localStorage.setItem(RECENTS_KEY, JSON.stringify(recents.slice(0, MAX_RECENTS)));
  }

  // Search & Filters
  onSearchChange(event: Event) {
    const input = event.target as HTMLInputElement;
    this.searchQuery.set(input.value);
  }

  clearSearch() {
    this.searchQuery.set('');
  }

  toggleFilter(categoryKey: string, value: string) {
    const current = this.activeFilters();
    const categorySet = new Set(current[categoryKey] || []);

    if (categorySet.has(value)) {
      categorySet.delete(value);
    } else {
      categorySet.add(value);
    }

    this.activeFilters.set({
      ...current,
      [categoryKey]: categorySet
    });
  }

  getSelectedCount(category: FilterCategory): number {
    return category.options.filter(o => o.selected).length;
  }

  // Execution
  startRun() {
    const protocol = this.selectedProtocol();
    if (protocol && this.parametersFormGroup.valid && !this.isStartingRun()) {
      this.isStartingRun.set(true);
      const runName = `${protocol.name} - ${new Date().toLocaleString()}`;
      const params = this.parametersFormGroup.value;

      this.executionService.startRun(
        protocol.accession_id,
        runName,
        params,
        this.store.simulationMode()  // Use global store
      ).pipe(
        finalize(() => this.isStartingRun.set(false))
      ).subscribe({
        next: (res) => {
          console.log('Run started', res);
          this.router.navigate(['live'], { relativeTo: this.route });
        },
        error: (err) => console.error('Failed to start run', err)
      });
    }
  }
}