import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DeckViewComponent } from './deck-view.component';
import { PlrResource } from '@core/models/plr.models';
import { describe, it, expect, beforeEach } from 'vitest';

describe('DeckViewComponent', () => {
  let component: DeckViewComponent;
  let fixture: ComponentFixture<DeckViewComponent>;

  const mockResource: PlrResource = {
    name: 'root',
    type: 'Deck',
    location: { x: 0, y: 0, z: 0 },
    size_x: 100,
    size_y: 100,
    size_z: 10,
    children: [
      {
        name: 'child1',
        type: 'Plate',
        location: { x: 10, y: 10, z: 0 },
        size_x: 20,
        size_y: 20,
        size_z: 5,
        children: []
      }
    ]
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DeckViewComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(DeckViewComponent);
    component = fixture.componentInstance;
    component.resource.set(mockResource);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should calculate container dimensions', () => {
    // pixelsPerMm is 0.5
    expect(component.containerWidth()).toBe(50); // 100 * 0.5
    expect(component.containerHeight()).toBe(50); // 100 * 0.5
  });

  it('should render child resources', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const children = compiled.querySelectorAll('.resource-node');
    // One for root, one for child
    expect(children.length).toBe(2);

    // Check child positioning (10, 10) * 0.5 = 5px
    // Find the child element (not the root)
    const childNode = Array.from(children).find(el => (el as HTMLElement).title.includes('child1')) as HTMLElement;
    expect(childNode).toBeTruthy();
    expect(childNode.style.left).toBe('5px');
    expect(childNode.style.top).toBe('5px');
    expect(childNode.style.width).toBe('10px'); // 20 * 0.5
  });
});
