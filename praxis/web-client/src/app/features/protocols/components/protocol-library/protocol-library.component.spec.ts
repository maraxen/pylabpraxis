import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ProtocolLibraryComponent } from './protocol-library.component';
import { ProtocolService } from '../../services/protocol.service';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { of } from 'rxjs';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { ProtocolDefinition } from '../../models/protocol.models';
import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('ProtocolLibraryComponent', () => {
  let component: ProtocolLibraryComponent;
  let fixture: ComponentFixture<ProtocolLibraryComponent>;
  let mockProtocolService: { getProtocols: any; uploadProtocol: any };
  let mockRouter: { navigate: any };
  let mockDialog: { open: any };

  const mockProtocols: ProtocolDefinition[] = [
    {
      accession_id: 'p1',
      name: 'Protocol 1',
      version: '1.0',
      is_top_level: true,
      category: 'DNA Extraction',
      parameters: [],
      assets: [],
      simulation_result: { passed: true } as any
    },
    {
      accession_id: 'p2',
      name: 'Protocol 2',
      version: '1.0',
      is_top_level: false,
      category: 'DNA Extraction',
      parameters: [],
      assets: [],
      simulation_result: { passed: false } as any
    },
    {
      accession_id: 'p3',
      name: 'Protocol 3',
      version: '1.0',
      is_top_level: true,
      category: 'Liquid Handling',
      parameters: [],
      assets: [],
      // No simulation result
    }
  ];

  beforeEach(async () => {
    mockProtocolService = {
      getProtocols: vi.fn().mockReturnValue(of(mockProtocols)),
      uploadProtocol: vi.fn()
    };

    mockRouter = {
      navigate: vi.fn()
    };

    mockDialog = {
      open: vi.fn()
    };

    await TestBed.configureTestingModule({
      imports: [ProtocolLibraryComponent, NoopAnimationsModule],
      providers: [
        { provide: ProtocolService, useValue: mockProtocolService },
        { provide: Router, useValue: mockRouter },
        { provide: MatDialog, useValue: mockDialog }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ProtocolLibraryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges(); // triggers ngOnInit -> loadProtocols
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load protocols on init', () => {
    expect(component.protocols().length).toBe(3);
    // ViewConfig filters[0] is Category, options should include "All Categories" + unique categories
    const categoryFilter = component.viewConfig().filters?.find(f => f.key === 'category');
    // Options: "All Categories", "DNA Extraction", "Liquid Handling"
    expect(categoryFilter?.options?.length).toBe(3);
  });

  it('should filter by category', () => {
    component.onStateChange({
      ...component.viewState(),
      filters: { category: ['DNA Extraction'] }
    });
    fixture.detectChanges();
    expect(component.filteredProtocols().length).toBe(2);
    expect(component.filteredProtocols().every(p => p.category === 'DNA Extraction')).toBe(true);
  });

  it('should filter by type (top level)', () => {
    component.onStateChange({
      ...component.viewState(),
      filters: { type: ['top_level'] }
    });
    fixture.detectChanges();
    expect(component.filteredProtocols().length).toBe(2);
    expect(component.filteredProtocols().every(p => p.is_top_level)).toBe(true);
  });

  it('should filter by type (sub protocol)', () => {
    component.onStateChange({
      ...component.viewState(),
      filters: { type: ['sub'] }
    });
    fixture.detectChanges();
    expect(component.filteredProtocols().length).toBe(1);
    expect(component.filteredProtocols()[0].accession_id).toBe('p2');
  });

  it('should filter by status (passed)', () => {
    component.onStateChange({
      ...component.viewState(),
      filters: { status: ['passed'] }
    });
    fixture.detectChanges();
    expect(component.filteredProtocols().length).toBe(1);
    expect(component.filteredProtocols()[0].accession_id).toBe('p1');
  });

  it('should filter by status (failed)', () => {
    component.onStateChange({
      ...component.viewState(),
      filters: { status: ['failed'] }
    });
    fixture.detectChanges();
    expect(component.filteredProtocols().length).toBe(1);
    expect(component.filteredProtocols()[0].accession_id).toBe('p2');
  });

  it('should filter by status (none)', () => {
    component.onStateChange({
      ...component.viewState(),
      filters: { status: ['none'] }
    });
    fixture.detectChanges();
    expect(component.filteredProtocols().length).toBe(1);
    expect(component.filteredProtocols()[0].accession_id).toBe('p3');
  });

  it('should combine filters', () => {
    component.onStateChange({
      ...component.viewState(),
      filters: {
        category: ['DNA Extraction'],
        type: ['top_level']
      }
    });
    fixture.detectChanges();
    expect(component.filteredProtocols().length).toBe(1);
    expect(component.filteredProtocols()[0].accession_id).toBe('p1');
  });

  it('should support view switching', () => {
    expect(component.viewState().viewType).toBe('table');

    component.onStateChange({
      ...component.viewState(),
      viewType: 'card'
    });
    fixture.detectChanges();

    expect(component.viewState().viewType).toBe('card');
  });
});
