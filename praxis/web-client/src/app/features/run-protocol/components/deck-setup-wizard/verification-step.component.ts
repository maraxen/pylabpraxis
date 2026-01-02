import { Component, input, output, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { CarrierRequirement, SlotAssignment } from '../../models/carrier-inference.models';

/**
 * Step 3: Verification - confirm deck configuration matches physical setup.
 */
@Component({
    selector: 'app-verification-step',
    standalone: true,
    imports: [CommonModule, MatIconModule, MatButtonModule],
    template: `
        <div class="step-content">
            <h3 class="step-title">
                <mat-icon>verified</mat-icon>
                Step 3: Verify Configuration
            </h3>
            <p class="instruction">
                Review your deck configuration and confirm it matches the physical setup.
            </p>
            
            <div class="summary-section">
                <h4>Carriers ({{ carrierRequirements().length }})</h4>
                <div class="summary-list">
                    @for (req of carrierRequirements(); track req.carrierFqn) {
                        <div class="summary-item">
                            <mat-icon class="check">check_circle</mat-icon>
                            <span>{{ req.carrierName }} on Rail {{ req.suggestedRails[0] }}</span>
                        </div>
                    }
                </div>
            </div>
            
            <div class="summary-section">
                <h4>Resources ({{ slotAssignments().length }})</h4>
                <div class="summary-list">
                    @for (assignment of slotAssignments(); track assignment.resource.name) {
                        <div class="summary-item">
                            <mat-icon class="check">check_circle</mat-icon>
                            <span>
                                {{ assignment.resource.name }} in {{ assignment.carrier.name }}, 
                                {{ assignment.slot.name }}
                            </span>
                        </div>
                    }
                </div>
            </div>
            
            <div class="confirmation-warning">
                <mat-icon>warning</mat-icon>
                <div>
                    <strong>Important:</strong> Ensure the physical deck matches this configuration 
                    before proceeding. Incorrect placement may cause protocol errors.
                </div>
            </div>
        </div>
    `,
    styles: [`
        .step-content {
            padding: 16px;
        }
        
        .step-title {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 0 0 8px 0;
            color: var(--sys-on-surface);
        }
        
        .instruction {
            color: var(--sys-on-surface-variant);
            margin-bottom: 16px;
        }
        
        .summary-section {
            margin-bottom: 16px;
        }
        
        .summary-section h4 {
            margin: 0 0 8px 0;
            color: var(--sys-on-surface);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .summary-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 12px;
            background: var(--sys-surface-container);
            border-radius: 8px;
            max-height: 150px;
            overflow-y: auto;
        }
        
        .summary-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--sys-on-surface);
        }
        
        .summary-item .check {
            color: var(--sys-primary);
            font-size: 18px;
        }
        
        .confirmation-warning {
            display: flex;
            gap: 12px;
            padding: 16px;
            background: var(--sys-error-container);
            border-radius: 8px;
            color: var(--sys-on-error-container);
        }
        
        .confirmation-warning mat-icon {
            color: var(--sys-error);
            flex-shrink: 0;
        }
    `]
})
export class VerificationStepComponent {
    carrierRequirements = input.required<CarrierRequirement[]>();
    slotAssignments = input.required<SlotAssignment[]>();

    confirmed = output<void>();

    totalItems = computed(() =>
        this.carrierRequirements().length + this.slotAssignments().length
    );
}
