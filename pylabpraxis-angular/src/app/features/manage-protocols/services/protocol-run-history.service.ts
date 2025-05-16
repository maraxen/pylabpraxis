// src/app/features/manage-protocols/services/protocol-run-history.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http'; // Added HttpParams
import { Observable, throwError, of } from 'rxjs'; // Added of for returning empty array
import { catchError } from 'rxjs/operators';

import { environment } from '@env'; // Using path alias

// Define a model for what a historical run entry might look like.
export interface ProtocolRunRecord {
  id: string;
  protocolName: string;
  startTime: string; // Changed to string for easier JSON parsing, convert to Date in component
  endTime?: string; // Changed to string
  status: string;
  parameters?: Record<string, any>;
  // outcome?: any;
}

@Injectable({
  providedIn: 'root',
})
export class ProtocolRunHistoryService {
  private http = inject(HttpClient);

  // Construct the base URL for this specific service, including versioning
  // Assuming the history endpoint will be something like /api/v1/protocol-runs
  private baseServiceUrl = `${environment.apiUrl}/v1/protocol-runs`;

  constructor() {
    console.log('ProtocolRunHistoryService initialized. API URL:', this.baseServiceUrl);
  }

  getRunHistory(
    protocolName?: string,
    limit?: number,
    offset?: number
  ): Observable<ProtocolRunRecord[]> {
    let params = new HttpParams();
    if (protocolName) {
      params = params.set('protocolName', protocolName);
    }
    if (limit !== undefined) { // Check for undefined explicitly
      params = params.set('limit', limit.toString());
    }
    if (offset !== undefined) { // Check for undefined explicitly
      params = params.set('offset', offset.toString());
    }

    // Example: GET /api/v1/protocol-runs/history
    // Adjust the endpoint if your backend has a different structure
    console.warn('getRunHistory called. Ensure backend API at `${this.baseServiceUrl}/history` is implemented.');
    return this.http.get<ProtocolRunRecord[]>(`${this.baseServiceUrl}/history`, { params })
      .pipe(catchError(err => {
        this.handleError(err, 'getRunHistory');
        return of([]); // Return empty array on error or if API not ready
      }));
  }

  getRunDetails(runId: string): Observable<ProtocolRunRecord | null> { // Allow null for not found
    console.warn('getRunDetails called. Ensure backend API at `${this.baseServiceUrl}/${runId}` is implemented.');
    // Example: GET /api/v1/protocol-runs/{runId}
    return this.http.get<ProtocolRunRecord>(`${this.baseServiceUrl}/${runId}`)
      .pipe(catchError(err => {
        this.handleError(err, `getRunDetails for ID ${runId}`);
        return of(null); // Return null on error
      }));
  }

  private handleError(error: any, operation: string = 'operation') {
    console.error(`API Error in ${operation} (ProtocolRunHistoryService):`, error.message || error);
    let errorMessage = `Error during ${operation}. Please try again or check console.`;
    if (error.error instanceof ErrorEvent) {
      errorMessage = `Client Error in ${operation}: ${error.error.message}`;
    } else if (error.status) {
      errorMessage = `Server Error in ${operation} (Status ${error.status}): ${error.error?.detail || error.message}`;
    }
    // For now, we are returning of([]) or of(null) in the calling methods.
    // If you want to propagate the error to the component for specific handling:
    // return throwError(() => new Error(errorMessage));
  }
}
