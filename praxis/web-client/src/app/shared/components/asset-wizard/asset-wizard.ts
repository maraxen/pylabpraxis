import { Component, OnInit, inject, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatStepperModule } from '@angular/material/stepper';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatRadioModule } from '@angular/material/radio';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { AssetService, FacetItem } from '../../../features/assets/services/asset.service';
import { ModeService } from '../../../core/services/mode.service';
import { MachineDefinition, ResourceDefinition, MachineCreate, ResourceCreate } from '../../../features/assets/models/asset.models';
import { debounceTime, distinctUntilChanged, map, startWith, switchMap } from 'rxjs/operators';
import { Observable, Subject, of, firstValueFrom } from 'rxjs';

@Component({
  selector: 'app-asset-wizard',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatStepperModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatRadioModule,
    MatCardModule,
    MatIconModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatDialogModule
  ],
  templateUrl: './asset-wizard.html',
  styleUrl: './asset-wizard.scss',
})
export class AssetWizard implements OnInit {
  private fb = inject(FormBuilder);
  private assetService = inject(AssetService);
  public modeService = inject(ModeService);
  private dialogRef = inject(MatDialogRef<AssetWizard>);

  isLoading = signal(false);

  typeStepFormGroup: FormGroup = this.fb.group({
    assetType: ['', Validators.required],
    category: ['', Validators.required]
  });

  definitionStepFormGroup: FormGroup = this.fb.group({
    definition: ['', Validators.required]
  });

  configStepFormGroup: FormGroup = this.fb.group({
    name: ['', Validators.required],
    backend: [''],
    connection_info: [''],
    location: [''],
    description: ['']
  });

  categories$: Observable<string[]> = of([]);

  private searchSubject = new Subject<string>();
  searchResults$: Observable<any[]> = of([]);
  selectedDefinition: MachineDefinition | ResourceDefinition | null = null;
  availableSimulationBackends = ['Simulated', 'Chatterbox'];

  get availableBackends(): string[] {
    if (!this.selectedDefinition || this.typeStepFormGroup.get('assetType')?.value !== 'MACHINE') {
      return [];
    }
    const mDef = this.selectedDefinition as MachineDefinition;
    const compatible = mDef.compatible_backends || [];
    const simulated = mDef.available_simulation_backends || this.availableSimulationBackends;
    return [...new Set([...compatible, ...simulated])];
  }

  isSimulatedBackend(backend: string): boolean {
    const simulated = (this.selectedDefinition as MachineDefinition)?.available_simulation_backends || this.availableSimulationBackends;
    return simulated.includes(backend);
  }

  ngOnInit() {
    // Listen to assetType changes to update categories
    this.typeStepFormGroup.get('assetType')?.valueChanges.subscribe(type => {
      this.typeStepFormGroup.get('category')?.reset();
      if (type === 'MACHINE') {
        this.categories$ = this.assetService.getMachineFacets().pipe(
          map(facets => facets.machine_category.map(f => String(f.value)))
        );
        this.configStepFormGroup.get('backend')?.setValidators([Validators.required]);
      } else if (type === 'RESOURCE') {
        this.categories$ = this.assetService.getFacets().pipe(
          map(facets => facets.plr_category.map(f => String(f.value)))
        );
        this.configStepFormGroup.get('backend')?.clearValidators();
      }
      this.configStepFormGroup.get('backend')?.updateValueAndValidity();

      // Clear search when type changes
      this.searchSubject.next('');
    });

    // Handle search logic
    this.searchResults$ = this.searchSubject.pipe(
      startWith(''),
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(query => {
        const assetType = this.typeStepFormGroup.get('assetType')?.value;
        const category = this.typeStepFormGroup.get('category')?.value;
        if (!assetType) return of([]);

        if (assetType === 'MACHINE') {
          // Filter results to only show items where plr_category === 'Machine' (to hide raw backends)
          return this.assetService.searchMachineDefinitions(query).pipe(
            map(defs => defs.filter(d => d.plr_category === 'Machine'))
          );
        } else {
          return this.assetService.searchResourceDefinitions(query, category);
        }
      })
    );

    // Also trigger search when category changes
    this.typeStepFormGroup.get('category')?.valueChanges.subscribe(() => {
      this.searchSubject.next(this.typeStepFormGroup.get('assetType')?.value === 'MACHINE' ? '' : (this.searchSubject.asObservable() as any)._value || '');
      // Wait, Subject doesn't have _value. Let's just trigger with the current query if we can, or just trigger an update.
      // Actually, switchMap will pick it up if we combine them.
    });
  }

  searchDefinitions(query: string) {
    this.searchSubject.next(query);
  }

  selectDefinition(def: MachineDefinition | ResourceDefinition) {
    this.selectedDefinition = def;
    this.definitionStepFormGroup.patchValue({ definition: def.accession_id });

    // Pre-fill config
    this.configStepFormGroup.patchValue({
      name: def.name,
      description: def.description || ''
    });

    if (this.typeStepFormGroup.get('assetType')?.value === 'MACHINE') {
      const mDef = def as MachineDefinition;
      const backends = this.availableBackends;

      if (this.modeService.isBrowserMode()) {
        const autoSelect = backends.find(b => this.isSimulatedBackend(b)) || backends[0];
        if (autoSelect) {
          this.configStepFormGroup.patchValue({ backend: autoSelect });
        }
      } else if (backends.length === 1) {
        this.configStepFormGroup.patchValue({ backend: backends[0] });
      }
    }
  }

  async createAsset() {
    if (this.isLoading()) return;

    const assetType = this.typeStepFormGroup.get('assetType')?.value;
    const category = this.typeStepFormGroup.get('category')?.value;
    const config = this.configStepFormGroup.value;

    this.isLoading.set(true);

    try {
      let createdAsset: any;
      if (assetType === 'MACHINE') {
        const machinePayload: MachineCreate = {
          name: config.name,
          machine_category: category,
          machine_type: category, // Alias for backward compatibility
          description: config.description,
          machine_definition_accession_id: this.selectedDefinition?.accession_id,
          simulation_backend_name: config.backend,
          // If it's a real backend, we might want to map it differently in a real app, 
          // but here we follow the simplified createMachine logic.
          connection_info: config.connection_info ? { address: config.connection_info } : undefined
        };
        createdAsset = await firstValueFrom(this.assetService.createMachine(machinePayload));
      } else {
        const resourcePayload: ResourceCreate = {
          name: config.name,
          resource_definition_accession_id: this.selectedDefinition?.accession_id,
        };
        createdAsset = await firstValueFrom(this.assetService.createResource(resourcePayload));
      }

      this.dialogRef.close(createdAsset);
    } catch (error) {
      console.error('Error creating asset:', error);
      // In a real app, show a snackbar or error message
    } finally {
      this.isLoading.set(false);
    }
  }

  close() {
    this.dialogRef.close();
  }
}
