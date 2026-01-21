
import { Injectable, inject } from '@angular/core';
import { Observable, firstValueFrom } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import {
  Machine, MachineCreate, Resource, ResourceCreate,
  MachineDefinition, MachineFrontendDefinition, MachineBackendDefinition,
  ResourceDefinition, ActiveFilters,
  MachineStatus, ResourceStatus, Workcell
} from '../models/asset.models';
import { ModeService } from '../../../core/services/mode.service';
import { SqliteService } from '../../../core/services/sqlite.service';
import { ResourceDefinitionCatalog } from '../../../core/db/schema';
import { inferCategory } from '../utils/category-inference';

// API Generated imports
import { MachinesService } from '../../../core/api-generated/services/MachinesService';
import { MachineFrontendsService } from '../../../core/api-generated/services/MachineFrontendsService';
import { MachineBackendsService } from '../../../core/api-generated/services/MachineBackendsService';
import { ResourcesService } from '../../../core/api-generated/services/ResourcesService';
import { AssetsService } from '../../../core/api-generated/services/AssetsService';
import { DiscoveryService } from '../../../core/api-generated/services/DiscoveryService';
import { ApiWrapperService } from '../../../core/services/api-wrapper.service';
import { MachineCreate as ApiMachineCreate } from '../../../core/api-generated/models/MachineCreate';
import { MachineUpdate as ApiMachineUpdate } from '../../../core/api-generated/models/MachineUpdate';
import { ResourceCreate as ApiResourceCreate } from '../../../core/api-generated/models/ResourceCreate';
import { WorkcellsService } from '../../../core/api-generated/services/WorkcellsService';

// Facet item with value and count
export interface FacetItem {
  value: string | number;
  count: number;
}

// All facets returned by the API
export interface ResourceFacets {
  plr_category: FacetItem[];
  vendor: FacetItem[];
  num_items: FacetItem[];
  plate_type: FacetItem[];
  well_volume_ul: FacetItem[];
  tip_volume_ul: FacetItem[];
}

// Machine facets
export interface MachineFacets {
  machine_category: FacetItem[];
  manufacturer: FacetItem[];
}

@Injectable({
  providedIn: 'root'
})
export class AssetService {
  private modeService = inject(ModeService);
  private sqliteService = inject(SqliteService);
  private apiWrapper = inject(ApiWrapperService);
  private readonly API_URL = '/api/v1';

  // --- Machines ---
  getMachines(): Observable<Machine[]> {
    if (this.modeService.isBrowserMode()) {
      console.debug('[ASSET-DEBUG] getMachines: Browser mode, querying SqliteService.machines');
      return this.sqliteService.machines.pipe(
        map(repo => {
          const results = repo.findAll();
          console.debug('[ASSET-DEBUG] getMachines: Found', results.length, 'machines in DB', results);
          return results.map(m => ({
            ...m,
            status: m.status || 'OFFLINE',
            machine_type: m.machine_category,
            name: (m as Record<string, unknown>)['name'] as string || 'Unknown',
            fqn: (m as Record<string, unknown>)['fqn'] as string || ''
          }) as unknown as Machine);
        })
      );
    }
    return this.apiWrapper.wrap(MachinesService.getMultiApiV1MachinesGet()).pipe(
      map(machines => machines.map(m => m as unknown as Machine))
    );
  }

