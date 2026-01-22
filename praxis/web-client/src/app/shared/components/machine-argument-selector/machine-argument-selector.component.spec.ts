import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MachineArgumentSelectorComponent } from './machine-argument-selector.component';
import { AssetService } from '../../../features/assets/services/asset.service';
import { of } from 'rxjs';
import { PLRCategory } from '../../../core/db/plr-category';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('MachineArgumentSelectorComponent', () => {
  let component: MachineArgumentSelectorComponent;
  let fixture: ComponentFixture<MachineArgumentSelectorComponent>;
  let assetServiceSpy: any;

  beforeEach(async () => {
    assetServiceSpy = {
      getMachineFrontendDefinitions: vi.fn().mockReturnValue(of([])),
      getMachineBackendDefinitions: vi.fn().mockReturnValue(of([])),
      getMachines: vi.fn().mockReturnValue(of([]))
    };

    await TestBed.configureTestingModule({
      imports: [MachineArgumentSelectorComponent],
      providers: [
        { provide: AssetService, useValue: assetServiceSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(MachineArgumentSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('isMachineRequirement', () => {
    // Access private method by casting to any
    const isMachineRequirement = (req: any) => (component as any).isMachineRequirement(req);

    it('should return true for known machine categories', () => {
      const req = { required_plr_category: PLRCategory.LIQUID_HANDLER, type_hint_str: 'LiquidHandler' };
      expect(isMachineRequirement(req)).toBe(true);
    });

    it('should return true for PlateReader category', () => {
      const req = { required_plr_category: PLRCategory.PLATE_READER, type_hint_str: 'PlateReader' };
      expect(isMachineRequirement(req)).toBe(true);
    });

    it('should return true for PlateReader even if category is missing but type hint matches', () => {
      const req = { required_plr_category: null, type_hint_str: 'PlateReader' };
      expect(isMachineRequirement(req)).toBe(true);
    });

    it('should return false for Plate resource', () => {
      const req = { required_plr_category: PLRCategory.PLATE, type_hint_str: 'Plate' };
      expect(isMachineRequirement(req)).toBe(false);
    });

    it('should return false for category containing "plate" but not "reader"', () => {
      const req = { required_plr_category: 'MyPlate', type_hint_str: 'MyPlate' };
      expect(isMachineRequirement(req)).toBe(false);
    });

    it('should return true for category containing "plate" AND "reader"', () => {
      const req = { required_plr_category: 'MyPlateReader', type_hint_str: 'MyPlateReader' };
      expect(isMachineRequirement(req)).toBe(true);
    });
  });
});
