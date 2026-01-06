import { Injectable, inject, signal } from '@angular/core';
import { Observable, Subject, from, of } from 'rxjs';
import { ReplOutput, ReplRuntime, CompletionItem, SignatureInfo } from './repl-runtime.interface';
import { HardwareDiscoveryService } from './hardware-discovery.service';

interface WorkerResponse {
  type: string;
  id?: string;
  payload?: any;
}

interface RawIOPayload {
  command: 'OPEN' | 'CLOSE' | 'WRITE' | 'READ' | 'READLINE';
  port_id: string;
  data?: number[];
  size?: number;
  timeout?: number;
  request_id?: string;
  baudRate?: number;
}

@Injectable({
  providedIn: 'root'
})
export class PythonRuntimeService implements ReplRuntime {
  private worker: Worker | null = null;
  private responseMap = new Map<string, (value: any) => void>();
  private errorMap = new Map<string, (reason: any) => void>();
  private stdoutSubjects = new Map<string, Subject<ReplOutput>>();

  private hardwareService = inject(HardwareDiscoveryService);

  isReady = signal(false);

  constructor() {
    this.initWorker();
  }

  private initWorker() {
    if (typeof Worker !== 'undefined') {
      this.worker = new Worker(new URL('../workers/python.worker', import.meta.url), {
        type: 'module'
      });

      this.worker.onmessage = ({ data }: { data: WorkerResponse }) => {
        this.handleMessage(data);
      };

      this.sendMessage('INIT').then(() => {
        this.isReady.set(true);
      }).catch(err => {
        console.error('[PythonRuntime] Failed to initialize Pyodide:', err);
      });
    } else {
      console.warn('Web Workers are not supported in this environment.');
    }
  }

  // ReplRuntime Implementation
  connect(): Observable<void> {
    return this.isReady() ? of(void 0) : from(this.ensureReady());
  }

  disconnect(): void {
    // We don't want to terminate the main worker easily as it's shared,
    // but we could. For now, just a placeholder.
  }

  execute(code: string): Observable<ReplOutput> {
    const id = crypto.randomUUID();
    const subject = new Subject<ReplOutput>();
    this.stdoutSubjects.set(id, subject);

    this.ensureReady().then(() => {
      if (!this.worker) {
        subject.error('Worker not active');
        return;
      }
      this.worker.postMessage({ type: 'EXEC', id, payload: { code } });

      this.responseMap.set(id, (result) => {
        subject.next({ type: 'result', content: result });
        subject.complete();
        this.cleanupMaps(id);
      });

      this.errorMap.set(id, (error) => {
        subject.next({ type: 'error', content: error });
        subject.complete();
        this.cleanupMaps(id);
      });
    });

    return subject.asObservable();
  }

  interrupt(): void {
    // Terminate and restart worker is the only safe way to interrupt synchronous Pyodide execution
    console.warn('Interrupt not fully supported in Pyodide without worker restart');
  }

  async getCompletions(code: string, _cursor: number): Promise<CompletionItem[]> {
    if (!this.worker) return [];

    const id = crypto.randomUUID();
    const worker = this.worker; // Capture for closure
    return new Promise((resolve) => {
      return new Promise((resolve) => {
        const timeoutId = setTimeout(() => {
          worker?.removeEventListener('message', handler);
          resolve([]);
        }, 5000);

        const handler = ({ data }: MessageEvent) => {
          if (data.id === id && data.type === 'COMPLETE_RESULT') {
            worker?.removeEventListener('message', handler);
            clearTimeout(timeoutId);
            // Matches are now CompletionItem[] from the updated worker
            const matches = data.payload.matches || [];
            resolve(matches);
          }
        };

        worker!.addEventListener('message', handler);
        worker!.postMessage({ type: 'COMPLETE', id, payload: { code } });
      });
    });
  }

