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
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatTooltipModule } from '@angular/material/tooltip';
import { finalize } from 'rxjs/operators';

import { ProtocolDefinition } from '@features/protocols/models/protocol.models';
import { ProtocolService } from '@features/protocols/services/protocol.service';
import { ExecutionService } from './services/execution.service';
import { ParameterConfigComponent } from './components/parameter-config/parameter-config.component';
import { ProtocolCardComponent } from './components/protocol-card/protocol-card.component';
import { ProtocolCardSkeletonComponent } from './components/protocol-card/protocol-card-skeleton.component';
import { DeckVisualizerComponent } from './components/deck-visualizer/deck-visualizer.component';
import { AppStore } from '@core/store/app.store';
import { ModeService } from '@core/services/mode.service';
import { DeckGeneratorService } from './services/deck-generator.service';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
// import { GuidedSetupComponent } from './components/guided-setup/guided-setup.component';
import { DeckSetupWizardComponent } from './components/deck-setup-wizard/deck-setup-wizard.component';
import { MachineSelectionComponent, MachineCompatibility } from './components/machine-selection/machine-selection.component';
import { HardwareDiscoveryButtonComponent } from '@shared/components/hardware-discovery-button/hardware-discovery-button.component';
import { WizardStateService } from './services/wizard-state.service';

