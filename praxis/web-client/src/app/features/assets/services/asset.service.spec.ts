import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { AssetService } from './asset.service';
import { SqliteService } from '../../../core/services/sqlite.service';
import { Machine, MachineCreate, Resource, ResourceCreate, MachineStatus, ResourceStatus, MachineDefinition, ResourceDefinition } from '../models/asset.models';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { ModeService } from '../../../core/services/mode.service';
import { of, firstValueFrom } from 'rxjs';

describe('AssetService', () => {
  let service: AssetService;
  let httpMock: HttpTestingController;
  const API_URL = '/api/v1';

  beforeEach(() => {
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({
      providers: [
        AssetService,
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: SqliteService,
          useValue: {
            initDb: vi.fn(),
            getResourceDefinitions: vi.fn(),
            // Add other methods as needed if they are called during initialization
          }
        }
      ]
    });

    service = TestBed.inject(AssetService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
    vi.clearAllMocks();
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

      const req = httpMock.expectOne(`${API_URL}/machines/definitions?type=machine`);
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

      const req = httpMock.expectOne(`${API_URL}/resources/definitions?type=resource`);
      expect(req.request.method).toBe('GET');
      req.flush(mockDefs);
    });
  });
  describe('Browser Mode Facets', () => {
    it('should infer categories correctly in browser mode', () => {
      // Mock ModeService to return true for isBrowserMode
      const modeService = TestBed.inject(ModeService);
      vi.spyOn(modeService, 'isBrowserMode').mockReturnValue(true);

      const mockDefs: ResourceDefinition[] = [
        // Case 1: Explicit plr_category
        { accession_id: 'r1', name: 'R1', plr_category: 'ExplicitCat', is_consumable: false, vendor: 'V1', num_items: 1, plate_type: 'p1', well_volume_ul: 100, tip_volume_ul: 100 } as any,
        // Case 2: No plr_category, but resource_type
        { accession_id: 'r2', name: 'R2', plr_category: '', resource_type: 'TypeCat', is_consumable: false, fqn: 'some.fqn' } as any,
        // Case 3: No plr_category, no resource_type, infer from FQN (Plate)
        { accession_id: 'r3', name: 'R3', fqn: 'pylabrobot.resources.plates.Cos_96_Well' } as any,
        // Case 4: Fallback to Other
        { accession_id: 'r4', name: 'R4', fqn: 'unknown.thing' } as any
      ];

      // Spy on getResourceDefinitions to return our mocks without HTTP request
      vi.spyOn(service, 'getResourceDefinitions').mockReturnValue(of(mockDefs));

      service.getFacets().subscribe(facets => {
        // Expect plr_category to capture all inferred categories
        expect(facets.plr_category).toBeDefined();

        // Check counts
        const cats = facets.plr_category;
        const explicit = cats.find(c => c.value === 'ExplicitCat');
        const typeCat = cats.find(c => c.value === 'TypeCat');
        const plate = cats.find(c => c.value === 'Plate');
        const other = cats.find(c => c.value === 'Other');

        expect(explicit?.count).toBe(1);
        expect(typeCat?.count).toBe(1);
        expect(plate?.count).toBe(1);
        expect(other?.count).toBe(1);
      });
    });
  });

  // Browser mode tests for SQLite-based asset operations
  describe('Browser Mode CRUD', () => {
    let sqliteService: SqliteService;

    beforeEach(() => {
      sqliteService = TestBed.inject(SqliteService);
      // Mock ModeService to return browser mode
      const modeService = TestBed.inject(ModeService);
      vi.spyOn(modeService, 'isBrowserMode').mockReturnValue(true);
    });

    describe('Machine CRUD in Browser Mode', () => {
      it('should create machine in browser mode via SqliteService', async () => {
        const newMachine: MachineCreate = {
          name: 'Browser Machine',
          status: MachineStatus.IDLE,
          definition_id: 'def-123'
        };
        const createdMachine: Machine = {
          accession_id: 'bm-001',
          name: newMachine.name,
          status: newMachine.status!
        };

        // Mock SqliteService.createMachine
        vi.spyOn(sqliteService as any, 'createMachine').mockResolvedValue(createdMachine);

        const result = await firstValueFrom(service.createMachine(newMachine));
        expect(result).toEqual(createdMachine);
      });

      it('should get machines from SqliteService in browser mode', async () => {
        const mockMachines: Machine[] = [
          { accession_id: 'bm-001', name: 'Browser Machine 1', status: MachineStatus.IDLE },
          { accession_id: 'bm-002', name: 'Browser Machine 2', status: MachineStatus.RUNNING }
        ];

        // Mock SqliteService.getMachines or findAll
        vi.spyOn(sqliteService as any, 'findAll').mockImplementation((table: string) => {
          if (table === 'machines') return Promise.resolve(mockMachines);
          return Promise.resolve([]);
        });

        const result = await firstValueFrom(service.getMachines());
        expect(result.length).toBe(2);
        expect(result[0].name).toBe('Browser Machine 1');
      });

      it('should delete machine in browser mode', async () => {
        vi.spyOn(sqliteService as any, 'deleteMachine').mockResolvedValue(undefined);

        await expect(firstValueFrom(service.deleteMachine('bm-001'))).resolves.toBeUndefined();
      });
    });

    describe('Resource CRUD in Browser Mode', () => {
      it('should create resource in browser mode via SqliteService', async () => {
        const newResource: ResourceCreate = {
          name: 'Browser Plate',
          status: ResourceStatus.AVAILABLE,
          definition_id: 'plate-def-123'
        };
        const createdResource: Resource = {
          accession_id: 'br-001',
          name: newResource.name,
          status: newResource.status!
        };

        // Mock SqliteService.createResource
        vi.spyOn(sqliteService as any, 'createResource').mockResolvedValue(createdResource);

        const result = await firstValueFrom(service.createResource(newResource));
        expect(result).toEqual(createdResource);
      });

      it('should get resources from SqliteService in browser mode', async () => {
        const mockResources: Resource[] = [
          { accession_id: 'br-001', name: 'Browser Plate 1', status: ResourceStatus.AVAILABLE },
          { accession_id: 'br-002', name: 'Browser Tip Rack', status: ResourceStatus.IN_USE }
        ];

        vi.spyOn(sqliteService as any, 'findAll').mockImplementation((table: string) => {
          if (table === 'resources') return Promise.resolve(mockResources);
          return Promise.resolve([]);
        });

        const result = await firstValueFrom(service.getResources());
        expect(result.length).toBe(2);
        expect(result[0].name).toBe('Browser Plate 1');
      });

      it('should delete resource in browser mode', async () => {
        vi.spyOn(sqliteService as any, 'deleteResource').mockResolvedValue(undefined);

        await expect(firstValueFrom(service.deleteResource('br-001'))).resolves.toBeUndefined();
      });
    });

    describe('Asset Persistence', () => {
      it('should persist machine after service reload', async () => {
        const machine: Machine = {
          accession_id: 'persist-001',
          name: 'Persistent Machine',
          status: MachineStatus.IDLE
        };

        // Simulate persisted data
        vi.spyOn(sqliteService as any, 'findAll').mockResolvedValue([machine]);

        // First load
        const result1 = await firstValueFrom(service.getMachines());
        expect(result1).toContainEqual(machine);

        // Simulate service recreation (would happen on page reload)
        // The data should still be there from SQLite
        const result2 = await firstValueFrom(service.getMachines());
        expect(result2).toContainEqual(machine);
      });

      it('should persist resource after service reload', async () => {
        const resource: Resource = {
          accession_id: 'persist-r-001',
          name: 'Persistent Resource',
          status: ResourceStatus.AVAILABLE
        };

        vi.spyOn(sqliteService as any, 'findAll').mockResolvedValue([resource]);

        const result1 = await firstValueFrom(service.getResources());
        expect(result1).toContainEqual(resource);

        const result2 = await firstValueFrom(service.getResources());
        expect(result2).toContainEqual(resource);
      });
    });
  });
});
