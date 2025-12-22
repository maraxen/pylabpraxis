import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { AssetService } from './asset.service';
import { Machine, MachineCreate, Resource, ResourceCreate, MachineStatus, ResourceStatus, MachineDefinition, ResourceDefinition } from '../models/asset.models';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';

describe('AssetService', () => {
  let service: AssetService;
  let httpMock: HttpTestingController;
  const API_URL = '/api/v1';

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        AssetService,
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    });

    service = TestBed.inject(AssetService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  describe('Machines', () => {
    it('should get machines', () => {
      const mockMachines: Machine[] = [
        { accession_id: 'm1', name: 'Machine 1', status: MachineStatus.IDLE },
        { accession_id: 'm2', name: 'Machine 2', status: MachineStatus.RUNNING }
      ];

      service.getMachines().subscribe(machines => {
        expect(machines.length).toBe(2);
        expect(machines).toEqual(mockMachines);
      });

      const req = httpMock.expectOne(`${API_URL}/machines`);
      expect(req.request.method).toBe('GET');
      req.flush(mockMachines);
    });

    it('should create machine', () => {
      const newMachine: MachineCreate = { name: 'New Machine', status: MachineStatus.IDLE };
      const createdMachine: Machine = { accession_id: 'm3', name: newMachine.name, status: newMachine.status! };

      service.createMachine(newMachine).subscribe(machine => {
        expect(machine).toEqual(createdMachine);
      });

      const req = httpMock.expectOne(`${API_URL}/machines`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(newMachine);
      req.flush(createdMachine);
    });

    it('should delete machine', () => {
      service.deleteMachine('m1').subscribe(response => {
        expect(response).toBeNull();
      });

      const req = httpMock.expectOne(`${API_URL}/machines/m1`);
      expect(req.request.method).toBe('DELETE');
      req.flush(null);
    });
  });

  describe('Resources', () => {
    it('should get resources', () => {
      const mockResources: Resource[] = [
        { accession_id: 'r1', name: 'Resource 1', status: ResourceStatus.AVAILABLE },
        { accession_id: 'r2', name: 'Resource 2', status: ResourceStatus.IN_USE }
      ];

      service.getResources().subscribe(resources => {
        expect(resources.length).toBe(2);
        expect(resources).toEqual(mockResources);
      });

      const req = httpMock.expectOne(`${API_URL}/resources`);
      expect(req.request.method).toBe('GET');
      req.flush(mockResources);
    });

    it('should create resource', () => {
      const newResource: ResourceCreate = { name: 'New Resource', status: ResourceStatus.AVAILABLE };
      const createdResource: Resource = { accession_id: 'r3', name: newResource.name, status: newResource.status! };

      service.createResource(newResource).subscribe(resource => {
        expect(resource).toEqual(createdResource);
      });

      const req = httpMock.expectOne(`${API_URL}/resources`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(newResource);
      req.flush(createdResource);
    });

    it('should delete resource', () => {
      service.deleteResource('r1').subscribe(response => {
        expect(response).toBeNull();
      });

      const req = httpMock.expectOne(`${API_URL}/resources/r1`);
      expect(req.request.method).toBe('DELETE');
      req.flush(null);
    });
  });

  describe('Definitions', () => {
    it('should get machine definitions', () => {
      const mockDefs: MachineDefinition[] = [
        { accession_id: 'md1', name: 'Machine Def 1' },
        { accession_id: 'md2', name: 'Machine Def 2' }
      ];

      service.getMachineDefinitions().subscribe(defs => {
        expect(defs.length).toBe(2);
        expect(defs).toEqual(mockDefs);
      });

      const req = httpMock.expectOne(`${API_URL}/assets/definitions?type=machine`);
      expect(req.request.method).toBe('GET');
      req.flush(mockDefs);
    });

    it('should get resource definitions', () => {
      const mockDefs: ResourceDefinition[] = [
        { accession_id: 'rd1', name: 'Resource Def 1', is_consumable: false },
        { accession_id: 'rd2', name: 'Resource Def 2', is_consumable: true }
      ];

      service.getResourceDefinitions().subscribe(defs => {
        expect(defs.length).toBe(2);
        expect(defs).toEqual(mockDefs);
      });

      const req = httpMock.expectOne(`${API_URL}/assets/definitions?type=resource`);
      expect(req.request.method).toBe('GET');
      req.flush(mockDefs);
    });
  });
});
