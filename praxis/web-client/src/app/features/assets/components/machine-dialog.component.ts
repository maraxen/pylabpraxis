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
import { MachineStatus, MachineDefinition } from '../models/asset.models';
import { AssetService } from '../services/asset.service';
import { Observable, map, startWith, of } from 'rxjs';
import { ModeService } from '../../../core/services/mode.service';

// Custom validator for JSON string
const jsonValidator = (control: AbstractControl): ValidationErrors | null => {
  if (!control.value) {
    return null; // Don't validate empty values
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
    DynamicCapabilityFormComponent
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

          <!-- STEP 1: Category + Model Selection -->
          @if (currentStep === 0) {
            <div class="fade-in flex flex-col gap-5">
              <div>
                <h3 class="text-lg font-medium mb-3">Choose a category</h3>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                  @for (cat of machineCategories; track cat) {
                    <button type="button"
                      class="selection-card"
                      [class.card-selected]="selectedCategory === cat"
                      (click)="selectCategory(cat)">
                      <div class="flex items-center gap-3 w-full">
                        <div class="icon-chip"><mat-icon>{{ getCategoryIcon(cat) }}</mat-icon></div>
                        <div class="flex flex-col items-start">
                          <span class="font-medium">{{ cat }}</span>
                          <span class="text-xs sys-text-secondary">{{ getCategoryCount(cat) }} models</span>
                        </div>
                      </div>
                    </button>
                  }
                </div>
              </div>

              <div class="flex items-center gap-2">
                <h3 class="text-lg font-medium">Select a model</h3>
                <span class="text-xs sys-text-secondary" *ngIf="selectedCategory">Filtered by {{ selectedCategory }}</span>
              </div>
              <mat-form-field appearance="outline" class="w-full praxis-search-field">
                <mat-label>Search model</mat-label>
                <mat-icon matPrefix>search</mat-icon>
                <input matInput [formControl]="definitionSearchControl" placeholder="Filter by name or vendor...">
              </mat-form-field>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[360px] overflow-y-auto pr-1">
                @for (def of filteredDefinitions$ | async; track def) {
                  <button type="button"
                    class="selection-card definition-card"
                    [class.card-selected]="selectedDefinition?.accession_id === def.accession_id"
                    (click)="selectDefinition(def)">
                    <div class="flex items-start gap-3 w-full">
                      <div class="icon-chip subtle">
                        <mat-icon>{{ getCategoryIcon(def.machine_category || '') }}</mat-icon>
                      </div>
                      <div class="flex flex-col items-start min-w-0">
                        <div class="flex items-center gap-2 w-full">
                          <span class="font-medium truncate">{{ def.name }}</span>
                          @if (selectedDefinition?.accession_id === def.accession_id) {
                            <mat-icon class="text-primary !text-sm">check_circle</mat-icon>
                          }
                        </div>
                        <span class="text-xs sys-text-secondary truncate">
                          {{ def.manufacturer || 'Unknown vendor' }} — {{ def.model || getShortFqn(def.fqn || '') }}
                        </span>
                        <span class="text-[11px] text-sys-text-tertiary truncate">{{ def.fqn }}</span>
                      </div>
                    </div>
                  </button>
                }
                @if ((filteredDefinitions$ | async)?.length === 0) {
                  <div class="muted-box">No models match this category or search.</div>
                }
              </div>
            </div>
          }

          <!-- STEP 2: Backend & Config (sub-steps inline) -->
          @if (currentStep === 1) {
            <div class="fade-in flex flex-col gap-4">
              <div class="flex items-center gap-2 mb-1">
                <button mat-icon-button (click)="goBack()"><mat-icon>arrow_back</mat-icon></button>
                <h3 class="text-lg font-medium">Backend & Configuration</h3>
              </div>

              <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div class="section-card">
                  <div class="section-header">Backend</div>
                  <mat-form-field appearance="outline" class="w-full">
                    <mat-label>Driver / Backend</mat-label>
                    <mat-select formControlName="backend_driver" panelClass="theme-aware-panel">
                      <mat-option [value]="'sim'" class="font-mono text-sm">
                        <span class="font-semibold text-primary">Simulated</span>
                      </mat-option>
                      @if (selectedDefinition?.compatible_backends?.length) {
                        <mat-divider></mat-divider>
                        @for (backend of selectedDefinition?.compatible_backends; track backend) {
                          <mat-option [value]="backend" class="font-mono text-xs">
                            {{ getShortBackendName(backend) }}
                          </mat-option>
                        }
                      }
                    </mat-select>
                  </mat-form-field>

                  <mat-form-field appearance="outline" class="w-full">
                    <mat-label>Instance Name</mat-label>
                    <input matInput formControlName="name" placeholder="e.g. Robot 1">
                  </mat-form-field>

                  <mat-form-field appearance="outline" class="w-full">
                    <mat-label>Location (Optional)</mat-label>
                    <input matInput formControlName="location_label" placeholder="e.g. Bench A">
                  </mat-form-field>

                  <mat-form-field appearance="outline" class="w-full">
                    <mat-label>Initial Status</mat-label>
                    <mat-select formControlName="status" panelClass="theme-aware-panel">
                      <mat-option [value]="MachineStatus.OFFLINE">Offline</mat-option>
                      <mat-option [value]="MachineStatus.IDLE">Idle</mat-option>
                    </mat-select>
                  </mat-form-field>
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
                  <div class="muted-box mb-3">No capability schema detected for this model. Use generic fields or JSON override.</div>
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
                }

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
            [disabled]="form.invalid || !selectedDefinition"
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
    .step-text-active { color: var(--mat-sys-primary, #3f51b5); }
    .step-text-completed { color: var(--mat-sys-primary, #2e7d32); }
    .step-text-inactive { color: var(--mat-sys-on-surface-variant, #9aa0a6); }
    .step-circle-active { border-color: var(--mat-sys-primary, #3f51b5); background: var(--mat-sys-primary, #3f51b5); color: var(--mat-sys-on-primary, #ffffff); }
    .step-circle-completed { border-color: var(--mat-sys-primary, #2e7d32); background: var(--mat-sys-primary-container, #e8f5e9); color: var(--mat-sys-on-primary-container, #2e7d32); }
    .step-circle-inactive { border-color: var(--mat-sys-outline, #e0e0e0); color: var(--mat-sys-on-surface-variant, #9aa0a6); }

    .selection-card { border: 1px solid var(--theme-border, var(--mat-sys-outline-variant)); border-radius: 14px; padding: 12px 14px; background: linear-gradient(135deg, var(--mat-sys-surface) 0%, var(--mat-sys-surface-container-low, #f6f8fb) 100%); width: 100%; text-align: left; transition: all 0.18s ease; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
    .selection-card:hover { border-color: var(--mat-sys-primary); box-shadow: 0 6px 18px -12px var(--mat-sys-primary); transform: translateY(-1px); }
    .definition-card { align-self: stretch; }
    .card-selected { border-color: var(--mat-sys-primary); box-shadow: 0 8px 22px -14px var(--mat-sys-primary); }
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
    .text-primary { color: var(--mat-sys-primary, #3f51b5); }

    :host-context(.dark) {
       --mat-sys-surface: #121212;
       --mat-sys-surface-container: #1e1e1e;
       --mat-sys-surface-container-low: #181818;
       --mat-sys-on-surface: #e3e3e3;
       --mat-sys-on-surface-variant: #c4c7c5;
       --mat-sys-outline: #444746;
       --mat-sys-outline-variant: #444746;
       --mat-sys-primary: #a8c7fa;
       --mat-sys-primary-container: #0842a0;
       --mat-sys-on-primary-container: #d3e3fd;
       --mat-sys-secondary-container: #004b73;
       --mat-sys-on-secondary-container: #cce5ff;
    }
  `]
})
export class MachineDialogComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<MachineDialogComponent>);
  private assetService = inject(AssetService);
  private modeService = inject(ModeService);

  MachineStatus = MachineStatus;
  isBrowserMode = this.modeService.isBrowserMode();

  definitions: MachineDefinition[] = [];
  selectedDefinition: MachineDefinition | null = null;

  // Step State
  currentStep = 0;
  steps: Step[] = [
    { label: 'Category & Model', completed: false },
    { label: 'Backend & Config', completed: false }
  ];

  showAdvancedConnectionJson = false;
  showAdvancedCapabilitiesJson = false;

  // Category Selection
  machineCategories: string[] = [];
  selectedCategory: string | null = null;

  // Definition Selection
  definitionSearchControl = new FormControl<string>('');
  filteredDefinitions$: Observable<MachineDefinition[]> = of([]);

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

  private cdr = inject(ChangeDetectorRef);

  ngOnInit() {
    console.debug('[ASSET-DEBUG] MachineDialogComponent: ngOnInit started');
    this.assetService.getMachineDefinitions().subscribe(defs => {
      console.debug('[ASSET-DEBUG] MachineDialogComponent: Received definitions', defs.length);
      // Filter out definitions that are backend implementations (have frontend_fqn set)
      this.definitions = defs.filter(d => !d.frontend_fqn);
      // Extract categories
      this.machineCategories = [...new Set(this.definitions.map(d => d.machine_category || 'Other'))].sort();
      console.debug('[ASSET-DEBUG] MachineDialogComponent: Categories', this.machineCategories);

      if (this.genericCapabilities.length === 0) {
        this.addCapabilityPair();
      }

      this.filteredDefinitions$ = this.definitionSearchControl.valueChanges.pipe(
        startWith(''),
        map(val => this.filterDefinitions(val))
      );
      this.cdr.markForCheck();
    });
  }

  getCategoryIcon(cat: string): string {
    const lower = cat.toLowerCase();
    if (lower.includes('liquid')) return 'water_drop';
    if (lower.includes('plate') && lower.includes('reader')) return 'visibility';
    if (lower.includes('shaker') || lower.includes('heat')) return 'vibration';
    if (lower.includes('robot')) return 'smart_toy';
    return 'science';
  }

  getCategoryCount(cat: string): number {
    return this.definitions.filter(d => (d.machine_category || 'Other') === cat).length;
  }

  selectCategory(cat: string) {
    if (this.selectedCategory === cat) {
      this.selectedCategory = null;
      this.selectedDefinition = null;
      this.definitionSearchControl.setValue('');
      return;
    }
    this.selectedCategory = cat;
    this.selectedDefinition = null;
    this.definitionSearchControl.setValue(''); // Reset search
  }

  selectDefinition(def: MachineDefinition) {
    this.selectedDefinition = def;
    if (!this.selectedCategory && def.machine_category) {
      this.selectedCategory = def.machine_category;
    }
    this.onDefinitionSelected(def);
  }

  onDefinitionSelected(def: MachineDefinition) {
    // Auto-populate form
    this.form.patchValue({
      model: def.model || def.name,
      manufacturer: def.manufacturer || '',
      description: def.description || '',
      machine_definition_accession_id: def.accession_id,
      machine_category: def.machine_category || def.name || 'unknown',
      backend_driver: this.isBrowserMode ? 'sim' : (def.compatible_backends?.[0] || 'sim'),
      // Set reasonable name default
      name: `${def.name} ${Math.floor(Math.random() * 100) + 1}`,
      // Reset JSON fields to avoid [object Object] displaying in textareas
      connection_info: '',
      user_configured_capabilities: ''
    });
  }

  shouldShowConnectionConfig(): boolean {
    return !!this.selectedDefinition?.connection_config && this.form.get('backend_driver')?.value !== 'sim';
  }

  filterDefinitions(search: string | null): MachineDefinition[] {
    const query = (search || '').toLowerCase();
    return this.definitions.filter(d => {
      const matchesCategory = !this.selectedCategory || (d.machine_category || 'Other') === this.selectedCategory;
      const matchesSearch = !query ||
        d.name.toLowerCase().includes(query) ||
        (d.manufacturer || '').toLowerCase().includes(query);

      return matchesCategory && matchesSearch;
    });
  }

  nextStep() {
    this.steps[this.currentStep].completed = true;
    if (this.currentStep < this.steps.length - 1) {
      this.currentStep++;
    }
  }

  goBack() {
    if (this.currentStep > 0) {
      this.steps[this.currentStep].completed = false; // Mark current as incomplete
      this.currentStep--;
      this.steps[this.currentStep].completed = false; // Mark prev as incomplete since we are revisiting
    }
  }

  canProceed(): boolean {
    if (this.currentStep === 0) return !!this.selectedCategory && !!this.selectedDefinition;
    if (this.currentStep === 1) return !!this.selectedDefinition && !!this.form.get('name')?.valid && !!this.form.get('backend_driver')?.valid;
    return false;
  }

  getShortFqn(fqn: string): string {
    const parts = fqn.split('.');
    return parts.length > 2 ? parts.slice(-2).join('.') : fqn;
  }

  getShortBackendName(fqn: string): string {
    const parts = fqn.split('.');
    return parts[parts.length - 1];
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
      // Coerce booleans/numbers when obvious
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

      // Logic for "simulated" flag
      const isSimulated = value.backend_driver === 'sim' || (value.backend_driver || '').toLowerCase().includes('sim');

      if (value.backend_driver) {
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
        connection_info: connectionInfo,
        user_configured_capabilities: userConfiguredCapabilities,
        is_simulated: isSimulated // Pass this back to creator
      });
    }
  }
}