import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, AbstractControl, ValidationErrors, FormControl } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
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
    MatAutocompleteModule
  ],
  template: `
    <h2 mat-dialog-title>Add New Instrument</h2>
    <mat-dialog-content>
      <form [formGroup]="form" class="flex flex-col gap-4 py-4">
        <mat-form-field appearance="outline">
          <mat-label>Name</mat-label>
          <input matInput formControlName="name" placeholder="e.g. Robot 1">
          <mat-error *ngIf="form.get('name')?.hasError('required')">Name is required</mat-error>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Machine Type (PLR Definition)</mat-label>
          <input
            matInput
            [formControl]="definitionSearchControl"
            [matAutocomplete]="defAuto"
            placeholder="Search by name or FQN...">
          <mat-autocomplete
            #defAuto="matAutocomplete"
            [displayWith]="displayDefinition.bind(this)"
            (optionSelected)="onDefinitionSelected($event.option.value)">
            <mat-option *ngFor="let def of filteredDefinitions$ | async" [value]="def">
              <span style="font-weight: 500;">{{ getDisplayName(def) }}</span>
              <span style="font-size: 12px; opacity: 0.6; margin-left: 8px;" *ngIf="def.fqn">{{ getShortFqn(def.fqn) }}</span>
            </mat-option>
            <mat-option *ngIf="(filteredDefinitions$ | async)?.length === 0" disabled>
              No matching definitions found
            </mat-option>
          </mat-autocomplete>
          <mat-hint>Select a PLR machine type to auto-populate fields</mat-hint>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Model</mat-label>
          <input matInput formControlName="model" placeholder="e.g. Opentrons Flex">
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Manufacturer</mat-label>
          <input matInput formControlName="manufacturer" placeholder="e.g. Opentrons">
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Description</mat-label>
          <textarea matInput formControlName="description" rows="2" placeholder="Optional description"></textarea>
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
          <mat-label>Connection Info (JSON)</mat-label>
          <textarea matInput formControlName="connection_info" placeholder='{"host": "127.0.0.1", "port": 3000}' rows="4"></textarea>
           <mat-hint>Enter optional connection details as JSON</mat-hint>
           <mat-error *ngIf="form.get('connection_info')?.hasError('invalidJson')">Invalid JSON format</mat-error>
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
  definitionSearchControl = new FormControl<string | MachineDefinition>('');
  filteredDefinitions$: Observable<MachineDefinition[]> = of([]);

  form = this.fb.group({
    name: ['', Validators.required],
    model: [''],
    manufacturer: [''],
    description: [''],
    status: [MachineStatus.OFFLINE],
    connection_info: ['', jsonValidator],
    machine_definition_accession_id: [null as string | null]
  });

  ngOnInit() {
    // Load machine definitions
    this.assetService.getMachineDefinitions().subscribe(defs => {
      this.definitions = defs;
      // Setup filtering after definitions are loaded
      this.filteredDefinitions$ = this.definitionSearchControl.valueChanges.pipe(
        startWith(''),
        map(value => this.filterDefinitions(value))
      );
    });
  }

  private filterDefinitions(value: string | MachineDefinition | null): MachineDefinition[] {
    if (!value) {
      return this.definitions;
    }

    const filterValue = typeof value === 'string'
      ? value.toLowerCase()
      : value.name.toLowerCase();

    return this.definitions.filter(def =>
      def.name.toLowerCase().includes(filterValue) ||
      (def.fqn && def.fqn.toLowerCase().includes(filterValue)) ||
      (def.manufacturer && def.manufacturer.toLowerCase().includes(filterValue))
    );
  }

  displayDefinition(def: MachineDefinition | null): string {
    if (!def) return '';
    return this.getDisplayName(def);
  }

  getDisplayName(def: MachineDefinition): string {
    // Use the last part of FQN as the display name (factory function name)
    if (def.fqn) {
      const parts = def.fqn.split('.');
      return parts[parts.length - 1];
    }
    return def.name;
  }

  getShortFqn(fqn: string): string {
    // Show module path without the function name
    const parts = fqn.split('.');
    if (parts.length > 2) {
      return parts.slice(0, -1).join('.');
    }
    return fqn;
  }

  onDefinitionSelected(def: MachineDefinition) {
    // Auto-populate form fields from the selected definition
    this.form.patchValue({
      model: def.model || def.name,
      manufacturer: def.manufacturer || '',
      description: def.description || '',
      machine_definition_accession_id: def.accession_id
    });
  }

  save() {
    if (this.form.valid) {
      const value = this.form.value;

      let connectionInfo = {};
      if (value.connection_info) {
        connectionInfo = JSON.parse(value.connection_info); // Already validated by jsonValidator
      }

      this.dialogRef.close({
          ...value,
          connection_info: connectionInfo
      });
    }
  }
}