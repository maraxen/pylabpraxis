import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MachineCardComponent } from './machine-card.component';
import { MachineWithRuntime } from '../../../../features/workcell/models/workcell-view.models';
import { MachineStatus } from '../../../../features/assets/models/asset.models';
import { provideAnimations } from '@angular/platform-browser/animations';

describe('MachineCardComponent', () => {
    let component: MachineCardComponent;
    let fixture: ComponentFixture<MachineCardComponent>;

    const mockMachine: MachineWithRuntime = {
        name: 'Hamilton STAR',
        type: 'Liquid Handler',
        accession_id: 'machine-1',
        status: MachineStatus.IDLE,
        connectionState: 'connected',
        stateSource: 'live',
        alerts: [],
        plr_definition: {
            name: 'Hamilton STAR',
            type: 'HamiltonSTAR',
            size_x: 1000,
            size_y: 700,
            size_z: 500,
            location: { x: 0, y: 0, z: 0 },
            children: []
        } as any,
        plr_state: {}
    } as any;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [MachineCardComponent],
            providers: [provideAnimations()]
        }).compileComponents();

        fixture = TestBed.createComponent(MachineCardComponent);
        component = fixture.componentInstance;
    });

    it('should create', () => {
        component.machine = mockMachine;
        fixture.detectChanges();
        expect(component).toBeTruthy();
    });

    it('should display machine name', () => {
        component.machine = mockMachine;
        fixture.detectChanges();
        const nameElement = fixture.nativeElement.querySelector('.machine-name');
        expect(nameElement.textContent).toContain('Hamilton STAR');
    });

    it('should display machine type', () => {
        component.machine = mockMachine;
        fixture.detectChanges();
        const typeElement = fixture.nativeElement.querySelector('.machine-type');
        expect(typeElement.textContent).toContain('Liquid Handler');
    });

    it('should emit machineSelected on card click', () => {
        component.machine = mockMachine;
        fixture.detectChanges();
        const spy = vi.spyOn(component.machineSelected, 'emit');
        const card = fixture.nativeElement.querySelector('.machine-card');
        card.click();
        expect(spy).toHaveBeenCalledWith(mockMachine);
    });

    it('should show progress bar when currentRun is present', () => {
        const machineWithRun: MachineWithRuntime = {
            ...mockMachine,
            status: MachineStatus.RUNNING,
            currentRun: {
                id: 'run-1',
                protocolName: 'Sample Prep',
                currentStep: 5,
                totalSteps: 10,
                progress: 50,
                estimatedRemaining: 15
            }
        };
        component.machine = machineWithRun;
        fixture.detectChanges();

        const progressSection = fixture.nativeElement.querySelector('.progress-section');
        expect(progressSection).toBeTruthy();
        expect(progressSection.textContent).toContain('Sample Prep');
        expect(progressSection.textContent).toContain('Step 5/10');
        
        const progressBar = fixture.nativeElement.querySelector('mat-progress-bar');
        expect(progressBar).toBeTruthy();
    });

    it('should show alerts when present', () => {
        const machineWithAlerts: MachineWithRuntime = {
            ...mockMachine,
            alerts: [{ severity: 'warning', message: 'Low tips' }]
        };
        component.machine = machineWithAlerts;
        fixture.detectChanges();

        const alertsSection = fixture.nativeElement.querySelector('.alerts-section');
        expect(alertsSection).toBeTruthy();
        expect(alertsSection.textContent).toContain('Low tips');
    });
});
