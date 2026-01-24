import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { AssetService } from './asset.service';
import { SqliteService } from '@core/services/sqlite';
import { Machine, MachineCreate, Resource, ResourceCreate, MachineStatus, ResourceStatus, MachineDefinition, ResourceDefinition } from '../models/asset.models';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { ModeService } from '@core/services/mode.service';
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

  describe('Browser Mode CRUD', () => {
    let sqliteService: SqliteService;

    // Mock Repositories
    const mockMachineRepo = {
      findAll: vi.fn(),
      create: vi.fn(),
      delete: vi.fn(),
      findOneBy: vi.fn(),
      findBy: vi.fn()
    };

    const mockResourceRepo = {
      findAll: vi.fn(),
      create: vi.fn(),
      delete: vi.fn(),
      findOneBy: vi.fn(),
      findBy: vi.fn()
    };

    const mockResourceDefRepo = {
      findAll: vi.fn(), // Return array directly
      findOneBy: vi.fn(),
      findBy: vi.fn()
    }

    beforeEach(() => {
      sqliteService = TestBed.inject(SqliteService);
      // Mock ModeService to return browser mode
      const modeService = TestBed.inject(ModeService);
      vi.spyOn(modeService, 'isBrowserMode').mockReturnValue(true);

      // Mock the Observables on SqliteService
      // We use 'as any' to overwrite readonly properties for testing
      (sqliteService as any).machines = of(mockMachineRepo);
      (sqliteService as any).resources = of(mockResourceRepo);
      (sqliteService as any).resourceDefinitions = of(mockResourceDefRepo);

      // Reset spies
      vi.clearAllMocks();
    });

    describe('Machine CRUD in Browser Mode', () => {
      it('should create machine in browser mode via SqliteService', async () => {
        const newMachine: MachineCreate = {
          name: 'Browser Machine',
          status: MachineStatus.IDLE,
          machine_definition_accession_id: 'def-123'
        };

        // repo.create returns void/Promise<void> usually, checking implementation... 
        // asset.service.ts just calls repo.create(newMachine), doesn't await return
        mockMachineRepo.create.mockReturnValue(undefined);

        const result = await firstValueFrom(service.createMachine(newMachine));

        expect(result.name).toBe(newMachine.name);
        expect(result.status).toBe('idle'); // Service overrides status on create
        expect(result.asset_type).toBe('MACHINE');
        expect(result.maintenance_enabled).toBe(false);
        expect(result.maintenance_schedule_json).toEqual({ intervals: [], enabled: false });
        expect(mockMachineRepo.create).toHaveBeenCalled();
      });

      it('should get machines from SqliteService in browser mode', async () => {
        const mockMachines = [
          { accession_id: 'bm-001', name: 'Browser Machine 1', status: 'IDLE', machine_category: 'opentrons', fqn: 'mac.1' },
          { accession_id: 'bm-002', name: 'Browser Machine 2', status: 'RUNNING', machine_category: 'hamilton', fqn: 'mac.2' }
        ];

        mockMachineRepo.findAll.mockReturnValue(mockMachines);

        const result = await firstValueFrom(service.getMachines());
        expect(result.length).toBe(2);
        expect(result[0].name).toBe('Browser Machine 1');
        expect(mockMachineRepo.findAll).toHaveBeenCalled();
      });

      it('should delete machine in browser mode', async () => {
        mockMachineRepo.delete.mockReturnValue(undefined);

        await expect(firstValueFrom(service.deleteMachine('bm-001'))).resolves.toBeUndefined();
        expect(mockMachineRepo.delete).toHaveBeenCalledWith('bm-001');
      });
    });

    describe('Resource CRUD in Browser Mode', () => {
      it('should create resource in browser mode via SqliteService', async () => {
        const newResource: ResourceCreate = {
          name: 'Browser Plate',
          status: ResourceStatus.AVAILABLE,
          resource_definition_accession_id: 'plate-def-123'
        };

        mockResourceRepo.create.mockReturnValue(undefined);

        const result = await firstValueFrom(service.createResource(newResource));

        expect(result.name).toBe(newResource.name);
        expect(result.status).toBe('available');
        expect(result.asset_type).toBe('RESOURCE');
        expect(mockResourceRepo.create).toHaveBeenCalled();
      });

      it('should get resources from SqliteService in browser mode', async () => {
        const mockResources = [
          { accession_id: 'br-001', name: 'Browser Plate 1', status: 'available' },
          { accession_id: 'br-002', name: 'Browser Tip Rack', status: 'in_use' }
        ];

        mockResourceRepo.findAll.mockReturnValue(mockResources);

        const result = await firstValueFrom(service.getResources());
        expect(result.length).toBe(2);
        expect(result[0].name).toBe('Browser Plate 1');
        // Check inferred category or other props if needed
      });

      it('should delete resource in browser mode', async () => {
        mockResourceRepo.delete.mockReturnValue(undefined);

        await expect(firstValueFrom(service.deleteResource('br-001'))).resolves.toBeUndefined();
        expect(mockResourceRepo.delete).toHaveBeenCalledWith('br-001');
      });
    });

    describe('Asset Persistence', () => {
      it('should persist machine after service reload', async () => {
        // In this unit test with mocks, we verify that the SERVICE attempts to fetch from the REPO
        // 'Persistence' in the unit test context essentially means 'calls the repo'
        const machine = {
          accession_id: 'persist-001',
          name: 'Persistent Machine',
          status: 'IDLE',
          machine_category: 'test'
        };

        mockMachineRepo.findAll.mockReturnValue([machine]);

        // First load
        const result1 = await firstValueFrom(service.getMachines());
        expect(result1[0].accession_id).toBe('persist-001');

        // Second load
        const result2 = await firstValueFrom(service.getMachines());
        expect(result2[0].accession_id).toBe('persist-001');

        expect(mockMachineRepo.findAll).toHaveBeenCalledTimes(2);
      });
    });
  });
});
