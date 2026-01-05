import { Component, inject, input, output, computed, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DragDropModule, CdkDragDrop } from '@angular/cdk/drag-drop';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatStepperModule } from '@angular/material/stepper';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';

import { ProtocolDefinition } from '@features/protocols/models/protocol.models';
import { PlrResource } from '@core/models/plr.models';
import { WizardStateService } from '../../services/wizard-state.service';
import { CarrierPlacementStepComponent } from './carrier-placement-step.component';
import { ResourcePlacementStepComponent } from './resource-placement-step.component';
import { VerificationStepComponent } from './verification-step.component';
import { DeckViewComponent } from '@shared/components/deck-view/deck-view.component';

/**
 * Main container for the 3-step Guided Deck Setup wizard.
 */
@Component({
    selector: 'app-deck-setup-wizard',
    standalone: true,
    imports: [
        CommonModule,
        MatStepperModule,
        MatButtonModule,
        MatIconModule,
        MatProgressBarModule,
        MatProgressBarModule,
        MatDialogModule,
        DragDropModule,
        CarrierPlacementStepComponent,
        ResourcePlacementStepComponent,
        VerificationStepComponent,
        DeckViewComponent
    ],
    template: `
        <div class="wizard-container" cdkDropListGroup>
            <div class="wizard-header">
                <h2>
                    <mat-icon>dashboard_customize</mat-icon>
                    Guided Deck Setup
                </h2>
                <mat-progress-bar 
                    mode="determinate" 
                    [value]="wizardState.progress()">
                </mat-progress-bar>
            </div>
            
            <div class="wizard-content">
                <div class="step-panel">
                    @switch (wizardState.currentStep()) {
                        @case ('carrier-placement') {
                            <app-carrier-placement-step
                                [carrierRequirements]="wizardState.carrierRequirements()"
                                (carrierPlaced)="onCarrierPlaced($event)">
                            </app-carrier-placement-step>
                        }
                        @case ('resource-placement') {
                            <app-resource-placement-step
                                [assignments]="wizardState.slotAssignments()"
                                (resourcePlaced)="onResourcePlaced($event)">
                            </app-resource-placement-step>
                        }
                        @case ('verification') {
                            <app-verification-step
                                [carrierRequirements]="wizardState.carrierRequirements()"
                                [slotAssignments]="wizardState.slotAssignments()"
                                (confirmed)="onConfirm()">
                            </app-verification-step>
                        }
                    }
                </div>
                
                <div class="deck-preview">
                    @if (deckResource()) {
                        <app-deck-view 
                            [resource]="deckResource()"
                            [state]="{}"
                            (itemDropped)="onDropOnDeck($event)">
                        </app-deck-view>
                    }
                </div>
            </div>
            
            <div class="wizard-footer">
                <button mat-stroked-button 
                        color="warn"
                        (click)="onSkip()">
                    Skip Setup
                </button>
                
                <div class="spacer"></div>
                
                @if (wizardState.currentStep() !== 'carrier-placement') {
                    <button mat-stroked-button (click)="onBack()">
                        <mat-icon>arrow_back</mat-icon>
                        Back
                    </button>
                }
                
                @if (wizardState.currentStep() !== 'verification') {
                    <button mat-flat-button 
                            color="primary" 
                            [disabled]="!canProceed()"
                            (click)="onNext()">
                        Next
                        <mat-icon>arrow_forward</mat-icon>
                    </button>
                } @else {
                    <button mat-flat-button 
                            color="primary" 
                            (click)="onConfirm()">
                        <mat-icon>check</mat-icon>
                        Confirm & Continue
                    </button>
                }
            </div>
        </div>
    `,
    styles: [`
        .wizard-container {
            display: flex;
            flex-direction: column;
            height: 100%;
            min-height: 500px;
        }
        
        .wizard-header {
            padding: 16px 24px;
            border-bottom: 1px solid var(--sys-outline-variant);
        }
        
        .wizard-header h2 {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 0 0 12px 0;
            color: var(--sys-on-surface);
        }
        
        .wizard-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            flex: 1;
            padding: 24px;
            overflow: hidden;
        }
        
        .step-panel {
            overflow-y: auto;
        }
        
        .deck-preview {
            background: var(--sys-surface-container);
            border-radius: 8px;
            padding: 16px;
            overflow: auto;
        }
        
        .wizard-footer {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 24px;
            border-top: 1px solid var(--sys-outline-variant);
        }
        
        .spacer {
            flex: 1;
        }
        
        @media (max-width: 768px) {
            .wizard-content {
                grid-template-columns: 1fr;
            }
            
            .deck-preview {
                max-height: 250px;
            }
        }
    `]
})
export class DeckSetupWizardComponent implements OnInit {
    // Input for inline usage (when not opened via dialog)
    data = input<{ protocol: ProtocolDefinition, deckResource: PlrResource | null, assetMap?: Record<string, any> } | null>(null);

