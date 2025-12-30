import { TestBed } from '@angular/core/testing';
import { PythonRuntimeService } from './python-runtime.service';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

describe('PythonRuntimeService', () => {
  let service: PythonRuntimeService;
  let mockWorker: any;

  beforeEach(() => {
    // Mock Worker instance
    mockWorker = {
      postMessage: vi.fn(),
      onmessage: null,
      terminate: vi.fn()
    };

    // Mock Worker Constructor
    class MockWorker {
      constructor() {
        return mockWorker;
      }
    }

    // Store original Worker
    const originalWorker = window.Worker;
    (window as any).Worker = MockWorker;

    TestBed.configureTestingModule({});
    service = TestBed.inject(PythonRuntimeService);
  });
  
  afterEach(() => {
     vi.restoreAllMocks();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should initialize worker', () => {
    expect(mockWorker.postMessage).toHaveBeenCalledWith(expect.objectContaining({ type: 'INIT' }));
  });

  it('should handle execution', async () => {
    // Simulate init complete
    const initCall = mockWorker.postMessage.mock.calls[0];
    const initId = initCall[0].id;
    
    mockWorker.onmessage({ data: { type: 'INIT_COMPLETE', id: initId } });
    
    // Allow promise microtasks to resolve so isReady becomes true
    await new Promise(resolve => setTimeout(resolve, 0));
    
    expect(service.isReady()).toBe(true);
    
    // Clear previous calls to focus on EXEC
    mockWorker.postMessage.mockClear();

    // Now execute
    const execPromise = service.execute('print("hello")');
    
    // Allow ensuringReady to pass
    await new Promise(resolve => setTimeout(resolve, 0));
    
    const execCall = mockWorker.postMessage.mock.calls[0];
    expect(execCall[0].type).toBe('EXEC');
    expect(execCall[0].payload).toEqual({ code: 'print("hello")' });
    
    // Simulate response
    const execId = execCall[0].id;
    mockWorker.onmessage({ data: { type: 'EXEC_COMPLETE', id: execId, payload: 'hello' } });
    
    const result = await execPromise;
    expect(result).toBe('hello');
  });
});
