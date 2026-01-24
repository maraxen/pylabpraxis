import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MachineFocusViewComponent } from './machine-focus-view.component';
import { MachineWithRuntime } from '../models/workcell-view.models';
import { MachineStatus } from '@features/assets/models/asset.models';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('MachineFocusViewComponent', () => {
  let component: MachineFocusViewComponent;
  let fixture: ComponentFixture<MachineFocusViewComponent>;

  const mockMachine: MachineWithRuntime = {
    accession_id: 'test-id',
    name: 'Test Machine',
    status: MachineStatus.IDLE,
    connectionState: 'connected',
    stateSource: 'live',
    alerts: [],
    plr_definition: {
      name: 'test-deck',
      type: 'HamiltonSTAR',
      location: { x: 0, y: 0, z: 0 },
      size_x: 1000,
      size_y: 500,
      size_z: 0,
      children: []
    } as any,
    plr_state: {}
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MachineFocusViewComponent, NoopAnimationsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(MachineFocusViewComponent);
    component = fixture.componentInstance;
    component.machine = mockMachine;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display the machine name', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('Test Machine');
  });

  it('should emit back when back button is clicked', () => {
    const backSpy = vi.spyOn(component.back, 'emit');
    const backButton = fixture.nativeElement.querySelector('button[title*="Back"]');
    backButton.click();
    expect(backSpy).toHaveBeenCalled();
  });

  it('should emit back when Escape key is pressed', () => {
    const backSpy = vi.spyOn(component.back, 'emit');
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    expect(backSpy).toHaveBeenCalled();
  });
});