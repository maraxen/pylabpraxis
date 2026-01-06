import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { StateResolutionDialogComponent } from './state-resolution-dialog.component';
import {
    StateResolutionDialogData,
    StateResolutionDialogResult,
    UncertainStateChange,
} from '../../models/state-resolution.models';

describe('StateResolutionDialogComponent', () => {
    let component: StateResolutionDialogComponent;
    let fixture: ComponentFixture<StateResolutionDialogComponent>;
    let dialogRef: jasmine.SpyObj<MatDialogRef<StateResolutionDialogComponent>>;

    const mockUncertainStates: UncertainStateChange[] = [
        {
            state_key: 'plate.A1.volume',
            current_value: 100.0,
            expected_value: 50.0,
            description: 'Volume after aspiration',
            resolution_type: 'volume',
            resource_name: 'plate.A1',
            property_name: 'volume',
            property_type: 'volume',
            suggested_resolutions: ['Confirm success', 'Confirm failure'],
        },
        {
            state_key: 'tip_rack.tips_loaded',
            current_value: false,
            expected_value: true,
            description: 'Tips loaded state',
            resolution_type: 'boolean',
            resource_name: 'tip_rack',
            property_name: 'tips_loaded',
            property_type: 'tip_loaded',
            suggested_resolutions: [],
        },
    ];

    const mockDialogData: StateResolutionDialogData = {
        runId: 'run-123',
        operation: {
            operation_id: 'op-1',
            method_name: 'aspirate',
            description: 'Aspirate 50µL from plate.A1',
            error_message: 'Pressure fault detected',
            error_type: 'PressureFault',
        },
        uncertainStates: mockUncertainStates,
    };

    beforeEach(async () => {
        dialogRef = jasmine.createSpyObj('MatDialogRef', ['close']);

        await TestBed.configureTestingModule({
            imports: [
                StateResolutionDialogComponent,
                NoopAnimationsModule,
                ReactiveFormsModule,
            ],
            providers: [
                { provide: MatDialogRef, useValue: dialogRef },
                { provide: MAT_DIALOG_DATA, useValue: mockDialogData },
            ],
        }).compileComponents();

        fixture = TestBed.createComponent(StateResolutionDialogComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should initialize form with default values', () => {
        expect(component.form.get('resolutionType')?.value).toBe('unknown');
        expect(component.form.get('notes')?.value).toBe('');
    });

    it('should initialize resolved values from uncertain states', () => {
        expect(component.resolvedValues['plate.A1.volume']).toBe(100.0);
        expect(component.resolvedValues['tip_rack.tips_loaded']).toBe(false);
    });

    it('should have resolution type options', () => {
        expect(component.resolutionTypeOptions.length).toBe(5);
        expect(component.resolutionTypeOptions[0].value).toBe('confirmed_success');
    });

    describe('formatValue', () => {
        it('should format numbers', () => {
            expect(component.formatValue(100.5)).toBe('100.50');
        });

        it('should format booleans', () => {
            expect(component.formatValue(true)).toBe('Yes');
            expect(component.formatValue(false)).toBe('No');
        });

        it('should handle null/undefined', () => {
            expect(component.formatValue(null)).toBe('Unknown');
            expect(component.formatValue(undefined)).toBe('Unknown');
        });
    });

    describe('getPropertyTypeLabel', () => {
        it('should return labels for known types', () => {
            expect(component.getPropertyTypeLabel('volume')).toBe('Volume');
            expect(component.getPropertyTypeLabel('has_liquid')).toBe('Contains Liquid');
        });

        it('should fallback for unknown types', () => {
            expect(component.getPropertyTypeLabel('unknown_type')).toBe('State');
        });
    });

    describe('quick actions', () => {
        it('confirmAsSuccess should set resolution type and expected values', () => {
            component.confirmAsSuccess();

            expect(component.form.get('resolutionType')?.value).toBe('confirmed_success');
            expect(component.resolvedValues['plate.A1.volume']).toBe(50.0);
        });

        it('confirmAsFailure should set resolution type and current values', () => {
            component.confirmAsFailure();

            expect(component.form.get('resolutionType')?.value).toBe('confirmed_failure');
            expect(component.resolvedValues['plate.A1.volume']).toBe(100.0);
        });
    });

    describe('canEditValues', () => {
        it('should return true for partial or arbitrary resolution types', () => {
            component.form.patchValue({ resolutionType: 'partial' });
            expect(component.canEditValues()).toBeTrue();

            component.form.patchValue({ resolutionType: 'arbitrary' });
            expect(component.canEditValues()).toBeTrue();
        });

        it('should return false for other resolution types', () => {
            component.form.patchValue({ resolutionType: 'confirmed_success' });
            expect(component.canEditValues()).toBeFalse();

            component.form.patchValue({ resolutionType: 'unknown' });
            expect(component.canEditValues()).toBeFalse();
        });
    });

    describe('submit actions', () => {
        it('submitAndResume should close dialog with resume action', () => {
            component.form.patchValue({ resolutionType: 'confirmed_success' });
            component.submitAndResume();

            expect(dialogRef.close).toHaveBeenCalled();
            const result = dialogRef.close.calls.mostRecent().args[0] as StateResolutionDialogResult;
            expect(result.action).toBe('resume');
            expect(result.resolution?.resolution_type).toBe('confirmed_success');
        });

        it('submitAndAbort should close dialog with abort action', () => {
            component.submitAndAbort();

            expect(dialogRef.close).toHaveBeenCalled();
            const result = dialogRef.close.calls.mostRecent().args[0] as StateResolutionDialogResult;
            expect(result.action).toBe('abort');
        });

        it('cancel should close dialog with null', () => {
            component.cancel();

            expect(dialogRef.close).toHaveBeenCalledWith(null);
        });
    });

    describe('updateResolvedValue', () => {
        it('should parse numeric values', () => {
            const event = { target: { value: '75.5' } } as unknown as Event;
            component.updateResolvedValue('plate.A1.volume', event);

            expect(component.resolvedValues['plate.A1.volume']).toBe(75.5);
        });

        it('should parse boolean string values', () => {
            const eventTrue = { target: { value: 'true' } } as unknown as Event;
            component.updateResolvedValue('tip_rack.tips_loaded', eventTrue);
            expect(component.resolvedValues['tip_rack.tips_loaded']).toBe(true);

            const eventFalse = { target: { value: 'false' } } as unknown as Event;
            component.updateResolvedValue('tip_rack.tips_loaded', eventFalse);
            expect(component.resolvedValues['tip_rack.tips_loaded']).toBe(false);
        });

        it('should keep string values as-is', () => {
            const event = { target: { value: 'some_text' } } as unknown as Event;
            component.updateResolvedValue('arbitrary.key', event);

            expect(component.resolvedValues['arbitrary.key']).toBe('some_text');
        });
    });
});
