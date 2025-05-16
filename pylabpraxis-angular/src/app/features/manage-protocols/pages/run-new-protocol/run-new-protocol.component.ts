// src/app/features/manage-protocols/pages/run-new-protocol.component.ts
import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormArray, AbstractControl } from '@angular/forms';
import { MatStepperModule } from '@angular/material/stepper';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar'; // For notifications
import { CdkStepperModule } from '@angular/cdk/stepper';

import { RunNewProtocolService } from '@protocolsServices/run-new-protocol.service';
import {
  ProtocolInfo,
  ProtocolDetails,
  ParameterConfig,
  ProtocolParameterType,
  ProtocolAsset,
  ProtocolPrepareRequest,
  ProtocolStartRequest
} from '@protocols/protocol.models';
import { Subscription, Observable, of, throwError } from 'rxjs';
import { catchError, finalize, tap } from 'rxjs/operators';

// Helper function to get object keys for ngFor
export function getObjectKeys(obj: any): string[] {
  return Object.keys(obj);
}

@Component({
  selector: 'app-run-new-protocol',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatStepperModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatCardModule,
    MatListModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    CdkStepperModule,
  ],
  templateUrl: './run-new-protocol.component.html',
  styleUrls: ['./run-new-protocol.component.scss'],
})
export class RunNewProtocolComponent implements OnInit, OnDestroy {
  // Inject services and FormBuilder
  private runProtocolService = inject(RunNewProtocolService);
  private fb = inject(FormBuilder);
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);

  // Component State
  isLoadingProtocols = false;
  isLoadingDetails = false;
  isPreparing = false;
  isStarting = false;

  discoveredProtocols: ProtocolInfo[] = [];
  selectedProtocol: ProtocolDetails | null = null;
  selectedProtocolPath: string | null = null;
  deckLayouts: string[] = [];
  selectedDeckLayout: string | null = null;
  uploadedDeckFile: File | null = null;
  preparedConfig: any = null; // Stores the validated config from prepare step

  // Forms
  protocolSelectionForm: FormGroup;
  parameterForm: FormGroup;
  assetForm: FormGroup;
  deckForm: FormGroup;

  // Subscriptions
  private subscriptions: Subscription = new Subscription();

  // Expose helper to template
  objectKeys = getObjectKeys;

  constructor() {
    // Initialize forms
    this.protocolSelectionForm = this.fb.group({
      protocolPath: ['', Validators.required],
    });
    this.parameterForm = this.fb.group({}); // Parameters will be added dynamically
    this.assetForm = this.fb.group({}); // Assets will be added dynamically
    this.deckForm = this.fb.group({
      selectedDeckLayout: [''],
      deckFile: [null]
    });
  }

  ngOnInit(): void {
    this.loadDiscoveredProtocols();
    this.loadDeckLayouts();

    // Subscribe to protocol selection changes
    const selectionSub = this.protocolSelectionForm.get('protocolPath')?.valueChanges.subscribe(path => {
      if (path) {
        this.selectedProtocolPath = path;
        this.loadProtocolDetails(path);
      } else {
        this.selectedProtocol = null;
        this.selectedProtocolPath = null;
        this.parameterForm = this.fb.group({}); // Reset forms
        this.assetForm = this.fb.group({});
        this.preparedConfig = null;
      }
    });
    if (selectionSub) {
      this.subscriptions.add(selectionSub);
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  // Step 1: Load and Select Protocol
  loadDiscoveredProtocols(): void {
    this.isLoadingProtocols = true;
    const sub = this.runProtocolService.discoverProtocols().pipe(
      finalize(() => this.isLoadingProtocols = false)
    ).subscribe({
      next: (protocols) => {
        this.discoveredProtocols = protocols;
      },
      error: (err) => this.showError('Failed to load protocols', err)
    });
    this.subscriptions.add(sub);
  }

  loadProtocolDetails(protocolPath: string): void {
    this.isLoadingDetails = true;
    this.selectedProtocol = null; // Reset previous selection
    this.parameterForm = this.fb.group({}); // Reset forms
    this.assetForm = this.fb.group({});
    this.preparedConfig = null;

    const sub = this.runProtocolService.getProtocolDetails(protocolPath).pipe(
      finalize(() => this.isLoadingDetails = false)
    ).subscribe({
      next: (details) => {
        this.selectedProtocol = details;
        this.buildParameterForm();
        this.buildAssetForm();
      },
      error: (err) => this.showError(`Failed to load details for ${protocolPath}`, err)
    });
    this.subscriptions.add(sub);
  }

  // Step 2: Configure Parameters
  buildParameterForm(): void {
    if (!this.selectedProtocol || !this.selectedProtocol.has_parameters) {
      this.parameterForm = this.fb.group({}); // Ensure form is empty if no params
      return;
    }
    const controls: { [key: string]: any } = {};
    for (const paramName in this.selectedProtocol.parameters) {
      if (this.selectedProtocol.parameters.hasOwnProperty(paramName)) {
        const paramConfig = this.selectedProtocol.parameters[paramName];
        const validators = [];
        if (paramConfig.required) {
          validators.push(Validators.required);
        }
        // Add more validators based on paramConfig.constraints if needed (e.g., min, max, pattern)
        // For now, just handling required.
        controls[paramName] = [paramConfig.default !== undefined ? paramConfig.default : '', validators];
      }
    }
    this.parameterForm = this.fb.group(controls);
  }

  // Step 3: Assign Assets
  buildAssetForm(): void {
    if (!this.selectedProtocol || !this.selectedProtocol.has_assets) {
      this.assetForm = this.fb.group({}); // Ensure form is empty if no assets
      return;
    }
    const controls: { [key: string]: any } = {};
    this.selectedProtocol.assets.forEach(asset => {
      const validators = [];
      if (asset.required) {
        validators.push(Validators.required);
      }
      controls[asset.name] = ['', validators]; // Asset assignment will be a string (name/ID of assigned asset)
    });
    this.assetForm = this.fb.group(controls);
  }

  // Step 4: Deck Layout
  loadDeckLayouts(): void {
    const sub = this.runProtocolService.getDeckLayouts().subscribe({
      next: (layouts) => this.deckLayouts = layouts,
      error: (err) => this.showError('Failed to load deck layouts', err)
    });
    this.subscriptions.add(sub);
  }

  onDeckFileSelected(event: Event): void {
    const element = event.currentTarget as HTMLInputElement;
    const fileList: FileList | null = element.files;
    if (fileList && fileList.length > 0) {
      this.uploadedDeckFile = fileList[0];
      this.deckForm.patchValue({ selectedDeckLayout: '' }); // Clear selection if file is chosen
      this.selectedDeckLayout = null;
    }
  }

  onDeckSelectionChange(event: any): void {
    this.selectedDeckLayout = event.value;
    this.uploadedDeckFile = null; // Clear file if selection is made
    this.deckForm.patchValue({ deckFile: null });
  }

  async handleDeckLayout(): Promise<string | null> {
    if (this.uploadedDeckFile) {
      try {
        const response = await this.runProtocolService.uploadDeckFile(this.uploadedDeckFile).toPromise();
        this.showSuccess(`Deck file "${this.uploadedDeckFile.name}" uploaded successfully.`);
        return response?.path || null; // Return path of uploaded deck file
      } catch (err) {
        this.showError(`Failed to upload deck file "${this.uploadedDeckFile.name}"`, err);
        return null;
      }
    } else if (this.selectedDeckLayout) {
      return this.selectedDeckLayout; // Return path of selected existing deck file
    }
    return null; // No deck layout specified or an error occurred
  }


  // Step 5: Prepare Protocol
  async prepareProtocol(): Promise<void> {
    if (!this.selectedProtocolPath) {
      this.showError('No protocol selected.');
      return;
    }

    this.isPreparing = true;
    this.preparedConfig = null;

    const deckLayoutPath = await this.handleDeckLayout();
    // If deckLayoutPath is null and a deck was required by the protocol, this might be an issue.
    // For now, we proceed; backend validation should catch this if it's a problem.

    const request: ProtocolPrepareRequest = {
      protocol_path: this.selectedProtocolPath,
      parameters: this.parameterForm.value,
      asset_assignments: this.assetForm.value,
      // deck_layout_path: deckLayoutPath, // TODO: Add to ProtocolPrepareRequest if backend supports it
    };
    // Note: The backend /prepare endpoint doesn't explicitly take deck_layout_path yet.
    // This might need to be part of the 'parameters' or a general config blob if the protocol itself reads it.
    // Or, the startProtocol step might consume it. For now, we've uploaded/selected it.

    const sub = this.runProtocolService.prepareProtocol(request).pipe(
      finalize(() => this.isPreparing = false)
    ).subscribe({
      next: (response) => {
        if (response.status === 'ready' && response.config) {
          this.preparedConfig = response.config;
          this.showSuccess('Protocol prepared successfully. Ready to start.');
          // Optionally, move to next step in stepper automatically
        } else {
          this.showError('Protocol preparation failed.', response.errors || 'Unknown error');
          this.preparedConfig = null;
        }
      },
      error: (err) => {
        this.showError('Failed to prepare protocol', err);
        this.preparedConfig = null;
      }
    });
    this.subscriptions.add(sub);
  }

  // Step 6: Start Protocol
  async startProtocol(): Promise<void> {
    if (!this.preparedConfig) {
      this.showError('Protocol not prepared or preparation failed. Please prepare first.');
      return;
    }

    this.isStarting = true;

    // The `preparedConfig` should be the validated configuration from the backend.
    // It might need to be augmented with the deck_layout_path if the start endpoint expects it
    // and it wasn't part of the `prepare` step's direct input/output for the config object.
    // For now, let's assume `preparedConfig` is what `startProtocol` needs.
    // If deck layout needs to be explicitly passed to start, adjust here:
    // const finalConfigForStart = { ...this.preparedConfig, deck_layout_path: await this.handleDeckLayout() };

    const sub = this.runProtocolService.startProtocol(this.preparedConfig).pipe(
      finalize(() => this.isStarting = false)
    ).subscribe({
      next: (response) => {
        this.showSuccess(`Protocol "${response.name}" started with status: ${response.status}`);
        // Optionally, navigate away or reset the form
        this.router.navigate(['/protocols']); // Navigate to dashboard after starting
      },
      error: (err) => this.showError('Failed to start protocol', err)
    });
    this.subscriptions.add(sub);
  }


  // Utility for showing snackbar messages
  private showMessage(message: string, panelClass: string = 'info-snackbar'): void {
    this.snackBar.open(message, 'Close', {
      duration: 5000,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: [panelClass]
    });
  }

  private showError(message: string, errorDetails?: any): void {
    console.error(message, errorDetails);
    const displayMessage = errorDetails?.message || errorDetails?.detail || (typeof errorDetails === 'string' ? errorDetails : 'See console for details.');
    this.showMessage(`${message}: ${displayMessage}`, 'error-snackbar');
  }

  private showSuccess(message: string): void {
    this.showMessage(message, 'success-snackbar');
  }

  // Helper to get parameter keys for the template
  getParameterKeys(parameters: Record<string, ParameterConfig> | undefined | null): string[] {
    return parameters ? Object.keys(parameters) : [];
  }

  // Helper to get asset names for the template
  getAssetNames(assets: ProtocolAsset[] | undefined | null): string[] {
    return assets ? assets.map(a => a.name) : [];
  }

  // Get a specific parameter config
  getParamConfig(paramName: string): ParameterConfig | undefined {
    return this.selectedProtocol?.parameters?.[paramName];
  }

  // Get a specific asset config
  getAssetConfig(assetName: string): ProtocolAsset | undefined {
    return this.selectedProtocol?.assets?.find(a => a.name === assetName);
  }
}
