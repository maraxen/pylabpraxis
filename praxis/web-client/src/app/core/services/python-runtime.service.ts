import { Injectable, signal } from '@angular/core';

interface WorkerResponse {
  type: string;
  id?: string;
  payload?: any;
}

@Injectable({
  providedIn: 'root'
})
export class PythonRuntimeService {
  private worker: Worker | null = null;
  private responseMap = new Map<string, (value: any) => void>();
  private errorMap = new Map<string, (reason: any) => void>();
  
  isReady = signal(false);
  
  constructor() {
    this.initWorker();
  }

  private initWorker() {
    if (typeof Worker !== 'undefined') {
      // Use standard ESM worker syntax which Angular/Vite supports
      this.worker = new Worker(new URL('../workers/python.worker', import.meta.url), {
        type: 'module'
      });
      
      this.worker.onmessage = ({ data }: { data: WorkerResponse }) => {
        this.handleMessage(data);
      };
      
      this.sendMessage('INIT').then(() => {
        console.log('Pyodide Runtime Initialized');
        this.isReady.set(true);
      }).catch(err => {
        console.error('Failed to initialize Pyodide', err);
      });
    } else {
      console.warn('Web Workers are not supported in this environment.');
    }
  }

  async execute(code: string): Promise<any> {
    await this.ensureReady();
    return this.sendMessage('EXEC', { code });
  }

  async install(packages: string[]): Promise<void> {
    await this.ensureReady();
    return this.sendMessage('INSTALL', { packages });
  }

  private ensureReady(): Promise<void> {
    if (this.isReady()) return Promise.resolve();
    // Simple polling/wait could be implemented here, or just fail
    // For MVP, we assume check is done by caller or we wait
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
    
    if (type === 'ERROR' && id) {
      const reject = this.errorMap.get(id);
      if (reject) {
        reject(payload);
        this.cleanupMaps(id);
      }
      return;
    }

    if (id) {
      const resolve = this.responseMap.get(id);
      if (resolve) {
        resolve(payload);
        this.cleanupMaps(id);
      }
    }
  }

  private cleanupMaps(id: string) {
    this.responseMap.delete(id);
    this.errorMap.delete(id);
  }
}
