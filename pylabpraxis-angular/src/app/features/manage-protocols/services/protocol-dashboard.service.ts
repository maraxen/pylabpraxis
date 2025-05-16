// src/app/features/manage-protocols/services/protocol-dashboard.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { environment } from '@env'; // Using path alias
import { ProtocolInfo, ProtocolStatusResponse } from '@protocols/protocol.models'; // Using path alias
import { RunNewProtocolService } from './run-new-protocol.service';

@Injectable({
  providedIn: 'root',
})
export class ProtocolDashboardService {
  private http = inject(HttpClient);
  private runNewProtocolService = inject(RunNewProtocolService);

  // Construct the base URL for this specific service, including versioning
  private baseServiceUrl = `${environment.apiUrl}/v1/protocols`; // e.g., http://localhost:8000/api/v1/protocols

  constructor() {
    console.log('ProtocolDashboardService initialized. API URL:', this.baseServiceUrl);
  }

  discoverProtocols(): Observable<ProtocolInfo[]> {
    return this.runNewProtocolService.discoverProtocols();
  }

  getProtocolStatus(protocolName: string): Observable<ProtocolStatusResponse> {
    return this.runNewProtocolService.getProtocolStatus(protocolName);
  }

  listManagedProtocols(): Observable<string[]> {
    // This endpoint in the backend is directly under /protocols/, not /protocols/managed or similar
    // So, it will use the baseServiceUrl which is already .../protocols
    return this.http.get<string[]>(`${this.baseServiceUrl}/`).pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: any) {
    console.error('API Error in ProtocolDashboardService:', error.message || error);
    let errorMessage = 'An API error occurred in DashboardService. Please try again or check console.';
    if (error.error instanceof ErrorEvent) {
      errorMessage = `Client Error: ${error.error.message}`;
    } else if (error.status) {
      errorMessage = `Server Error (Status ${error.status}): ${error.error?.detail || error.message}`;
    }
    return throwError(() => new Error(errorMessage));
  }
}
