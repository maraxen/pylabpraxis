import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { DynamicCapabilityFormComponent } from './dynamic-capability-form.component';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, AbstractControl, ValidationErrors, FormControl, FormArray, FormGroup } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatStepperModule } from '@angular/material/stepper';
import { MatCardModule } from '@angular/material/card';
import { PraxisSelectComponent, SelectOption } from '@shared/components/praxis-select/praxis-select.component';
import { MachineStatus, MachineDefinition } from '../models/asset.models';
import { AssetService } from '../services/asset.service';
import { ModeService } from '../../../core/services/mode.service';

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
              [class.step-text-active]="currentStep === i"
              [class.step-text-inactive]="currentStep !== i && !step.completed"
              [class.step-text-completed]="step.completed"
              [class.font-bold]="currentStep === i">
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
                  @for (ft of frontendTypes; track ft.fqn) {
                    <button type="button"
                      class="selection-card"
                      [class.card-selected]="selectedFrontendFqn === ft.fqn"
                      (click)="selectFrontendType(ft.fqn)">
                      <div class="flex items-center gap-3 w-full">
                        <div class="icon-chip"><mat-icon>{{ ft.icon }}</mat-icon></div>
                        <div class="flex flex-col items-start">
                          <span class="font-medium">{{ ft.label }}</span>
                          <span class="text-xs sys-text-secondary">{{ ft.backendCount }} backend(s)</span>
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
              <div class="flex items-center gap-2 mb-1">
                <button mat-icon-button (click)="goBack()"><mat-icon>arrow_back</mat-icon></button>
                <h3 class="text-lg font-medium">Select Backend</h3>
              </div>
              <p class="text-sm sys-text-secondary">Choose the hardware driver for your {{ getSelectedFrontendLabel() }}. Simulator backends are available for testing without hardware.</p>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[300px] overflow-y-auto pr-1">
                @for (def of filteredBackends; track def.accession_id) {
                  <button type="button"
                    class="selection-card definition-card"
                    [class.card-selected]="selectedDefinition?.accession_id === def.accession_id"
                    (click)="selectBackend(def)">
                    <div class="flex items-start gap-3 w-full">
                      <div class="icon-chip subtle">
                        <mat-icon>memory</mat-icon>
                      </div>
                      <div class="flex flex-col items-start min-w-0">
                        <div class="flex items-center gap-2 w-full">
                          <span class="font-medium truncate">{{ def.name }}</span>
                          @if (isSimulatedDefinition(def)) {
                            <span class="simulated-chip">Simulated</span>
                          }
                          @if (selectedDefinition?.accession_id === def.accession_id) {
                            <mat-icon class="text-primary !text-sm ml-auto">check_circle</mat-icon>
                          }
                        </div>
                        <span class="text-xs sys-text-secondary truncate">
                          {{ def.manufacturer || 'Unknown vendor' }}
                        </span>
                        <span class="text-[11px] text-sys-text-tertiary fqn-wrap">{{ getShortFqn(def.fqn || '') }}</span>
                      </div>
                    </div>
                  </button>
                }
                @if (filteredBackends.length === 0) {
                  <div class="muted-box col-span-2">No backends available for this machine type.</div>
                }
              </div>
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
                      [config]="selectedDefinition!.connection_config"
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
                @if (selectedDefinition?.capabilities_config) {
                  <app-dynamic-capability-form
                    [config]="selectedDefinition!.capabilities_config"
                    (valueChange)="updateCapabilities($event)">
                  </app-dynamic-capability-form>
                } @else if (selectedDefinition) {
                  <div class="muted-box mb-3">No capability schema for this backend. Use generic fields or JSON override.</div>
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

                @if (selectedDefinition) {
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
    .step-text-active { color: var(--primary-color, var(--mat-sys-primary, #ED7A9B)); }
    .step-text-completed { color: var(--primary-color, var(--mat-sys-primary, #ED7A9B)); }
    .step-text-inactive { color: var(--mat-sys-on-surface-variant, #9aa0a6); }
    .step-circle-active { border-color: var(--primary-color, var(--mat-sys-primary, #ED7A9B)); background: var(--primary-color, var(--mat-sys-primary, #ED7A9B)); color: var(--theme-text-primary, #ffffff); }
    .step-circle-completed { border-color: var(--primary-color, var(--mat-sys-primary, #ED7A9B)); background: var(--mat-sys-primary-container, #ffd9de); color: var(--primary-color, var(--mat-sys-primary, #ED7A9B)); }
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
    .text-primary { color: var(--primary-color, var(--mat-sys-primary, #ED7A9B)); }

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

  // All definitions (backends have frontend_fqn set)
  allDefinitions: MachineDefinition[] = [];

  // Frontend types derived from unique frontend_fqn values
  frontendTypes: FrontendType[] = [];
  selectedFrontendFqn: string | null = null;

  // Backends filtered by selected frontend type
  filteredBackends: MachineDefinition[] = [];
  selectedDefinition: MachineDefinition | null = null;

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
    connection_info: ['', jsonValidator],
    user_configured_capabilities: ['', jsonValidator],
    machine_definition_accession_id: [null as string | null],
    machine_category: [''],
    location_label: [''],
    generic_capabilities: this.fb.array([])
  });

  get genericCapabilities(): FormArray<FormGroup> {
    return this.form.get('generic_capabilities') as FormArray<FormGroup>;
  }

  // Mapping from frontend FQN to user-friendly labels
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
    this.assetService.getMachineDefinitions().subscribe(defs => {
      console.debug('[ASSET-DEBUG] MachineDialogComponent: Received definitions', defs.length);

      // Store all definitions (backends have frontend_fqn set)
      this.allDefinitions = defs.filter(d => d.frontend_fqn);

      // Build unique frontend types from frontend_fqn
      const fqnCounts = new Map<string, number>();
      this.allDefinitions.forEach(d => {
        if (d.frontend_fqn) {
          fqnCounts.set(d.frontend_fqn, (fqnCounts.get(d.frontend_fqn) || 0) + 1);
        }
      });

      // Show ALL known frontend types so users can select "Simulated" even if no backends exist
      this.frontendTypes = Object.entries(this.frontendFqnToLabel).map(([fqn, mapping]) => ({
        fqn,
        label: mapping.label,
        icon: mapping.icon,
        backendCount: fqnCounts.get(fqn) || 0
      })).sort((a, b) => a.label.localeCompare(b.label));

      console.debug('[ASSET-DEBUG] MachineDialogComponent: Frontend types', this.frontendTypes);

      if (this.genericCapabilities.length === 0) {
        this.addCapabilityPair();
      }

      this.cdr.markForCheck();
    });
  }

  selectFrontendType(fqn: string) {
    if (this.selectedFrontendFqn === fqn) {
      this.selectedFrontendFqn = null;
      this.filteredBackends = [];
      return;
    }
    this.selectedFrontendFqn = fqn;
    this.filteredBackends = this.allDefinitions.filter(d => d.frontend_fqn === fqn);
    this.selectedDefinition = null;
    this.form.patchValue({ backend_driver: 'sim' });
  }

  getSelectedFrontendLabel(): string {
    if (!this.selectedFrontendFqn) return 'machine';
    const ft = this.frontendTypes.find(f => f.fqn === this.selectedFrontendFqn);
    return ft?.label || 'machine';
  }

  selectSimulated() {
    this.selectedDefinition = null;
    this.form.patchValue({
      backend_driver: 'sim',
      machine_definition_accession_id: null,
      connection_info: '',
      user_configured_capabilities: '',
      name: `Simulated ${this.getSelectedFrontendLabel()} ${Math.floor(Math.random() * 100) + 1}`
    });
  }

  /** Check if a backend definition is a simulation backend */
  isSimulatedDefinition(def: MachineDefinition): boolean {
    const fqnLower = (def.fqn || '').toLowerCase();
    const nameLower = (def.name || '').toLowerCase();
    return fqnLower.includes('chatterbox') ||
      fqnLower.includes('simulator') ||
      nameLower.includes('simulated');
  }

  selectBackend(def: MachineDefinition) {
    this.selectedDefinition = def;

    const isSimulatedBackend = this.isSimulatedDefinition(def);

    this.form.patchValue({
      model: def.model || def.name,
      manufacturer: def.manufacturer || '',
      description: def.description || '',
      machine_definition_accession_id: def.accession_id,
      machine_category: def.machine_category || 'unknown',
      backend_driver: isSimulatedBackend ? 'sim' : (def.fqn || def.name),
      name: `${def.name} ${Math.floor(Math.random() * 100) + 1}`,
      connection_info: '',
      user_configured_capabilities: ''
    });
  }

  shouldShowConnectionConfig(): boolean {
    return !!this.selectedDefinition?.connection_config && this.form.get('backend_driver')?.value !== 'sim';
  }

  nextStep() {
    this.steps[this.currentStep].completed = true;
    if (this.currentStep < this.steps.length - 1) {
      this.currentStep++;
    }
  }

  goBack() {
    if (this.currentStep > 0) {
      this.steps[this.currentStep].completed = false;
      this.currentStep--;
      this.steps[this.currentStep].completed = false;
    }
  }

  canProceed(): boolean {
    if (this.currentStep === 0) return !!this.selectedFrontendFqn;
    if (this.currentStep === 1) return !!this.selectedDefinition;
    if (this.currentStep === 2) return !!this.form.get('name')?.valid;
    return false;
  }

  getShortFqn(fqn: string): string {
    const parts = fqn.split('.');
    return parts.length > 2 ? parts.slice(-2).join('.') : fqn;
  }

  updateCapabilities(val: any) {
    this.form.patchValue({
      user_configured_capabilities: JSON.stringify(val, null, 2)
    });
  }

  updateConnectionInfo(val: any) {
    this.form.patchValue({
      connection_info: JSON.stringify(val, null, 2)
    });
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
      let connectionInfo: any = {};

      if (value.connection_info) {
        try {
          connectionInfo = JSON.parse(value.connection_info);
        } catch (e) { console.error(e); }
      }

      const isSimulated = value.backend_driver === 'sim';

      if (value.backend_driver && value.backend_driver !== 'sim') {
        connectionInfo['backend_fqn'] = value.backend_driver;
      }

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
        frontend_fqn: this.selectedFrontendFqn,
        connection_info: connectionInfo,
        user_configured_capabilities: userConfiguredCapabilities,
        is_simulated: isSimulated
      });
    }
  }
}