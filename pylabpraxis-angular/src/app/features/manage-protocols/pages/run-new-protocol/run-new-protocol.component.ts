// src/app/features/manage-protocols/pages/run-new-protocol.component.ts
import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormArray, AbstractControl, FormControl } from '@angular/forms';
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
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CdkStepperModule } from '@angular/cdk/stepper';

import { RunNewProtocolService } from '@protocolsServices/run-new-protocol.service';
import {
  ProtocolInfo,
  ProtocolDetails,
  ParameterConfig,
  ProtocolAsset,
  ProtocolPrepareRequest,
  ProtocolParameterType
} from '@protocols/protocol.models';
import { Subscription } from 'rxjs';
import { finalize } from 'rxjs/operators';

export function getObjectKeys(obj: any): string[] {
  if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
    return Object.keys(obj);
  }
  return [];
}

interface GroupedParameter {
  type: ProtocolParameterType | 'numeric';
  title: string;
  parameters: { name: string; config: ParameterConfig }[];
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
    MatCheckboxModule,
    MatTooltipModule,
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

  groupedParameters: GroupedParameter[] = [];

  private subscriptions: Subscription = new Subscription();
  objectKeys = getObjectKeys;

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
      this.selectedProtocol = null;
      this.parameterForm = this.fb.group({});
      this.assetForm = this.fb.group({});
      this.preparedConfig = null;
      this.groupedParameters = [];
      console.log('[ngOnInit] Protocol selection changed. Resetting state.');

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
    console.log(`[loadProtocolDetails] Attempting to load details for: ${protocolPath}.`);

