import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MachineStatusBadgeComponent } from './machine-status-badge.component';
import { MachineStatus } from '../../../../features/assets/models/asset.models';

describe('MachineStatusBadgeComponent', () => {
    let component: MachineStatusBadgeComponent;
    let fixture: ComponentFixture<MachineStatusBadgeComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [MachineStatusBadgeComponent]
        }).compileComponents();

        fixture = TestBed.createComponent(MachineStatusBadgeComponent);
        component = fixture.componentInstance;
    });

    it('should create', () => {
        component.status = MachineStatus.IDLE;
        fixture.detectChanges();
        expect(component).toBeTruthy();
    });

    it('should apply correct status class', () => {
        component.status = MachineStatus.RUNNING;
        fixture.detectChanges();
        const badge = fixture.nativeElement.querySelector('.status-badge');
        expect(badge.classList).toContain('running');
    });

    it('should show label by default', () => {
        component.status = MachineStatus.IDLE;
        fixture.detectChanges();
        const label = fixture.nativeElement.querySelector('.status-label');
        expect(label).toBeTruthy();
        expect(label.textContent).toContain('Idle');
    });

    it('should hide label when showLabel is false', () => {
        component.status = MachineStatus.IDLE;
        component.showLabel = false;
        fixture.detectChanges();
        const label = fixture.nativeElement.querySelector('.status-label');
        expect(label).toBeFalsy();
    });

    it('should show source tag when stateSource is not live', () => {
        component.status = MachineStatus.IDLE;
        component.stateSource = 'simulated';
        fixture.detectChanges();
        const sourceTag = fixture.nativeElement.querySelector('.source-tag');
        expect(sourceTag).toBeTruthy();
        expect(sourceTag.textContent).toContain('SIMULATED');
    });

    it('should hide source tag when stateSource is live', () => {
        component.status = MachineStatus.IDLE;
        component.stateSource = 'live';
        fixture.detectChanges();
        const sourceTag = fixture.nativeElement.querySelector('.source-tag');
        expect(sourceTag).toBeFalsy();
    });

    it('should apply compact class when compact is true', () => {
        component.status = MachineStatus.IDLE;
        component.compact = true;
        fixture.detectChanges();
        const badge = fixture.nativeElement.querySelector('.status-badge');
        expect(badge.classList).toContain('compact');
    });
});