    // Signals initialized from Dialog Data or Input
    protocol = signal<ProtocolDefinition | null>(null);
    deckResource = signal<PlrResource | null>(null);

    setupComplete = output<void>();
    setupSkipped = output<void>();

    wizardState = inject(WizardStateService);
    private dialog = inject(MatDialog);
    // Optional injection in case it's not opened via dialog
    private dialogRef = inject(MatDialogRef, { optional: true });

    // Optional dialog data injection
    private dialogData = inject<{ protocol: ProtocolDefinition, deckResource: PlrResource } | null>(MAT_DIALOG_DATA, { optional: true });

    constructor() {
        // Initialize from dialog data if present
        if (this.dialogData) {
            this.protocol.set(this.dialogData.protocol);
            this.deckResource.set(this.dialogData.deckResource);
        }
    }

    canProceed = computed(() => {
        const step = this.wizardState.currentStep();
        if (step === 'carrier-placement') {
            return this.wizardState.allCarriersPlaced();
        }
        if (step === 'resource-placement') {
            return this.wizardState.allResourcesPlaced();
        }
        return true;
    });

    ngOnInit(): void {
        // Check input binding (for inline usage) if dialog data wasn't available
        const inputData = this.data();
        if (inputData && !this.protocol()) {
            this.protocol.set(inputData.protocol);
            this.deckResource.set(inputData.deckResource);
        }

        const p = this.protocol();
        if (p) {
            // Extract assetMap from input data if available
            // For dialog usage, we might need to update the dialog data interface too, 
            // but currently the priority is inline usage.
            const assetMap = (inputData as any)?.assetMap || {};
            this.wizardState.initialize(p, 'HamiltonSTARDeck', assetMap);
        }
    }


    onCarrierPlaced(event: { carrierFqn: string; placed: boolean }): void {
        this.wizardState.markCarrierPlaced(event.carrierFqn, event.placed);
    }

    onResourcePlaced(event: { resourceName: string; placed: boolean }): void {
        this.wizardState.markResourcePlaced(event.resourceName, event.placed);
    }

    onNext(): void {
        this.wizardState.nextStep();
    }

    onBack(): void {
        this.wizardState.previousStep();
    }

    onSkip(): void {
        // TODO: Add confirmation dialog
        this.wizardState.skip();
        this.setupSkipped.emit();
        this.dialogRef?.close();
    }

    onConfirm(): void {
        this.wizardState.complete();
        this.setupComplete.emit();
        // Return expected result format for RunProtocolComponent
        const result = {
            assetMap: this.wizardState.getAssetMap()
        };
        this.dialogRef?.close(result);
    }

    onDropOnDeck(event: any): void {
        // Handle drop event from DeckView
        if (event && event.item && event.item.data) {
            const assignment = event.item.data;
            if (assignment && assignment.resource) {
                this.onResourcePlaced({
                    resourceName: assignment.resource.name,
                    placed: true
                });
            }
        }
    }
}