  createMachine(machine: MachineCreate): Observable<Machine> {
    console.debug('[ASSET-DEBUG] createMachine called with:', machine);
    if (this.modeService.isBrowserMode()) {
      console.debug('[ASSET-DEBUG] createMachine: Browser mode, creating via SqliteService');
      return this.sqliteService.machines.pipe(
        switchMap(async repo => {
          const defaults = {
            status: MachineStatus.IDLE,
            location: 'Unknown',
            maintenance_enabled: false,
            maintenance_schedule_json: { intervals: [], enabled: false },
            is_simulated: false,
            serial_number: 'N/A',
            firmware_version: '0.0.0'
          };

          const newMachine: Machine = {
            ...defaults,
            ...machine,
            accession_id: crypto.randomUUID(),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            asset_type: 'MACHINE',
            // Simple FQN generation
            fqn: `machines.${machine.name.replace(/\s+/g, '_').toLowerCase()}`,
            machine_category: machine.machine_category || machine.machine_type || 'unknown'
          };
          console.debug('[ASSET-DEBUG] createMachine: Calling repo.create with:', newMachine);
          repo.create(newMachine as any);
          await this.sqliteService.save();
          console.debug('[ASSET-DEBUG] createMachine: Machine created and saved to store');
          return newMachine;
        })
      );
    }
    // Note: The generated create method now has a requestBody parameter
    return this.apiWrapper.wrap(MachinesService.createApiV1MachinesPost(machine as unknown as ApiMachineCreate)).pipe(
      map(m => m as unknown as Machine)
    );
  }

  deleteMachine(accessionId: string): Observable<void> {
    if (this.modeService.isBrowserMode()) {
      return this.sqliteService.machines.pipe(
        map(repo => {
          repo.delete(accessionId);
        })
      );
    }
    return this.apiWrapper.wrap(MachinesService.deleteApiV1MachinesAccessionIdDelete(accessionId));
  }

  updateMachine(accessionId: string, machine: Partial<MachineCreate>): Observable<Machine> {
    if (this.modeService.isBrowserMode()) {
      // Browser update logic omitted for brevity in this POC, but it was not implemented before either
      throw new Error('Update machine not implemented for browser mode');
    }
    return this.apiWrapper.wrap(MachinesService.updateApiV1MachinesAccessionIdPut(accessionId, machine as ApiMachineUpdate)).pipe(
      map(m => m as unknown as Machine)
    );
  }

  // --- Resources ---
  getResources(): Observable<Resource[]> {
    if (this.modeService.isBrowserMode()) {
      console.debug('[ASSET-DEBUG] getResources: Browser mode, querying SqliteService.resources');
      return this.sqliteService.resources.pipe(
        map(repo => {
          const results = repo.findAll();
          console.debug('[ASSET-DEBUG] getResources: Found', results.length, 'resources in DB', results);
          return results.map(r => ({
            ...r,
            status: r.status || 'available',
            name: (r as Record<string, unknown>)['name'] as string || 'Unknown',
            fqn: (r as Record<string, unknown>)['fqn'] as string || ''
          }) as unknown as Resource);
        })
      );
    }
    return this.apiWrapper.wrap(ResourcesService.getMultiApiV1ResourcesGet()).pipe(
      map(resources => resources.map(r => r as unknown as Resource))
    );
  }

  createResource(resource: ResourceCreate): Observable<Resource> {
    console.debug('[ASSET-DEBUG] createResource called with:', resource);
    if (this.modeService.isBrowserMode()) {
      console.debug('[ASSET-DEBUG] createResource: Browser mode, creating via SqliteService');
      return this.sqliteService.resources.pipe(
        switchMap(async repo => {
          const newResource: Resource = {
            ...resource,
            accession_id: crypto.randomUUID(),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            status: ResourceStatus.AVAILABLE,
            asset_type: 'RESOURCE',
            // Simple FQN generation
            fqn: `resources.${resource.name.replace(/\s+/g, '_').toLowerCase()}`,
          };
          console.debug('[ASSET-DEBUG] createResource: Calling repo.create with:', newResource);
          repo.create(newResource as any);
          await this.sqliteService.save();
          console.debug('[ASSET-DEBUG] createResource: Resource created and saved to store');
          return newResource;
        })
      );
    }
    return this.apiWrapper.wrap(ResourcesService.createApiV1ResourcesPost(resource as unknown as ApiResourceCreate)).pipe(
      map(r => r as unknown as Resource)
    );
  }

