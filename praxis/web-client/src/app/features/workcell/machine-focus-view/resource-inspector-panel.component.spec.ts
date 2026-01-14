import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ResourceInspectorPanelComponent } from './resource-inspector-panel.component';

describe('ResourceInspectorPanelComponent', () => {
  let component: ResourceInspectorPanelComponent;
  let fixture: ComponentFixture<ResourceInspectorPanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ResourceInspectorPanelComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(ResourceInspectorPanelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should show placeholder when no resource is selected', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Click a resource on the deck to inspect');
  });

  it('should display resource details when provided', () => {
    fixture.componentRef.setInput('resource', {
      name: 'Test Plate',
      type: '96-well plate',
      location: { x: 10, y: 20, z: 0 },
      dimensions: { x: 127, y: 85, z: 14 },
      volume: 50,
      maxVolume: 200,
      slotId: 'Slot 1'
    });
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Test Plate');
    expect(compiled.textContent).toContain('96-well plate');
    expect(compiled.textContent).toContain('Slot 1');
    expect(compiled.textContent).toContain('50');
    expect(compiled.textContent).toContain('200');
  });
});