    const sub = this.runProtocolService.getProtocolDetails(protocolPath).pipe(
      finalize(() => {
        this.isLoadingDetails = false;
        console.log('[loadProtocolDetails] Finalized API call.');
      })
    ).subscribe({
      next: (details) => {
        console.log('[loadProtocolDetails] Raw details from service:', JSON.parse(JSON.stringify(details)));

        if (!details) {
          console.error('[loadProtocolDetails] CRITICAL: Service returned null/undefined details!');
          this.selectedProtocol = null;
          this.showError('Protocol details are missing or invalid.', 'Received no data.');
          this.groupedParameters = [];
          this.parameterForm = this.fb.group({});
          this.assetForm = this.fb.group({});
          return;
        }

        details.assets = (details.has_assets && this.isArray(details.assets)) ? details.assets : [];
        details.parameters = (details.has_parameters && details.parameters && typeof details.parameters === 'object' && !this.isArray(details.parameters)) ? details.parameters : {};

        this.selectedProtocol = details;
        console.log('[loadProtocolDetails] Assigned normalized details to this.selectedProtocol.');

        this.groupParameters();
        this.buildParameterForm();
        this.buildAssetForm();
      },
      error: (err) => {
        this.showError(`Failed to load details for ${protocolPath}`, err);
        this.selectedProtocol = null;
        this.groupedParameters = [];
        this.parameterForm = this.fb.group({});
        this.assetForm = this.fb.group({});
      }
    });
    this.subscriptions.add(sub);
  }

  groupParameters(): void {
    this.groupedParameters = [];
    if (!this.selectedProtocol || !this.selectedProtocol.parameters) {
      console.log('[groupParameters] No selected protocol or parameters to group.');
      return;
    }

    const parameters = this.selectedProtocol.parameters;
    const tempGroups: Record<string, { name: string; config: ParameterConfig }[]> = {
      string: [], numeric: [], boolean: [], array: [], dict: [], other: []
    };

    for (const paramName in parameters) {
      if (parameters.hasOwnProperty(paramName)) {
        const config = parameters[paramName];
        if (!config || !config.type) {
          console.warn(`[groupParameters] Param '${paramName}' has invalid/missing config/type. SKIPPING. Config:`, JSON.parse(JSON.stringify(config)));
          continue;
        }
        const item = { name: paramName, config };
        switch (config.type) {
          case 'string': tempGroups['string'].push(item); break;
          case 'integer':
          case 'float':
          case 'number': tempGroups['numeric'].push(item); break;
          case 'boolean': tempGroups['boolean'].push(item); break;
          case 'array': tempGroups['array'].push(item); break;
          case 'dict': tempGroups['dict'].push(item); break;
          default:
            console.warn(`[groupParameters] Param '${paramName}' has unknown type '${config.type}'. Grouping as 'other'.`);
            tempGroups['other'].push(item);
            break;
        }
      }
    }

    if (tempGroups['string'].length) this.groupedParameters.push({ type: 'string', title: 'String Parameters', parameters: tempGroups['string'] });
    if (tempGroups['numeric'].length) this.groupedParameters.push({ type: 'numeric', title: 'Numeric Parameters', parameters: tempGroups['numeric'] });
    if (tempGroups['boolean'].length) this.groupedParameters.push({ type: 'boolean', title: 'Boolean Parameters', parameters: tempGroups['boolean'] });
    if (tempGroups['array'].length) this.groupedParameters.push({ type: 'array', title: 'Array Parameters', parameters: tempGroups['array'] });
    if (tempGroups['dict'].length) this.groupedParameters.push({ type: 'dict', title: 'Dictionary Parameters', parameters: tempGroups['dict'] });
    if (tempGroups['other'].length) this.groupedParameters.push({ type: 'string', title: 'Other Parameters', parameters: tempGroups['other'] });

    console.log('[groupParameters] Completed. Grouped parameters for template:', JSON.parse(JSON.stringify(this.groupedParameters)));
  }

  buildParameterForm(): void {
    const newParameterFormControls: { [key: string]: AbstractControl } = {};
    let hasAnyParamsDefined = false;

    if (this.selectedProtocol && this.selectedProtocol.has_parameters && this.selectedProtocol.parameters) {
      const protocolParams = this.selectedProtocol.parameters;
      console.log('[buildParameterForm] Starting for parameters:', JSON.parse(JSON.stringify(protocolParams)));

      for (const paramName in protocolParams) {
        if (protocolParams.hasOwnProperty(paramName)) {
          hasAnyParamsDefined = true;
          const paramConfig = protocolParams[paramName];

          if (!paramConfig || !paramConfig.type) {
            console.error(`[buildParameterForm] CRITICAL: Parameter '${paramName}' has invalid config or missing type. IT WILL BE SKIPPED in form generation. Config:`, JSON.parse(JSON.stringify(paramConfig)));
            continue; // Skip this parameter, it won't be added to the form.
          }

          const validators = paramConfig.required ? [Validators.required] : [];
          let defaultValue = paramConfig.default;

          if (paramConfig.type === 'array') {
            const arrayItems = (defaultValue && Array.isArray(defaultValue) ? defaultValue : []);
            const arrayControls = arrayItems.map((item: any) => this.fb.control(item, paramConfig.required ? Validators.required : null));
            newParameterFormControls[paramName] = this.fb.array(arrayControls, validators);
            console.log(`[buildParameterForm] Added FormArray for array param '${paramName}'`);
          } else if (paramConfig.type === 'dict') {
            const dictItems = (defaultValue && typeof defaultValue === 'object' && !Array.isArray(defaultValue) ? defaultValue : {});
            const dictControls: FormGroup[] = [];
            Object.entries(dictItems).forEach(([key, value]) => {
              dictControls.push(this.fb.group({
                key: [key, Validators.required],
                value: [value, paramConfig.required ? Validators.required : null]
              }));
            });
            newParameterFormControls[paramName] = this.fb.array(dictControls, validators);
            console.log(`[buildParameterForm] Added FormArray for dict param '${paramName}'`);
          } else if (paramConfig.type === 'boolean') {
            newParameterFormControls[paramName] = this.fb.control(defaultValue ?? false, validators);
            console.log(`[buildParameterForm] Added FormControl for boolean param '${paramName}'`);
          } else { // Covers string, integer, float, number, and 'other' types
            newParameterFormControls[paramName] = this.fb.control(defaultValue ?? '', validators);
            console.log(`[buildParameterForm] Added FormControl for ${paramConfig.type} param '${paramName}'`);
          }
        }
      }
    } else {
      console.log('[buildParameterForm] Conditions not met: No selected protocol, or has_parameters is false, or parameters object is missing.');
    }

    if (!hasAnyParamsDefined && this.selectedProtocol && this.selectedProtocol.has_parameters) {
      console.log('[buildParameterForm] Protocol indicates it has parameters, but none were found or processed. Resulting form will be empty.');
    }

    this.parameterForm = this.fb.group(newParameterFormControls);
    console.log('[buildParameterForm] FINAL parameterForm assigned. Value:', this.parameterForm.value);
    const finalFormControlKeys = Object.keys(this.parameterForm.controls);
    console.log('[buildParameterForm] FINAL parameterForm controls keys:', finalFormControlKeys);

    // Crucial Debugging Step: Compare what the template will try to render vs. what's in the form
    const groupedParamNamesForTemplate = new Set<string>();
    this.groupedParameters.forEach(g => g.parameters.forEach(p => groupedParamNamesForTemplate.add(p.name)));

    console.log('[buildParameterForm] DEBUG: Parameter names template will try to render (from groupedParameters):', Array.from(groupedParamNamesForTemplate));

    groupedParamNamesForTemplate.forEach(name => {
      if (!finalFormControlKeys.includes(name)) {
        console.error(`[buildParameterForm] DEBUG MISMATCH: Parameter '${name}' is in groupedParameters (template will try to render it) but is MISSING from the final parameterForm.controls! This is likely the cause of 'registerOnChange' errors.`);
      }
    });

    finalFormControlKeys.forEach(name => {
      if (!groupedParamNamesForTemplate.has(name) && this.selectedProtocol?.parameters?.hasOwnProperty(name)) {
        console.warn(`[buildParameterForm] DEBUG INFO: Parameter '${name}' is in parameterForm.controls but MISSING from groupedParameters. This means it was in protocol definition but skipped by groupParameters() (e.g. bad type).`);
      } else if (!groupedParamNamesForTemplate.has(name) && !this.selectedProtocol?.parameters?.hasOwnProperty(name)) {
        // This case should ideally not happen if form is reset properly
        console.warn(`[buildParameterForm] DEBUG INFO: Parameter '${name}' is in parameterForm.controls but NOT in groupedParameters AND NOT in current protocol definition. Potentially a stale control if form wasn't fully reset.`);
      }
    });
  }

  private safeGetFormArray(paramName: string): FormArray | null {
    if (!this.parameterForm) {
      console.error(`[safeGetFormArray] parameterForm is NULL for '${paramName}'.`);
      return null;
    }
    const control = this.parameterForm.get(paramName);
    if (!control) {
      console.error(`[safeGetFormArray] Control '${paramName}' does NOT EXIST in parameterForm. Available:`, Object.keys(this.parameterForm.controls));
      return null;
    }
    if (control instanceof FormArray) {
      return control;
    }
    console.error(`[safeGetFormArray] Control '${paramName}' IS NOT a FormArray. It is: ${control.constructor.name}. Value:`, control.value);
    return null;
  }

  getArrayControls(paramName: string): AbstractControl[] {
    const formArray = this.safeGetFormArray(paramName);
    return formArray ? formArray.controls : [];
  }

  addArrayItem(paramName: string, paramConfig: ParameterConfig): void {
    const formArray = this.safeGetFormArray(paramName);
    if (formArray) {
      let newItemDefault: any = '';
      if (paramConfig.constraints?.subvariables?.['0']?.type) {
        const itemType = paramConfig.constraints.subvariables['0'].type;
        if (itemType === 'number' || itemType === 'integer' || itemType === 'float') newItemDefault = 0;
        else if (itemType === 'boolean') newItemDefault = false;
      }
      formArray.push(this.fb.control(newItemDefault, paramConfig.required ? Validators.required : null));
    } else {
      console.error(`[addArrayItem] Cannot add item: FormArray for '${paramName}' not found or invalid.`);
    }
  }

  removeArrayItem(paramName: string, index: number): void {
    const formArray = this.safeGetFormArray(paramName);
    if (formArray) {
      formArray.removeAt(index);
    } else {
      console.error(`[removeArrayItem] Cannot remove item: FormArray for '${paramName}' not found or invalid.`);
    }
  }

  getDictControls(paramName: string): AbstractControl[] {
    const formArray = this.safeGetFormArray(paramName);
    return formArray ? formArray.controls : [];
  }

  addDictItem(paramName: string, paramConfig: ParameterConfig): void {
    const formArray = this.safeGetFormArray(paramName);
    if (formArray) {
      formArray.push(this.fb.group({
        key: ['', Validators.required],
        value: ['', paramConfig.required ? Validators.required : null]
      }));
    } else {
      console.error(`[addDictItem] Cannot add dict item: FormArray for '${paramName}' not found or invalid.`);
    }
  }

  removeDictItem(paramName: string, index: number): void {
    const formArray = this.safeGetFormArray(paramName);
    if (formArray) {
      formArray.removeAt(index);
    } else {
      console.error(`[removeDictItem] Cannot remove dict item: FormArray for '${paramName}' not found or invalid.`);
    }
  }

  buildAssetForm(): void {
    if (!this.selectedProtocol || !this.selectedProtocol.has_assets || !this.isArray(this.selectedProtocol.assets) || this.selectedProtocol.assets.length === 0) {
      this.assetForm = this.fb.group({});
      return;
    }
    const controls: { [key: string]: any } = {};
    (this.selectedProtocol.assets as ProtocolAsset[]).forEach(asset => {
      if (asset && typeof asset.name === 'string') {
        controls[asset.name] = ['', asset.required ? [Validators.required] : []];
      } else {
        console.error('[buildAssetForm] Invalid asset structure:', asset);
      }
    });
    this.assetForm = this.fb.group(controls);
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

  prepareProtocolFormValues(): Record<string, any> {
    if (!this.parameterForm) return {};
    const rawValues = this.parameterForm.getRawValue();
    const processedValues: Record<string, any> = {};

    for (const paramName in rawValues) {
      if (rawValues.hasOwnProperty(paramName) && this.selectedProtocol?.parameters[paramName]) {
        const paramConfig = this.selectedProtocol.parameters[paramName];
        const value = rawValues[paramName];

        if (paramConfig.type === 'dict') {
          const dictObject: Record<string, any> = {};
          if (Array.isArray(value)) {
            value.forEach((pair: { key: string, value: any }) => {
              if (pair.key) {
                dictObject[pair.key] = pair.value;
              }
            });
          }
          processedValues[paramName] = dictObject;
        } else {
          processedValues[paramName] = value;
        }
      } else if (rawValues.hasOwnProperty(paramName)) {
        console.warn(`[prepareProtocolFormValues] Param '${paramName}' in form but not in selectedProtocol.parameters.`);
        processedValues[paramName] = rawValues[paramName];
      }
    }
    console.log('[prepareProtocolFormValues] Processed parameters:', processedValues);
    return processedValues;
  }


  async prepareProtocol(): Promise<void> {
    if (!this.selectedProtocolPath) {
      this.showError('No protocol selected.');
      return;
    }
    if (!this.parameterForm.valid) {
      this.showError('Parameter form is invalid. Please check fields.');
      this.parameterForm.markAllAsTouched();
      return;
    }
    this.isPreparing = true;
    this.preparedConfig = null;
    const deckLayoutPath = await this.handleDeckLayout();
    const processedParameters = this.prepareProtocolFormValues();

    const request: ProtocolPrepareRequest = {
      protocol_path: this.selectedProtocolPath,
      parameters: processedParameters,
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
    const detailMsg = errorDetails?.message || errorDetails?.error?.detail || errorDetails?.detail || (typeof errorDetails === 'string' ? errorDetails : 'See console for full error object.');
    this.showMessage(`${message}: ${detailMsg}`, 'error-snackbar');
  }

  private showSuccess(message: string): void {
    this.showMessage(message, 'success-snackbar');
  }

  getParameterKeys(parameters: Record<string, ParameterConfig> | undefined | null): string[] {
    if (parameters && typeof parameters === 'object' && !this.isArray(parameters)) {
      return Object.keys(parameters);
    }
    return [];
  }

  getParamConfig(paramName: string): ParameterConfig | undefined {
    if (this.selectedProtocol?.parameters) {
      return this.selectedProtocol.parameters[paramName];
    }
    return undefined;
  }

  getAssetConfig(assetName: string): ProtocolAsset | undefined {
    if (this.selectedProtocol && this.isArray(this.selectedProtocol.assets)) {
      return (this.selectedProtocol.assets as ProtocolAsset[]).find(a => a.name === assetName);
    }
    return undefined;
  }

  toFormGroup(control: AbstractControl | null): FormGroup {
    if (!(control instanceof FormGroup)) {
      console.error("toFormGroup: Attempted to cast a non-FormGroup control to FormGroup:", control);
      return this.fb.group({}); // Return an empty FormGroup to prevent cascading template errors
    }
    return control as FormGroup;
  }
}