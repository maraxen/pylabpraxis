import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ProtocolProgressPanelComponent } from './protocol-progress-panel.component';

describe('ProtocolProgressPanelComponent', () => {
  let component: ProtocolProgressPanelComponent;
  let fixture: ComponentFixture<ProtocolProgressPanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProtocolProgressPanelComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(ProtocolProgressPanelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should show "No active protocol" when no run is provided', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('No active protocol');
  });

  it('should show progress when run is provided', () => {
    fixture.componentRef.setInput('run', {
      id: 'run-1',
      protocolName: 'Test Protocol',
      currentStep: 2,
      totalSteps: 10,
      progress: 20
    });
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Test Protocol');
    expect(compiled.textContent).toContain('20%');
    expect(compiled.textContent).toContain('2 / 10');
  });
});