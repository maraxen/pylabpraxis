import { Component, inject, OnInit } from '@angular/core';
import { DynamicCapabilityFormComponent } from './dynamic-capability-form.component';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, AbstractControl, ValidationErrors, FormControl } from '@angular/forms';
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
        <div class="mb-6 flex items-center justify-between px-2">
          @for (step of steps; track step; let i = $index) {
            <div
              class="flex items-center gap-2 text-sm"
              [class.step-text-active]="currentStep === i"
              [class.step-text-inactive]="currentStep !== i && !step.completed"
              [class.step-text-completed]="step.completed"
              [class.font-bold]="currentStep === i">
              <div class="w-6 h-6 rounded-full flex items-center justify-center border transition-all"
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
                <div class="h-[1px] w-4 ml-2 sys-divider"></div>
              }
            </div>
          }
        </div>
    
        <form [formGroup]="form" class="flex flex-col gap-4 py-2">
    
          <!-- STEP 1: Category Selection -->
          @if (currentStep === 0) {
            <div class="fade-in">
              <h3 class="text-lg font-medium mb-4">Select Machine Category</h3>
              <div class="grid grid-cols-2 gap-4">
                @for (cat of machineCategories; track cat) {
                  <div
                    class="category-card sys-border border rounded-xl p-4 cursor-pointer transition-all text-center flex flex-col items-center gap-2"
                    (click)="selectCategory(cat)">
                    <mat-icon class="scale-125 sys-text-secondary">{{ getCategoryIcon(cat) }}</mat-icon>
                    <span class="font-medium">{{ cat }}</span>
                  </div>
                }
              </div>
            </div>
          }
    
          <!-- STEP 2: Model & Backend Selection -->
          @if (currentStep === 1) {
            <div class="fade-in">
              <div class="flex items-center gap-2 mb-4">
                <button mat-icon-button (click)="goBack()"><mat-icon>arrow_back</mat-icon></button>
                <h3 class="text-lg font-medium">Select Model & Driver</h3>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Left: Model Selection -->
                <div class="flex flex-col gap-2">
                  <mat-form-field appearance="outline" class="w-full praxis-search-field">
                    <mat-label>Search Model</mat-label>
                    <mat-icon matPrefix>search</mat-icon>
                    <input matInput [formControl]="definitionSearchControl" placeholder="Filter by name...">
                  </mat-form-field>
                  <div class="grid grid-cols-1 gap-2 max-h-[300px] overflow-y-auto pr-2">
                    @for (def of filteredDefinitions$ | async; track def) {
                      <div
                        class="definition-item sys-border border rounded-lg p-3 cursor-pointer flex justify-between items-center transition-colors"
                        [class.selected-def]="selectedDefinition?.accession_id === def.accession_id"
                        (click)="selectDefinition(def)">
                        <div class="flex flex-col">
                          <span class="font-medium text-sm">{{ def.name }}</span>
                          <span class="text-[10px] sys-text-secondary">{{ def.manufacturer }} - {{ def.model || getShortFqn(def.fqn || '') }}</span>
                        </div>
                        @if (selectedDefinition?.accession_id === def.accession_id) {
                          <mat-icon class="text-primary">check_circle</mat-icon>
                        } @else {
                          <mat-icon class="text-xs opacity-20">chevron_right</mat-icon>
                        }
                      </div>
                    }
                  </div>
                </div>

                <!-- Right: Backend & Basic Details -->
                <div class="flex flex-col gap-3 p-4 sys-surface-container rounded-xl border sys-border" [class.opacity-50]="!selectedDefinition">
                   <h4 class="text-sm font-bold uppercase tracking-wider text-sys-text-tertiary">Configuration</h4>
                   
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
                </div>
              </div>
            </div>
          }
    
          <!-- STEP 3: Capabilities & Connection -->
          @if (currentStep === 2) {
            <div class="fade-in">
              <div class="flex items-center gap-2 mb-4">
                <button mat-icon-button (click)="goBack()"><mat-icon>arrow_back</mat-icon></button>
                <h3 class="text-lg font-medium">Additional Configuration</h3>
              </div>
              <!-- Connection Settings (Only if not sim, usually) -->
              @if (selectedDefinition?.connection_config && form.get('backend_driver')?.value !== 'sim') {
                <div class="border sys-border rounded-lg p-3 sys-surface flex flex-col gap-2 mb-4">
                  <div class="text-sm font-medium sys-text-secondary">Connection Settings</div>
                  <app-dynamic-capability-form
                    [config]="selectedDefinition!.connection_config"
                    (valueChange)="updateConnectionInfo($event)">
                  </app-dynamic-capability-form>
                </div>
              } @else {
                <!-- Only show manual JSON if strictly needed or if connection_config missing but manual allowed -->
                @if (form.get('backend_driver')?.value !== 'sim') {
                  <div class="mb-4">
                    <mat-form-field appearance="outline" class="w-full">
                      <mat-label>Connection Info (JSON)</mat-label>
                      <textarea matInput formControlName="connection_info" placeholder='{"host": "127.0.0.1", "port": 3000}' rows="2"></textarea>
                      @if (form.get('connection_info')?.hasError('invalidJson')) {
                        <mat-error>Invalid JSON format</mat-error>
                      }
                    </mat-form-field>
                  </div>
                }
              }
              <!-- Capabilities -->
              @if (selectedDefinition?.capabilities_config) {
                <div class="border sys-border rounded-lg p-3 sys-surface flex flex-col gap-2">
                  <div class="text-sm font-medium sys-text-secondary">Configuration</div>
                  <app-dynamic-capability-form
                    [config]="selectedDefinition!.capabilities_config"
                    (valueChange)="updateCapabilities($event)">
                  </app-dynamic-capability-form>
                </div>
              } @else {
                @if (selectedDefinition) {
                  <mat-form-field appearance="outline" class="w-full">
                    <mat-label>User Configured Capabilities (JSON)</mat-label>
                    <textarea matInput formControlName="user_configured_capabilities" placeholder='{"has_iswap": true, "has_core96": true}' rows="2"></textarea>
                    @if (form.get('user_configured_capabilities')?.hasError('invalidJson')) {
                      <mat-error>Invalid JSON format</mat-error>
                    }
                    <mat-hint>Configure optional modules (e.g. iSWAP, CoRe96).</mat-hint>
                  </mat-form-field>
                }
              }
              <div class="mt-4">
                <mat-form-field appearance="outline" class="w-full">
                  <mat-label>Initial Status</mat-label>
                  <mat-select formControlName="status" panelClass="theme-aware-panel">
                    <mat-option [value]="MachineStatus.OFFLINE">Offline</mat-option>
                    <mat-option [value]="MachineStatus.IDLE">Idle</mat-option>
                  </mat-select>
                </mat-form-field>
              </div>
            </div>
          }
    
        </form>
      </mat-dialog-content>
    
      <mat-dialog-actions align="end" class="flex-shrink-0 border-t sys-border p-4 z-10">
        <button mat-button mat-dialog-close>Cancel</button>
    
        @if (currentStep < 2) {
          <button mat-flat-button color="primary"
            [disabled]="!canProceed()"
            (click)="nextStep()">
            Next
          </button>
        }
    
        @if (currentStep === 2) {
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
    .fade-in {
      animation: fadeIn 0.3s ease-in-out;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(5px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    /* Theme helpers - Variables should be provided by Material theme, but we add fallbacks */
    .sys-surface-container {
      background-color: var(--mat-sys-surface-container, #f0f4f8);
      color: var(--mat-sys-on-surface, #1f1f1f);
    }
    .sys-surface {
      background-color: var(--mat-sys-surface, #ffffff);
      color: var(--mat-sys-on-surface, #1f1f1f);
    }
    .sys-text-secondary {
      color: var(--mat-sys-on-surface-variant, #444746);
    }
    .sys-border {
      border-color: var(--mat-sys-outline-variant, #c4c7c5);
    }
    .sys-divider {
      background-color: var(--mat-sys-outline-variant, #e0e0e0);
    }
    .text-primary {
      color: var(--mat-sys-primary, #3f51b5);
    }

    /* Stepper Styling */
    .step-text-active { color: var(--mat-sys-primary, #3f51b5); }
    .step-text-completed { color: var(--mat-sys-primary, #2e7d32); }
    .step-text-inactive { color: var(--mat-sys-on-surface-variant, #9aa0a6); }

    .step-circle-active {
      border-color: var(--mat-sys-primary, #3f51b5);
      background-color: var(--mat-sys-primary-container, #e8eaf6);
      color: var(--mat-sys-on-primary-container, #3f51b5);
    }
    .step-circle-completed {
      border-color: var(--mat-sys-primary, #2e7d32); /* Use primary or specific success color */
      background-color: var(--mat-sys-primary-container, #e8f5e9);
      color: var(--mat-sys-on-primary-container, #2e7d32);
    }
    .step-circle-inactive {
      border-color: var(--mat-sys-outline, #e0e0e0);
      color: var(--mat-sys-on-surface-variant, #9aa0a6);
    }

    /* Cards */
    .category-card:hover, .definition-item:hover {
      border-color: var(--mat-sys-primary, #3f51b5);
      background-color: var(--mat-sys-primary-container, #e8eaf6); /* Subtle tint on hover */
    }

    .definition-item.selected-def {
      border-color: var(--mat-sys-primary);
      background-color: var(--mat-sys-primary-container);
    }

    /* Info Box */
    .info-box {
      background-color: var(--mat-sys-secondary-container, #e3f2fd);
      color: var(--mat-sys-on-secondary-container, #0d47a1);
    }

    /* Dark Mode Pattern */
    :host-context(.dark) {
       --mat-sys-surface: #121212;
       --mat-sys-surface-container: #1e1e1e;
       --mat-sys-on-surface: #e3e3e3;
       --mat-sys-on-surface-variant: #c4c7c5;
       --mat-sys-outline: #444746;
       --mat-sys-outline-variant: #444746;
       --mat-sys-primary: #a8c7fa; /* Lighter primary for dark mode */
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
    { label: 'Category', completed: false },
    { label: 'Model & Driver', completed: false },
    { label: 'Optional Config', completed: false }
  ];

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
    location_label: ['']
  });

  ngOnInit() {
    this.assetService.getMachineDefinitions().subscribe(defs => {
      this.definitions = defs;
      // Extract categories
      this.machineCategories = [...new Set(defs.map(d => d.machine_category || 'Other'))].sort();

      this.filteredDefinitions$ = this.definitionSearchControl.valueChanges.pipe(
        startWith(''),
        map(val => this.filterDefinitions(val))
      );
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

  selectCategory(cat: string) {
    this.selectedCategory = cat;
    this.definitionSearchControl.setValue(''); // Reset search
    this.nextStep();
  }

  selectDefinition(def: MachineDefinition) {
    this.selectedDefinition = def;
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
      name: `${def.name} ${Math.floor(Math.random() * 100) + 1}`
    });
  }

  filterDefinitions(search: string | null): MachineDefinition[] {
    const query = (search || '').toLowerCase();
    return this.definitions.filter(d => {
      const matchesCategory = (d.machine_category || 'Other') === this.selectedCategory;
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
    if (this.currentStep === 0) return !!this.selectedCategory;
    if (this.currentStep === 1) return !!this.selectedDefinition && this.form.get('name')?.valid && this.form.get('backend_driver')?.valid ? true : false;
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
      user_configured_capabilities: JSON.stringify(val)
    });
  }

  updateConnectionInfo(val: any) {
    this.form.patchValue({
      connection_info: JSON.stringify(val)
    });
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