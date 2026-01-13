/**
 * StateInspectorComponent
 * 
 * Time travel debugging component that allows users to scrub through
 * operation sequences and inspect state at any point.
 */

import { Component, input, output, computed, signal, effect } from '@angular/core';

import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSliderModule } from '@angular/material/slider';
import { MatCardModule } from '@angular/material/card';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';

import { StateHistory, OperationStateSnapshot, StateSnapshot } from '@core/models/simulation.models';
import { StateDisplayComponent } from './state-display.component';

@Component({
  selector: 'app-state-inspector',
  standalone: true,
  imports: [
    MatIconModule,
    MatButtonModule,
    MatSliderModule,
    MatCardModule,
    MatTooltipModule,
    MatDividerModule,
    StateDisplayComponent
  ],
  template: `
    <div class="state-inspector">
      <!-- Header -->
      <div class="inspector-header">
        <mat-icon>timeline</mat-icon>
        <h3>State Inspector</h3>
        @if (stateHistory()) {
          <span class="operation-count">
            {{ currentOperationIndex() + 1 }} / {{ stateHistory()!.operations.length }}
          </span>
        }
      </div>
      
      @if (!stateHistory() || stateHistory()!.operations.length === 0) {
        <div class="empty-state">
          <mat-icon>hourglass_empty</mat-icon>
          <p>No state history available for this run.</p>
        </div>
      } @else {
        <!-- Timeline Scrubber -->
        <div class="timeline-section">
          <div class="timeline-controls">
            <button mat-icon-button 
                    (click)="goToFirst()" 
                    [disabled]="currentOperationIndex() === 0"
                    matTooltip="First operation">
              <mat-icon>first_page</mat-icon>
            </button>
            <button mat-icon-button 
                    (click)="goToPrevious()" 
                    [disabled]="currentOperationIndex() === 0"
                    matTooltip="Previous operation">
              <mat-icon>chevron_left</mat-icon>
            </button>
            
            <div class="scrubber-container">
              <input type="range" 
                     class="timeline-scrubber"
                     [min]="0" 
                     [max]="maxIndex()"
                     [value]="currentOperationIndex()"
                     (input)="onScrub($event)">
              <div class="scrubber-labels">
                <span>Start</span>
                <span>End</span>
              </div>
            </div>
            
            <button mat-icon-button 
                    (click)="goToNext()" 
                    [disabled]="currentOperationIndex() >= maxIndex()"
                    matTooltip="Next operation">
              <mat-icon>chevron_right</mat-icon>
            </button>
            <button mat-icon-button 
                    (click)="goToLast()" 
                    [disabled]="currentOperationIndex() >= maxIndex()"
                    matTooltip="Last operation">
              <mat-icon>last_page</mat-icon>
            </button>
          </div>
        </div>
        
        <!-- Current Operation Display -->
        <mat-card class="operation-card">
          <mat-card-header>
            <mat-icon mat-card-avatar [class]="operationStatusClass()">
              {{ operationStatusIcon() }}
            </mat-icon>
            <mat-card-title>{{ currentOperation()?.method_name || 'Unknown' }}</mat-card-title>
            <mat-card-subtitle>
              @if (currentOperation()?.resource) {
                {{ currentOperation()!.resource }}
              }
              @if (currentOperation()?.timestamp) {
                · {{ formatTime(currentOperation()!.timestamp) }}
              }
            </mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            @if (currentOperation()?.duration_ms) {
              <div class="operation-meta">
                <span class="meta-label">Duration:</span>
                <span class="meta-value">{{ currentOperation()!.duration_ms!.toFixed(0) }}ms</span>
              </div>
            }
            @if (currentOperation()?.error_message) {
              <div class="error-banner">
                <mat-icon>error</mat-icon>
                {{ currentOperation()!.error_message }}
              </div>
            }
          </mat-card-content>
        </mat-card>
        
        <!-- State Comparison View -->
        <div class="state-comparison">
          <div class="state-column">
            <h4>
              <mat-icon>arrow_back</mat-icon>
              State Before
            </h4>
            <div class="state-content">
              @if (currentOperation()?.state_before) {
                <app-state-display [state]="currentOperation()!.state_before" />
              }
            </div>
          </div>
          
          <div class="state-arrow">
            <mat-icon>arrow_forward</mat-icon>
          </div>
          
          <div class="state-column">
            <h4>
              <mat-icon>arrow_forward</mat-icon>
              State After
            </h4>
            <div class="state-content">
              @if (currentOperation()?.state_after) {
                <app-state-display [state]="currentOperation()!.state_after" />
              }
            </div>
          </div>
        </div>
        
        <!-- State Diff -->
        @if (stateDiff().length > 0) {
          <div class="state-diff">
            <h4>
              <mat-icon>difference</mat-icon>
              Changes
            </h4>
            <div class="diff-list">
              @for (diff of stateDiff(); track diff.key) {
                <div class="diff-item" [class.increase]="diff.direction === 'increase'" [class.decrease]="diff.direction === 'decrease'">
                  <span class="diff-key">{{ diff.key }}</span>
                  <span class="diff-values">
                    <span class="old-value">{{ diff.before }}</span>
                    <mat-icon class="diff-arrow">arrow_forward</mat-icon>
                    <span class="new-value">{{ diff.after }}</span>
                  </span>
                </div>
              }
            </div>
          </div>
        }
      }
    </div>
  `,
  styles: [`
    .state-inspector {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 16px;
      background: var(--sys-surface-container-low);
      border-radius: 12px;
    }

    .inspector-header {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .inspector-header h3 {
      flex: 1;
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
    }

    .inspector-header mat-icon {
      color: var(--sys-primary);
    }

    .operation-count {
      padding: 4px 12px;
      border-radius: 16px;
      background: var(--sys-primary-container);
      color: var(--sys-on-primary-container);
      font-size: 0.75rem;
      font-weight: 500;
    }

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      padding: 48px 24px;
      color: var(--sys-on-surface-variant);
      text-align: center;
    }

    .empty-state mat-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
      opacity: 0.5;
    }

    .timeline-section {
      padding: 12px 16px;
      background: var(--sys-surface-container);
      border-radius: 8px;
    }

    .timeline-controls {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .scrubber-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .timeline-scrubber {
      width: 100%;
      height: 8px;
      appearance: none;
      background: var(--sys-surface-variant);
      border-radius: 4px;
      cursor: pointer;
    }

    .timeline-scrubber::-webkit-slider-thumb {
      appearance: none;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: var(--sys-primary);
      cursor: pointer;
      transition: transform 0.15s ease;
    }

    .timeline-scrubber::-webkit-slider-thumb:hover {
      transform: scale(1.2);
    }

    .scrubber-labels {
      display: flex;
      justify-content: space-between;
      font-size: 0.625rem;
      color: var(--sys-on-surface-variant);
    }

    .operation-card {
      background: var(--sys-surface-container);
      border: 1px solid var(--sys-outline-variant);
    }

    .operation-card mat-icon[mat-card-avatar] {
      font-size: 24px;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      background: var(--sys-surface-container-high);
    }

    .operation-card mat-icon[mat-card-avatar].completed {
      color: var(--sys-primary);
    }

    .operation-card mat-icon[mat-card-avatar].failed {
      color: var(--sys-error);
    }

    .operation-meta {
      display: flex;
      gap: 8px;
      font-size: 0.75rem;
    }

    .meta-label {
      color: var(--sys-on-surface-variant);
    }

    .error-banner {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      margin-top: 12px;
      background: color-mix(in srgb, var(--sys-error) 10%, var(--sys-surface));
      border-radius: 6px;
      color: var(--sys-error);
      font-size: 0.75rem;
    }

    .state-comparison {
      display: grid;
      grid-template-columns: 1fr auto 1fr;
      gap: 12px;
      align-items: start;
    }

    .state-column {
      padding: 12px;
      background: var(--sys-surface-container);
      border-radius: 8px;
    }

    .state-column h4 {
      display: flex;
      align-items: center;
      gap: 6px;
      margin: 0 0 12px 0;
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--sys-on-surface-variant);
    }

    .state-column h4 mat-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
    }

    .state-arrow {
      display: flex;
      align-items: center;
      justify-content: center;
      padding-top: 40px;
      color: var(--sys-primary);
    }

    .state-diff {
      padding: 12px;
      background: var(--sys-surface-container);
      border-radius: 8px;
    }

    .state-diff h4 {
      display: flex;
      align-items: center;
      gap: 6px;
      margin: 0 0 12px 0;
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--sys-on-surface-variant);
    }

    .diff-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .diff-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      background: var(--sys-surface-container-high);
      border-radius: 6px;
      font-size: 0.75rem;
    }

    .diff-key {
      font-family: 'Fira Code', monospace;
      color: var(--sys-on-surface);
    }

    .diff-values {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .old-value {
      color: var(--sys-on-surface-variant);
      text-decoration: line-through;
    }

    .new-value {
      font-weight: 600;
    }

    .diff-item.increase .new-value {
      color: var(--sys-primary);
    }

    .diff-item.decrease .new-value {
      color: var(--sys-error);
    }

    .diff-arrow {
      font-size: 14px;
      width: 14px;
      height: 14px;
      color: var(--sys-on-surface-variant);
    }
  `]
})
export class StateInspectorComponent {
  /** Full state history for the run */
  stateHistory = input<StateHistory | null>(null);

