import { Component, inject, signal, ViewChild, OnInit, AfterViewInit, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatStepperModule, MatStepper } from '@angular/material/stepper';
import { TypeSelectionStepComponent } from './steps/type-selection-step.component';
import { QuickAddResult } from '../../../shared/components/quick-add-autocomplete/quick-add-autocomplete.component';
import { DefinitionSelectionStepComponent } from './steps/definition-selection-step.component';
import { ConfigurationStepComponent } from './steps/configuration-step.component';
import { MachineDefinition, ResourceDefinition } from '../../../features/assets/models/asset.models';

@Component({
  selector: 'app-add-asset-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatStepperModule,
    TypeSelectionStepComponent,
    DefinitionSelectionStepComponent,
    ConfigurationStepComponent
  ],
  template: `
    <div class="h-full flex flex-col max-h-[90vh] min-w-[700px]">
      <div class="flex items-center justify-between px-6 pt-6 pb-2">
        <h2 class="text-2xl font-bold">Add New Asset</h2>
        <button mat-icon-button mat-dialog-close><mat-icon>close</mat-icon></button>
      </div>

      <mat-dialog-content class="flex-grow overflow-hidden !m-0 !p-0">
        <mat-stepper [linear]="true" #stepper class="h-full flex flex-col">
          <!-- Step 1: Type Selection -->
          <mat-step [completed]="!!assetType()">
            <ng-template matStepLabel>Type</ng-template>
            <div class="px-6 h-full overflow-y-auto">
              <app-type-selection-step
                (typeSelected)="onTypeSelected($event)"
                (quickSelect)="onQuickSelect($event)"
              ></app-type-selection-step>
            </div>
          </mat-step>

          <!-- Step 2: Definition Selection -->
          <mat-step [completed]="!!selectedDefinition()">
            <ng-template matStepLabel>Definition</ng-template>
            <div class="px-6 h-full overflow-y-auto">
              <app-definition-selection-step
                [assetType]="assetType()"
                (definitionSelected)="onDefinitionSelected($event)"
              ></app-definition-selection-step>
            </div>
          </mat-step>

          <!-- Step 3: Configuration -->
          <mat-step [completed]="isConfigValid()">
            <ng-template matStepLabel>Configuration</ng-template>
            <div class="px-6 h-full overflow-y-auto">
              <app-configuration-step
                [assetType]="assetType()"
                [definition]="selectedDefinition()"
                (configChanged)="onConfigChanged($event)"
                (validityChanged)="onConfigValidityChanged($event)"
              ></app-configuration-step>
            </div>
          </mat-step>
        </mat-stepper>
      </mat-dialog-content>

      <mat-dialog-actions align="end" class="px-6 py-4 border-t sys-border bg-sys-surface">
        <button mat-button (click)="goBack()" [disabled]="(stepper?.selectedIndex ?? 0) === 0">Back</button>
        
        @if ((stepper?.selectedIndex ?? 0) < 2) {
          <button mat-flat-button color="primary" (click)="goForward()" [disabled]="!canGoForward()">
            Next
          </button>
        } @else {
          <button mat-flat-button color="primary" (click)="save()" [disabled]="!isConfigValid()">
            Create {{ assetType() === 'machine' ? 'Machine' : 'Resource' }}
          </button>
        }
      </mat-dialog-actions>
    </div>
  `,
  styles: [`
    :host { display: block; height: 100%; }
    ::ng-deep .mat-horizontal-stepper-header-container { padding: 0 24px; }
    ::ng-deep .mat-horizontal-content-container { padding: 0 !important; flex-grow: 1; overflow-y: auto; }
    .sys-border { border-color: var(--mat-sys-outline-variant); }
    .sys-text-secondary { color: var(--mat-sys-on-surface-variant); }
  `]
})
export class AddAssetDialogComponent implements OnInit, AfterViewInit {
  private dialogRef = inject(MatDialogRef<AddAssetDialogComponent>);

  @ViewChild(MatStepper) stepper?: MatStepper;

  @Input() initialAssetType: 'machine' | 'resource' | null = null;

  assetType = signal<'machine' | 'resource' | null>(null);
  selectedDefinition = signal<MachineDefinition | ResourceDefinition | null>(null);
  configData = signal<any>(null);
  isConfigValid = signal(false);

  ngOnInit() {
    if (this.initialAssetType) {
      this.assetType.set(this.initialAssetType);
    }
  }

  ngAfterViewInit() {
    if (this.initialAssetType) {
      // Small delay to let stepper initialize
      setTimeout(() => {
        if (this.stepper) {
          this.stepper.selectedIndex = 1;
        }
      }, 0);
    }
  }

  onTypeSelected(type: 'machine' | 'resource') {
    this.assetType.set(type);
    this.selectedDefinition.set(null); // Reset downstream
    setTimeout(() => this.stepper?.next(), 0);
  }

  onQuickSelect(result: QuickAddResult) {
    this.assetType.set(result.type);
    this.selectedDefinition.set(result.definition);
    // Jump directly to Configuration step (index 2)
    setTimeout(() => {
      if (this.stepper) {
        this.stepper.selectedIndex = 2;
      }
    }, 0);
  }

  onDefinitionSelected(def: MachineDefinition | ResourceDefinition) {
    this.selectedDefinition.set(def);
    setTimeout(() => this.stepper?.next(), 0);
  }

  onConfigChanged(data: any) {
    this.configData.set(data);
  }

  onConfigValidityChanged(isValid: boolean) {
    this.isConfigValid.set(isValid);
  }

  canGoForward(): boolean {
    if (!this.stepper) return false;
    const index = this.stepper.selectedIndex;
    if (index === 0) return !!this.assetType();
    if (index === 1) return !!this.selectedDefinition();
    return false;
  }

  goForward() {
    this.stepper?.next();
  }

  goBack() {
    this.stepper?.previous();
  }

  save() {
    if (!this.isConfigValid()) return;

    const type = this.assetType();
    const def = this.selectedDefinition();
    const config = this.configData();

    if (type === 'machine' && def) {
      const mDef = def as MachineDefinition;
      const isSimulated = this.isSimulated(mDef);

      let connectionInfo: any = {};
      if (config.connection_info) {
        try {
          connectionInfo = JSON.parse(config.connection_info);
        } catch (e) { console.error(e); }
      }

      if (!isSimulated && mDef.fqn) {
        connectionInfo['backend_fqn'] = mDef.fqn;
      }

      let userConfiguredCapabilities: any = null;
      if (config.user_configured_capabilities) {
        try {
          userConfiguredCapabilities = JSON.parse(config.user_configured_capabilities);
        } catch { /* Invalid JSON */ }
      }

      this.dialogRef.close({
        ...config,
        machine_definition_accession_id: mDef.accession_id,
        frontend_fqn: mDef.frontend_fqn,
        connection_info: connectionInfo,
        user_configured_capabilities: userConfiguredCapabilities,
        is_simulated: isSimulated,
        machine_type: mDef.machine_category // Ensure machine_type is set for legacy compatibility
      });
    } else if (type === 'resource' && def) {
      const rDef = def as ResourceDefinition;
      this.dialogRef.close({
        ...config,
        resource_definition_accession_id: rDef.accession_id
      });
    }
  }

  private isSimulated(def: MachineDefinition): boolean {
    const fqnLower = (def.fqn || '').toLowerCase();
    const nameLower = (def.name || '').toLowerCase();
    return fqnLower.includes('chatterbox') || fqnLower.includes('simulator') || nameLower.includes('simulated');
  }
}
