import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MachineCardMiniComponent } from './machine-card-mini.component';
import { MachineWithRuntime } from '../../../../features/workcell/models/workcell-view.models';
import { MachineStatus } from '../../../../features/assets/models/asset.models';
import { provideAnimations } from '@angular/platform-browser/animations';

describe('MachineCardMiniComponent', () => {
    let component: MachineCardMiniComponent;
    let fixture: ComponentFixture<MachineCardMiniComponent>;

    const mockMachine: MachineWithRuntime = {
        name: 'Hamilton STAR',
        type: 'Liquid Handler',
        accession_id: 'machine-1',
        status: MachineStatus.IDLE,
        connectionState: 'connected',
        stateSource: 'live',
        alerts: [],
        plr_definition: {} as any,
        plr_state: {}
    } as any;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [MachineCardMiniComponent],
            providers: [provideAnimations()]
        }).compileComponents();

        fixture = TestBed.createComponent(MachineCardMiniComponent);
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

    it('should emit machineSelected on click', () => {
        component.machine = mockMachine;
        fixture.detectChanges();
        const spy = vi.spyOn(component.machineSelected, 'emit');
        const card = fixture.nativeElement.querySelector('.machine-mini-card');
        card.click();
        expect(spy).toHaveBeenCalledWith(mockMachine);
    });

    it('should show protocol info when running', () => {
        const machineWithRun: MachineWithRuntime = {
            ...mockMachine,
            status: MachineStatus.RUNNING,
            currentRun: {
                id: 'run-1',
                protocolName: 'Sample Prep',
                currentStep: 5,
                totalSteps: 10,
                progress: 50
            }
        };
        component.machine = machineWithRun;
        fixture.detectChanges();

        const protocolName = fixture.nativeElement.querySelector('.protocol-name');
        expect(protocolName.textContent).toContain('Sample Prep');
        
        const progressBar = fixture.nativeElement.querySelector('mat-progress-bar');
        expect(progressBar).toBeTruthy();
    });
});
