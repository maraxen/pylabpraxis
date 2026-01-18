import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { AbstractControl, FormArray, FormBuilder, FormGroup, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatStepperModule } from '@angular/material/stepper';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PraxisSelectComponent, SelectOption } from '@shared/components/praxis-select/praxis-select.component';
import { ModeService } from '../../../core/services/mode.service';
import { MachineBackendDefinition, MachineDefinition, MachineFrontendDefinition, MachineStatus } from '../models/asset.models';
import { AssetService } from '../services/asset.service';
import { DynamicCapabilityFormComponent } from './dynamic-capability-form.component';

// Custom validator for JSON string
const jsonValidator = (control: AbstractControl): ValidationErrors | null => {
  if (!control.value) {
    return null;
  }
  try {
    JSON.parse(control.value);
  } catch (e) {
    return { invalidJson: true };
  }
  return null;
};

interface Step {
  label: string;
  completed: boolean;
}

interface FrontendType {
  fqn: string;
  label: string;
  icon: string;
  backendCount: number;
}

@Component({
  selector: 'app-machine-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatAutocompleteModule,
    MatChipsModule,
    MatIconModule,
    MatDividerModule,
    MatStepperModule,
    MatCardModule,
    MatTooltipModule,
    DynamicCapabilityFormComponent,
    PraxisSelectComponent
  ],
  template: `
    <div class="h-full flex flex-col max-h-[85vh]">
      <h2 mat-dialog-title class="flex-shrink-0">Add New Machine</h2>

      <mat-dialog-content class="flex-grow overflow-auto">
        <!-- Progress Steps -->
        <div class="mb-6 flex items-center justify-between px-2 stepper">
          @for (step of steps; track step; let i = $index) {
            <div
              class="flex items-center gap-2 text-sm"
              [class.cursor-pointer]="isStepValid(i) || i < currentStep"
              [class.step-text-active]="currentStep === i"
              [class.step-text-inactive]="currentStep !== i && !step.completed"
              [class.step-text-completed]="step.completed"
              [class.font-bold]="currentStep === i"
              (click)="goToStep(i)">
              <div class="w-7 h-7 rounded-full flex items-center justify-center border transition-all"
                [class.step-circle-active]="currentStep === i"
                [class.step-circle-inactive]="currentStep !== i && !step.completed"
                [class.step-circle-completed]="step.completed">
                @if (step.completed) {
                  <mat-icon class="text-xs !w-4 !h-4 flex items-center justify-center">check</mat-icon>
                }
                @if (!step.completed) {
                  <span>{{ i + 1 }}</span>
                }
              </div>
              <span class="hidden sm:inline">{{ step.label }}</span>
              @if (i < steps.length - 1) {
                <div class="h-[1px] w-6 ml-2 sys-divider"></div>
              }
            </div>
          }
        </div>

        <form [formGroup]="form" class="flex flex-col gap-4 py-2">

          <!-- STEP 1: Machine Type (Frontend) Selection -->
          @if (currentStep === 0) {
            <div class="fade-in flex flex-col gap-5">
              <div>
                <h3 class="text-lg font-medium mb-3">Choose Machine Type</h3>
                <p class="text-sm sys-text-secondary mb-4">Select the type of machine you want to add.</p>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                  @for (frontend of frontendDefinitions; track frontend.accession_id) {
                    <button type="button"
                      class="selection-card"
                      [class.card-selected]="selectedFrontendId === frontend.accession_id"
                      (click)="selectFrontend(frontend)">
                      <div class="flex items-center gap-3 w-full">
                        <div class="icon-chip"><mat-icon>{{ getFrontendIcon(frontend) }}</mat-icon></div>
                        <div class="flex flex-col items-start min-w-0">
                          <span class="font-medium truncate w-full">{{ getFrontendLabel(frontend) }}</span>
                          <span class="text-[10px] sys-text-secondary truncate w-full">{{ frontend.fqn }}</span>
                        </div>
                      </div>
                    </button>
                  }
                </div>
              </div>
            </div>
          }

          <!-- STEP 2: Backend Selection -->
          @if (currentStep === 1) {
            <div class="fade-in flex flex-col gap-4">
              @if (!selectedFrontendId) {
                <div class="muted-box text-center py-8 flex flex-col items-center justify-center gap-2">
                  <mat-icon class="!text-4xl opacity-20 mb-2">arrow_back</mat-icon>
                  <p>Please select a machine type first</p>
                  <button mat-stroked-button (click)="goBack()">Go Back</button>
                </div>
              } @else {
                <div class="flex items-center gap-2 mb-1">
                  <button mat-icon-button (click)="goBack()"><mat-icon>arrow_back</mat-icon></button>
                  <h3 class="text-lg font-medium">Select Backend</h3>
                </div>
                <p class="text-sm sys-text-secondary">Choose the hardware driver for your {{ getSelectedFrontendLabel() }}. Simulator backends are available for testing without hardware.</p>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[300px] overflow-y-auto pr-1">
                  @for (backend of compatibleBackends; track backend.accession_id) {
                    <button type="button"
                      class="selection-card definition-card"
                      [class.card-selected]="selectedBackend?.accession_id === backend.accession_id"
                      (click)="selectBackend(backend)">
                      <div class="flex items-start gap-3 w-full">
                        <div class="icon-chip subtle">
                          <mat-icon>{{ isSimulatedBackend(backend) ? 'terminal' : 'memory' }}</mat-icon>
                        </div>
                        <div class="flex flex-col items-start min-w-0">
                          <div class="flex items-center gap-2 w-full">
                            <span class="font-medium truncate" 
                                   [matTooltip]="backend.name || ''" 
                                   matTooltipShowDelay="300">{{ getTruncatedName(backend.name || '') }}</span>
                            @if (isSimulatedBackend(backend)) {
                              <span class="simulated-chip">Simulated</span>
                            }
                            @if (selectedBackend?.accession_id === backend.accession_id) {
                              <mat-icon class="text-primary !text-sm ml-auto">check_circle</mat-icon>
                            }
                          </div>
                          <span class="text-xs sys-text-secondary truncate">
                            {{ backend.manufacturer || 'Unknown vendor' }}
                          </span>
                          <span class="text-[11px] text-sys-text-tertiary fqn-wrap"
                                [matTooltip]="backend.fqn"
                                matTooltipShowDelay="300">{{ getShortFqn(backend.fqn || '') }}</span>
                        </div>
                      </div>
                    </button>
                  }
                  @if (compatibleBackends.length === 0) {
                    <div class="muted-box col-span-2">No backends available for this machine type.</div>
                  }
                </div>
              }
            </div>
          }

          <!-- STEP 3: Configuration -->
          @if (currentStep === 2) {
            <div class="fade-in flex flex-col gap-4">
              <div class="flex items-center gap-2 mb-1">
                <button mat-icon-button (click)="goBack()"><mat-icon>arrow_back</mat-icon></button>
                <h3 class="text-lg font-medium">Configure Machine</h3>
              </div>

              <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div class="section-card">
                  <div class="section-header">Instance Details</div>
                  <mat-form-field appearance="outline" class="w-full">
                    <mat-label>Instance Name</mat-label>
                    <input matInput formControlName="name" placeholder="e.g. Robot 1">
                  </mat-form-field>

                  <mat-form-field appearance="outline" class="w-full">
                    <mat-label>Location (Optional)</mat-label>
                    <input matInput formControlName="location_label" placeholder="e.g. Bench A">
                  </mat-form-field>

                  <div class="mb-4">
                    <label class="text-xs font-medium text-sys-text-secondary mb-1 block">Initial Status</label>
                    <app-praxis-select
                      placeholder="Initial Status"
                      formControlName="status"
                      [options]="statusOptions"
                    ></app-praxis-select>
                  </div>
                </div>

                <div class="section-card" [class.opacity-60]="form.get('backend_driver')?.value === 'sim'">
                  <div class="section-header">Connection</div>
                  @if (shouldShowConnectionConfig()) {
                    <app-dynamic-capability-form
                      [config]="$any(selectedBackend!.connection_config)"
                      (valueChange)="updateConnectionInfo($event)">
                    </app-dynamic-capability-form>
                  } @else if (form.get('backend_driver')?.value !== 'sim') {
                    <div class="muted-box mb-3">No structured connection schema; enter JSON if required.</div>
                  } @else {
                    <div class="muted-box">Simulated mode — no connection required.</div>
                  }

                  @if (form.get('backend_driver')?.value !== 'sim') {
                    <button mat-stroked-button type="button" class="w-full justify-between" (click)="showAdvancedConnectionJson = !showAdvancedConnectionJson">
                      <span>Advanced JSON</span>
                      <mat-icon>{{ showAdvancedConnectionJson ? 'expand_less' : 'expand_more' }}</mat-icon>
                    </button>
                    @if (showAdvancedConnectionJson) {
                      <mat-form-field appearance="outline" class="w-full mt-3">
                        <mat-label>Connection Info (JSON)</mat-label>
                        <textarea matInput formControlName="connection_info" placeholder='{"host": "127.0.0.1", "port": 3000}' rows="3"></textarea>
                        @if (form.get('connection_info')?.hasError('invalidJson')) {
                          <mat-error>Invalid JSON format</mat-error>
                        }
                      </mat-form-field>
                    }
                  }
                </div>
              </div>

              <div class="section-card">
                <div class="section-header">Capabilities</div>
                @if (selectedFrontend?.capabilities_config) {
                  <app-dynamic-capability-form
                    [config]="$any(selectedFrontend!.capabilities_config)"
                    (valueChange)="updateCapabilities($event)">
                  </app-dynamic-capability-form>
                } @else if (selectedFrontend) {
                  <div class="muted-box mb-3">No capability schema for this frontend. Use generic fields or JSON override.</div>
                  <div class="flex flex-col gap-2">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium">Generic capability flags</span>
                      <button mat-stroked-button type="button" (click)="addCapabilityPair()" class="!py-1">Add field</button>
                    </div>
                    <div class="flex flex-col gap-2">
                      @for (pair of genericCapabilities.controls; track pair; let idx = $index) {
                        <div class="grid grid-cols-5 gap-2 items-center">
                          <mat-form-field appearance="outline" class="col-span-2">
                            <mat-label>Key</mat-label>
                            <input matInput [formControl]="$any(pair.get('key'))" (input)="syncGenericCapabilities()" placeholder="e.g. has_iswap">
                          </mat-form-field>
                          <mat-form-field appearance="outline" class="col-span-2">
                            <mat-label>Value</mat-label>
                            <input matInput [formControl]="$any(pair.get('value'))" (input)="syncGenericCapabilities()" placeholder="true">
                          </mat-form-field>
                          <button mat-icon-button color="warn" class="col-span-1" (click)="removeCapabilityPair(idx)" [disabled]="genericCapabilities.length === 1">
                            <mat-icon>delete</mat-icon>
                          </button>
                        </div>
                      }
                    </div>
                  </div>
                } @else {
                  <div class="muted-box">Simulated mode — default capabilities used.</div>
                }

                @if (selectedFrontend) {
                  <button mat-stroked-button type="button" class="w-full justify-between mt-3" (click)="showAdvancedCapabilitiesJson = !showAdvancedCapabilitiesJson">
                    <span>Advanced JSON</span>
                    <mat-icon>{{ showAdvancedCapabilitiesJson ? 'expand_less' : 'expand_more' }}</mat-icon>
                  </button>
                  @if (showAdvancedCapabilitiesJson) {
                    <mat-form-field appearance="outline" class="w-full mt-3">
                      <mat-label>User Configured Capabilities (JSON)</mat-label>
                      <textarea matInput formControlName="user_configured_capabilities" placeholder='{"has_iswap": true, "has_core96": true}' rows="3"></textarea>
                      @if (form.get('user_configured_capabilities')?.hasError('invalidJson')) {
                        <mat-error>Invalid JSON format</mat-error>
                      }
                    </mat-form-field>
                  }
                }
              </div>
            </div>
          }

        </form>
      </mat-dialog-content>

      <mat-dialog-actions align="end" class="flex-shrink-0 border-t sys-border p-4 z-10">
        <button mat-button mat-dialog-close>Cancel</button>

        @if (currentStep < steps.length - 1) {
          <button mat-flat-button color="primary"
            [disabled]="!canProceed()"
            (click)="nextStep()">
            Next
          </button>
        }

        @if (currentStep === steps.length - 1) {
          <button mat-flat-button color="primary"
            [disabled]="form.invalid"
            (click)="save()">
            Finish
          </button>
        }
      </mat-dialog-actions>
    </div>
    `,
  styles: [`
    .fade-in { animation: fadeIn 0.25s ease-in-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

    .stepper { background: linear-gradient(90deg, var(--mat-sys-surface) 0%, var(--mat-sys-surface-container-low, #eef2f7) 100%); border-radius: 12px; padding: 12px 16px; border: 1px solid var(--mat-sys-outline-variant, #c4c7c5); }
    .step-text-active { color: var(--primary-color, var(--mat-sys-primary, var(--primary-color))); }
    .step-text-completed { color: var(--primary-color, var(--mat-sys-primary, var(--primary-color))); }
    .step-text-inactive { color: var(--mat-sys-on-surface-variant, #9aa0a6); }
    .step-circle-active { border-color: var(--primary-color, var(--mat-sys-primary, var(--primary-color))); background: var(--primary-color, var(--mat-sys-primary, var(--primary-color))); color: var(--theme-text-primary, #ffffff); }
    .step-circle-completed { border-color: var(--primary-color, var(--mat-sys-primary, var(--primary-color))); background: var(--mat-sys-primary-container, #ffd9de); color: var(--primary-color, var(--mat-sys-primary, var(--primary-color))); }
    .step-circle-inactive { border-color: var(--mat-sys-outline, #e0e0e0); color: var(--mat-sys-on-surface-variant, #9aa0a6); }

    .selection-card { border: 1px solid var(--theme-border, var(--mat-sys-outline-variant)); border-radius: 14px; padding: 12px 14px; background: linear-gradient(135deg, var(--mat-sys-surface) 0%, var(--mat-sys-surface-container-low, #f6f8fb) 100%); width: 100%; text-align: left; transition: all 0.18s ease; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
    .selection-card:hover { border-color: var(--primary-color, var(--mat-sys-primary)); box-shadow: 0 6px 18px -12px var(--primary-color, var(--mat-sys-primary)); transform: translateY(-1px); }
    .definition-card { align-self: stretch; }
    .card-selected { border-color: var(--primary-color, var(--mat-sys-primary)); box-shadow: 0 8px 22px -14px var(--primary-color, var(--mat-sys-primary)); }
    .icon-chip { width: 40px; height: 40px; border-radius: 12px; background: var(--mat-sys-surface-container-high, #e8edf5); display: grid; place-items: center; }
    .icon-chip.subtle { background: var(--mat-sys-surface-container-low, #f4f7fb); }

    .section-card { border: 1px solid var(--mat-sys-outline-variant); border-radius: 14px; padding: 16px; background: linear-gradient(135deg, var(--mat-sys-surface) 0%, var(--mat-sys-surface-container-low, #f6f8fb) 100%); box-shadow: 0 1px 6px rgba(0,0,0,0.04); display: flex; flex-direction: column; gap: 12px; }
    .section-header { font-size: 0.85rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: var(--mat-sys-on-surface-variant); }

    .muted-box { border: 1px dashed var(--mat-sys-outline-variant); border-radius: 10px; padding: 10px; color: var(--mat-sys-on-surface-variant); background: var(--mat-sys-surface-container); }

    .sys-surface-container { background-color: var(--mat-sys-surface-container, #f0f4f8); color: var(--mat-sys-on-surface, #1f1f1f); }
    .sys-surface { background-color: var(--mat-sys-surface, #ffffff); color: var(--mat-sys-on-surface, #1f1f1f); }
    .sys-text-secondary { color: var(--mat-sys-on-surface-variant, #444746); }
    .sys-text-tertiary { color: var(--mat-sys-on-surface-variant, #7a7f85); }
    .sys-border { border-color: var(--mat-sys-outline-variant, #c4c7c5); }
    .sys-divider { background-color: var(--mat-sys-outline-variant, #e0e0e0); }
    .text-primary { color: var(--primary-color, var(--mat-sys-primary, var(--primary-color))); }

    /* FQN text wrapping (replaced marquee) */
    .fqn-wrap { 
      display: block; 
      width: 100%; 
      white-space: normal; 
      overflow-wrap: break-word;
      word-break: break-word;
      line-height: 1.25;
    }

    .simulated-chip {
      font-size: 10px;
      background-color: var(--mat-sys-tertiary-container);
      color: var(--mat-sys-on-tertiary-container);
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 500;
      margin-left: 4px;
    }
  `]
})
export class MachineDialogComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<MachineDialogComponent>);
  private assetService = inject(AssetService);
  private modeService = inject(ModeService);
  private cdr = inject(ChangeDetectorRef);

  MachineStatus = MachineStatus;
  isBrowserMode = this.modeService.isBrowserMode();

  readonly statusOptions: SelectOption[] = [
    { label: 'Offline', value: MachineStatus.OFFLINE },
    { label: 'Idle', value: MachineStatus.IDLE }
  ];

  // Frontend types derived from MachineFrontendDefinition
  frontendDefinitions: MachineFrontendDefinition[] = [];
  selectedFrontendId: string | null = null;
  selectedFrontend: MachineFrontendDefinition | null = null;

  // Backends filtered by selected frontend
  compatibleBackends: MachineBackendDefinition[] = [];
  selectedBackend: MachineBackendDefinition | null = null;

  // Step State - Now 3 steps
  currentStep = 0;
  steps: Step[] = [
    { label: 'Machine Type', completed: false },
    { label: 'Backend', completed: false },
    { label: 'Configuration', completed: false }
  ];

  showAdvancedConnectionJson = false;
  showAdvancedCapabilitiesJson = false;

  form = this.fb.group({
    name: ['', Validators.required],
    model: [''],
    manufacturer: [''],
    description: [''],
    status: [MachineStatus.OFFLINE],
    backend_driver: ['sim'],
    simulation_backend_name: [''],
    connection_info: ['', jsonValidator],
    backend_config: [null as any], // New field
    user_configured_capabilities: ['', jsonValidator],
    machine_definition_accession_id: [null as string | null],
    frontend_definition_accession_id: [null as string | null], // New field
    backend_definition_accession_id: [null as string | null], // New field
    machine_category: [''],
    location_label: [''],
    generic_capabilities: this.fb.array([])
  });

  get genericCapabilities(): FormArray<FormGroup> {
    return this.form.get('generic_capabilities') as FormArray<FormGroup>;
  }

  // Mapping from frontend FQN to user-friendly labels/icons
  private frontendFqnToLabel: Record<string, { label: string; icon: string }> = {
    'pylabrobot.liquid_handling.LiquidHandler': { label: 'Liquid Handler', icon: 'water_drop' },
    'pylabrobot.plate_reading.PlateReader': { label: 'Plate Reader', icon: 'visibility' },
    'pylabrobot.heating_shaking.HeaterShaker': { label: 'Heater Shaker', icon: 'vibration' },
    'pylabrobot.shaking.Shaker': { label: 'Shaker', icon: 'vibration' },
    'pylabrobot.temperature_controlling.TemperatureController': { label: 'Temperature Controller', icon: 'thermostat' },
    'pylabrobot.centrifuging.Centrifuge': { label: 'Centrifuge', icon: 'rotate_right' },
    'pylabrobot.thermocycling.Thermocycler': { label: 'Thermocycler', icon: 'thermostat' },
    'pylabrobot.pumping.Pump': { label: 'Pump', icon: 'air' },
    'pylabrobot.pumping.PumpArray': { label: 'Pump Array', icon: 'air' },
    'pylabrobot.fans.Fan': { label: 'Fan', icon: 'air' },
    'pylabrobot.plate_sealing.Sealer': { label: 'Plate Sealer', icon: 'check_box' },
    'pylabrobot.plate_peeling.Peeler': { label: 'Plate Peeler', icon: 'layers_clear' },
    'pylabrobot.powder_dispensing.PowderDispenser': { label: 'Powder Dispenser', icon: 'grain' },
    'pylabrobot.incubating.Incubator': { label: 'Incubator', icon: 'ac_unit' },
    'pylabrobot.scara.SCARA': { label: 'SCARA Robot', icon: 'smart_toy' }
  };

  ngOnInit() {
    console.debug('[ASSET-DEBUG] MachineDialogComponent: ngOnInit started');
    
    // Fetch frontend definitions
    this.assetService.getMachineFrontendDefinitions().subscribe(frontends => {
      console.debug('[ASSET-DEBUG] MachineDialogComponent: Received frontends', frontends.length);
      this.frontendDefinitions = frontends.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
      this.cdr.markForCheck();
    });

    if (this.genericCapabilities.length === 0) {
      this.addCapabilityPair();
    }
  }

  getFrontendIcon(frontend: MachineFrontendDefinition): string {
    return this.frontendFqnToLabel[frontend.fqn]?.icon || 'settings';
  }

  getFrontendLabel(frontend: MachineFrontendDefinition): string {
    return frontend.name || this.frontendFqnToLabel[frontend.fqn]?.label || frontend.fqn;
  }

  selectFrontend(frontend: MachineFrontendDefinition) {
    if (this.selectedFrontendId === frontend.accession_id) {
      this.selectedFrontendId = null;
      this.selectedFrontend = null;
      this.compatibleBackends = [];
      this.steps[0].completed = false;
      return;
    }
    
    this.selectedFrontendId = frontend.accession_id;
    this.selectedFrontend = frontend;
    this.selectedBackend = null;
    
    // Fetch compatible backends
    this.assetService.getBackendsForFrontend(frontend.accession_id).subscribe(backends => {
      this.compatibleBackends = backends;
      this.cdr.markForCheck();
    });

    // Reset downstream steps
    this.steps[1].completed = false;
    this.steps[2].completed = false;
  }

  getSelectedFrontendLabel(): string {
    return this.selectedFrontend ? this.getFrontendLabel(this.selectedFrontend) : 'machine';
  }

  /** Check if a backend definition is a simulation backend */
  isSimulatedBackend(backend: MachineBackendDefinition): boolean {
    return backend.backend_type === 'simulator' || 
           (backend.fqn || '').toLowerCase().includes('chatterbox') ||
           (backend.name || '').toLowerCase().includes('simulator');
  }

  /** Truncate name for display */
  getTruncatedName(name: string, maxLength = 30): string {
    if (!name) return '';
    return name.length > maxLength ? name.substring(0, maxLength) + '...' : name;
  }

  /** Get short FQN for display (last 2 segments) */
  getShortFqn(fqn: string): string {
    if (!fqn) return '';
    const parts = fqn.split('.');
    return parts.length > 2 ? '...' + parts.slice(-2).join('.') : fqn;
  }

  /** Update capabilities from dynamic form */
  updateCapabilities(val: any) {
    this.form.patchValue({
      user_configured_capabilities: JSON.stringify(val, null, 2)
    });
  }

  selectBackend(backend: MachineBackendDefinition) {
    this.selectedBackend = backend;

    const isSimulated = this.isSimulatedBackend(backend);
    
    // Generate instance name
    const randomNum = Math.floor(Math.random() * 100) + 1;
    const name = `${backend.name || 'Machine'} ${randomNum}`;

    this.form.patchValue({
      name: name,
      model: backend.model || '',
      manufacturer: backend.manufacturer || '',
      description: backend.description || '',
      backend_definition_accession_id: backend.accession_id,
      frontend_definition_accession_id: this.selectedFrontendId,
      machine_category: this.selectedFrontend?.machine_category || 'unknown',
      backend_driver: isSimulated ? 'sim' : backend.fqn,
      backend_config: {},
      connection_info: '',
      user_configured_capabilities: ''
    });

    // Reset downstream step
    this.steps[2].completed = false;
  }

  shouldShowConnectionConfig(): boolean {
    return !!this.selectedBackend?.connection_config && this.form.get('backend_driver')?.value !== 'sim';
  }

  updateConnectionInfo(val: any) {
    this.form.patchValue({
      backend_config: val,
      connection_info: JSON.stringify(val, null, 2)
    });
  }

  nextStep() {
    if (this.canProceed()) {
      this.steps[this.currentStep].completed = true;
      if (this.currentStep < this.steps.length - 1) {
        this.currentStep++;
      }
    }
  }

  goBack() {
    if (this.currentStep > 0) {
      this.currentStep--;
    }
  }

  goToStep(index: number) {
    if (index === this.currentStep) return;
    if (index < this.currentStep) {
      this.currentStep = index;
      return;
    }
    for (let i = this.currentStep; i < index; i++) {
      if (!this.isStepValid(i)) return;
      this.steps[i].completed = true;
    }
    this.currentStep = index;
  }

  isStepValid(stepIndex: number): boolean {
    if (stepIndex === 0) return !!this.selectedFrontendId;
    if (stepIndex === 1) return !!this.selectedBackend;
    if (stepIndex === 2) {
      return !!this.form.get('name')?.valid;
    }
    return false;
  }

  canProceed(): boolean {
    return this.isStepValid(this.currentStep);
  }

  createCapabilityPair(): FormGroup {
    return this.fb.group({ key: [''], value: [''] });
  }

  addCapabilityPair() {
    this.genericCapabilities.push(this.createCapabilityPair());
  }

  removeCapabilityPair(idx: number) {
    if (this.genericCapabilities.length > 1) {
      this.genericCapabilities.removeAt(idx);
      this.syncGenericCapabilities();
    }
  }

  syncGenericCapabilities() {
    const obj = this.buildGenericCapabilitiesObject();
    if (Object.keys(obj).length) {
      this.form.patchValue({ user_configured_capabilities: JSON.stringify(obj, null, 2) }, { emitEvent: false });
    }
  }

  private buildGenericCapabilitiesObject(): Record<string, any> {
    const pairs = this.genericCapabilities.controls || [];
    return pairs.reduce<Record<string, any>>((acc, ctrl) => {
      const key = (ctrl.get('key')?.value || '').toString().trim();
      const rawVal = (ctrl.get('value')?.value ?? '').toString().trim();
      if (!key) return acc;
      const lower = rawVal.toLowerCase();
      if (lower === 'true' || lower === 'false') {
        acc[key] = lower === 'true';
      } else if (!isNaN(Number(rawVal)) && rawVal !== '') {
        acc[key] = Number(rawVal);
      } else {
        acc[key] = rawVal;
      }
      return acc;
    }, {});
  }

  save() {
    if (this.form.valid) {
      const value = this.form.value;
      
      let userConfiguredCapabilities: any = null;
      if (value.user_configured_capabilities) {
        try {
          userConfiguredCapabilities = JSON.parse(value.user_configured_capabilities);
        } catch { /* Invalid JSON */ }
      } else {
        const generic = this.buildGenericCapabilitiesObject();
        userConfiguredCapabilities = Object.keys(generic).length ? generic : null;
      }

      this.dialogRef.close({
        ...value,
        frontend_fqn: this.selectedFrontend?.fqn,
        user_configured_capabilities: userConfiguredCapabilities,
        is_simulated: this.selectedBackend ? this.isSimulatedBackend(this.selectedBackend) : true
      });
    }
  }
}