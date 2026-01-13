import { Component, EventEmitter, Input, OnInit, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, Validators, ReactiveFormsModule, FormGroup } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MachineDefinition, ResourceDefinition, MachineStatus, ResourceStatus } from '../../../../features/assets/models/asset.models';
import { PraxisSelectComponent, SelectOption } from '@shared/components/praxis-select/praxis-select.component';
import { DynamicCapabilityFormComponent } from '../../../../features/assets/components/dynamic-capability-form.component';

@Component({
    selector: 'app-configuration-step',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatButtonModule,
        MatIconModule,
        MatInputModule,
        MatFormFieldModule,
        PraxisSelectComponent,
        DynamicCapabilityFormComponent
    ],
    template: `
    <div class="fade-in flex flex-col gap-5 py-2">
      <div class="flex items-center gap-3 p-4 bg-sys-surface-container rounded-xl border border-sys-border">
        <div class="icon-chip">
          <mat-icon>{{ assetType === 'machine' ? 'precision_manufacturing' : 'science' }}</mat-icon>
        </div>
        <div class="flex flex-col min-w-0">
          <span class="text-xs font-bold uppercase tracking-wider text-sys-text-secondary">Selected Definition</span>
          <span class="font-medium truncate">{{ definition?.name }}</span>
          <span class="text-[10px] sys-text-secondary truncate">{{ definition?.fqn }}</span>
        </div>
      </div>

      <form [formGroup]="form" class="flex flex-col gap-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-4">
            <mat-form-field appearance="outline" class="w-full">
              <mat-label>Asset Name</mat-label>
              <input matInput formControlName="name" placeholder="e.g. Robot 1 or Plate A">
              @if (form.get('name')?.hasError('required')) {
                <mat-error>Name is required</mat-error>
              }
            </mat-form-field>

            <mat-form-field appearance="outline" class="w-full">
              <mat-label>Location Label (Optional)</mat-label>
              <input matInput formControlName="location_label" placeholder="e.g. Bench A, Shelf 2">
            </mat-form-field>

            <div>
              <label class="text-xs font-medium text-sys-text-secondary mb-1 block">Initial Status</label>
              <app-praxis-select
                [options]="statusOptions"
                formControlName="status"
              ></app-praxis-select>
            </div>
          </div>

          <div class="flex flex-col gap-4">
            <mat-form-field appearance="outline" class="w-full">
              <mat-label>Description (Optional)</mat-label>
              <textarea matInput formControlName="description" rows="3" placeholder="Enter optional details..."></textarea>
            </mat-form-field>
          </div>
        </div>

        @if (assetType === 'machine' && machineDefinition?.connection_config) {
          <div class="section-card mt-2">
            <div class="section-header">Connection configuration</div>
            <app-dynamic-capability-form
              [config]="machineDefinition!.connection_config"
              (valueChange)="updateConnectionInfo($event)">
            </app-dynamic-capability-form>
          </div>
        }

        @if (assetType === 'machine' && machineDefinition?.capabilities_config) {
          <div class="section-card">
            <div class="section-header">Capabilities</div>
            <app-dynamic-capability-form
              [config]="machineDefinition!.capabilities_config"
              (valueChange)="updateCapabilities($event)">
            </app-dynamic-capability-form>
          </div>
        }
      </form>
    </div>
  `,
    styles: [`
    .fade-in { animation: fadeIn 0.25s ease-in-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

    .icon-chip {
      width: 40px;
      height: 40px;
      border-radius: 12px;
      background: var(--mat-sys-surface-container-high);
      display: grid;
      place-items: center;
      color: var(--mat-sys-primary);
    }

    .section-card {
      border: 1px solid var(--mat-sys-outline-variant);
      border-radius: 14px;
      padding: 16px;
      background: linear-gradient(135deg, var(--mat-sys-surface) 0%, var(--mat-sys-surface-container-low) 100%);
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .section-header {
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: var(--mat-sys-on-surface-variant);
    }

    .sys-text-secondary { color: var(--mat-sys-on-surface-variant); }
  `]
})
export class ConfigurationStepComponent implements OnInit {
    @Input() assetType: 'machine' | 'resource' | null = null;
    @Input() definition: MachineDefinition | ResourceDefinition | null = null;
    @Output() configChanged = new EventEmitter<any>();
    @Output() validityChanged = new EventEmitter<boolean>();

    private fb = inject(FormBuilder);

    form: FormGroup = this.fb.group({
        name: ['', Validators.required],
        location_label: [''],
        status: [''],
        description: [''],
        connection_info: [''],
        user_configured_capabilities: ['']
    });

    statusOptions: SelectOption[] = [];

    get machineDefinition(): MachineDefinition | null {
        return this.assetType === 'machine' ? this.definition as MachineDefinition : null;
    }

    ngOnInit() {
        if (this.assetType === 'machine') {
            this.statusOptions = [
                { label: 'Offline', value: MachineStatus.OFFLINE },
                { label: 'Idle', value: MachineStatus.IDLE }
            ];
            this.form.patchValue({ status: MachineStatus.OFFLINE });
        } else {
            this.statusOptions = [
                { label: 'Available', value: ResourceStatus.AVAILABLE },
                { label: 'In Use', value: ResourceStatus.IN_USE },
                { label: 'Depleted', value: ResourceStatus.DEPLETED }
            ];
            this.form.patchValue({ status: ResourceStatus.AVAILABLE });
        }

        // Propose default name
        if (this.definition) {
            const randomId = Math.floor(Math.random() * 100) + 1;
            this.form.patchValue({ name: `${this.definition.name} ${randomId}` });
        }

        this.form.valueChanges.subscribe(val => {
            this.configChanged.emit(val);
            this.validityChanged.emit(this.form.valid);
        });

        // Initial emit
        this.validityChanged.emit(this.form.valid);
    }

    onConfigChanged(data: any) {
        this.configChanged.emit(data);
    }

    onValidityChanged(isValid: boolean) {
        this.validityChanged.emit(isValid);
    }

    updateConnectionInfo(val: Record<string, any>) {
        this.form.patchValue({ connection_info: JSON.stringify(val) });
    }

    updateCapabilities(val: Record<string, any>) {
        this.form.patchValue({ user_configured_capabilities: JSON.stringify(val) });
    }
}