  deleteResource(accessionId: string): Observable<void> {
    if (this.modeService.isBrowserMode()) {
      return this.sqliteService.resources.pipe(
        map(repo => {
          repo.delete(accessionId);
        })
      );
    }
    return this.apiWrapper.wrap(ResourcesService.deleteApiV1ResourcesAccessionIdDelete(accessionId));
  }

  // --- Workcells ---
  getWorkcells(): Observable<Workcell[]> {
    if (this.modeService.isBrowserMode()) {
      return this.sqliteService.workcells.pipe(
        map(repo => {
          const results = repo.findAll();
          return results.map(w => ({
            ...w,
            status: w.status || 'unknown'
          }) as unknown as Workcell);
        })
      );
    }
    return this.apiWrapper.wrap(WorkcellsService.getMultiApiV1WorkcellGet()).pipe(
      map(workcells => workcells.map(w => w as unknown as Workcell))
    );
  }

  // --- Definitions (Discovery) ---
  getMachineDefinitions(): Observable<MachineDefinition[]> {
    if (this.modeService.isBrowserMode()) {
      return this.sqliteService.machineDefinitions.pipe(
        map(repo => {
          const defs = repo.findAll();
          console.debug('[ASSET-DEBUG] getMachineDefinitions: Found', defs.length, 'definitions in DB');
          return defs.map(d => ({
            ...d,
            name: (d as Record<string, unknown>)['name'] as string || 'Unknown Definition',
            compatible_backends: (typeof d.compatible_backends === 'string'
              ? (() => { try { return JSON.parse(d.compatible_backends); } catch { return []; } })()
              : (Array.isArray(d.compatible_backends) ? d.compatible_backends : []))
          }) as unknown as MachineDefinition);
        })
      );
    }
    return this.apiWrapper.wrap(MachinesService.getMultiApiV1MachinesDefinitionsGet(100)).pipe(
      map(defs => defs.map(d => d as unknown as MachineDefinition))
    );
  }

  getMachineFrontendDefinitions(): Observable<MachineFrontendDefinition[]> {
    if (this.modeService.isBrowserMode()) {
      return this.sqliteService.machineFrontendDefinitions.pipe(
        map(repo => {
          const defs = repo.findAll();
          return defs.map(d => ({
            ...d,
            name: (d as any).name || 'Unknown Frontend'
          }) as unknown as MachineFrontendDefinition);
        })
      );
    }
    return this.apiWrapper.wrap(MachineFrontendsService.listFrontendDefinitionsApiV1MachineFrontendsGet(0, 100)).pipe(
      map(defs => defs.map(d => d as unknown as MachineFrontendDefinition))
    );
  }

  getMachineBackendDefinitions(): Observable<MachineBackendDefinition[]> {
    if (this.modeService.isBrowserMode()) {
      return this.sqliteService.machineBackendDefinitions.pipe(
        map(repo => {
          const defs = repo.findAll();
          return defs.map(d => ({
            ...d,
            name: (d as any).name || 'Unknown Backend'
          }) as unknown as MachineBackendDefinition);
        })
      );
    }
    return this.apiWrapper.wrap(MachineBackendsService.listBackendDefinitionsApiV1MachineBackendsGet(0, 100)).pipe(
      map(defs => defs.map(d => d as unknown as MachineBackendDefinition))
    );
  }

  searchMachineDefinitions(query: string): Observable<MachineDefinition[]> {
    return this.getMachineDefinitions().pipe(
      map(defs => defs.filter(d =>
        d.name.toLowerCase().includes(query.toLowerCase()) ||
        d.description?.toLowerCase().includes(query.toLowerCase()) ||
        d.manufacturer?.toLowerCase().includes(query.toLowerCase())
      ))
    );
  }

