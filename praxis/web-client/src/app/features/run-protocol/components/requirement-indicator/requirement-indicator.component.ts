/**
 * RequirementIndicatorComponent
 * 
 * Displays a single inferred requirement with its status.
 * States: ✅ met, ⚠️ warning, 🔴 not met
 */

import { Component, input, computed } from '@angular/core';

import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { InferredRequirement, RequirementStatus } from '@core/models/simulation.models';

@Component({
  selector: 'app-requirement-indicator',
  standalone: true,
  imports: [MatIconModule, MatTooltipModule],
  template: `
    <div class="requirement-item" 
         [class.met]="isMet()"
         [class.warning]="isWarning()"
         [class.unmet]="!isMet() && !isWarning()"
         [matTooltip]="tooltipText()"
         [matTooltipShowDelay]="600">
      
      <div class="status-icon">
        @if (isMet() && !isWarning()) {
          <mat-icon class="icon-met">check_circle</mat-icon>
        } @else if (isWarning()) {
          <mat-icon class="icon-warning">warning</mat-icon>
        } @else {
          <mat-icon class="icon-unmet">error</mat-icon>
        }
      </div>
      
      <div class="requirement-content">
        <span class="requirement-label">{{ label() }}</span>
        @if (details()) {
          <span class="requirement-details">{{ details() }}</span>
        }
      </div>
    </div>
  `,
  styles: [`
    .requirement-item {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 12px 16px;
      border-radius: 8px;
      background: var(--sys-surface-container);
      transition: all 0.2s ease;
    }

    .requirement-item:hover {
      background: var(--sys-surface-container-high);
    }

    .requirement-item.met {
      border-left: 3px solid var(--sys-primary);
    }

    .requirement-item.warning {
      border-left: 3px solid var(--sys-tertiary);
      background: color-mix(in srgb, var(--sys-tertiary) 8%, var(--sys-surface-container));
    }

    .requirement-item.unmet {
      border-left: 3px solid var(--sys-error);
      background: color-mix(in srgb, var(--sys-error) 8%, var(--sys-surface-container));
    }

    .status-icon {
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
    }

    .status-icon mat-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .icon-met {
      color: var(--sys-primary);
    }

    .icon-warning {
      color: var(--sys-tertiary);
    }

    .icon-unmet {
      color: var(--sys-error);
    }

    .requirement-content {
      display: flex;
      flex-direction: column;
      gap: 2px;
      min-width: 0;
    }

    .requirement-label {
      font-weight: 500;
      color: var(--sys-on-surface);
      font-size: 0.875rem;
    }

    .requirement-details {
      font-size: 0.75rem;
      color: var(--sys-on-surface-variant);
    }
  `]
})
export class RequirementIndicatorComponent {
  /** The requirement status to display */
  status = input.required<RequirementStatus>();

  /** Whether the requirement is met */
  isMet = computed(() => this.status().isMet);

  /** Whether the requirement is in warning state */
  isWarning = computed(() => this.status().isWarning);

  /** Human-readable label for the requirement */
  label = computed(() => {
    const req = this.status().requirement;

    switch (req.requirement_type) {
      case 'resource_on_deck':
        return `${req.resource || 'Resource'} must be placed on deck`;
      case 'liquid_present':
        return `${req.resource || 'Source'} must contain liquid`;
      case 'tips_required':
        return 'Tips must be available';
      default:
        return req.requirement_type.replace(/_/g, ' ');
    }
  });

  /** Details text from requirement */
  details = computed(() => {
    const req = this.status().requirement;
    const details = req.details;

    if (!details || Object.keys(details).length === 0) {
      return this.status().message || '';
    }

    // Format specific detail types
    if (details['before_operation']) {
      return `Required before: ${details['before_operation']}`;
    }

    if (details['wells']) {
      const wells = details['wells'] as string[];
      return `Wells: ${wells.slice(0, 5).join(', ')}${wells.length > 5 ? '...' : ''}`;
    }

    if (details['min_volume']) {
      return `Minimum volume: ${details['min_volume']}µL`;
    }

    return this.status().message || '';
  });

  /** Tooltip text with full requirement information */
  tooltipText = computed(() => {
    const req = this.status().requirement;
    const parts = [
      `Type: ${req.requirement_type}`,
    ];

    if (req.resource) {
      parts.push(`Resource: ${req.resource}`);
    }

    if (req.inferred_at_level) {
      parts.push(`Detected at: ${req.inferred_at_level} level`);
    }

    if (this.status().message) {
      parts.push(this.status().message!);
    }

    return parts.join('\n');
  });
}
