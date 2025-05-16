// src/app/features/manage-protocols/pages/run-new-protocol.component.ts
import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatStepperModule } from '@angular/material/stepper';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { CdkStepperModule } from '@angular/cdk/stepper';

import { RunNewProtocolService } from '@protocolsServices/run-new-protocol.service';
import {
  ProtocolInfo,
  ProtocolDetails,
  ParameterConfig,
  ProtocolAsset,
  ProtocolPrepareRequest
} from '@protocols/protocol.models';
import { Subscription } from 'rxjs';
import { finalize } from 'rxjs/operators';

// Helper function to get object keys for ngFor
export function getObjectKeys(obj: any): string[] {
  if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
    return Object.keys(obj);
  }
  return [];
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
  private runProtocolService = inject(RunNewProtocolService);
  private fb = inject(FormBuilder);
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);

  // Make Array.isArray available to the template
  public isArray = Array.isArray;

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
  preparedConfig: any = null;

  protocolSelectionForm: FormGroup;
  parameterForm: FormGroup;
  assetForm: FormGroup;
  deckForm: FormGroup;

  private subscriptions: Subscription = new Subscription();
  objectKeys = getObjectKeys; // Expose helper to template

  constructor() {
    this.protocolSelectionForm = this.fb.group({
      protocolPath: ['', Validators.required],
    });
    this.parameterForm = this.fb.group({});
    this.assetForm = this.fb.group({});
    this.deckForm = this.fb.group({
      selectedDeckLayout: [''],
      deckFile: [null]
    });
  }

  ngOnInit(): void {
    this.loadDiscoveredProtocols();
    this.loadDeckLayouts();

    const selectionSub = this.protocolSelectionForm.get('protocolPath')?.valueChanges.subscribe(path => {
      // Reset state when selection changes, before loading new details
      this.selectedProtocol = null;
      this.parameterForm = this.fb.group({});
      this.assetForm = this.fb.group({});
      this.preparedConfig = null;
      console.log('[ngOnInit] Protocol selection changed. Resetting selectedProtocol.');

      if (path) {
        this.selectedProtocolPath = path;
        this.loadProtocolDetails(path);
      } else {
        this.selectedProtocolPath = null;
      }
    });
    if (selectionSub) {
      this.subscriptions.add(selectionSub);
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  loadDiscoveredProtocols(): void {
    this.isLoadingProtocols = true;
    const sub = this.runProtocolService.discoverProtocols().pipe(
      finalize(() => this.isLoadingProtocols = false)
    ).subscribe({
      next: (protocols) => this.discoveredProtocols = protocols,
      error: (err) => this.showError('Failed to load protocols', err)
    });
    this.subscriptions.add(sub);
  }

  loadProtocolDetails(protocolPath: string): void {
    this.isLoadingDetails = true;
    // Ensure selectedProtocol is null before the async call completes
    // This was already moved to the subscription of protocolPath valueChanges
    // this.selectedProtocol = null;
    console.log(`[loadProtocolDetails] Attempting to load details for: ${protocolPath}. Current selectedProtocol:`, this.selectedProtocol);


    const sub = this.runProtocolService.getProtocolDetails(protocolPath).pipe(
      finalize(() => {
        this.isLoadingDetails = false;
        console.log('[loadProtocolDetails] Finalized API call. isLoadingDetails:', this.isLoadingDetails);
        // Log the state of selectedProtocol *after* the API call and assignment logic
        console.log('[loadProtocolDetails] Final state of this.selectedProtocol after API call:', JSON.parse(JSON.stringify(this.selectedProtocol)));
      })
    ).subscribe({
      next: (details) => {
        console.log('[loadProtocolDetails] Raw details from service:', JSON.parse(JSON.stringify(details)));

        if (!details) {
          console.error('[loadProtocolDetails] CRITICAL: Service returned null or undefined details!');
          this.selectedProtocol = null;
          this.showError('Protocol details are missing or invalid.', 'Received no data from service.');
          this.buildParameterForm(); // Build empty forms
          this.buildAssetForm();     // Build empty forms
          return;
        }

        // Normalize assets: ensure it's an array
        if (details.has_assets) {
          if (!this.isArray(details.assets)) {
            console.warn(`[loadProtocolDetails] 'has_assets' is true, but 'details.assets' is not an array. Original:`, details.assets, `. Normalizing to empty array.`);
            details.assets = []; // Normalize to prevent errors, though this indicates a data issue
          }
        } else {
          // If has_assets is false, ensure assets is an empty array for consistency
          console.log(`[loadProtocolDetails] 'has_assets' is false. Ensuring 'details.assets' is an empty array. Original:`, details.assets);
          details.assets = [];
        }

        // Normalize parameters: ensure it's an object
        if (details.has_parameters) {
          if (!details.parameters || typeof details.parameters !== 'object' || this.isArray(details.parameters)) {
            console.warn(`[loadProtocolDetails] 'has_parameters' is true, but 'details.parameters' is not a valid object. Original:`, details.parameters, `. Normalizing to empty object.`);
            details.parameters = {};
          }
        } else {
          console.log(`[loadProtocolDetails] 'has_parameters' is false. Ensuring 'details.parameters' is an empty object. Original:`, details.parameters);
          details.parameters = {};
        }

        this.selectedProtocol = details;
        console.log('[loadProtocolDetails] Successfully assigned normalized details to this.selectedProtocol.');

        this.buildParameterForm();
        this.buildAssetForm();
      },
      error: (err) => {
        this.showError(`Failed to load details for ${protocolPath}`, err);
        this.selectedProtocol = null;
        this.buildParameterForm(); // Still call to reset/clear forms
        this.buildAssetForm();
      }
    });
    this.subscriptions.add(sub);
  }

  buildParameterForm(): void {
    console.log('[buildParameterForm] Called. Current this.selectedProtocol:', JSON.parse(JSON.stringify(this.selectedProtocol)));
    if (!this.selectedProtocol || !this.selectedProtocol.has_parameters || !this.selectedProtocol.parameters || typeof this.selectedProtocol.parameters !== 'object' || this.isArray(this.selectedProtocol.parameters)) {
      console.log('[buildParameterForm] No valid parameters to build form. Resetting parameterForm.');
      this.parameterForm = this.fb.group({});
      return;
    }
    const controls: { [key: string]: any } = {};
    for (const paramName in this.selectedProtocol.parameters) {
      if (this.selectedProtocol.parameters.hasOwnProperty(paramName)) {
        const paramConfig = this.selectedProtocol.parameters[paramName];
        const validators = paramConfig.required ? [Validators.required] : [];
        controls[paramName] = [paramConfig.default ?? '', validators];
      }
    }
    this.parameterForm = this.fb.group(controls);
    console.log('[buildParameterForm] parameterForm created:', this.parameterForm.value);
  }

  buildAssetForm(): void {
    console.log('[buildAssetForm] Called. Current this.selectedProtocol:', JSON.parse(JSON.stringify(this.selectedProtocol)));

    if (!this.selectedProtocol) {
      console.warn('[buildAssetForm] No selected protocol. Resetting assetForm.');
      this.assetForm = this.fb.group({});
      return;
    }

    console.log('[buildAssetForm] selectedProtocol.has_assets:', this.selectedProtocol.has_assets);
    // Ensure selectedProtocol.assets is logged *before* the isArray check
    console.log('[buildAssetForm] selectedProtocol.assets (before isArray check):', JSON.parse(JSON.stringify(this.selectedProtocol.assets)));
    console.log('[buildAssetForm] Is selectedProtocol.assets an array?:', this.isArray(this.selectedProtocol.assets));

    if (!this.selectedProtocol.has_assets || !this.isArray(this.selectedProtocol.assets) || this.selectedProtocol.assets.length === 0) {
      console.log('[buildAssetForm] No assets to build form for, or assets is not a valid array or is empty. Resetting assetForm.');
      this.assetForm = this.fb.group({});
      return;
    }

    const controls: { [key: string]: any } = {};
    (this.selectedProtocol.assets as ProtocolAsset[]).forEach(asset => {
      if (asset && typeof asset.name === 'string') {
        controls[asset.name] = ['', asset.required ? [Validators.required] : []];
      } else {
        console.error('[buildAssetForm] Invalid asset structure found in selectedProtocol.assets:', asset);
      }
    });
    this.assetForm = this.fb.group(controls);
    console.log('[buildAssetForm] assetForm created:', this.assetForm.value);
  }

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
      this.deckForm.patchValue({ selectedDeckLayout: '' });
      this.selectedDeckLayout = null;
    }
  }

  onDeckSelectionChange(event: any): void {
    this.selectedDeckLayout = event.value;
    this.uploadedDeckFile = null;
    this.deckForm.patchValue({ deckFile: null });
  }

  async handleDeckLayout(): Promise<string | null> {
    if (this.uploadedDeckFile) {
      try {
        // Ensure toPromise() is available; for newer RxJS, use lastValueFrom or firstValueFrom
        const response = await (this.runProtocolService.uploadDeckFile(this.uploadedDeckFile) as any).toPromise();
        this.showSuccess(`Deck file "${this.uploadedDeckFile.name}" uploaded.`);
        return response?.path || null;
      } catch (err) {
        this.showError(`Failed to upload deck file`, err);
        return null;
      }
    }
    return this.selectedDeckLayout;
  }

  async prepareProtocol(): Promise<void> {
    if (!this.selectedProtocolPath) {
      this.showError('No protocol selected.');
      return;
    }
    this.isPreparing = true;
    this.preparedConfig = null;
    const deckLayoutPath = await this.handleDeckLayout();

    const request: ProtocolPrepareRequest = {
      protocol_path: this.selectedProtocolPath,
      parameters: this.parameterForm.value,
      asset_assignments: this.assetForm.value,
    };

    const sub = this.runProtocolService.prepareProtocol(request).pipe(
      finalize(() => this.isPreparing = false)
    ).subscribe({
      next: (response) => {
        if (response.status === 'ready' && response.config) {
          this.preparedConfig = response.config;
          if (deckLayoutPath && !this.preparedConfig.deck_layout_path) {
            this.preparedConfig.deck_layout_path = deckLayoutPath;
          }
          this.showSuccess('Protocol prepared. Ready to start.');
        } else {
          this.showError('Protocol preparation failed.', response.errors || 'Unknown error');
        }
      },
      error: (err) => this.showError('Failed to prepare protocol', err)
    });
    this.subscriptions.add(sub);
  }

  async startProtocol(): Promise<void> {
    if (!this.preparedConfig) {
      this.showError('Protocol not prepared. Please prepare first.');
      return;
    }
    this.isStarting = true;
    const sub = this.runProtocolService.startProtocol(this.preparedConfig).pipe(
      finalize(() => this.isStarting = false)
    ).subscribe({
      next: (response) => {
        this.showSuccess(`Protocol "${response.name}" started with status: ${response.status}`);
        this.router.navigate(['/protocols']);
      },
      error: (err) => this.showError('Failed to start protocol', err)
    });
    this.subscriptions.add(sub);
  }

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
    const detailMsg = errorDetails?.message || errorDetails?.detail || (typeof errorDetails === 'string' ? errorDetails : 'See console.');
    this.showMessage(`${message}: ${detailMsg}`, 'error-snackbar');
  }

  private showSuccess(message: string): void {
    this.showMessage(message, 'success-snackbar');
  }

  getParameterKeys(parameters: Record<string, ParameterConfig> | undefined | null): string[] {
    if (parameters && typeof parameters === 'object' && !this.isArray(parameters)) { // Use component's isArray
      return Object.keys(parameters);
    }
    return [];
  }

  getAssetNames(assets: ProtocolAsset[] | undefined | null): string[] {
    console.log('[getAssetNames] Called with assets:', JSON.parse(JSON.stringify(assets)));
    if (assets) {
      console.log('[getAssetNames] Type of assets:', typeof assets, '| IsArray:', this.isArray(assets));
    }
    if (!this.isArray(assets)) {
      console.error('[getAssetNames] Received non-array or null/undefined for assets:', assets);
      return [];
    }
    return (assets as ProtocolAsset[]).map(a => a.name);
  }

  getParamConfig(paramName: string): ParameterConfig | undefined {
    if (this.selectedProtocol && this.selectedProtocol.parameters &&
      typeof this.selectedProtocol.parameters === 'object' &&
      !this.isArray(this.selectedProtocol.parameters)) { // Use component's isArray
      return this.selectedProtocol.parameters[paramName];
    }
    return undefined;
  }

  getAssetConfig(assetName: string): ProtocolAsset | undefined {
    if (this.selectedProtocol && this.isArray(this.selectedProtocol.assets)) { // Use component's isArray
      return (this.selectedProtocol.assets as ProtocolAsset[]).find(a => a.name === assetName);
    }
    console.warn(`[getAssetConfig] selectedProtocol.assets is not an array or selectedProtocol is null. Assets:`, this.selectedProtocol?.assets);
    return undefined;
  }
}