  getBackendsForFrontend(frontendAccessionId: string): Observable<MachineBackendDefinition[]> {
    if (this.modeService.isBrowserMode()) {
      return this.sqliteService.machineBackendDefinitions.pipe(
        map(repo => {
          const defs = repo.findByFrontend(frontendAccessionId);
          return defs.map(d => ({
            ...d,
            name: (d as any).name || 'Unknown Backend'
          }) as unknown as MachineBackendDefinition);
        })
      );
    }
    return this.apiWrapper.wrap(MachineFrontendsService.getCompatibleBackendsApiV1MachineFrontendsAccessionIdBackendsGet(frontendAccessionId)).pipe(
      map(defs => defs.map(d => d as unknown as MachineBackendDefinition))
    );
  }

  getResourceDefinitions(plrCategory?: string): Observable<ResourceDefinition[]> {
    if (this.modeService.isBrowserMode()) {
      return this.sqliteService.resourceDefinitions.pipe(
        map(repo => {
          let defs = repo.findAll();
          if (plrCategory) {
            defs = defs.filter(d => d.plr_category === plrCategory);
          }
          return defs.map(d => ({
            ...d,
            name: (d as Record<string, unknown>)['name'] as string || 'Unknown Definition'
          }) as unknown as ResourceDefinition);
        })
      );
    }
    // Note: We use the search_filters object to pass the plr_category if the generated client doesn't have it as a top-level param yet.
    // However, since we added it to SearchFilters in the backend, it might be available as a query param eventually.
    // For now, let's try to pass it if the generated service allows it or via search_filters.
    return this.apiWrapper.wrap(AssetsService.getMultiApiV1ResourcesDefinitionsGet(
      100,
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      plrCategory ? { search_filters: { plr_category: plrCategory } } : undefined
    )).pipe(
      map(defs => defs.map(d => d as unknown as ResourceDefinition))
    );
  }

  searchResourceDefinitions(query: string, plrCategory?: string): Observable<ResourceDefinition[]> {
    return this.getResourceDefinitions(plrCategory).pipe(
      map(defs => defs.filter(d =>
        d.name.toLowerCase().includes(query.toLowerCase()) ||
        d.description?.toLowerCase().includes(query.toLowerCase()) ||
        d.vendor?.toLowerCase().includes(query.toLowerCase())
      ))
    );
  }

  /**
   * Universal lookup for a single resource definition.
   * Handles both API (Production) and SQLite (Browser) modes.
   */
  async getResourceDefinition(fqn?: string, partialName?: string): Promise<ResourceDefinition | null> {
    if (this.modeService.isBrowserMode()) {
      // Browser Mode: Use SqliteService
      try {
        const repo = await firstValueFrom(this.sqliteService.resourceDefinitions);
        let def: ResourceDefinitionCatalog | null = null;

        if (fqn) {
          def = repo.findOneBy({ fqn } as Partial<ResourceDefinitionCatalog>);
        }

        if (!def && partialName) {
          const all = repo.findBy({} as Partial<ResourceDefinitionCatalog>);
          def = all.find(d =>
            d.name?.toLowerCase().includes(partialName.toLowerCase()) ||
            d.plr_category?.toLowerCase().includes(partialName.toLowerCase())
          ) || null;
        }

        if (def) {
          return {
            ...def,
            is_consumable: def.is_consumable ?? false,
          } as ResourceDefinition;
        }
        return null;
      } catch (err) {
        console.warn('Sqlite lookup failed', err);
        return null;
      }
    } else {
      // Production Mode: Use API
      try {
        // Optimized lookup using generated client
        const allDefs = await firstValueFrom(this.getResourceDefinitions());

        if (fqn) {
          const match = allDefs.find(d => d.fqn === fqn);
          if (match) return match;
        }

        if (partialName) {
          const match = allDefs.find(d =>
            d.name.toLowerCase().includes(partialName.toLowerCase()) ||
            d.plr_category?.toLowerCase().includes(partialName.toLowerCase())
          );
          if (match) return match;
        }

        return null;
      } catch (err) {
        console.warn('API lookup failed', err);
        return null;
      }
    }
  }

