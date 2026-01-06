/**
 * State Resolution Dialog Component
 *
 * This dialog is shown when a protocol operation fails and there is uncertainty
 * about the resulting state. The user can review affected states and provide
 * resolutions indicating what actually happened.
 */
import { CommonModule } from '@angular/common';
import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatRadioModule } from '@angular/material/radio';
import { MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';

import {
    ResolutionAction,
    ResolutionType,
    StateResolution,
    StateResolutionDialogData,
    StateResolutionDialogResult,
    UncertainStateChange,
} from '../../models/state-resolution.models';

@Component({
    selector: 'app-state-resolution-dialog',
    standalone: true,
    imports: [
    ReactiveFormsModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatRadioModule,
    MatSelectModule,
    MatTooltipModule
],
    templateUrl: './state-resolution-dialog.component.html',
    styleUrl: './state-resolution-dialog.component.scss',
})
export class StateResolutionDialogComponent implements OnInit {
    form: FormGroup;
    resolvedValues: Record<string, unknown> = {};
    selectedResolutionType: ResolutionType = 'unknown';

    /** Resolution type options for the radio group. */
    resolutionTypeOptions: { value: ResolutionType; label: string; description: string }[] = [
        {
            value: 'confirmed_success',
            label: 'Operation Succeeded',
            description: 'The operation completed successfully as intended',
        },
        {
            value: 'confirmed_failure',
            label: 'Operation Failed',
            description: 'The operation did not execute at all - state unchanged',
        },
        {
            value: 'partial',
            label: 'Partial Execution',
            description: 'The operation partially completed - specify values below',
        },
        {
            value: 'arbitrary',
            label: 'Custom Values',
            description: 'I inspected the equipment and will provide exact values',
        },
        {
            value: 'unknown',
            label: 'Cannot Determine',
            description: 'Unable to determine - system will use conservative estimate',
        },
    ];

    constructor(
        public dialogRef: MatDialogRef<StateResolutionDialogComponent>,
        @Inject(MAT_DIALOG_DATA) public data: StateResolutionDialogData,
        private fb: FormBuilder
    ) {
        this.form = this.fb.group({
            resolutionType: ['unknown', Validators.required],
            notes: [''],
        });
    }

    ngOnInit(): void {
        // Initialize resolved values with current values
        this.data.uncertainStates.forEach((state) => {
            this.resolvedValues[state.state_key] = state.current_value;
        });
    }

    /**
     * Get user-friendly label for property type.
     */
    getPropertyTypeLabel(type: string): string {
        const labels: Record<string, string> = {
            volume: 'Volume',
            has_liquid: 'Contains Liquid',
            has_tip: 'Has Tip',
            tip_loaded: 'Tip Loaded',
            temperature: 'Temperature',
            position: 'Position',
            arbitrary: 'State',
        };
        return labels[type] || 'State';
    }

    /**
     * Format a value for display.
     */
    formatValue(value: unknown): string {
        if (value === null || value === undefined) {
            return 'Unknown';
        }
        if (typeof value === 'number') {
            return value.toFixed(2);
        }
        if (typeof value === 'boolean') {
            return value ? 'Yes' : 'No';
        }
        return String(value);
    }

    /**
     * Update resolved value for a specific state.
     */
    updateResolvedValue(stateKey: string, event: Event): void {
        const input = event.target as HTMLInputElement;
        const value = input.value;

        // Try to parse as number
        const numValue = parseFloat(value);
        if (!isNaN(numValue)) {
            this.resolvedValues[stateKey] = numValue;
        } else if (value.toLowerCase() === 'true') {
            this.resolvedValues[stateKey] = true;
        } else if (value.toLowerCase() === 'false') {
            this.resolvedValues[stateKey] = false;
        } else {
            this.resolvedValues[stateKey] = value;
        }
    }

    /**
     * Quick action: set resolved values assuming success.
     */
    confirmAsSuccess(): void {
        this.form.patchValue({ resolutionType: 'confirmed_success' });
        this.data.uncertainStates.forEach((state) => {
            if (state.expected_value !== undefined) {
                this.resolvedValues[state.state_key] = state.expected_value;
            }
        });
    }

    /**
     * Quick action: set resolved values assuming failure (unchanged).
     */
    confirmAsFailure(): void {
        this.form.patchValue({ resolutionType: 'confirmed_failure' });
        this.data.uncertainStates.forEach((state) => {
            this.resolvedValues[state.state_key] = state.current_value;
        });
    }

    /**
     * Submit resolution and resume the run.
     */
    submitAndResume(): void {
        if (!this.form.valid) return;

        const resolution = this.buildResolution();
        const result: StateResolutionDialogResult = {
            action: 'resume',
            resolution,
        };
        this.dialogRef.close(result);
    }

    /**
     * Submit resolution and abort the run.
     */
    submitAndAbort(): void {
        const resolution = this.buildResolution();
        const result: StateResolutionDialogResult = {
            action: 'abort',
            resolution,
        };
        this.dialogRef.close(result);
    }

    /**
     * Cancel without resolving.
     */
    cancel(): void {
        this.dialogRef.close(null);
    }

    /**
     * Check if custom values can be edited.
     */
    canEditValues(): boolean {
        const type = this.form.get('resolutionType')?.value;
        return type === 'partial' || type === 'arbitrary';
    }

    /**
     * Build the resolution object from form state.
     */
    private buildResolution(): StateResolution {
        const formValue = this.form.value;
        return {
            operation_id: this.data.operation.operation_id,
            resolution_type: formValue.resolutionType,
            resolved_values: this.resolvedValues,
            notes: formValue.notes || undefined,
        };
    }
}
