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
    // categoryOptions includes "All Categories" + unique categories
    expect(component.categoryOptions().length).toBe(3); // All, DNA Extraction, Liquid Handling
  });

  it('should filter by category', () => {
    component.selectedCategory.set('DNA Extraction');
    fixture.detectChanges();
    expect(component.filteredProtocols().length).toBe(2);
    expect(component.filteredProtocols().every(p => p.category === 'DNA Extraction')).toBe(true);
  });

  it('should filter by type (top level)', () => {
    component.selectedType.set('top_level');
    fixture.detectChanges();
    expect(component.filteredProtocols().length).toBe(2);
    expect(component.filteredProtocols().every(p => p.is_top_level)).toBe(true);
  });

  it('should filter by type (sub protocol)', () => {
    component.selectedType.set('sub');
    fixture.detectChanges();
    expect(component.filteredProtocols().length).toBe(1);
    expect(component.filteredProtocols()[0].accession_id).toBe('p2');
  });

  it('should filter by status (passed)', () => {
    component.selectedStatus.set('passed');
    fixture.detectChanges();
    expect(component.filteredProtocols().length).toBe(1);
    expect(component.filteredProtocols()[0].accession_id).toBe('p1');
  });

  it('should filter by status (failed)', () => {
    component.selectedStatus.set('failed');
    fixture.detectChanges();
    expect(component.filteredProtocols().length).toBe(1);
    expect(component.filteredProtocols()[0].accession_id).toBe('p2');
  });

  it('should filter by status (none)', () => {
    component.selectedStatus.set('none');
    fixture.detectChanges();
    expect(component.filteredProtocols().length).toBe(1);
    expect(component.filteredProtocols()[0].accession_id).toBe('p3');
  });

  it('should combine filters', () => {
    component.selectedCategory.set('DNA Extraction');
    component.selectedType.set('top_level');
    fixture.detectChanges();
    expect(component.filteredProtocols().length).toBe(1);
    expect(component.filteredProtocols()[0].accession_id).toBe('p1');
  });

  it('should clear filters', () => {
    component.selectedCategory.set('Liquid Handling');
    component.selectedType.set('sub');
    component.clearFilters();
    fixture.detectChanges();
    expect(component.selectedCategory()).toBeNull();
    expect(component.selectedType()).toBe('all');
    expect(component.selectedStatus()).toBe('all');
    expect(component.filteredProtocols().length).toBe(3);
  });

  it('should update filter count', () => {
    expect(component.filterCount()).toBe(0);
    component.selectedCategory.set('DNA Extraction');
    expect(component.filterCount()).toBe(1);
    component.selectedType.set('sub');
    expect(component.filterCount()).toBe(2);
    component.selectedStatus.set('failed');
    expect(component.filterCount()).toBe(3);
  });
});
