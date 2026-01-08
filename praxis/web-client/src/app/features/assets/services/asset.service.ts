
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, from, of, firstValueFrom } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { Machine, MachineCreate, Resource, ResourceCreate, MachineDefinition, ResourceDefinition, ActiveFilters } from '../models/asset.models';
import { ModeService } from '../../../core/services/mode.service';
import { SqliteService } from '../../../core/services/sqlite.service';
import { ResourceDefinitionCatalog } from '../../../core/db/schema';
import { inferCategory } from '../utils/category-inference';

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
  private http = inject(HttpClient);
  private modeService = inject(ModeService);
  private sqliteService = inject(SqliteService);
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
            name: (m as any).name || 'Unknown',
            fqn: (m as any).fqn || ''
          }) as unknown as Machine);
        })
      );
    }
    return this.http.get<Machine[]>(`${this.API_URL}/machines`);
  }

  createMachine(machine: MachineCreate): Observable<Machine> {
    console.debug('[ASSET-DEBUG] createMachine called with:', machine);
    if (this.modeService.isBrowserMode()) {
      console.debug('[ASSET-DEBUG] createMachine: Browser mode, creating via SqliteService');
      return this.sqliteService.machines.pipe(
        switchMap(async repo => {
          const newMachine: Machine = {
            ...machine,
            accession_id: crypto.randomUUID(),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            status: 'AVAILABLE' as any,
            asset_type: 'MACHINE',
            // Simple FQN generation
            fqn: `machines.${machine.name.replace(/\s+/g, '_').toLowerCase()}`,
          };
          console.debug('[ASSET-DEBUG] createMachine: Calling repo.create with:', newMachine);
          repo.create(newMachine as any);
          await this.sqliteService.save();
          console.debug('[ASSET-DEBUG] createMachine: Machine created and saved to store');
          return newMachine;
        })
      );
    }
    return this.http.post<Machine>(`${this.API_URL}/machines`, machine);
  }

  deleteMachine(accessionId: string): Observable<void> {
    if (this.modeService.isBrowserMode()) {
      return this.sqliteService.machines.pipe(
        map(repo => {
          repo.delete(accessionId);
        })
      );
    }
    return this.http.delete<void>(`${this.API_URL}/machines/${accessionId}`);
  }

  updateMachine(accessionId: string, machine: Partial<MachineCreate>): Observable<Machine> {
    return this.http.patch<Machine>(`${this.API_URL}/machines/${accessionId}`, machine);
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
            name: (r as any).name || 'Unknown',
            fqn: (r as any).fqn || ''
          }) as unknown as Resource);
        })
      );
    }
    return this.http.get<Resource[]>(`${this.API_URL}/resources`);
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
            status: 'available' as any,
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
    return this.http.post<Resource>(`${this.API_URL}/resources`, resource);
  }

  deleteResource(accessionId: string): Observable<void> {
    if (this.modeService.isBrowserMode()) {
      return this.sqliteService.resources.pipe(
        map(repo => {
          repo.delete(accessionId);
        })
      );
    }
    return this.http.delete<void>(`${this.API_URL}/resources/${accessionId}`);
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
            name: (d as any).name || 'Unknown Definition',
            compatible_backends: (typeof d.compatible_backends === 'string'
              ? (() => { try { return JSON.parse(d.compatible_backends); } catch { return []; } })()
              : (Array.isArray(d.compatible_backends) ? d.compatible_backends : []))
          }) as unknown as MachineDefinition);
        })
      );
    }
    return this.http.get<MachineDefinition[]>(`${this.API_URL}/machines/definitions?type=machine`);
  }

  getResourceDefinitions(): Observable<ResourceDefinition[]> {
    if (this.modeService.isBrowserMode()) {
      return this.sqliteService.resourceDefinitions.pipe(
        map(repo => repo.findAll().map(d => ({
          ...d,
          name: (d as any).name || 'Unknown Definition'
        }) as unknown as ResourceDefinition))
      );
    }
    return this.http.get<ResourceDefinition[]>(`${this.API_URL}/resources/definitions?type=resource`);
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
        const params: any = { type: 'resource' };
        if (fqn) params.fqn = fqn;

        // Optimize: If FQN is known, we might be able to filter by it via API if supported
        // But currently standard CRUD might not support exact match filtering on FQN without custom implementation
        // So we might fetch list and filter in memory if FQN is not supported. 
        // However, fetching All definitions is heavy.
        // Let's assume we can fetch all for now as a safe fallback or that standard filtering works.
        const allDefs = await firstValueFrom(this.http.get<ResourceDefinition[]>(`${this.API_URL}/resources/definitions`, { params }));

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
            filtered = filtered.filter(d => filters.num_items!.includes(d.num_items as any));
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
    let params = {};
    // Map active filters to query params
    // Only send the first value for now as backend query logic handles single values well for faceting
    if (filters.plr_category?.length) params = { ...params, plr_category: filters.plr_category[0] };
    if (filters.vendor?.length) params = { ...params, vendor: filters.vendor[0] };
    if (filters.num_items?.length) params = { ...params, num_items: filters.num_items[0] };
    if (filters.plate_type?.length) params = { ...params, plate_type: filters.plate_type[0] };

    return this.http.get<ResourceFacets>(`${this.API_URL}/resources/definitions/facets`, { params });
  }

  getMachineFacets(): Observable<MachineFacets> {
    return this.http.get<MachineFacets>(`${this.API_URL}/machines/definitions/facets`);
  }

  syncDefinitions(): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.API_URL}/discovery/sync-all`, {});
  }
}
