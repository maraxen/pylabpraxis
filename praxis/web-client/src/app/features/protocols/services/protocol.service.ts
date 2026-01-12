import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { ProtocolsService } from '../../../core/api-generated/services/ProtocolsService';
import { ApiWrapperService } from '../../../core/services/api-wrapper.service';
import { FunctionProtocolDefinitionResponse } from '../../../core/api-generated/models/FunctionProtocolDefinitionResponse';
import { ProtocolRunRead } from '../../../core/api-generated/models/ProtocolRunRead';

@Injectable({
  providedIn: 'root'
})
export class ProtocolService {
  private apiWrapper = inject(ApiWrapperService);
  private http = inject(HttpClient);
  private readonly API_URL = '/api/v1';

  getProtocols(): Observable<FunctionProtocolDefinitionResponse[]> {
    return this.apiWrapper.wrap(ProtocolsService.getMultiApiV1ProtocolsDefinitionsGet());
  }

  getRuns(): Observable<ProtocolRunRead[]> {
    return this.apiWrapper.wrap(ProtocolsService.getMultiApiV1ProtocolsRunsGet());
  }

  // If uploading a file
  // NOTE: This endpoint is not yet in the generated API client
  uploadProtocol(file: File): Observable<FunctionProtocolDefinitionResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<FunctionProtocolDefinitionResponse>(`${this.API_URL}/protocols/upload`, formData);
  }
}
