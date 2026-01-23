import { Component, Input, Output, EventEmitter, signal, computed } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatChipsModule } from '@angular/material/chips';

import { SetupInstruction } from '@features/protocols/models/protocol.models';

/**
 * Component to display protocol setup instructions in the Deck Setup wizard.
 *
 * Features:
 * - Checkbox list with severity color-coding
 * - Position badges for deck-specific instructions
 * - "X / Y completed" summary
 * - Responsive design
 */
@Component({
  selector: 'app-setup-instructions',
  standalone: true,
  imports: [
    FormsModule,
    MatCheckboxModule,
    MatIconModule,
    MatTooltipModule,
    MatChipsModule
  ],
  template: `
    @if (instructions && instructions.length > 0) {
      <div class="setup-instructions-panel">
        <div class="panel-header">
          <mat-icon class="header-icon">checklist</mat-icon>
          <span class="header-title">Pre-Run Setup</span>
          <span class="completion-badge" [class.complete]="isComplete()">
            {{ checkedCount() }} / {{ instructions.length }} completed
          </span>
        </div>

        <div class="instructions-list">
          @for (instruction of instructions; track instruction.message; let i = $index) {
            <div
              class="instruction-item"
              [class.required]="instruction.severity === 'required'"
              [class.recommended]="instruction.severity === 'recommended'"
              [class.info]="instruction.severity === 'info'"
              [class.checked]="checkedState()[i]"
            >
              <mat-checkbox
                [checked]="checkedState()[i]"
                (change)="toggleCheck(i)"
                [color]="getSeverityColor(instruction.severity)"
              >
                <span class="instruction-message">{{ instruction.message }}</span>
              </mat-checkbox>

              <div class="instruction-badges">
                @if (instruction.position) {
                  <mat-chip class="position-badge" [highlighted]="false">
                    Position {{ instruction.position }}
                  </mat-chip>
                }
                @if (instruction.resource_type) {
                  <span class="resource-type-hint">
                    {{ instruction.resource_type }}
                  </span>
                }
              </div>
            </div>
          }
        </div>

        @if (showLegend) {
          <div class="severity-legend">
            <span class="legend-item required">
              <mat-icon>priority_high</mat-icon> Required
            </span>
            <span class="legend-item recommended">
              <mat-icon>thumb_up</mat-icon> Recommended
            </span>
            <span class="legend-item info">
              <mat-icon>info</mat-icon> Info
            </span>
          </div>
        }
      </div>
    }
  `,
  styles: [`
    .setup-instructions-panel {
      background: var(--surface-container-low, #f5f5f5);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 16px;
    }

    .panel-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
    }

    .header-icon {
      color: var(--primary);
    }

    .header-title {
      font-weight: 500;
      font-size: 1rem;
      flex: 1;
    }

    .completion-badge {
      font-size: 0.85rem;
      color: var(--on-surface-variant);
      padding: 4px 8px;
      border-radius: 16px;
      background: var(--surface-container);
    }

    .completion-badge.complete {
      background: var(--primary-container);
      color: var(--on-primary-container);
    }

    .instructions-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .instruction-item {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      padding: 8px 12px;
      border-radius: 8px;
      background: var(--surface);
      border-left: 3px solid transparent;
      transition: all 0.2s ease;
    }

    .instruction-item.required {
      border-left-color: var(--error, #d32f2f);
    }

    .instruction-item.recommended {
      border-left-color: var(--primary, var(--status-info));
    }

    .instruction-item.info {
      border-left-color: var(--secondary, #9e9e9e);
    }

    .instruction-item.checked {
      opacity: 0.7;
    }

    .instruction-item.checked .instruction-message {
      text-decoration: line-through;
    }

    .instruction-message {
      line-height: 1.5;
    }

    .instruction-badges {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }

    .position-badge {
      font-size: 0.75rem;
    }

    .resource-type-hint {
      font-size: 0.75rem;
      color: var(--on-surface-variant);
      font-style: italic;
    }

    .severity-legend {
      display: flex;
      gap: 16px;
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid var(--outline-variant);
      font-size: 0.75rem;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .legend-item mat-icon {
      font-size: 14px;
      width: 14px;
      height: 14px;
    }

    .legend-item.required {
      color: var(--error, #d32f2f);
    }

    .legend-item.recommended {
      color: var(--primary, var(--status-info));
    }

    .legend-item.info {
      color: var(--secondary, #9e9e9e);
    }
  `],
})
export class SetupInstructionsComponent {
  /**
   * List of setup instructions to display.
   */
  @Input() instructions: SetupInstruction[] | null = null;

  /**
   * Whether to show the severity legend at the bottom.
   */
  @Input() showLegend = false;

  /**
   * Emits when all required instructions have been checked.
   */
  @Output() allRequiredChecked = new EventEmitter<boolean>();

  /**
   * Emits the current checked state array.
   */
  @Output() checkedStateChange = new EventEmitter<boolean[]>();

  /**
   * Internal signal tracking checked state of each instruction.
   */
  checkedState = signal<boolean[]>([]);

  /**
   * Computed signal for the count of checked items.
   */
  checkedCount = computed(() => this.checkedState().filter(Boolean).length);

  /**
   * Computed signal for whether all items are complete.
   */
  isComplete = computed(() => {
    const state = this.checkedState();
    return state.length > 0 && state.every(Boolean);
  });

  /**
   * Computed signal for whether all required items are checked.
   */
  allRequiredComplete = computed(() => {
    if (!this.instructions) return true;
    const state = this.checkedState();
    return this.instructions.every((inst, i) =>
      inst.severity !== 'required' || state[i]
    );
  });

  ngOnChanges(): void {
    // Initialize checked state array when instructions change
    if (this.instructions) {
      this.checkedState.set(new Array(this.instructions.length).fill(false));
    }
  }

  /**
   * Toggle the checked state of an instruction.
   */
  toggleCheck(index: number): void {
    const current = this.checkedState();
    const updated = [...current];
    updated[index] = !updated[index];
    this.checkedState.set(updated);

    this.checkedStateChange.emit(updated);
    this.allRequiredChecked.emit(this.allRequiredComplete());
  }

  /**
   * Get the Material color for a severity level.
   */
  getSeverityColor(severity: string): 'warn' | 'primary' | 'accent' {
    switch (severity) {
      case 'required':
        return 'warn';
      case 'recommended':
        return 'primary';
      default:
        return 'accent';
    }
  }
}
