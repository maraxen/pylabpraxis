import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map, shareReplay } from 'rxjs/operators';

// Define an interface for the structure of a protocol (based on your backend)
// This is a basic example; adjust it to match your actual protocol data structure.
export interface Protocol {
  id: string; // Or number, depending on your backend
  name: string;
  description?: string;
  version?: string;
  author?: string;
  created_at?: string; // Or Date
  updated_at?: string; // Or Date
  schema?: any; // The JSON schema for parameters
  // Add other relevant fields
}

// Interface for the API response if it's a list wrapped in an object
// export interface ProtocolsApiResponse {
//   protocols: Protocol[];
//   total?: number;
//   // any other metadata
// }

@Injectable({
  providedIn: 'root' // Provided in root, or in a specific feature module if preferred
})
export class ProtocolService {
  private http = inject(HttpClient);
  // Adjust the API base URL as needed. This could also come from environment variables.
  private apiUrl = '/api/v1/protocols'; // Assuming your backend is proxied or on the same domain

  // Cache for the list of protocols to avoid repeated API calls
  private protocolsCache$: Observable<Protocol[]> | undefined;

  constructor() { }

  /**
   * Fetches the list of all available protocols from the backend.
   * Implements caching to avoid redundant API calls.
   * @returns Observable<Protocol[]>
   */
  getProtocols(): Observable<Protocol[]> {
    if (!this.protocolsCache$) {
      this.protocolsCache$ = this.http.get<Protocol[]>(this.apiUrl).pipe(
        // If your API returns an object like { protocols: [...] }, map it:
        // map(response => response.protocols),
        tap(protocols => console.log(`Fetched ${protocols.length} protocols`)),
        shareReplay(1), // Cache the last emitted value and replay for new subscribers
        catchError(this.handleError)
      );
    }
    return this.protocolsCache$;
  }

  /**
   * Fetches a single protocol by its ID.
   * @param protocolId The ID of the protocol to fetch.
   * @returns Observable<Protocol>
   */
  getProtocolById(protocolId: string): Observable<Protocol> {
    // No caching for single protocol by default, but can be added if needed
    return this.http.get<Protocol>(`${this.apiUrl}/${protocolId}`).pipe(
      tap(protocol => console.log(`Fetched protocol with id=${protocolId}`)),
      catchError(this.handleError)
    );
  }

  /**
   * Clears the protocols list cache.
   * Call this if you know the list of protocols might have changed (e.g., after adding a new one).
   */
  clearCache(): void {
    this.protocolsCache$ = undefined;
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unknown error occurred!';
    if (error.error instanceof ErrorEvent) {
      // A client-side or network error occurred. Handle it accordingly.
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // The backend returned an unsuccessful response code.
      // The response body may contain clues as to what went wrong.
      errorMessage = `Server returned code: ${error.status}, error message is: ${error.message}`;
    }
    console.error(errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
