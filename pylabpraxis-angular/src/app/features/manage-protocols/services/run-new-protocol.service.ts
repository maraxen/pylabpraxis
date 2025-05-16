// src/app/features/manage-protocols/services/run-new-protocol.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

// Import environment configuration using the path alias
import { environment } from '@env'; // Uses tsconfig.json path alias

import {
  ProtocolInfo,
  ProtocolDetails,
  ProtocolPrepareRequest,
  ProtocolPrepareResponse,
  ProtocolStatusResponse,
  FileUploadResponse
} from '@protocols/protocol.models'; // Using path alias for models

@Injectable({
  providedIn: 'root',
})
export class RunNewProtocolService {
  private http = inject(HttpClient);

  // Construct the base URL for this specific service, including versioning
  private baseServiceUrl = `${environment.apiUrl}/v1/protocols`; // e.g., http://localhost:8000/api/v1/protocols

  constructor() {
    console.log('RunNewProtocolService initialized. API URL:', this.baseServiceUrl);
  }

  /**
   * Discover available protocol files.
   * Corresponds to GET /api/v1/protocols/discover
   */
  discoverProtocols(): Observable<ProtocolInfo[]> {
    return this.http.get<ProtocolInfo[]>(`${this.baseServiceUrl}/discover`).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Get details about a specific protocol.
   * Corresponds to GET /api/v1/protocols/details
   * @param protocolPath The file path of the protocol.
   */
  getProtocolDetails(protocolPath: string): Observable<ProtocolDetails> {
    const params = new HttpParams().set('protocol_path', protocolPath);
    return this.http.get<ProtocolDetails>(`${this.baseServiceUrl}/details`, { params }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Get JSONSchema for a protocol's parameters.
   * Corresponds to GET /api/v1/protocols/schema
   * @param protocolPath The file path of the protocol.
   */
  getProtocolSchema(protocolPath: string): Observable<any> {
    const params = new HttpParams().set('protocol_path', protocolPath);
    return this.http.get<any>(`${this.baseServiceUrl}/schema`, { params }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Prepare a protocol by loading its requirements and matching assets.
   * Corresponds to POST /api/v1/protocols/prepare
   * @param payload The preparation request data.
   */
  prepareProtocol(payload: ProtocolPrepareRequest): Observable<ProtocolPrepareResponse> {
    return this.http.post<ProtocolPrepareResponse>(`${this.baseServiceUrl}/prepare`, payload).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Start a protocol with a validated configuration.
   * Corresponds to POST /api/v1/protocols/start
   * @param config The validated protocol configuration (typically from prepareProtocol response).
   */
  startProtocol(config: any): Observable<ProtocolStatusResponse> {
    return this.http.post<ProtocolStatusResponse>(`${this.baseServiceUrl}/start`, config).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Uploads a protocol configuration file (JSON).
   * Corresponds to POST /api/v1/protocols/upload_config_file
   * @param file The JSON configuration file to upload.
   */
  uploadConfigFile(file: File): Observable<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    return this.http.post<FileUploadResponse>(`${this.baseServiceUrl}/upload_config_file`, formData).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Uploads a deck layout file (JSON).
   * Corresponds to POST /api/v1/protocols/upload_deck_file
   * @param file The JSON deck layout file to upload.
   */
  uploadDeckFile(file: File): Observable<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    return this.http.post<FileUploadResponse>(`${this.baseServiceUrl}/upload_deck_file`, formData).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Get a list of available deck layout files.
   * Corresponds to GET /api/v1/protocols/deck_layouts
   */
  getDeckLayouts(): Observable<string[]> {
    return this.http.get<string[]>(`${this.baseServiceUrl}/deck_layouts`).pipe(
      catchError(this.handleError)
    );
  }


  /**
   * Get the status of a specific protocol.
   * Corresponds to GET /api/v1/protocols/{protocol_name}
   * @param protocolName The name of the protocol.
   */
  getProtocolStatus(protocolName: string): Observable<ProtocolStatusResponse> {
    return this.http.get<ProtocolStatusResponse>(`${this.baseServiceUrl}/${protocolName}`).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Sends a command to a running protocol.
   * Corresponds to POST /api/v1/protocols/{protocol_name}/command
   * @param protocolName The name of the protocol.
   * @param command The command to send.
   */
  sendProtocolCommand(protocolName: string, command: string): Observable<any> {
    return this.http.post<any>(`${this.baseServiceUrl}/${protocolName}/command`, { command }).pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: any) {
    console.error('API Error in RunNewProtocolService:', error.message || error);
    let errorMessage = 'An API error occurred. Please try again or check console for details.';
    if (error.error instanceof ErrorEvent) {
      errorMessage = `Client Error: ${error.error.message}`;
    } else if (error.status) {
      errorMessage = `Server Error (Status ${error.status}): ${error.error?.detail || error.message}`;
    }
    return throwError(() => new Error(errorMessage));
  }
}