  /** Initial operation index */
  initialOperationIndex = input(0);

  /** Emitted when user navigates to a different operation */
  operationSelected = output<number>();

  /** Current operation index */
  currentOperationIndex = signal(0);

  /** Maximum index (for range slider) */
  maxIndex = computed(() => {
    const history = this.stateHistory();
    return history ? Math.max(0, history.operations.length - 1) : 0;
  });

  /** Current operation being inspected */
  currentOperation = computed<OperationStateSnapshot | null>(() => {
    const history = this.stateHistory();
    if (!history || history.operations.length === 0) return null;
    return history.operations[this.currentOperationIndex()] || null;
  });

  /** State differences between before and after */
  stateDiff = computed(() => {
    const op = this.currentOperation();
    if (!op) return [];
    return this.computeStateDiff(op.state_before, op.state_after);
  });

  constructor() {
    // Sync initial index
    effect(() => {
      const initial = this.initialOperationIndex();
      this.currentOperationIndex.set(initial);
    }, { allowSignalWrites: true });
  }

  operationStatusClass(): string {
    const op = this.currentOperation();
    return op?.status || 'completed';
  }

  operationStatusIcon(): string {
    const op = this.currentOperation();
    switch (op?.status) {
      case 'completed': return 'check_circle';
      case 'failed': return 'error';
      case 'skipped': return 'skip_next';
      default: return 'radio_button_unchecked';
    }
  }

