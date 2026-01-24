import { TestBed } from '@angular/core/testing';
import { PythonRuntimeService } from './python-runtime.service';
import { InteractionService } from './interaction.service';
import { HardwareDiscoveryService } from './hardware-discovery.service';
import { firstValueFrom } from 'rxjs';
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

    (window as any).Worker = MockWorker;

    TestBed.configureTestingModule({
      providers: [
        PythonRuntimeService,
        {
          provide: InteractionService,
          useValue: { handleInteraction: vi.fn().mockResolvedValue({}) }
        },
        {
          provide: HardwareDiscoveryService,
          useValue: {
            openPort: vi.fn(),
            closePort: vi.fn(),
            writeToPort: vi.fn(),
            readFromPort: vi.fn(),
            readLineFromPort: vi.fn()
          }
        }
      ]
    });
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

    // Mock crypto.randomUUID
    const uuidSpy = vi.spyOn(crypto, 'randomUUID').mockReturnValue('test-uuid' as any);

    // Now execute
    const execPromise = firstValueFrom(service.execute('print("hello")'));

    // Allow ensuringReady to pass
    await new Promise(resolve => setTimeout(resolve, 0));

    const execCall = mockWorker.postMessage.mock.calls[0];
    expect(execCall[0].type).toBe('EXEC');
    expect(execCall[0].id).toBe('test-uuid');
    expect(execCall[0].payload).toEqual({ code: 'print("hello")' });

    // Simulate response
    mockWorker.onmessage({ data: { type: 'EXEC_COMPLETE', id: 'test-uuid', payload: 'hello' } });

    const result = await execPromise;
    expect(result).toEqual({ type: 'result', content: 'hello' });

    uuidSpy.mockRestore();
  });
});
