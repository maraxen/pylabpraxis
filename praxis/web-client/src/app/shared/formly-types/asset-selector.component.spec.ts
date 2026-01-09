import { ComponentFixture, TestBed, getTestBed } from '@angular/core/testing';
import { AssetSelectorComponent } from './asset-selector.component';
import { AssetService } from '../../features/assets/services/asset.service';
import { of } from 'rxjs';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { FormlyModule } from '@ngx-formly/core';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { Resource, ResourceDefinition } from '../../features/assets/models/asset.models';
import { describe, it, expect, beforeEach, afterEach, vi, beforeAll } from 'vitest';
import { BrowserDynamicTestingModule, platformBrowserDynamicTesting } from '@angular/platform-browser-dynamic/testing';
import { MatDialog } from '@angular/material/dialog';

describe('AssetSelectorComponent', () => {
  let component: AssetSelectorComponent;
  let fixture: ComponentFixture<AssetSelectorComponent>;
  let mockAssetService: any;
  let mockDialog: any;

  beforeAll(() => {
    const testBed = getTestBed();
    if (!testBed.platform) {
      testBed.initTestEnvironment(
        BrowserDynamicTestingModule,
        platformBrowserDynamicTesting()
      );
    }
  });

  afterEach(() => {
    vi.useRealTimers();
    getTestBed().resetTestingModule();
  });

  const mockResources: Resource[] = [
    { accession_id: 'res-1', name: 'Plate 1', status: 'available' as any, resource_definition_accession_id: 'def-1' },
    { accession_id: 'res-2', name: 'TipRack 1', status: 'available' as any, resource_definition_accession_id: 'def-2' },
    { accession_id: 'res-3', name: 'Plate 2', status: 'in_use' as any, resource_definition_accession_id: 'def-1' }
  ];

  const mockDefinitions: ResourceDefinition[] = [
    { accession_id: 'def-1', name: 'Standard 96 Plate', plr_category: 'plate', is_consumable: true, num_items: 96, plate_type: 'v-bottom' },
    { accession_id: 'def-2', name: 'Standard Tip Rack', plr_category: 'tip_rack', is_consumable: true, tip_volume_ul: 300 }
  ];

  beforeEach(async () => {
    vi.useFakeTimers();
    mockAssetService = {
      getResources: vi.fn().mockReturnValue(of(mockResources)),
      getResourceDefinitions: vi.fn().mockReturnValue(of(mockDefinitions)),
      getMachines: vi.fn().mockReturnValue(of([])),
      createResource: vi.fn()
    };

    mockDialog = {
      open: vi.fn()
    };

    await TestBed.configureTestingModule({
      imports: [
        AssetSelectorComponent,
        ReactiveFormsModule,
        FormlyModule.forRoot(),
        NoopAnimationsModule
      ],
      providers: [
        { provide: AssetService, useValue: mockAssetService },
        { provide: MatDialog, useValue: mockDialog }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AssetSelectorComponent);
    component = fixture.componentInstance;

    const formControl = new FormControl();
    const field: any = {
      key: 'asset',
      formControl: formControl,
      templateOptions: { placeholder: 'Select Asset' }
    };

    component.field = field;
    Object.defineProperty(component, 'to', { get: () => component.field.templateOptions });
    Object.defineProperty(component, 'props', { get: () => component.field.templateOptions });
  });

  it('should create', () => {
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });



  it('should open dialog and create resource on save', () => {
    if (component.field.templateOptions) {
      component.field.templateOptions['assetType'] = 'resource';
    }
    fixture.detectChanges();

    const mockResult = { name: 'New Res' };
    const mockCreatedRes = { accession_id: 'new-1', name: 'New Res' };

    mockDialog.open.mockReturnValue({
      afterClosed: () => of(mockResult)
    });

    mockAssetService.createResource.mockReturnValue(of(mockCreatedRes));

    // We expect openDialog method to exist
    (component as any).openDialog();

    expect(mockDialog.open).toHaveBeenCalled();
    expect(mockAssetService.createResource).toHaveBeenCalledWith(mockResult);
    expect(component.formControl.value).toEqual(mockCreatedRes);
  });

  it('should prioritize available assets over in_use assets in auto mode', () => {
    if (component.field.templateOptions) {
      component.field.templateOptions['assetType'] = 'resource';
      component.field.templateOptions['plrTypeFilter'] = 'plate';
    }

    // Initial load triggers loadAssets -> selectBestAuto
    fixture.detectChanges();

    // res-1 is available, res-3 is in_use. Both are plates (implied by definitions)
    // res-1 should be selected
    const autoAsset = component.autoAsset();
    expect(autoAsset).toBeTruthy();
    expect(autoAsset?.accession_id).toBe('res-1');
  });

  it('should sort options by score (available first)', (done) => {
    if (component.field.templateOptions) {
      component.field.templateOptions['assetType'] = 'resource';
    }
    fixture.detectChanges();

    // Trigger filtering
    (component as any).getFilteredOptions('').subscribe((options: any[]) => {
      // options should be sorted: res-1 (available), res-2 (available), res-3 (in_use)
      // Note: both 1 and 2 are available. Tie-breaker is name length?
      // "Plate 1" vs "TipRack 1". Plate 1 is shorter.

      expect(options.length).toBe(3);
      expect(options[0].asset.accession_id).toBe('res-1');
      expect(options[options.length - 1].asset.accession_id).toBe('res-3');
      done();
    });
  });
});
