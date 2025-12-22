
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Machine, MachineCreate, Resource, ResourceCreate, MachineDefinition, ResourceDefinition } from '../models/asset.models';

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
      return this.http.get<MachineDefinition[]>(`${this.API_URL}/assets/definitions?type=machine`);
  }

  getResourceDefinitions(): Observable<ResourceDefinition[]> {
      return this.http.get<ResourceDefinition[]>(`${this.API_URL}/assets/definitions?type=resource`);
  }
}
