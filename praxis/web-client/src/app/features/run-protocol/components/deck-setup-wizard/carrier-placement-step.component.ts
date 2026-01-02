import { Component, input, output, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { CarrierRequirement } from '../../models/carrier-inference.models';

/**
 * Step 1: Guide user to place carriers on deck rails.
 */
@Component({
    selector: 'app-carrier-placement-step',
    standalone: true,
    imports: [CommonModule, FormsModule, MatCheckboxModule, MatIconModule],
    template: `
        <div class="step-content">
            <h3 class="step-title">
                <mat-icon>view_column</mat-icon>
                Step 1: Place Carriers on Deck
            </h3>
            <p class="instruction">
                Slide the following carriers into the indicated rail positions:
            </p>
            
            <div class="carrier-list">
                @for (req of carrierRequirements(); track req.carrierFqn) {
                    <div class="carrier-item" [class.completed]="req.placed">
                        <mat-checkbox 
                            [checked]="req.placed" 
                            (change)="onPlacedChange(req, $event.checked)">
                            <div class="carrier-info">
                                <span class="carrier-name">{{ req.carrierName }}</span>
                                <span class="carrier-arrow">→</span>
                                <span class="rail-position">Rail {{ req.suggestedRails[0] || '—' }}</span>
                            </div>
                            <div class="carrier-details">
                                <span class="slot-count">{{ req.slotsNeeded }}/{{ req.slotsAvailable }} slots</span>
                                <span class="carrier-type">({{ req.carrierType }})</span>
                            </div>
                        </mat-checkbox>
                    </div>
                }
                
                @if (carrierRequirements().length === 0) {
                    <div class="no-carriers">
                        <mat-icon>check_circle</mat-icon>
                        <span>No carriers required for this protocol</span>
                    </div>
                }
            </div>
            
            <div class="progress-summary">
                <mat-icon [class.complete]="allPlaced()">
                    {{ allPlaced() ? 'check_circle' : 'pending' }}
                </mat-icon>
                <span>{{ placedCount() }}/{{ carrierRequirements().length }} carriers placed</span>
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
        
        .carrier-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .carrier-item {
            padding: 12px 16px;
            background: var(--sys-surface-container);
            border-radius: 8px;
            border: 1px solid var(--sys-outline-variant);
            transition: all 0.2s ease;
        }
        
        .carrier-item.completed {
            background: var(--sys-primary-container);
            border-color: var(--sys-primary);
        }
        
        .carrier-info {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
        }
        
        .carrier-name {
            color: var(--sys-on-surface);
        }
        
        .carrier-arrow {
            color: var(--sys-primary);
        }
        
        .rail-position {
            color: var(--sys-primary);
            font-weight: 600;
        }
        
        .carrier-details {
            margin-top: 4px;
            font-size: 0.875rem;
            color: var(--sys-on-surface-variant);
            margin-left: 24px;
        }
        
        .no-carriers {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 16px;
            background: var(--sys-secondary-container);
            border-radius: 8px;
            color: var(--sys-on-secondary-container);
        }
        
        .progress-summary {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px;
            background: var(--sys-surface-container-high);
            border-radius: 8px;
        }
        
        .progress-summary mat-icon.complete {
            color: var(--sys-primary);
        }
    `]
})
export class CarrierPlacementStepComponent {
    carrierRequirements = input.required<CarrierRequirement[]>();

    carrierPlaced = output<{ carrierFqn: string; placed: boolean }>();

    placedCount = computed(() =>
        this.carrierRequirements().filter(r => r.placed).length
    );

    allPlaced = computed(() =>
        this.carrierRequirements().length > 0 &&
        this.carrierRequirements().every(r => r.placed)
    );

    onPlacedChange(req: CarrierRequirement, placed: boolean): void {
        this.carrierPlaced.emit({ carrierFqn: req.carrierFqn, placed });
    }
}