  formatTime(isoString?: string): string {
    if (!isoString) return '';
    try {
      return new Date(isoString).toLocaleTimeString();
    } catch {
      return isoString;
    }
  }

  goToFirst(): void {
    this.currentOperationIndex.set(0);
    this.operationSelected.emit(0);
  }

  goToPrevious(): void {
    const newIndex = Math.max(0, this.currentOperationIndex() - 1);
    this.currentOperationIndex.set(newIndex);
    this.operationSelected.emit(newIndex);
  }

  goToNext(): void {
    const newIndex = Math.min(this.maxIndex(), this.currentOperationIndex() + 1);
    this.currentOperationIndex.set(newIndex);
    this.operationSelected.emit(newIndex);
  }

  goToLast(): void {
    const lastIndex = this.maxIndex();
    this.currentOperationIndex.set(lastIndex);
    this.operationSelected.emit(lastIndex);
  }

  onScrub(event: Event): void {
    const input = event.target as HTMLInputElement;
    const newIndex = parseInt(input.value, 10);
    this.currentOperationIndex.set(newIndex);
    this.operationSelected.emit(newIndex);
  }

  private computeStateDiff(before: StateSnapshot, after: StateSnapshot): Array<{
    key: string;
    before: string;
    after: string;
    direction: 'increase' | 'decrease' | 'change';
  }> {
    const diffs: Array<{
      key: string;
      before: string;
      after: string;
      direction: 'increase' | 'decrease' | 'change';
    }> = [];

    const compareObjects = (obj1: any, obj2: any, prefix = ''): void => {
      const allKeys = new Set([
        ...Object.keys(obj1 || {}),
        ...Object.keys(obj2 || {})
      ]);

      for (const key of allKeys) {
        const val1 = obj1?.[key];
        const val2 = obj2?.[key];
        const fullKey = prefix ? `${prefix}.${key}` : key;

        // Skip if values are identical or both effectively empty/equal
        if (val1 === val2) continue;
        if (JSON.stringify(val1) === JSON.stringify(val2)) continue;

        // Recursively compare if both are objects (and not null)
        if (
          typeof val1 === 'object' && val1 !== null &&
          typeof val2 === 'object' && val2 !== null &&
          !Array.isArray(val1) && !Array.isArray(val2)
        ) {
          compareObjects(val1, val2, fullKey);
          continue;
        }

        // Handle array comparison (simple string representation for now)
        if (Array.isArray(val1) || Array.isArray(val2)) {
          diffs.push({
            key: fullKey,
            before: JSON.stringify(val1 || []),
            after: JSON.stringify(val2 || []),
            direction: 'change'
          });
          continue;
        }

        // Basic types diff
        const beforeStr = this.formatValue(fullKey, val1);
        const afterStr = this.formatValue(fullKey, val2);

        let direction: 'increase' | 'decrease' | 'change' = 'change';
        if (typeof val1 === 'number' && typeof val2 === 'number') {
          direction = val2 > val1 ? 'increase' : 'decrease';
        } else if (val1 === undefined || val1 === null || val1 === false) {
          direction = 'increase';
        } else if (val2 === undefined || val2 === null || val2 === false) {
          direction = 'decrease';
        }

        diffs.push({
          key: fullKey,
          before: beforeStr,
          after: afterStr,
          direction
        });
      }
    };

    compareObjects(before, after);
    return diffs;
  }

  private formatValue(key: string, value: any): string {
    if (value === undefined || value === null) return 'None';
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';

    // Specialized formatting for known keys
    if (key.includes('liquids.')) {
      return `${value}µL`;
    }

    return String(value);
  }
}

