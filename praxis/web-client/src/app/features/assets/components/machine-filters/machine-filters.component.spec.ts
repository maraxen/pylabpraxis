import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MachineFiltersComponent } from './machine-filters.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { describe, it, expect, beforeEach } from 'vitest';
import { Machine, MachineStatus, MachineDefinition } from '../../models/asset.models';

describe('MachineFiltersComponent', () => {
    let component: MachineFiltersComponent;
    let fixture: ComponentFixture<MachineFiltersComponent>;

    const mockMachines: Machine[] = [
        { accession_id: '1', name: 'Robot 1', status: MachineStatus.IDLE, machine_category: 'LiquidHandler' } as any,
        { accession_id: '2', name: 'Reader 1', status: MachineStatus.RUNNING, machine_category: 'PlateReader' } as any,
        { accession_id: '3', name: 'Backend 1', status: MachineStatus.IDLE, machine_category: 'STAR' } as any,
        { accession_id: '4', name: 'Backend 2', status: MachineStatus.IDLE, machine_category: 'OT2Backend' } as any,
        { accession_id: '5', name: 'Backend 3', status: MachineStatus.IDLE, machine_category: 'ChatterboxBackend' } as any,
    ];

    const mockMachineDefinitions: MachineDefinition[] = [
        { accession_id: 'def1', name: 'Def 1', compatible_backends: ['STAR', 'Simulator'] } as any
    ];

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [MachineFiltersComponent, NoopAnimationsModule],
        }).compileComponents();

        fixture = TestBed.createComponent(MachineFiltersComponent);
        component = fixture.componentInstance;
        
        // Standard @Input setters
        component.machines = mockMachines;
        component.machineDefinitions = mockMachineDefinitions;
        
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should filter out backend names from availableCategories', () => {
        const categories = component.availableCategories();
        
        // Should include valid categories
        expect(categories).toContain('LiquidHandler');
        expect(categories).toContain('PlateReader');
        
        // Should EXCLUDE backend names
        expect(categories).not.toContain('STAR'); // From availableBackends
        expect(categories).not.toContain('OT2Backend'); // Matches 'Backend' pattern
        expect(categories).not.toContain('ChatterboxBackend'); // Matches 'Backend' pattern
    });

    it('should include backends in availableBackends', () => {
        const backends = component.availableBackends();
        expect(backends).toContain('STAR');
        expect(backends).toContain('Simulator');
    });
});