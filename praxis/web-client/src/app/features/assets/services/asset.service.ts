
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Machine, MachineCreate, Resource, ResourceCreate, MachineDefinition, ResourceDefinition, ActiveFilters } from '../models/asset.models';

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
}
