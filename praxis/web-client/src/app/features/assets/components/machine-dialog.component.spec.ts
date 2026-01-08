import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MachineDialogComponent } from './machine-dialog.component';
import { AssetService } from '../services/asset.service';
import { ModeService } from '../../../core/services/mode.service';
import { MatDialogRef } from '@angular/material/dialog';
import { of } from 'rxjs';
import { MachineDefinition } from '../models/asset.models';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('MachineDialogComponent', () => {
    let component: MachineDialogComponent;
    let fixture: ComponentFixture<MachineDialogComponent>;
    let mockAssetService: any;
    let mockModeService: any;
    let mockDialogRef: any;

    const mockDefinitions: MachineDefinition[] = [
        {
            accession_id: 'backend-1',
            name: 'HamiltonBackend',
            machine_category: 'liquid_handler_backend',
            frontend_fqn: 'pylabrobot.liquid_handling.LiquidHandler',
            manufacturer: 'Hamilton'
        } as any,
        {
            accession_id: 'backend-2',
            name: 'ChatterBoxBackend',
            machine_category: 'liquid_handler_backend',
            frontend_fqn: 'pylabrobot.liquid_handling.LiquidHandler'
        } as any,
        {
            accession_id: 'backend-3',
            name: 'BMGBackend',
            machine_category: 'plate_reader_backend',
            frontend_fqn: 'pylabrobot.plate_reading.PlateReader'
        } as any
    ];

    beforeEach(async () => {
        mockAssetService = {
            getMachineDefinitions: vi.fn().mockReturnValue(of(mockDefinitions))
        };

        mockModeService = {
            isBrowserMode: vi.fn().mockReturnValue(false)
        };

        mockDialogRef = {
            close: vi.fn()
        };

        await TestBed.configureTestingModule({
            imports: [MachineDialogComponent, NoopAnimationsModule],
            providers: [
                { provide: AssetService, useValue: mockAssetService },
                { provide: ModeService, useValue: mockModeService },
                { provide: MatDialogRef, useValue: mockDialogRef }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(MachineDialogComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should have 3 steps', () => {
        expect(component.steps.length).toBe(3);
        expect(component.steps[0].label).toBe('Machine Type');
        expect(component.steps[1].label).toBe('Backend');
        expect(component.steps[2].label).toBe('Configuration');
    });

    it('should derive frontend types from unique frontend_fqn values', () => {
        expect(component.frontendTypes.length).toBe(2);

        const lhType = component.frontendTypes.find(ft => ft.fqn === 'pylabrobot.liquid_handling.LiquidHandler');
        expect(lhType).toBeDefined();
        expect(lhType?.label).toBe('Liquid Handler');
        expect(lhType?.backendCount).toBe(2);

        const prType = component.frontendTypes.find(ft => ft.fqn === 'pylabrobot.plate_reading.PlateReader');
        expect(prType).toBeDefined();
        expect(prType?.label).toBe('Plate Reader');
        expect(prType?.backendCount).toBe(1);
    });

    it('should filter backends by selected frontend type', () => {
        component.selectFrontendType('pylabrobot.liquid_handling.LiquidHandler');

        expect(component.filteredBackends.length).toBe(2);
        expect(component.filteredBackends.find(b => b.name === 'HamiltonBackend')).toBeDefined();
        expect(component.filteredBackends.find(b => b.name === 'ChatterBoxBackend')).toBeDefined();
        expect(component.filteredBackends.find(b => b.name === 'BMGBackend')).toBeUndefined();
    });

    it('should toggle frontend type selection', () => {
        component.selectFrontendType('pylabrobot.liquid_handling.LiquidHandler');
        expect(component.selectedFrontendFqn).toBe('pylabrobot.liquid_handling.LiquidHandler');

        component.selectFrontendType('pylabrobot.liquid_handling.LiquidHandler');
        expect(component.selectedFrontendFqn).toBeNull();
    });

    it('should allow progression through steps', () => {
        // Step 0: can't proceed without selection
        expect(component.canProceed()).toBe(false);

        // Select a frontend type
        component.selectFrontendType('pylabrobot.liquid_handling.LiquidHandler');
        expect(component.canProceed()).toBe(true);

        // Move to step 1
        component.nextStep();
        expect(component.currentStep).toBe(1);

        // Can proceed with simulated
        expect(component.canProceed()).toBe(true);

        // Move to step 2
        component.nextStep();
        expect(component.currentStep).toBe(2);

        // Can't proceed without name
        expect(component.canProceed()).toBe(false);

        // Set name
        component.form.patchValue({ name: 'Test Machine' });
        expect(component.canProceed()).toBe(true);
    });
});
