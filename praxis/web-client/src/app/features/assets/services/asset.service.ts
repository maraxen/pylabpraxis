
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, from, of, firstValueFrom } from 'rxjs';
import { map } from 'rxjs/operators';
import { Machine, MachineCreate, Resource, ResourceCreate, MachineDefinition, ResourceDefinition, ActiveFilters } from '../models/asset.models';
import { ModeService } from '../../../core/services/mode.service';
import { SqliteService } from '../../../core/services/sqlite.service';
import { ResourceDefinitionCatalog } from '../../../core/db/schema';

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
    return this.http.get<Machine[]>(`${this.API_URL}/machines`);
  }

  createMachine(machine: MachineCreate): Observable<Machine> {
    return this.http.post<Machine>(`${this.API_URL}/machines`, machine);
  }

  deleteMachine(accessionId: string): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/machines/${accessionId}`);
  }

  updateMachine(accessionId: string, machine: Partial<MachineCreate>): Observable<Machine> {
    return this.http.patch<Machine>(`${this.API_URL}/machines/${accessionId}`, machine);
  }

  // --- Resources ---
  getResources(): Observable<Resource[]> {
    return this.http.get<Resource[]>(`${this.API_URL}/resources`);
  }

  createResource(resource: ResourceCreate): Observable<Resource> {
    return this.http.post<Resource>(`${this.API_URL}/resources`, resource);
  }

  deleteResource(accessionId: string): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/resources/${accessionId}`);
  }

  // --- Definitions (Discovery) ---
  getMachineDefinitions(): Observable<MachineDefinition[]> {
    return this.http.get<MachineDefinition[]>(`${this.API_URL}/machines/definitions?type=machine`);
  }

  getResourceDefinitions(): Observable<ResourceDefinition[]> {
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
        let params: any = { type: 'resource' };
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
