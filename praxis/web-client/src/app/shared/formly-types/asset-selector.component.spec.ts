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
  });

  it('should create', () => {
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should filter resources by name', () => {
    component.field.templateOptions['assetType'] = 'resource';
    fixture.detectChanges(); // Calls ngOnInit
    
    let result: any[] = [];
    component.filteredAssets$.subscribe(assets => result = assets);

    // Initial load
    vi.advanceTimersByTime(350);

    // Trigger value change
    component.formControl.setValue('Plate');
    
    // Wait for debounce
    vi.advanceTimersByTime(350);
    
    expect(result.length).toBe(2);
    expect(result.map(a => a.name)).toEqual(expect.arrayContaining(['Plate 1', 'Plate 2']));
  });

  it('should filter resources by plrTypeFilter', () => {
    component.field.templateOptions['assetType'] = 'resource';
    component.field.templateOptions['plrTypeFilter'] = 'plate';
    fixture.detectChanges();

    let result: any[] = [];
    component.filteredAssets$.subscribe(assets => result = assets);

    component.formControl.setValue(''); 
    
    vi.advanceTimersByTime(350);
    
    expect(result.length).toBe(2);
    expect(result.every(a => a.name.includes('Plate'))).toBe(true);
  });

  it('should provide definition details for hover tags', () => {
    component.field.templateOptions['assetType'] = 'resource';
    fixture.detectChanges();

    let result: any[] = [];
    component.filteredAssets$.subscribe(assets => result = assets);

    component.formControl.setValue('');
    vi.advanceTimersByTime(350);

    expect(result.length).toBeGreaterThan(0);
    const plate1 = result.find(a => a.name === 'Plate 1');
    const details = component.getAssetDetails(plate1!);
    expect(details).toContain('96');
    expect(details).toContain('v-bottom');
  });

  it('should open dialog and create resource on save', () => {
     component.field.templateOptions['assetType'] = 'resource';
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
});