const RECENTS_KEY = 'praxis_recent_protocols';
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
    MatBadgeModule,
    MatProgressSpinnerModule,
    MatSlideToggleModule,
    MatButtonToggleModule,
    MatTooltipModule,
    ParameterConfigComponent,
    ProtocolCardComponent,
    ProtocolCardSkeletonComponent,
    DeckVisualizerComponent,
    MachineSelectionComponent,
    HardwareDiscoveryButtonComponent,
    DeckSetupWizardComponent,
  ],
  template: `
    <div class="h-full flex flex-col p-6 max-w-screen-2xl mx-auto">
      <!-- Top Bar -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-3xl font-bold text-sys-text-primary mb-1">Execute Protocol</h1>
          <p class="text-sys-text-secondary">Configure and run experimental procedures</p>
        </div>
        
        <!-- Simulation Mode Toggle -->
        <div class="flex items-center gap-3">
           <mat-button-toggle-group
             hideSingleSelectionIndicator
             [value]="store.simulationMode()"
             (change)="store.setSimulationMode($event.value)"
             class="!rounded-full !border-[var(--theme-border)] !bg-[var(--mat-sys-surface-variant)] !overflow-hidden">
             <mat-button-toggle [value]="false" class="!px-4 !text-sm !font-medium" [class.!text-sys-text-primary]="!store.simulationMode()">Physical</mat-button-toggle>
             <mat-button-toggle [value]="true" class="!px-4 !text-sm !font-medium" [class.!text-primary]="store.simulationMode()">Simulation</mat-button-toggle>
           </mat-button-toggle-group>
        </div>
      </div>

      <!-- Main Content Surface -->
      <div class="bg-surface border border-[var(--theme-border)] rounded-3xl overflow-y-auto overflow-x-hidden backdrop-blur-xl flex-1 min-h-0 shadow-xl flex flex-col">
        <mat-stepper [linear]="true" #stepper class="!bg-transparent h-full flex flex-col">
          
          <!-- Step 1: Select Protocol -->
          <mat-step [stepControl]="protocolFormGroup" label="Select Protocol">
            <form [formGroup]="protocolFormGroup" class="h-full flex flex-col p-6">
              @if (selectedProtocol()) {
                <div class="flex flex-col h-full items-center justify-center gap-8 overflow-y-auto">
                  <div class="max-w-2xl w-full bg-surface-elevated border border-primary/30 rounded-3xl p-8 relative overflow-hidden group shadow-2xl">
                    <div class="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-50"></div>
                    
                    <div class="relative z-10 flex flex-col items-center text-center gap-4">
                      <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center shadow-lg shadow-primary/30 mb-2">
                        <mat-icon class="!w-8 !h-8 !text-[32px] text-white">science</mat-icon>
                      </div>
                      
                      <h2 class="text-3xl font-bold text-sys-text-primary mb-0">{{ selectedProtocol()?.name }}</h2>
                      <p class="text-lg text-sys-text-secondary max-w-lg">{{ selectedProtocol()?.description }}</p>
                      
                      <div class="flex gap-2 mt-2">
                          <span class="px-3 py-1 rounded-full bg-[var(--mat-sys-surface-variant)] border border-[var(--theme-border)] text-sys-text-secondary text-sm flex items-center gap-2">
                            <mat-icon class="!w-4 !h-4 !text-[16px]">category</mat-icon> {{ selectedProtocol()?.category || 'General' }}
                          </span>
                          <span class="px-3 py-1 rounded-full bg-[var(--mat-sys-surface-variant)] border border-[var(--theme-border)] text-sys-text-secondary text-sm flex items-center gap-2">
                            <mat-icon class="!w-4 !h-4 !text-[16px]">tag</mat-icon> {{ selectedProtocol()?.version }}
                          </span>
                      </div>

                      <div class="flex gap-4 mt-6 w-full justify-center">
                        <button mat-button class="!border-[var(--theme-border)] !text-sys-text-primary !rounded-xl !px-6 !py-6 w-40" (click)="clearProtocol()">
                          Change
                        </button>
                        <button mat-flat-button class="!bg-primary !text-white !rounded-xl !px-6 !py-6 !font-bold w-40 shadow-lg shadow-primary/25" matStepperNext>
                          Continue
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              } @else {
                <div class="flex h-full gap-6">
                  <!-- Sidebar Filters -->
                  <aside class="w-72 flex-shrink-0 flex flex-col gap-6">
                    <div class="bg-[var(--mat-sys-surface-variant)] border border-[var(--theme-border)] rounded-2xl p-4">
                      <div class="relative mb-4">
                        <mat-icon class="absolute left-3 top-1/2 -translate-y-1/2 text-sys-text-tertiary">search</mat-icon>
                        <input 
                          class="w-full bg-[var(--mat-sys-surface-variant)] border border-[var(--theme-border)] rounded-xl py-3 pl-10 pr-10 text-sys-text-primary placeholder-sys-text-tertiary focus:outline-none focus:border-primary/50 transition-colors"
                          [value]="searchQuery()" 
                          (input)="onSearchChange($event)" 
                          placeholder="Search protocols..."
                        >
                        @if (searchQuery()) {
                          <button class="absolute right-3 top-1/2 -translate-y-1/2 text-sys-text-tertiary hover:text-sys-text-primary" (click)="clearSearch()">
                            <mat-icon class="!w-5 !h-5 !text-[20px]">close</mat-icon>
                          </button>
                        }
                      </div>

                      <div class="flex flex-col gap-4">
                        @for (category of filterCategories(); track category.key) {
                          <div class="flex flex-col gap-2">
                            <h4 class="text-xs font-bold text-sys-text-tertiary uppercase tracking-wider px-2">{{ category.label }}</h4>
                            @for (option of category.options; track option.value) {
                              <button 
                                class="flex items-center justify-between w-full px-3 py-2 rounded-lg text-sm transition-all hover:bg-[var(--mat-sys-surface-variant)] text-left"
                                [class.bg-primary-10]="option.selected"
                                [class.text-primary]="option.selected"
                                [class.text-sys-text-secondary]="!option.selected"
                                (click)="toggleFilter(category.key, option.value)"
                              >
                                <span>{{ option.value }}</span>
                                <span class="bg-[var(--mat-sys-surface-variant)] px-1.5 py-0.5 rounded text-xs opacity-60">{{ option.count }}</span>
                              </button>
                            }
                          </div>
                        }
                      </div>
                    </div>
                  </aside>

                  <!-- Main Grid -->
                  <div class="flex-1 overflow-auto pr-2">
                    <!-- Recents -->
                    @if (recentProtocols().length > 0 && !searchQuery()) {
                      <div class="mb-8">
                        <h3 class="text-sys-text-primary text-lg font-medium mb-4 flex items-center gap-2">
                          <mat-icon class="text-primary/70">history</mat-icon> Recently Used
                        </h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          @for (protocol of recentProtocols(); track protocol.accession_id) {
                            <app-protocol-card
                              [protocol]="protocol"
                              [compact]="true"
                              (select)="selectProtocol($event)"
                              class="transform hover:-translate-y-1 transition-transform duration-300"
                            />
                          }
                        </div>
                      </div>
                    }

                    <!-- All Protocols -->
                    <div>
                      <h3 class="text-sys-text-primary text-lg font-medium mb-4 flex items-center gap-2">
                        <mat-icon class="text-primary/70">grid_view</mat-icon> All Protocols
                      </h3>
                      
                      @if (isLoading()) {
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          @for (i of [1, 2, 3, 4, 5, 6]; track i) {
                            <app-protocol-card-skeleton />
                          }
                        </div>
                      } @else if (filteredProtocols().length === 0) {
                        <div class="flex flex-col items-center justify-center py-20 text-sys-text-tertiary">
                          <mat-icon class="!w-16 !h-16 !text-[64px] opacity-20 mb-4">search_off</mat-icon>
                          <p class="text-lg">No protocols found matching your criteria</p>
                          <button mat-button class="mt-4 !text-primary" (click)="clearSearch()">Clear Filters</button>
                        </div>
                      } @else {
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pb-8">
                          @for (protocol of filteredProtocols(); track protocol.accession_id) {
                            <app-protocol-card
                              [protocol]="protocol"
                              (select)="selectProtocol($event)"
                              class="transform hover:-translate-y-1 transition-transform duration-300"
                            />
                          }
                        </div>
                      }
                    </div>
                  </div>
                </div>
              }
            </form>
          </mat-step>

          <!-- Step 2: Configure Parameters -->
          <mat-step [stepControl]="parametersFormGroup" label="Configure Parameters">
            <form [formGroup]="parametersFormGroup" class="h-full flex flex-col p-6">
              <div class="flex-1 overflow-y-auto max-w-3xl mx-auto w-full">
                <div class="bg-[var(--mat-sys-surface-variant)] border border-[var(--theme-border)] rounded-2xl p-8">
                  <h3 class="text-xl font-bold text-sys-text-primary mb-6 flex items-center gap-3">
                    <div class="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
                      <mat-icon>tune</mat-icon>
                    </div>
                    Protocol Parameters
                  </h3>
                  
                  <app-parameter-config
                    [protocol]="selectedProtocol()"
                    [formGroup]="parametersFormGroup">
                  </app-parameter-config>
                </div>
              </div>

              <div class="mt-6 flex justify-between border-t border-[var(--theme-border)] pt-6">
                <button mat-button matStepperPrevious class="!text-sys-text-secondary">Back</button>
                <button mat-flat-button color="primary" matStepperNext class="!rounded-xl !px-8 !py-6">Continue</button>
              </div>
            </form>
          </mat-step>

          <!-- Step 3: Machine Selection -->
          <mat-step [stepControl]="machineFormGroup" label="Select Machine">
            <div class="h-full flex flex-col p-6">
              <div class="flex-1 overflow-y-auto">
                <h3 class="text-xl font-bold text-sys-text-primary mb-6 flex items-center gap-3">
                   <div class="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
                     <mat-icon>precision_manufacturing</mat-icon>
                   </div>
                   Select Execution Machine
                   <span class="flex-1"></span>
                   <app-hardware-discovery-button></app-hardware-discovery-button>
                </h3>

                @if (isLoadingCompatibility()) {
                  <div class="flex flex-col items-center justify-center py-12">
                    <mat-spinner diameter="40"></mat-spinner>
                    <p class="mt-4 text-sys-text-tertiary">Checking compatibility...</p>
                  </div>
                } @else {
                  <app-machine-selection
                    [machines]="compatibilityData()"
                    [selected]="selectedMachine()"
                    (select)="onMachineSelect($event)"
                  ></app-machine-selection>
                }
              </div>

              <div class="mt-6 flex justify-between border-t border-[var(--theme-border)] pt-6">
                 <button mat-button matStepperPrevious class="!text-sys-text-secondary">Back</button>
                 <button mat-flat-button color="primary" matStepperNext [disabled]="!selectedMachine()" class="!rounded-xl !px-8 !py-6">Continue</button>
              </div>
            </div>
          </mat-step>

          <!-- Step 4: Deck Setup (Inline Wizard) -->
          <mat-step label="Deck Setup">
            <div class="h-full flex flex-col">
              @if (selectedProtocol()) {
                <app-deck-setup-wizard
                  [data]="{ protocol: selectedProtocol()!, deckResource: deckData()?.resource || null }"
                  (setupComplete)="onDeckSetupComplete()"
                  (setupSkipped)="onDeckSetupSkipped()">
                </app-deck-setup-wizard>
              } @else {
                <div class="flex flex-col items-center justify-center h-full text-sys-text-tertiary">
                  <mat-icon class="!w-16 !h-16 !text-[64px] opacity-20 mb-4">build</mat-icon>
                  <p>Select a protocol first to configure the deck.</p>
                </div>
              }
            </div>
          </mat-step>

          <!-- Step 4: Review & Run -->
          <mat-step label="Review & Run">
             <div class="h-full flex flex-col items-center p-6 text-center max-w-2xl mx-auto overflow-y-auto">
               <div class="my-auto w-full">
               <div class="w-24 h-24 rounded-full bg-primary/20 flex items-center justify-center text-primary mb-6 shadow-[0_0_30px_rgba(237,122,155,0.3)]">
                 <mat-icon class="!w-12 !h-12 !text-[48px]">rocket_launch</mat-icon>
               </div>
               
               <h2 class="text-4xl font-bold text-sys-text-primary mb-2">Ready to Launch</h2>
               <p class="text-xl text-sys-text-secondary mb-12">Confirm execution parameters before starting</p>
               
               <div class="grid grid-cols-2 gap-4 w-full mb-12">
                  <div class="bg-[var(--mat-sys-surface-variant)] border border-[var(--theme-border)] rounded-2xl p-6 flex flex-col items-center">
                     <span class="text-sys-text-tertiary text-sm uppercase tracking-wider font-bold mb-2">Protocol</span>
                     <span class="text-sys-text-primary text-lg font-medium">{{ selectedProtocol()?.name }}</span>
                  </div>
                                  <div class="bg-[var(--mat-sys-surface-variant)] border border-[var(--theme-border)] rounded-2xl p-6 flex flex-col items-center">
                     <span class="text-sys-text-tertiary text-sm uppercase tracking-wider font-bold mb-2">Mode</span>
                    <span class="text-lg font-medium" [class.text-primary]="store.simulationMode()" [class.text-blue-400]="!store.simulationMode()">
                      {{ store.simulationMode() ? 'Simulation' : 'Physical Run' }}
                    </span>
                 </div>
               </div>

               <div class="flex gap-4 w-full justify-center">
                  <button mat-button matStepperPrevious class="!border-[var(--theme-border)] !text-sys-text-secondary !rounded-xl !px-8 !py-6 w-40 border">Back</button>
                  
                  <!-- Schedule Button -->
                  <button mat-stroked-button color="primary" 
                    class="!rounded-xl !px-6 !py-6 !font-bold !text-lg w-48 !border-primary/50"
                    [disabled]="modeService.isBrowserMode() || isStartingRun() || executionService.isRunning()"
                    [matTooltip]="modeService.isBrowserMode() ? 'Scheduling is not supported in browser mode' : 'Schedule this protocol for later'"
                    matTooltipPosition="above">
                    <div class="flex items-center gap-2">
                      <mat-icon>calendar_today</mat-icon>
                      Schedule
                    </div>
                  </button>
                  
                  <button mat-raised-button class="!bg-gradient-to-r !from-green-500 !to-emerald-600 !text-white !rounded-xl !px-8 !py-6 !font-bold !text-lg w-64 shadow-lg shadow-green-500/20 hover:shadow-green-500/40 hover:-translate-y-0.5 transition-all" (click)="startRun()" 
                    [disabled]="isStartingRun() || executionService.isRunning() || !configuredAssets()">
                    @if (isStartingRun()) {
                      <mat-spinner diameter="24" class="mr-2"></mat-spinner>
                      Initializing...
                    } @else {
                      <div class="flex items-center gap-2">
                        <mat-icon>play_circle</mat-icon>
                        Start Execution
                      </div>
                    }
                  </button>
               </div>
             </div>
             </div>
          </mat-step>
        </mat-stepper>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      height: 100%;
    }
    
    /* Utilities */
    .bg-primary-10 { background-color: rgba(var(--primary-color-rgb), 0.1); }
    .text-white-70 { color: var(--theme-text-secondary); }
    .border-green-500-30 { border-color: rgba(74, 222, 128, 0.3) !important; }
    .bg-green-500-05 { background-color: rgba(74, 222, 128, 0.05) !important; }

    /* Fix Stepper Content Scrolling - MDC Classes */
    ::ng-deep .mat-horizontal-stepper-wrapper {
      flex: 1 1 auto;
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 0;
    }

    ::ng-deep .mat-horizontal-content-container {
      flex: 1 1 auto;
      height: 100%;
      min-height: 0;
      padding: 0 !important;
      overflow: hidden !important;
    }

    /* Active Step Content */
    ::ng-deep .mat-horizontal-stepper-content.mat-horizontal-stepper-content-current {
      height: 100% !important;
      display: flex !important;
      flex-direction: column !important;
      min-height: 0 !important;
      /* Ensure overflow is hidden on the container so inner scrollable div takes over */
      overflow: hidden !important;
      visibility: visible !important;
    }

    /* Inactive Step Content: Hide everything else */
    ::ng-deep .mat-horizontal-stepper-content:not(.mat-horizontal-stepper-content-current) {
      height: 0 !important;
      overflow: hidden !important;
      visibility: hidden !important;
      display: none !important;
    }

    /* Stepper Overrides */
    ::ng-deep .mat-step-header {
      border-radius: 12px;
      transition: background 0.2s;
      height: auto !important; /* Allow growing for wrapped text */
      padding: 8px 16px !important; /* Reduced padding */
      align-items: flex-start !important; /* Align top when wrapped */
    }
    ::ng-deep .mat-step-header:hover {
      background: var(--mat-sys-surface-variant);
    }
    ::ng-deep .mat-step-label {
      color: var(--theme-text-secondary) !important;
      font-size: 0.85rem !important; /* Smaller labels */
      white-space: normal !important; /* Allow wrapping */
      overflow: visible !important;
      line-height: 1.3 !important;
    }
    ::ng-deep .mat-step-label-selected {
      color: var(--theme-text-primary) !important;
      font-weight: 600 !important;
    }
    ::ng-deep .mat-step-icon {
      background-color: var(--mat-sys-surface-variant) !important;
      color: var(--theme-text-secondary) !important; /* Ensure number is readable */
    }
    ::ng-deep .mat-step-icon-selected {
      background-color: var(--primary-color) !important;
      color: white !important; /* White text on primary color */
    }
    ::ng-deep .mat-step-icon-content {
      /* Ensure the inner text (number) inherits the color correctly */
      color: inherit !important; 
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RunProtocolComponent implements OnInit {
  private _formBuilder = inject(FormBuilder);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private protocolService = inject(ProtocolService);
  public executionService = inject(ExecutionService);
  private deckGenerator = inject(DeckGeneratorService);
  private dialog = inject(MatDialog);
  public modeService = inject(ModeService);

  protocolFormGroup = this._formBuilder.group({ protocolId: [''] });
  machineFormGroup = this._formBuilder.group({ machineId: [''] });
  parametersFormGroup = this._formBuilder.group({});

  // Signals
  protocols = signal<ProtocolDefinition[]>([]);
  selectedProtocol = signal<ProtocolDefinition | null>(null);
  selectedMachine = signal<MachineCompatibility | null>(null);
  compatibilityData = signal<MachineCompatibility[]>([]);
  isLoadingCompatibility = signal(false);

  isLoading = signal(true);
  isStartingRun = signal(false);
  searchQuery = signal('');
  activeFilters = signal<Record<string, Set<string>>>({});
  configuredAssets = signal<Record<string, any> | null>(null);

  // Computed Deck Data
  deckData = computed(() => {
    const protocol = this.selectedProtocol();
    const machineCompat = this.selectedMachine();
    if (!protocol) return null;
    return this.deckGenerator.generateDeckForProtocol(
      protocol,
      this.configuredAssets() || undefined,
      machineCompat?.machine
    );
  });

  // Inject global store for simulation mode
  store = inject(AppStore);

  // WizardStateService for inline deck setup
  wizardState = inject(WizardStateService);

  /** Called when inline deck setup wizard completes */
  onDeckSetupComplete() {
    // Get asset map from wizard state
    const assetMap = this.wizardState.getAssetMap();
    this.configuredAssets.set(assetMap);
  }

  /** Called when inline deck setup wizard is skipped */
  onDeckSetupSkipped() {
    // Allow proceeding even if skipped
    this.configuredAssets.set({});
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
    this.loadCompatibility(protocol.accession_id);
  }

  loadCompatibility(protocolId: string) {
    this.isLoadingCompatibility.set(true);
    this.executionService.getCompatibility(protocolId)
      .pipe(finalize(() => this.isLoadingCompatibility.set(false)))
      .subscribe({
        next: (data) => {
          this.compatibilityData.set(data);
          // Auto-select if only one compatible machine
          const compatible = data.filter(d => d.compatibility.is_compatible);
          if (compatible.length === 1) {
            this.onMachineSelect(compatible[0]);
          }
        },
        error: (err) => console.error('Failed to load compatibility', err)
      });
  }

  onMachineSelect(machine: MachineCompatibility) {
    this.selectedMachine.set(machine);
    this.machineFormGroup.patchValue({ machineId: machine.machine.accession_id });
  }

  clearProtocol() {
    this.selectedProtocol.set(null);
    this.selectedMachine.set(null);
    this.compatibilityData.set([]);
    this.protocolFormGroup.reset();
    this.machineFormGroup.reset();
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
    // Validate parameters form AND ensure deck is configured
    if (protocol && this.parametersFormGroup.valid && !this.isStartingRun() && this.configuredAssets()) {
      this.isStartingRun.set(true);
      const runName = `${protocol.name} - ${new Date().toLocaleString()}`;

      // Merge parameters form values with configured assets
      // This ensures backend receives both standard parameters and asset mappings
      const params = {
        ...this.parametersFormGroup.value,
        ...this.configuredAssets()
      };

      this.executionService.startRun(
        protocol.accession_id,
        runName,
        params,
        this.store.simulationMode()  // Use global store
      ).pipe(
        finalize(() => this.isStartingRun.set(false))
      ).subscribe({
        next: () => {
          this.router.navigate(['live'], { relativeTo: this.route });
        },
        error: (err) => console.error('[RunProtocol] Failed to start run:', err)
      });
    }
  }
}