  async getSignatures(code: string, _cursor: number): Promise<SignatureInfo[]> {
    if (!this.worker) return [];

    const id = crypto.randomUUID();
    const worker = this.worker;
    return new Promise((resolve) => {
      return new Promise((resolve) => {
        const timeoutId = setTimeout(() => {
          worker?.removeEventListener('message', handler);
          resolve([]);
        }, 5000);

        const handler = ({ data }: MessageEvent) => {
          if (data.id === id && data.type === 'SIGNATURE_RESULT') {
            worker?.removeEventListener('message', handler);
            clearTimeout(timeoutId);
            resolve(data.payload.signatures || []);
          }
        };

        worker!.addEventListener('message', handler);
        worker!.postMessage({ type: 'SIGNATURES', id, payload: { code } });
      });
    });
  }

  // Legacy/Internal methods
  async install(packages: string[]): Promise<void> {
    await this.ensureReady();
    return this.sendMessage('INSTALL', { packages });
  }

  private ensureReady(): Promise<void> {
    if (this.isReady()) return Promise.resolve();
    return new Promise((resolve) => {
      const interval = setInterval(() => {
        if (this.isReady()) {
          clearInterval(interval);
          resolve();
        }
      }, 100);
    });
  }

  private sendMessage(type: string, payload?: any): Promise<any> {
    if (!this.worker) return Promise.reject('Worker not active');

    const id = crypto.randomUUID();
    return new Promise((resolve, reject) => {
      this.responseMap.set(id, resolve);
      this.errorMap.set(id, reject);

      this.worker!.postMessage({ type, id, payload });
    });
  }

  private handleMessage(data: WorkerResponse) {
    const { type, id, payload } = data;

    if (type === 'STDOUT' && id) {
      this.stdoutSubjects.get(id)?.next({ type: 'stdout', content: payload });
      return;
    }

    if (type === 'STDERR' && id) {
      this.stdoutSubjects.get(id)?.next({ type: 'stderr', content: payload });
      return;
    }

    // Handle RAW_IO messages from Python - route to HardwareDiscoveryService
    if (type === 'RAW_IO' && payload) {
      this.handleRawIO(payload as RawIOPayload);
      return;
    }

    if (type === 'ERROR' && id) {
      const reject = this.errorMap.get(id);
      if (reject) {
        reject(payload);
      }
      return;
    }

    if (id) {
      const resolve = this.responseMap.get(id);
      if (resolve) {
        resolve(payload);
      }
    }
  }

  /**
   * Handle RAW_IO commands from Python and route to WebSerial via HardwareDiscoveryService
   */
  private async handleRawIO(payload: RawIOPayload) {
    const { command, port_id, data, size, request_id, baudRate } = payload;

    try {
      switch (command) {
        case 'OPEN':
          await this.hardwareService.openPort(port_id, { baudRate: baudRate || 9600 });
          console.log(`[RAW_IO] Opened port ${port_id}`);
          break;

        case 'CLOSE':
          await this.hardwareService.closePort(port_id);
          console.log(`[RAW_IO] Closed port ${port_id}`);
          break;

        case 'WRITE':
          if (data) {
            await this.hardwareService.writeToPort(port_id, new Uint8Array(data));
            console.log(`[RAW_IO] Wrote ${data.length} bytes to ${port_id}`);
          }
          break;

        case 'READ':
          if (size !== undefined && request_id) {
            const result = await this.hardwareService.readFromPort(port_id, size);
            // Send response back to Python worker
            this.worker?.postMessage({
              type: 'RAW_IO_RESPONSE',
              payload: { request_id, data: Array.from(result) }
            });
            console.log(`[RAW_IO] Read ${result.length} bytes from ${port_id}`);
          }
          break;

        case 'READLINE':
          if (request_id) {
            const result = await this.hardwareService.readLineFromPort(port_id);
            this.worker?.postMessage({
              type: 'RAW_IO_RESPONSE',
              payload: { request_id, data: Array.from(result) }
            });
            console.log(`[RAW_IO] Read line from ${port_id}`);
          }
          break;
      }
    } catch (error) {
      console.error(`[RAW_IO] Error handling ${command} on ${port_id}:`, error);
      // Send error response back to Python if there's a request_id
      if (request_id) {
        this.worker?.postMessage({
          type: 'RAW_IO_RESPONSE',
          payload: { request_id, data: [], error: String(error) }
        });
      }
    }
  }

  private cleanupMaps(id: string) {
    this.responseMap.delete(id);
    this.errorMap.delete(id);
    this.stdoutSubjects.delete(id);
  }
}

