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
    expect(childNode.style.bottom).toBe('5px');
    expect(childNode.style.width).toBe('10px'); // 20 * 0.5
  });

  it('should correctly visualize tip presence from parent bitmask', () => {
    // Setup a TipRack with children
    const tipRack: PlrResource = {
      name: 'tip_rack',
      type: 'TipRack',
      location: { x: 0, y: 0, z: 0 },
      size_x: 100, size_y: 60, size_z: 10,
      children: [
        { name: 'tip_A1', type: 'Container', location: { x:0, y:0, z:0 }, size_x: 9, size_y: 9, size_z: 10, children: [] },
        { name: 'tip_B1', type: 'Container', location: { x:9, y:0, z:0 }, size_x: 9, size_y: 9, size_z: 10, children: [] }
      ]
    };
    
    component.resource.set(tipRack);
    
    // Bitmask "1" means first bit is 1 (tip_A1), second is 0 (tip_B1)
    // Hex "1" -> 0001 (binary). If index 0 corresponds to LSB, then A1 has tip.
    // Wait, let's check decodeBitmask logic: (bigInt & (1n << BigInt(i))) !== 0n
    // i=0 is 1st bit. 
    component.state.set({
      'tip_rack': { tip_mask: '1' } // 1 in hex is 1 in binary. Bit 0 is set.
    });
    
    fixture.detectChanges();
    
    // Check hasTip logic
    expect(component.hasTip(tipRack.children[0], tipRack, 0)).toBe(true);
    expect(component.hasTip(tipRack.children[1], tipRack, 1)).toBe(false);
  });

  it('should correctly visualize liquid volume from parent arrays', () => {
    // Setup a Plate
    const plate: PlrResource = {
      name: 'plate',
      type: 'Plate',
      location: { x: 0, y: 0, z: 0 },
      size_x: 100, size_y: 60, size_z: 10,
      children: [
        { name: 'well_A1', type: 'Well', location: { x:0, y:0, z:0 }, size_x: 9, size_y: 9, size_z: 10, children: [] },
        { name: 'well_B1', type: 'Well', location: { x:9, y:0, z:0 }, size_x: 9, size_y: 9, size_z: 10, children: [] }
      ]
    };

    component.resource.set(plate);
    component.state.set({
      'plate': { volumes: [50, 0] } // 50ul in first well, 0 in second
    });

    fixture.detectChanges();

    expect(component.hasLiquid(plate.children[0], plate, 0)).toBe(true);
    expect(component.getVolume(plate.children[0], plate, 0)).toBe(50);
    
    expect(component.hasLiquid(plate.children[1], plate, 1)).toBe(false);
    expect(component.getVolume(plate.children[1], plate, 1)).toBe(0);
  });
});
