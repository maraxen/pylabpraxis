import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { AffectedStateViewerComponent } from './affected-state-viewer.component';
import { UncertainStateChange } from '../../models/state-resolution.models';

describe('AffectedStateViewerComponent', () => {
    let component: AffectedStateViewerComponent;
    let fixture: ComponentFixture<AffectedStateViewerComponent>;

    const mockStates: UncertainStateChange[] = [
        {
            state_key: 'plate.A1.volume',
            current_value: 100.0,
            expected_value: 50.0,
            description: 'Volume after aspiration',
            resolution_type: 'volume',
            resource_name: 'plate.A1',
            property_name: 'volume',
            property_type: 'volume',
            suggested_resolutions: [],
        },
        {
            state_key: 'tip_rack.tips',
            current_value: false,
            expected_value: true,
            description: 'Tips loaded',
            resolution_type: 'boolean',
            resource_name: 'tip_rack',
            property_name: 'has_tip',
            property_type: 'has_tip',
            suggested_resolutions: [],
        },
        {
            state_key: 'plate.temperature',
            current_value: 25.0,
            expected_value: undefined,
            description: 'Temperature',
            resolution_type: 'temperature',
            resource_name: 'plate',
            property_name: 'temp',
            property_type: 'temperature',
            suggested_resolutions: [],
        },
    ];

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [AffectedStateViewerComponent, NoopAnimationsModule],
        }).compileComponents();

        fixture = TestBed.createComponent(AffectedStateViewerComponent);
        component = fixture.componentInstance;
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should display states when provided', () => {
        component.states = mockStates;
        fixture.detectChanges();

        const rows = fixture.nativeElement.querySelectorAll('.state-row');
        // Header row + data rows
        expect(rows.length).toBe(3);
    });

    it('should show empty state when no states', () => {
        component.states = [];
        fixture.detectChanges();

        const emptyState = fixture.nativeElement.querySelector('.empty-state');
        expect(emptyState).toBeTruthy();
    });

    describe('getPropertyTypeLabel', () => {
        it('should return correct labels', () => {
            expect(component.getPropertyTypeLabel('volume')).toBe('Volume (µL)');
            expect(component.getPropertyTypeLabel('has_liquid')).toBe('Contains Liquid');
            expect(component.getPropertyTypeLabel('has_tip')).toBe('Has Tip');
            expect(component.getPropertyTypeLabel('temperature')).toBe('Temperature (°C)');
        });

        it('should return State for unknown types', () => {
            expect(component.getPropertyTypeLabel('custom')).toBe('State');
        });
    });

    describe('getPropertyIcon', () => {
        it('should return correct icons', () => {
            expect(component.getPropertyIcon('volume')).toBe('water_drop');
            expect(component.getPropertyIcon('has_tip')).toBe('push_pin');
            expect(component.getPropertyIcon('temperature')).toBe('thermostat');
        });

        it('should return info for unknown types', () => {
            expect(component.getPropertyIcon('custom')).toBe('info');
        });
    });

    describe('formatValue', () => {
        it('should format numbers to 2 decimal places', () => {
            expect(component.formatValue(100.5)).toBe('100.50');
            expect(component.formatValue(0)).toBe('0.00');
        });

        it('should format booleans as Yes/No', () => {
            expect(component.formatValue(true)).toBe('Yes');
            expect(component.formatValue(false)).toBe('No');
        });

        it('should return — for null/undefined', () => {
            expect(component.formatValue(null)).toBe('—');
            expect(component.formatValue(undefined)).toBe('—');
        });

        it('should convert other values to string', () => {
            expect(component.formatValue('text')).toBe('text');
        });
    });

    describe('getChangeClass', () => {
        it('should return change-unknown when expected is undefined', () => {
            const state = { ...mockStates[2], expected_value: undefined };
            expect(component.getChangeClass(state as UncertainStateChange)).toBe('change-unknown');
        });

        it('should return change-increase for increasing values', () => {
            const state = { ...mockStates[0], current_value: 50, expected_value: 100 };
            expect(component.getChangeClass(state as UncertainStateChange)).toBe('change-increase');
        });

        it('should return change-decrease for decreasing values', () => {
            const state = { ...mockStates[0], current_value: 100, expected_value: 50 };
            expect(component.getChangeClass(state as UncertainStateChange)).toBe('change-decrease');
        });

        it('should return change-none for equal values', () => {
            const state = { ...mockStates[0], current_value: 100, expected_value: 100 };
            expect(component.getChangeClass(state as UncertainStateChange)).toBe('change-none');
        });

        it('should return change-modified for non-numeric changes', () => {
            const state = { ...mockStates[1], current_value: false, expected_value: true };
            expect(component.getChangeClass(state as UncertainStateChange)).toBe('change-modified');
        });
    });

    describe('editable mode', () => {
        beforeEach(() => {
            component.states = mockStates;
            component.editable = true;
            component.resolvedValues = { 'plate.A1.volume': 75.0 };
            fixture.detectChanges();
        });

        it('should show resolved column when editable', () => {
            const headers = fixture.nativeElement.querySelectorAll('th');
            const headerTexts = Array.from(headers).map((h: any) => h.textContent.trim());
            expect(headerTexts).toContain('Actual Value');
        });

        it('should emit valueChange on input', () => {
            spyOn(component.valueChange, 'emit');

            component.onValueChange('plate.A1.volume', {
                target: { value: '80' },
            } as unknown as Event);

            expect(component.valueChange.emit).toHaveBeenCalledWith({
                key: 'plate.A1.volume',
                value: 80,
            });
        });

        it('should parse boolean values correctly', () => {
            spyOn(component.valueChange, 'emit');

            component.onValueChange('tip_rack.tips', {
                target: { value: 'true' },
            } as unknown as Event);

            expect(component.valueChange.emit).toHaveBeenCalledWith({
                key: 'tip_rack.tips',
                value: true,
            });
        });
    });

    describe('getResolvedValue', () => {
        it('should return value from resolvedValues', () => {
            component.resolvedValues = { 'plate.A1.volume': 75 };
            expect(component.getResolvedValue('plate.A1.volume')).toBe(75);
        });

        it('should return undefined for missing keys', () => {
            component.resolvedValues = {};
            expect(component.getResolvedValue('missing.key')).toBeUndefined();
        });
    });
});
