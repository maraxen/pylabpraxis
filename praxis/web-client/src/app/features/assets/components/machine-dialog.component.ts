import { Component, inject, OnInit } from '@angular/core';
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
import { MachineStatus, MachineDefinition } from '../models/asset.models';
import { AssetService } from '../services/asset.service';
import { Observable, map, startWith, of } from 'rxjs';

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
    MatDividerModule
  ],
  template: `
    <h2 mat-dialog-title>Add New Machine</h2>
    <mat-dialog-content>
      <form [formGroup]="form" class="flex flex-col gap-4 py-4">
        
        <!-- Step 1: Type & Manufacturer Selection (Collapsible Logic) -->
        <mat-form-field appearance="outline">
          <mat-label>Search Machine Type</mat-label>
          <input
            matInput
            [formControl]="definitionSearchControl"
            [matAutocomplete]="defAuto"
            placeholder="Search by name, manufacturer or capability...">
          <mat-autocomplete
            #defAuto="matAutocomplete"
            [displayWith]="displayDefinition.bind(this)"
            (optionSelected)="onDefinitionSelected($event.option.value)">
            
            <mat-optgroup *ngFor="let group of groupedDefinitions$ | async" [label]="group.type">
              <mat-option *ngFor="let def of group.definitions" [value]="def">
                <div class="flex flex-col">
                  <span>{{ def.name }}</span>
                  <span class="text-xs opacity-60">{{ def.manufacturer }} - {{ def.model || getShortFqn(def.fqn || '') }}</span>
                </div>
              </mat-option>
            </mat-optgroup>

            <mat-option *ngIf="(groupedDefinitions$ | async)?.length === 0" disabled>
              No matching machines found
            </mat-option>
          </mat-autocomplete>
          <mat-hint>Search specifically (e.g. "96-channel", "Hamilton")</mat-hint>
        </mat-form-field>

        <!-- Selected Machine Details Card -->
        <div *ngIf="selectedDefinition" class="bg-gray-50 border rounded-lg p-3 flex flex-col gap-2">
            <div class="flex justify-between items-start">
                <div class="font-medium text-sm text-gray-700">Capabilities</div>
                 <div class="text-xs text-gray-500 font-mono">{{ getShortFqn(selectedDefinition.fqn || '') }}</div>
            </div>
            
            <mat-chip-listbox>
                <mat-chip-option *ngFor="let channel of selectedDefinition.capabilities?.channels" color="accent" selected>
                    {{ channel }}-channel
                </mat-chip-option>
                 <mat-chip-option *ngFor="let mod of selectedDefinition.capabilities?.modules" selected>
                    {{ mod }}
                </mat-chip-option>
                <mat-chip-option *ngIf="!selectedDefinition.capabilities" disabled>
                    Standard Config
                </mat-chip-option>
            </mat-chip-listbox>
        </div>

        <mat-form-field appearance="outline">
          <mat-label>Name</mat-label>
          <input matInput formControlName="name" placeholder="e.g. Robot 1">
          <mat-error *ngIf="form.get('name')?.hasError('required')">Name is required</mat-error>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Driver / Backend</mat-label>
           <mat-select formControlName="backend_driver">
              <mat-option [value]="'sim'" class="font-mono text-sm">
                <span class="font-semibold text-blue-600">Simulated</span> (ChatterBoxBackend)
              </mat-option>
              <ng-container *ngIf="selectedDefinition?.compatible_backends?.length">
                  <mat-divider></mat-divider>
                  <mat-option *ngFor="let backend of selectedDefinition?.compatible_backends" [value]="backend" class="font-mono text-xs">
                     {{ getShortBackendName(backend) }}
                  </mat-option>
              </ng-container>
           </mat-select>
           <mat-hint>Select 'Simulated' for offline/testing mode.</mat-hint>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Status</mat-label>
          <mat-select formControlName="status">
              <mat-option [value]="MachineStatus.OFFLINE">Offline</mat-option>
              <mat-option [value]="MachineStatus.IDLE">Idle</mat-option>
              <mat-option [value]="MachineStatus.RUNNING">Running</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Connection Info (JSON) - Advanced</mat-label>
          <textarea matInput formControlName="connection_info" placeholder='{"host": "127.0.0.1", "port": 3000}' rows="2"></textarea>
           <mat-error *ngIf="form.get('connection_info')?.hasError('invalidJson')">Invalid JSON format</mat-error>
        </mat-form-field>

        <mat-form-field appearance="outline" *ngIf="selectedDefinition">
          <mat-label>User Configured Capabilities (JSON)</mat-label>
          <textarea matInput formControlName="user_configured_capabilities" placeholder='{"has_iswap": true, "has_core96": true}' rows="2"></textarea>
           <mat-error *ngIf="form.get('user_configured_capabilities')?.hasError('invalidJson')">Invalid JSON format</mat-error>
           <mat-hint>Configure optional modules (e.g. iSWAP, CoRe96) for this specific machine unit.</mat-hint>
        </mat-form-field>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button mat-flat-button color="primary" [disabled]="form.invalid" (click)="save()">Save</button>
    </mat-dialog-actions>
  `
})
export class MachineDialogComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<MachineDialogComponent>);
  private assetService = inject(AssetService);

  MachineStatus = MachineStatus; // Expose enum to template

  definitions: MachineDefinition[] = [];
  selectedDefinition: MachineDefinition | null = null;
  definitionSearchControl = new FormControl<string | MachineDefinition>('');

  // Grouped definitions for UI
  groupedDefinitions$: Observable<{ type: string, definitions: MachineDefinition[] }[]> = of([]);

  form = this.fb.group({
    name: ['', Validators.required],
    model: [''],
    manufacturer: [''],
    description: [''],
    status: [MachineStatus.OFFLINE],
    backend_driver: ['sim'], // Default to simulated
    connection_info: ['', jsonValidator],
    user_configured_capabilities: ['', jsonValidator],
    machine_definition_accession_id: [null as string | null]
  });

  ngOnInit() {
    // Load machine definitions
    this.assetService.getMachineDefinitions().subscribe(defs => {
      this.definitions = defs;
      // Setup filtering
      this.groupedDefinitions$ = this.definitionSearchControl.valueChanges.pipe(
        startWith(''),
        map(value => this.filterAndGroupDefinitions(value))
      );
    });
  }

  private filterAndGroupDefinitions(value: string | MachineDefinition | null): { type: string, definitions: MachineDefinition[] }[] {
    const filterValue = (!value || typeof value !== 'string') ? '' : value.toLowerCase();

    const filtered = this.definitions.filter(def => {
      if (!filterValue) return true;
      return (
        def.name.toLowerCase().includes(filterValue) ||
        (def.fqn && def.fqn.toLowerCase().includes(filterValue)) ||
        (def.manufacturer && def.manufacturer.toLowerCase().includes(filterValue)) ||
        // Search capability chips too
        (def.capabilities?.modules && def.capabilities.modules.some((m: string) => m.toLowerCase().includes(filterValue)))
      );
    });

    // Group by Manufacturer for now, or Category if available?
    // User requested: Type -> Manufacturer -> Model.
    // Assuming 'machine_category' exists, if not use a conceptual grouping.
    // Since we don't have a strong 'Type' field on all definitions yet, let's group by Manufacturer.
    // Or if manufacturer is missing, 'Other'.

    const groups: { [key: string]: MachineDefinition[] } = {};

    filtered.forEach(def => {
      const key = def.manufacturer || 'General';
      if (!groups[key]) groups[key] = [];
      groups[key].push(def);
    });

    return Object.keys(groups).sort().map(key => ({
      type: key,
      definitions: groups[key]
    }));
  }

  displayDefinition(def: MachineDefinition | null): string {
    if (!def) return '';
    return def.name;
  }

  getShortFqn(fqn: string): string {
    // Show module path without the function name
    const parts = fqn.split('.');
    if (parts.length > 2) {
      return parts.slice(-2).join('.');
    }
    return fqn;
  }

  getShortBackendName(fqn: string): string {
    const parts = fqn.split('.');
    return parts[parts.length - 1];
  }

  onDefinitionSelected(def: MachineDefinition) {
    this.selectedDefinition = def;
    // Auto-populate form fields from the selected definition
    this.form.patchValue({
      model: def.model || def.name,
      manufacturer: def.manufacturer || '',
      description: def.description || '',
      machine_definition_accession_id: def.accession_id,
      backend_driver: 'sim', // Reset to sim on new selection
    });
  }

  save() {
    if (this.form.valid) {
      const value = this.form.value;

      let connectionInfo: any = {};
      if (value.connection_info) {
        connectionInfo = JSON.parse(value.connection_info);
      }

      // Inject backend driver selection into connection_info
      // This is the contract we established: backend info goes here.
      if (value.backend_driver) {
        connectionInfo['backend_fqn'] = value.backend_driver;
        if (value.backend_driver === 'sim') {
          // Maybe explicit flag for simulation override?
          // But 'sim' is just a backend choice here. 
          // Ideally we shouldn't set is_simulation_override unless explicitly asked, 
          // but selecting 'sim' driver implies it.
          // Let's leave is_simulation_override to the separate flag if we add it, or infer it.
        }
      }

      let userConfiguredCapabilities: any = null;
      if (value.user_configured_capabilities) {
        userConfiguredCapabilities = JSON.parse(value.user_configured_capabilities);
      }

      this.dialogRef.close({
        ...value,
        connection_info: connectionInfo,
        user_configured_capabilities: userConfiguredCapabilities
      });
    }
  }
}