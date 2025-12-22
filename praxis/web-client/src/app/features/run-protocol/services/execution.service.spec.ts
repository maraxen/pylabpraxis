import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { ExecutionService } from './execution.service';
import { ExecutionStatus } from '../models/execution.models';
import { Subject } from 'rxjs';
import { vi, describe, beforeEach, afterEach, it, expect } from 'vitest';

// Mock rxjs/webSocket
const mockWebSocketSubject = new Subject<any>();
// Add a complete method to the mock subject as it is expected by the service
(mockWebSocketSubject as any).complete = vi.fn();

vi.mock('rxjs/webSocket', () => ({
  webSocket: vi.fn(() => mockWebSocketSubject)
}));

describe('ExecutionService', () => {
  let service: ExecutionService;
  let httpMock: HttpTestingController;
  const API_URL = '/api/v1';

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ExecutionService,
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    });

    service = TestBed.inject(ExecutionService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
    service.disconnect();
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should have null current run initially', () => {
      expect(service.currentRun()).toBeNull();
    });

    it('should not be connected initially', () => {
      expect(service.isConnected()).toBe(false);
    });

    it('should not be running initially', () => {
      expect(service.isRunning()).toBe(false);
    });
  });

  describe('startRun', () => {
    it('should start a protocol run', () => {
      const protocolId = 'protocol-123';
      const runName = 'Test Run';
      const parameters = { temp: 37, volume: 100 };

      service.startRun(protocolId, runName, parameters).subscribe(response => {
        expect(response.run_id).toBe('run-456');
      });

      const req = httpMock.expectOne(`${API_URL}/runs`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({
        protocol_definition_accession_id: protocolId,
        name: runName,
        parameters
      });

      req.flush({ run_id: 'run-456' });
    });

    it('should update current run state after starting', () => {
      service.startRun('protocol-1', 'Run 1').subscribe(() => {
        const currentRun = service.currentRun();
        expect(currentRun).not.toBeNull();
        expect(currentRun?.runId).toBe('run-123');
        expect(currentRun?.protocolName).toBe('Run 1');
        expect(currentRun?.status).toBe(ExecutionStatus.PENDING);
        expect(currentRun?.progress).toBe(0);
        expect(currentRun?.logs).toEqual([]);
      });

      const req = httpMock.expectOne(`${API_URL}/runs`);
      req.flush({ run_id: 'run-123' });
    });

    it('should handle start run without parameters', () => {
      service.startRun('protocol-1', 'Run 1').subscribe();

      const req = httpMock.expectOne(`${API_URL}/runs`);
      expect(req.request.body.parameters).toBeUndefined();
      req.flush({ run_id: 'run-123' });
    });

    it('should handle start run errors', () => {
      service.startRun('invalid-protocol', 'Test').subscribe({
        next: () => expect(true).toBe(false),
        error: (error) => {
          expect(error.status).toBe(404);
        }
      });

      const req = httpMock.expectOne(`${API_URL}/runs`);
      req.flush('Protocol not found', { status: 404, statusText: 'Not Found' });
    });

    it('should handle complex parameters', () => {
      const complexParams = {
        temperature: 37.5,
        volumes: [10, 20, 30],
        enabled: true,
        config: { mode: 'fast', retries: 3 }
      };

      service.startRun('protocol-1', 'Complex Run', complexParams).subscribe();

      const req = httpMock.expectOne(`${API_URL}/runs`);
      expect(req.request.body.parameters).toEqual(complexParams);
      req.flush({ run_id: 'run-complex' });
    });
  });

  describe('stopRun', () => {
    it('should stop a running protocol', () => {
      // Start a run first
      service.startRun('protocol-1', 'Test Run').subscribe();
      const startReq = httpMock.expectOne(`${API_URL}/runs`);
      startReq.flush({ run_id: 'run-123' });

      // Now stop it
      service.stopRun().subscribe();

      const req = httpMock.expectOne(`${API_URL}/runs/run-123/stop`);
      expect(req.request.method).toBe('POST');
      req.flush(null);

      // Check status after flush
      const currentRun = service.currentRun();
      expect(currentRun?.status).toBe(ExecutionStatus.CANCELLED);
    });

    it('should disconnect WebSocket after stopping', () => {
      // Start a run first
      service.startRun('protocol-1', 'Test Run').subscribe();
      const startReq = httpMock.expectOne(`${API_URL}/runs`);
      startReq.flush({ run_id: 'run-123' });

      // Stop it
      service.stopRun().subscribe();

      const req = httpMock.expectOne(`${API_URL}/runs/run-123/stop`);
      req.flush(null);

      expect(service.isConnected()).toBe(false);
    });

    it('should handle stop when no run is active', () => {
      service.stopRun().subscribe(() => {
        // Should complete without error
        expect(service.currentRun()).toBeNull();
      });
    });

    it('should handle stop run errors', () => {
      // Start a run first
      service.startRun('protocol-1', 'Test Run').subscribe();
      const startReq = httpMock.expectOne(`${API_URL}/runs`);
      startReq.flush({ run_id: 'run-123' });

      // Try to stop with error
      service.stopRun().subscribe({
        next: () => expect(true).toBe(false),
        error: (error) => {
          expect(error.status).toBe(500);
        }
      });

      const req = httpMock.expectOne(`${API_URL}/runs/run-123/stop`);
      req.flush('Error stopping run', { status: 500, statusText: 'Internal Server Error' });
    });
  });

  describe('clearRun', () => {
    it('should clear current run state', () => {
      // Start a run first
      service.startRun('protocol-1', 'Test Run').subscribe();
      const req = httpMock.expectOne(`${API_URL}/runs`);
      req.flush({ run_id: 'run-123' });

      expect(service.currentRun()).not.toBeNull();

      service.clearRun();

      expect(service.currentRun()).toBeNull();
    });

    it('should disconnect WebSocket when clearing', () => {
      service.clearRun();

      expect(service.isConnected()).toBe(false);
    });

    it('should handle multiple clear calls', () => {
      service.clearRun();
      service.clearRun();
      service.clearRun();

      expect(service.currentRun()).toBeNull();
      expect(service.isConnected()).toBe(false);
    });
  });

  describe('disconnect', () => {
    it('should set isConnected to false', () => {
      service.disconnect();
      expect(service.isConnected()).toBe(false);
    });

    it('should handle disconnect when not connected', () => {
      expect(service.isConnected()).toBe(false);
      service.disconnect();
      expect(service.isConnected()).toBe(false);
    });

    it('should handle multiple disconnect calls', () => {
      service.disconnect();
      service.disconnect();
      service.disconnect();
      expect(service.isConnected()).toBe(false);
    });
  });

  describe('Signal Reactivity', () => {
    it('should have isRunning computed from status', () => {
      service.startRun('protocol-1', 'Test Run').subscribe();
      
      const req = httpMock.expectOne(`${API_URL}/runs`);
      req.flush({ run_id: 'run-123' });

      // Initially PENDING
      expect(service.isRunning()).toBe(false);
    });

    it('should expose currentRun as readonly signal', () => {
      service.startRun('protocol-1', 'Test').subscribe();
      
      const req = httpMock.expectOne(`${API_URL}/runs`);
      req.flush({ run_id: 'run-123' });

      const currentRun = service.currentRun();
      expect(currentRun).not.toBeNull();
      expect(typeof currentRun).toBe('object');
    });

    it('should expose isConnected as readonly signal', () => {
      const isConnected = service.isConnected();
      expect(typeof isConnected).toBe('boolean');
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors on start', () => {
      service.startRun('protocol-1', 'Test').subscribe({
        next: () => expect(true).toBe(false),
        error: (error) => {
          expect(error.status).toBe(0);
        }
      });

      const req = httpMock.expectOne(`${API_URL}/runs`);
      req.error(new ProgressEvent('error'), { status: 0, statusText: 'Network error' });
    });

    it('should handle timeout errors', () => {
      service.startRun('protocol-1', 'Test').subscribe({
        next: () => expect(true).toBe(false),
        error: (error) => {
          expect(error.status).toBe(408);
        }
      });

      const req = httpMock.expectOne(`${API_URL}/runs`);
      req.flush('Timeout', { status: 408, statusText: 'Request Timeout' });
    });

    it('should handle unauthorized errors', () => {
      service.startRun('protocol-1', 'Test').subscribe({
        next: () => expect(true).toBe(false),
        error: (error) => {
          expect(error.status).toBe(401);
        }
      });

      const req = httpMock.expectOne(`${API_URL}/runs`);
      req.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
    });
  });

  describe('Integration', () => {
    it('should handle start -> stop flow', () => {
      // Start run
      service.startRun('protocol-1', 'Test Run').subscribe();
      const startReq = httpMock.expectOne(`${API_URL}/runs`);
      startReq.flush({ run_id: 'run-123' });

      expect(service.currentRun()?.runId).toBe('run-123');

      // Stop run
      service.stopRun().subscribe(() => {
        expect(service.currentRun()?.status).toBe(ExecutionStatus.CANCELLED);
        expect(service.isConnected()).toBe(false);
      });

      const stopReq = httpMock.expectOne(`${API_URL}/runs/run-123/stop`);
      stopReq.flush(null);
    });

    it('should handle start -> clear flow', () => {
      service.startRun('protocol-1', 'Test Run').subscribe();
      const req = httpMock.expectOne(`${API_URL}/runs`);
      req.flush({ run_id: 'run-123' });
      
      expect(service.currentRun()).not.toBeNull();

      service.clearRun();

      expect(service.currentRun()).toBeNull();
      expect(service.isConnected()).toBe(false);
    });

    it('should handle multiple sequential runs', () => {
      // First run
      service.startRun('protocol-1', 'Run 1').subscribe();
      const req1 = httpMock.expectOne(`${API_URL}/runs`);
      req1.flush({ run_id: 'run-1' });

      expect(service.currentRun()?.runId).toBe('run-1');

      service.clearRun();

      // Second run
      service.startRun('protocol-2', 'Run 2').subscribe(() => {
        expect(service.currentRun()?.runId).toBe('run-2');
      });

      const req2 = httpMock.expectOne(`${API_URL}/runs`);
      req2.flush({ run_id: 'run-2' });
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty run name', () => {
      service.startRun('protocol-1', '').subscribe();

      const req = httpMock.expectOne(`${API_URL}/runs`);
      expect(req.request.body.name).toBe('');
      req.flush({ run_id: 'run-empty' });
    });

    it('should handle very long run names', () => {
      const longName = 'a'.repeat(1000);
      service.startRun('protocol-1', longName).subscribe();

      const req = httpMock.expectOne(`${API_URL}/runs`);
      expect(req.request.body.name).toBe(longName);
      req.flush({ run_id: 'run-long' });
    });

    it('should handle special characters in protocol ID', () => {
      const specialId = 'protocol-123_abc-xyz';
      service.startRun(specialId, 'Test').subscribe();

      const req = httpMock.expectOne(`${API_URL}/runs`);
      expect(req.request.body.protocol_definition_accession_id).toBe(specialId);
      req.flush({ run_id: 'run-special' });
    });

    it('should handle null parameters gracefully', () => {
      service.startRun('protocol-1', 'Test', undefined).subscribe();

      const req = httpMock.expectOne(`${API_URL}/runs`);
      expect(req.request.body.parameters).toBeUndefined();
      req.flush({ run_id: 'run-null-params' });
    });
  });
});