  // --- Facets for dynamic filtering ---
  getFacets(filters: Partial<ActiveFilters> = {}): Observable<ResourceFacets> {
    // Browser mode: compute facets from resource definitions client-side
    if (this.modeService.isBrowserMode()) {
      return this.getResourceDefinitions().pipe(
        map(definitions => {
          // Apply filters first
          let filtered = definitions;
          // Pre-calculate categories for filtering
          const defsWithCat = filtered.map(d => ({ ...d, _inferredCategory: inferCategory(d) }));

          if (filters.plr_category?.length) {
            filtered = defsWithCat.filter(d => filters.plr_category!.includes(d._inferredCategory));
          }
          if (filters.vendor?.length) {
            filtered = filtered.filter(d => filters.vendor!.includes(d.vendor || ''));
          }
          if (filters.num_items?.length) {
            filtered = filtered.filter(d => filters.num_items!.includes(d.num_items as number));
          }
          if (filters.plate_type?.length) {
            filtered = filtered.filter(d => filters.plate_type!.includes(d.plate_type || ''));
          }

          // Compute facets from filtered definitions
          const countBy = <T extends string | number | undefined>(items: T[]): FacetItem[] => {
            const counts = new Map<string | number, number>();
            items.forEach(item => {
              if (item !== undefined && item !== null && item !== '') {
                const count = counts.get(item) || 0;
                counts.set(item, count + 1);
              }
            });
            return Array.from(counts.entries())
              .map(([value, count]) => ({ value, count }))
              .sort((a, b) => b.count - a.count);
          };

          // Use ALL definitions for plr_category (base facet), filtered for others
          return {
            plr_category: countBy(definitions.map(d => inferCategory(d))),
            vendor: countBy(filtered.map(d => d.vendor)),
            num_items: countBy(filtered.map(d => d.num_items)),
            plate_type: countBy(filtered.map(d => d.plate_type)),
            well_volume_ul: countBy(filtered.map(d => d.well_volume_ul)),
            tip_volume_ul: countBy(filtered.map(d => d.tip_volume_ul)),
          };
        })
      );
    }

    // Backend mode: use HTTP API
    // Mapping filters to generated method arguments
    return this.apiWrapper.wrap(AssetsService.getResourceDefinitionFacetsApiV1ResourcesDefinitionsFacetsGet(
      filters.plr_category?.[0] as string,
      filters.vendor?.[0] as string,
      filters.num_items?.[0] as unknown as number,
      filters.plate_type?.[0] as string
    )).pipe(
      map(facets => facets as unknown as ResourceFacets)
    );
  }

  getMachineFacets(): Observable<MachineFacets> {
    if (this.modeService.isBrowserMode()) {
      return this.getMachineDefinitions().pipe(
        map(definitions => {
          const countBy = <T extends string | number | undefined>(items: T[]): FacetItem[] => {
            const counts = new Map<string | number, number>();
            items.forEach(item => {
              if (item !== undefined && item !== null && item !== '') {
                const count = counts.get(item) || 0;
                counts.set(item, count + 1);
              }
            });
            return Array.from(counts.entries())
              .map(([value, count]) => ({ value, count }))
              .sort((a, b) => b.count - a.count);
          };

          return {
            machine_category: countBy(definitions.map(d => d.machine_category)),
            manufacturer: countBy(definitions.map(d => d.manufacturer))
          };
        })
      );
    }
    return this.apiWrapper.wrap(MachinesService.getMachineDefinitionFacetsApiV1MachinesDefinitionsFacetsGet()).pipe(
      map(facets => facets as unknown as MachineFacets)
    );
  }

  syncDefinitions(): Observable<{ message: string }> {
    return this.apiWrapper.wrap(DiscoveryService.syncAllDefinitionsApiV1DiscoverySyncAllPost()).pipe(
      map(result => result as { message: string })
    );
  }
}
