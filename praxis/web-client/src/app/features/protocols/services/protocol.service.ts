
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ProtocolDefinition } from '../models/protocol.models';

@Injectable({
  providedIn: 'root'
})
export class ProtocolService {
  private http = inject(HttpClient);
  private readonly API_URL = '/api/v1';

  getProtocols(): Observable<ProtocolDefinition[]> {
    return this.http.get<ProtocolDefinition[]>(`${this.API_URL}/protocols/definitions`);
  }

  // If uploading a file
  uploadProtocol(file: File): Observable<ProtocolDefinition> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<ProtocolDefinition>(`${this.API_URL}/protocols/upload`, formData);
  }
}
