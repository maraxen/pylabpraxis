import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { ProtocolService } from './protocol.service';
import { ProtocolDefinition } from '../models/protocol.models';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';

describe('ProtocolService', () => {
  let service: ProtocolService;
  let httpMock: HttpTestingController;
  const API_URL = '/api/v1';

  beforeEach(() => {
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({
      providers: [
        ProtocolService,
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    });

    service = TestBed.inject(ProtocolService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  describe('getProtocols', () => {
    it('should retrieve protocols', () => {
      const mockProtocols: ProtocolDefinition[] = [
        { accession_id: 'p1', name: 'Protocol 1', is_top_level: true, version: '1.0', parameters: [], assets: [] },
        { accession_id: 'p2', name: 'Protocol 2', is_top_level: false, version: '2.0', parameters: [], assets: [] }
      ];

      service.getProtocols().subscribe(protocols => {
        expect(protocols.length).toBe(2);
        expect(protocols).toEqual(mockProtocols);
      });

      const req = httpMock.expectOne(`${API_URL}/protocols/definitions`);
      expect(req.request.method).toBe('GET');
      req.flush(mockProtocols);
    });
  });

  describe('uploadProtocol', () => {
    it('should upload a protocol file', () => {
      const file = new File(['content'], 'protocol.py', { type: 'text/x-python' });
      const mockResponse: ProtocolDefinition = { accession_id: 'p3', name: 'protocol.py', is_top_level: true, version: '1.0', parameters: [], assets: [] };

      service.uploadProtocol(file).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${API_URL}/protocols/upload`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body instanceof FormData).toBe(true);
      expect(req.request.body.get('file')).toBe(file);

      req.flush(mockResponse);
    });
  });
});