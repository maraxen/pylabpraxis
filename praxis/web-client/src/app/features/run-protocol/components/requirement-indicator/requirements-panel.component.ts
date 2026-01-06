/**
 * RequirementsPanelComponent
 * 
 * Displays a list of inferred requirements with their validation status.
 * Used in the deck setup wizard to show what conditions must be met.
 */

import { Component, input, computed, inject, OnInit, signal, effect } from '@angular/core';

import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatExpansionModule } from '@angular/material/expansion';

import { RequirementIndicatorComponent } from './requirement-indicator.component';
import { SimulationResultsService } from '@core/services/simulation-results.service';
import { InferredRequirement, RequirementStatus } from '@core/models/simulation.models';

export interface DeckValidationState {
    /** Resources currently placed on deck */
    placedResources: Set<string>;
    /** Resources with confirmed liquid */
    liquidConfirmed: Set<string>;
    /** Whether tip rack is available */
    hasTipRack: boolean;
}

@Component({
    selector: 'app-requirements-panel',
    standalone: true,
    imports: [
    MatIconModule,
    MatProgressSpinnerModule,
    MatExpansionModule,
    RequirementIndicatorComponent
],
    template: `
    <div class="requirements-panel">
      <div class="panel-header">
        <mat-icon>checklist</mat-icon>
        <h3>Requirements</h3>
        @if (isLoading()) {
          <mat-spinner diameter="16"></mat-spinner>
        } @else {
          <span class="status-badge" [class.all-met]="allMet()">
            {{ metCount() }}/{{ requirements().length }}
          </span>
        }
      </div>
      
      @if (requirements().length === 0 && !isLoading()) {
        <div class="empty-state">
          <mat-icon>info_outline</mat-icon>
          <span>No specific requirements detected</span>
        </div>
      } @else {
        <div class="requirements-list">
          @for (status of requirementStatuses(); track status.requirement.requirement_type + status.requirement.resource) {
            <app-requirement-indicator [status]="status" />
          }
        </div>
        
        @if (!allMet()) {
          <div class="warning-banner">
            <mat-icon>warning</mat-icon>
            <span>Some requirements are not met. Please complete deck setup to proceed.</span>
          </div>
        }
      }
    </div>
  `,
    styles: [`
    .requirements-panel {
      display: flex;
      flex-direction: column;
      gap: 12px;
      padding: 16px;
      background: var(--sys-surface-container-low);
      border-radius: 12px;
      border: 1px solid var(--sys-outline-variant);
    }

    .panel-header {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .panel-header h3 {
      margin: 0;
      flex: 1;
      font-size: 0.875rem;
      font-weight: 600;
      color: var(--sys-on-surface);
    }

    .panel-header mat-icon {
      color: var(--sys-primary);
      width: 20px;
      height: 20px;
      font-size: 20px;
    }

    .status-badge {
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 500;
      background: var(--sys-error-container);
      color: var(--sys-on-error-container);
    }

    .status-badge.all-met {
      background: var(--sys-primary-container);
      color: var(--sys-on-primary-container);
    }

    .empty-state {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 16px;
      color: var(--sys-on-surface-variant);
      font-size: 0.875rem;
    }

    .empty-state mat-icon {
      opacity: 0.6;
    }

    .requirements-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .warning-banner {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      background: color-mix(in srgb, var(--sys-error) 10%, var(--sys-surface));
      border-radius: 8px;
      font-size: 0.75rem;
      color: var(--sys-error);
    }

    .warning-banner mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
    }
  `]
})
export class RequirementsPanelComponent implements OnInit {
    private readonly simulationService = inject(SimulationResultsService);

    /** Protocol ID to fetch requirements for */
    protocolId = input.required<string>();

    /** Current deck validation state */
    deckState = input<DeckValidationState>({
        placedResources: new Set(),
        liquidConfirmed: new Set(),
        hasTipRack: false
    });

    /** Loading state */
    isLoading = signal(false);

    /** Raw requirements from backend */
    requirements = signal<InferredRequirement[]>([]);

    /** Validated requirement statuses */
    requirementStatuses = computed<RequirementStatus[]>(() => {
        return this.validateRequirements(this.requirements(), this.deckState());
    });

    /** Count of met requirements */
    metCount = computed(() => {
        return this.requirementStatuses().filter(s => s.isMet || s.isWarning).length;
    });

    /** Whether all requirements are met */
    allMet = computed(() => {
        const statuses = this.requirementStatuses();
        return statuses.length === 0 || statuses.every(s => s.isMet || s.isWarning);
    });

    constructor() {
        // Reload requirements when protocol ID changes
        effect(() => {
            const id = this.protocolId();
            if (id) {
                this.loadRequirements(id);
            }
        });
    }

    ngOnInit(): void {
        // Initial load handled by effect
    }

    private loadRequirements(protocolId: string): void {
        this.isLoading.set(true);

        this.simulationService.getInferredRequirements(protocolId).subscribe({
            next: (requirements) => {
                this.requirements.set(requirements);
                this.isLoading.set(false);
            },
            error: (err) => {
                console.error('[RequirementsPanel] Failed to load requirements:', err);
                this.requirements.set([]);
                this.isLoading.set(false);
            }
        });
    }

    private validateRequirements(
        requirements: InferredRequirement[],
        deckState: DeckValidationState
    ): RequirementStatus[] {
        return requirements.map(req => {
            let isMet = false;
            let isWarning = false;
            let message = '';

            switch (req.requirement_type) {
                case 'resource_on_deck':
                    if (req.resource) {
                        isMet = deckState.placedResources.has(req.resource);
                        message = isMet ? 'Resource is placed' : 'Resource needs to be placed on deck';
                    }
                    break;

                case 'liquid_present':
                    if (req.resource) {
                        // Check if resource is on deck first
                        if (!deckState.placedResources.has(req.resource)) {
                            isMet = false;
                            message = 'Resource not yet placed';
                        } else if (deckState.liquidConfirmed.has(req.resource)) {
                            isMet = true;
                            message = 'Liquid confirmed';
                        } else {
                            // Can't verify liquid in wizard, show warning
                            isWarning = true;
                            message = 'Verify liquid is present before running';
                        }
                    }
                    break;

                case 'tips_required':
                    isMet = deckState.hasTipRack;
                    message = isMet ? 'Tip rack available' : 'Tip rack needed';
                    break;

                default:
                    // Unknown requirement types - show as warning
                    isWarning = true;
                    message = 'Cannot verify automatically';
            }

            return { requirement: req, isMet, isWarning, message };
        });
    }
}
