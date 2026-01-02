import { Component, input, output, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { SlotAssignment } from '../../models/carrier-inference.models';

/**
 * Step 2: Guide user to place resources in carrier slots.
 */
@Component({
    selector: 'app-resource-placement-step',
    standalone: true,
    imports: [CommonModule, MatIconModule, MatButtonModule, DragDropModule],
    template: `
        <div class="step-content">
            <h3 class="step-title">
                <mat-icon>science</mat-icon>
                Step 2: Place Resources in Slots
            </h3>
            <p class="instruction">
                Place each resource in its designated slot. Follow the order below for optimal access.
            </p>
            
            <div class="resource-list" cdkDropList>
                @for (assignment of assignments(); track assignment.resource.name; let i = $index) {
                    <div class="resource-item" 
                         [class.current]="i === currentIndex()"
                         [class.completed]="assignment.placed"
                         [class.pending]="!assignment.placed && i > currentIndex()"
                         cdkDrag
                         [cdkDragData]="assignment"
                         [cdkDragDisabled]="assignment.placed">
                        
                        <div class="drag-placeholder" *cdkDragPlaceholder></div>
                        <div class="drag-preview" *cdkDragPreview>
                            {{ assignment.resource.name }}
                        </div>
                        
                        <div class="order-badge" [class.active]="i === currentIndex()">
                            @if (assignment.placed) {
                                <mat-icon>check</mat-icon>
                            } @else {
                                {{ i + 1 }}
                            }
                        </div>
                        
                        <div class="resource-info">
                            <span class="resource-name">{{ assignment.resource.name }}</span>
                            <mat-icon class="arrow">arrow_forward</mat-icon>
                            <span class="slot-location">
                                {{ assignment.carrier.name }}, {{ assignment.slot.name }}
                            </span>
                        </div>
                        
                        @if (i === currentIndex() && !assignment.placed) {
                            <button mat-flat-button color="primary" 
                                    (click)="onMarkPlaced(assignment)">
                                Done
                            </button>
                        }
                    </div>
                }
                
                @if (assignments().length === 0) {
                    <div class="no-resources">
                        <mat-icon>check_circle</mat-icon>
                        <span>No resources to place</span>
                    </div>
                }
            </div>
            
            <div class="z-axis-hint" *ngIf="showZAxisHint()">
                <mat-icon>info</mat-icon>
                <span>Resources are ordered by Z-axis for optimal placement (lowest first)</span>
            </div>
            
            <div class="progress-summary">
                <mat-icon [class.complete]="allPlaced()">
                    {{ allPlaced() ? 'check_circle' : 'pending' }}
                </mat-icon>
                <span>{{ placedCount() }}/{{ assignments().length }} resources placed</span>
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
        
        .resource-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 16px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .resource-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            background: var(--sys-surface-container);
            border-radius: 8px;
            border: 1px solid var(--sys-outline-variant);
            transition: all 0.2s ease;
        }
        
        .resource-item.current {
            background: var(--sys-tertiary-container);
            border-color: var(--sys-tertiary);
        }
        
        .resource-item.completed {
            background: var(--sys-primary-container);
            border-color: var(--sys-primary);
            opacity: 0.8;
        }
        
        .resource-item.pending {
            opacity: 0.6;
        }
        
        .order-badge {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: var(--sys-surface-container-high);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.875rem;
            flex-shrink: 0;
        }
        
        .order-badge.active {
            background: var(--sys-tertiary);
            color: var(--sys-on-tertiary);
        }

        .resource-item:not(.completed) {
            cursor: grab;
        }
        
        .resource-item:not(.completed):active {
            cursor: grabbing;
        }

        .cdk-drag-preview {
            box-sizing: border-box;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            background: var(--sys-surface-container);
            padding: 12px 16px;
            color: var(--sys-on-surface);
            font-weight: 500;
            border: 1px solid var(--sys-primary);
            z-index: 1000;
        }
        
        .cdk-drag-placeholder {
            opacity: 0;
        }
        
        .cdk-drag-animating {
            transition: transform 250ms cubic-bezier(0, 0, 0.2, 1);
        }
        
        .resource-list.cdk-drop-list-dragging .resource-item:not(.cdk-drag-placeholder) {
            transition: transform 250ms cubic-bezier(0, 0, 0.2, 1);
        }
        
        .resource-item.completed .order-badge {
            background: var(--sys-primary);
            color: var(--sys-on-primary);
        }
        
        .resource-info {
            display: flex;
            align-items: center;
            gap: 8px;
            flex: 1;
        }
        
        .resource-name {
            font-weight: 500;
            color: var(--sys-on-surface);
        }
        
        .arrow {
            color: var(--sys-on-surface-variant);
            font-size: 18px;
        }
        
        .slot-location {
            color: var(--sys-on-surface-variant);
        }
        
        .no-resources {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 16px;
            background: var(--sys-secondary-container);
            border-radius: 8px;
            color: var(--sys-on-secondary-container);
        }
        
        .z-axis-hint {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px;
            background: var(--sys-tertiary-container);
            border-radius: 8px;
            color: var(--sys-on-tertiary-container);
            font-size: 0.875rem;
            margin-bottom: 16px;
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
export class ResourcePlacementStepComponent {
    assignments = input.required<SlotAssignment[]>();

    resourcePlaced = output<{ resourceName: string; placed: boolean }>();

    currentIndex = signal(0);

    placedCount = computed(() =>
        this.assignments().filter(a => a.placed).length
    );

    allPlaced = computed(() =>
        this.assignments().length > 0 &&
        this.assignments().every(a => a.placed)
    );

    showZAxisHint = computed(() =>
        this.assignments().length > 1
    );

    onMarkPlaced(assignment: SlotAssignment): void {
        this.resourcePlaced.emit({ resourceName: assignment.resource.name, placed: true });

        // Auto-advance to next unplaced item
        const nextIndex = this.assignments().findIndex((a, i) =>
            i > this.currentIndex() && !a.placed
        );
        if (nextIndex !== -1) {
            this.currentIndex.set(nextIndex);
        }
    }
}
