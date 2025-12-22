import { Component, ChangeDetectionStrategy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatStepperModule } from '@angular/material/stepper';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProtocolDefinition } from '@features/protocols/models/protocol.models';
import { ProtocolService } from '@features/protocols/services/protocol.service';
import { ExecutionService } from './services/execution.service';
import { ParameterConfigComponent } from './components/parameter-config/parameter-config.component';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner'; // Import MatProgressSpinnerModule
import { finalize } from 'rxjs/operators'; // Import finalize

@Component({
  selector: 'app-run-protocol',
  standalone: true,
  imports: [
    CommonModule,
    MatStepperModule,
    MatButtonModule,
    MatIconModule,
    FormsModule,
    ReactiveFormsModule,
    ParameterConfigComponent,
    MatProgressSpinnerModule // Add MatProgressSpinnerModule
  ],
  template: `
    <div class="run-protocol-container">
      <mat-stepper [linear]="true" #stepper>
        <!-- Step 1: Select Protocol (or verify selection) -->
        <mat-step [stepControl]="protocolFormGroup" label="Select Protocol">
          <form [formGroup]="protocolFormGroup">
            <div *ngIf="selectedProtocol(); else noProtocol">
              <h3>Selected Protocol: {{ selectedProtocol()?.name }}</h3>
              <p>{{ selectedProtocol()?.description }}</p>
              <button mat-button (click)="clearProtocol()">Change Protocol</button>
            </div>
            <ng-template #noProtocol>
              <p>Please select a protocol from the library.</p>
              <button mat-raised-button color="primary" routerLink="/protocols">Go to Library</button>
            </ng-template>
            <div class="actions">
              <button mat-button matStepperNext [disabled]="!selectedProtocol()">Next</button>
            </div>
          </form>
        </mat-step>

        <!-- Step 2: Configure Parameters -->
        <mat-step [stepControl]="parametersFormGroup" label="Configure Parameters">
          <form [formGroup]="parametersFormGroup">
            <app-parameter-config
              [protocol]="selectedProtocol()"
              [formGroup]="parametersFormGroup">
            </app-parameter-config>
            <div class="actions">
              <button mat-button matStepperPrevious>Back</button>
              <button mat-button matStepperNext>Next</button>
            </div>
          </form>
        </mat-step>

        <!-- Step 3: Deck Configuration (Placeholder) -->
        <mat-step label="Deck Configuration">
          <p>Deck configuration visualization will go here.</p>
          <div class="actions">
            <button mat-button matStepperPrevious>Back</button>
            <button mat-button matStepperNext>Next</button>
          </div>
        </mat-step>

        <!-- Step 4: Review & Run -->
        <mat-step label="Review & Run">
          <h3>Ready to Run</h3>
          <p>Protocol: {{ selectedProtocol()?.name }}</p>
          <p>Parameters Configured: {{ parametersFormGroup.valid ? 'Yes' : 'No' }}</p>
          
          <div class="actions">
            <button mat-button matStepperPrevious>Back</button>
            <button mat-raised-button color="primary" (click)="startRun()" [disabled]="isStartingRun()">
              <mat-icon *ngIf="!isStartingRun()">play_arrow</mat-icon>
              <mat-spinner *ngIf="isStartingRun()" diameter="20" class="button-spinner"></mat-spinner>
              {{ isStartingRun() ? 'Starting...' : 'Start Execution' }}
            </button>
          </div>
        </mat-step>
      </mat-stepper>
    </div>
  `,
  styles: [`
    .run-protocol-container {
      padding: 16px;
      height: 100%;
    }
    .actions {
      margin-top: 16px;
      display: flex;
      gap: 8px;
    }
    .button-spinner {
      margin-right: 8px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RunProtocolComponent {
  private _formBuilder = inject(FormBuilder);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private protocolService = inject(ProtocolService);
  private executionService = inject(ExecutionService);

  protocolFormGroup = this._formBuilder.group({
    protocolId: ['']
  });
  
  parametersFormGroup = this._formBuilder.group({});

  selectedProtocol = signal<ProtocolDefinition | null>(null);
  isStartingRun = signal(false); // New loading signal

  constructor() {
    this.route.queryParams.subscribe(params => {
      const protocolId = params['protocolId'];
      if (protocolId) {
        this.loadProtocol(protocolId);
      }
    });
  }

  loadProtocol(id: string) {
    this.protocolService.getProtocols().subscribe(protocols => {
      const found = protocols.find(p => p.accession_id === id);
      if (found) {
        this.selectedProtocol.set(found);
        this.protocolFormGroup.patchValue({ protocolId: id });
      }
    });
  }

  clearProtocol() {
    this.selectedProtocol.set(null);
    this.protocolFormGroup.reset();
    this.router.navigate([], { relativeTo: this.route, queryParams: { protocolId: null }, queryParamsHandling: 'merge' });
  }

  startRun() {
    const protocol = this.selectedProtocol();
    if (protocol && this.parametersFormGroup.valid && !this.isStartingRun()) {
      this.isStartingRun.set(true); // Set loading true
      const runName = `${protocol.name} - ${new Date().toLocaleString()}`;
      const params = this.parametersFormGroup.value;
      
      this.executionService.startRun(protocol.accession_id, runName, params).pipe(
        finalize(() => this.isStartingRun.set(false)) // Set loading false after completion
      ).subscribe({
        next: (res) => {
          console.log('Run started', res);
          // Navigate to a "Live Run" view or stay here and show progress?
          // The status bar will show it running.
          // Maybe reset stepper or show a success message.
        },
        error: (err) => console.error('Failed to start run', err)
      });
    }
  }
}