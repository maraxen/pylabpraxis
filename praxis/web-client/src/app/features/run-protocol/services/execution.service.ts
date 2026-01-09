
import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { MOCK_PROTOCOLS } from '@assets/browser-data/protocols';
import { ModeService } from '@core/services/mode.service';
import { PythonRuntimeService } from '@core/services/python-runtime.service';
import { SqliteService } from '@core/services/sqlite.service';
import { environment } from '@env/environment';
import { Observable, Subject, of } from 'rxjs';
import { catchError, retry, tap } from 'rxjs/operators';
import { WebSocketSubject, webSocket } from 'rxjs/webSocket';
import { ExecutionMessage, ExecutionState, ExecutionStatus } from '../models/execution.models';

@Injectable({
  providedIn: 'root'
})
export class ExecutionService {
  private http = inject(HttpClient);
  private modeService = inject(ModeService);
  private pythonRuntime = inject(PythonRuntimeService);
  private sqliteService = inject(SqliteService);

  private readonly WS_URL = environment.wsUrl;
  private readonly API_URL = environment.apiUrl;

  private socket$: WebSocketSubject<ExecutionMessage> | null = null;
  private messagesSubject = new Subject<ExecutionMessage>();

  // Use signals for reactive state
  private _currentRun = signal<ExecutionState | null>(null);
  private _isConnected = signal(false);

  // Public computed signals
  readonly currentRun = this._currentRun.asReadonly();
  readonly isConnected = this._isConnected.asReadonly();
  readonly isRunning = computed(() => this._currentRun()?.status === ExecutionStatus.RUNNING);

  messages$ = this.messagesSubject.asObservable();

  /**
   * Check protocol compatibility with available machines
   */
  getCompatibility(protocolId: string): Observable<any[]> {
    // In browser mode, return mock compatibility data
    if (this.modeService.isBrowserMode()) {
      return of([{
        machine: {
          accession_id: 'sim-machine-1',
          name: 'Simulation Machine',
          status: 'IDLE' as any,
          machine_category: 'HamiltonSTAR'
        },
        compatibility: { is_compatible: true, missing_capabilities: [], matched_capabilities: [], warnings: [] }
      }]);
    }
    return this.http.get<any[]>(`${this.API_URL}/protocols/${protocolId}/compatibility`);
  }

  /**
   * Start a new protocol run
   */
  startRun(
    protocolId: string,
    runName: string,
    parameters?: Record<string, any>,
    simulationMode: boolean = true,
    notes?: string
  ): Observable<{ run_id: string }> {
    // Browser mode: execute via Pyodide
    if (this.modeService.isBrowserMode()) {
      return this.startBrowserRun(protocolId, runName, parameters, notes);
    }

    // Production mode: use HTTP API
    return this.http.post<{ run_id: string }>(`${this.API_URL}/protocols/runs`, {
      protocol_definition_accession_id: protocolId,
      name: runName,
      parameters,
      simulation_mode: simulationMode
    }).pipe(
      tap(response => {
        this._currentRun.set({
          runId: response.run_id,
          protocolName: runName,
          status: ExecutionStatus.PENDING,
          progress: 0,
          logs: []
        });
        this.connectWebSocket(response.run_id);
      })
    );
  }

  /**
   * Execute protocol in browser mode using Pyodide
   */
  private startBrowserRun(
    protocolId: string,
    runName: string,
    parameters?: Record<string, any>,
    notes?: string
  ): Observable<{ run_id: string }> {
    const runId = crypto.randomUUID();

    // Initialize run state
    this._currentRun.set({
      runId,
      protocolName: runName,
      status: ExecutionStatus.PENDING,
      progress: 0,
      logs: ['[Browser Mode] Starting execution...']
    });

    // Persist run to IndexedDB
    const runRecord = {
      accession_id: runId,
      protocol_definition_accession_id: protocolId,
      name: runName,
      status: 'QUEUED',
      created_at: new Date().toISOString(),
      input_parameters_json: JSON.stringify(parameters || {}),
      properties_json: JSON.stringify({ notes, simulation_mode: true })
    };

    this.sqliteService.createProtocolRun(runRecord).subscribe({
      error: (err) => console.warn('[ExecutionService] Failed to persist run:', err)
    });

    // Execute asynchronously
    this.executeBrowserProtocol(protocolId, runId, parameters);

    return of({ run_id: runId });
  }

  /**
   * Execute protocol code in Pyodide worker
   */
  private async executeBrowserProtocol(
    protocolId: string,
    runId: string,
    parameters?: Record<string, any>
  ): Promise<void> {
    try {
      // Update status to running
      this.updateRunState({ status: ExecutionStatus.RUNNING });
      this.addLog('[Browser Mode] Loading protocol...');

      // Get protocol definition from SQLite
      const protocol = await this.sqliteService.getProtocolById(protocolId) ||
        MOCK_PROTOCOLS.find(p => p.accession_id === protocolId) || null;

      if (!protocol) {
        throw new Error(`Protocol not found: ${protocolId}`);
      }

      this.addLog(`[Browser Mode] Executing: ${protocol.name}`);
      this.updateRunState({ progress: 10, currentStep: 'Initializing' });

      // Build Python code to execute the protocol
      const code = this.buildProtocolExecutionCode(protocol, parameters);

      // Execute via PythonRuntimeService
      this.updateRunState({ progress: 20, currentStep: 'Running protocol' });

      await new Promise<void>((resolve, reject) => {
        let hasError = false;

        this.pythonRuntime.execute(code).subscribe({
          next: (output) => {
            if (output.type === 'stdout') {
              this.addLog(output.content);
            } else if (output.type === 'stderr') {
              this.addLog(`[Error] ${output.content}`);
              hasError = true;
            } else if (output.type === 'result') {
              this.addLog(`[Result] ${output.content}`);
            }
          },
          error: (err) => {
            this.addLog(`[Error] Execution failed: ${err}`);
            reject(err);
          },
          complete: () => {
            if (hasError) {
              reject(new Error('Protocol execution had errors'));
            } else {
              resolve();
            }
          }
        });
      });

      // Success
      this.updateRunState({
        status: ExecutionStatus.COMPLETED,
        progress: 100,
        endTime: new Date().toISOString()
      });
      this.addLog('[Browser Mode] Execution completed successfully.');

      // Update run status in IndexedDB
      this.sqliteService.updateProtocolRunStatus(runId, 'COMPLETED').subscribe();

    } catch (error) {
      console.error('[Browser Execution Error]', error);
      const current = this._currentRun();
      if (current) {
        this._currentRun.set({
          ...current,
          status: ExecutionStatus.FAILED,
          logs: [...current.logs, `[Error] ${String(error)}`]
        });
      }

      // Update run status in IndexedDB
      this.sqliteService.updateProtocolRunStatus(runId, 'FAILED').subscribe();
    }
  }

  /**
   * Build Python code to execute a protocol
   */
  private buildProtocolExecutionCode(
    protocol: { fqn: string; function_name?: string | null; module_name?: string | null },
    parameters?: Record<string, any>
  ): string {
    const moduleName = protocol.module_name || protocol.fqn.split('.').slice(0, -1).join('.');
    const functionName = protocol.function_name || protocol.fqn.split('.').pop() || 'run';

    // Serialize parameters for Python
    const paramsStr = parameters ? JSON.stringify(parameters) : '{}';

    return `
# Browser mode protocol execution
import json

print("[Browser] Setting up simulation environment...")

# Import the protocol module
try:
    from ${moduleName} import ${functionName}
except ImportError as e:
    print(f"[Browser] Protocol import not available in browser: {e}")
    print("[Browser] Running simulation placeholder instead...")

    # Simulation placeholder
    def ${functionName}(*args, **kwargs):
        print("[Simulation] Protocol started")
        print("[Simulation] Step 1: Initialize")
        print("[Simulation] Step 2: Execute")
        print("[Simulation] Step 3: Complete")
        return {"status": "simulated", "steps_executed": 3}

# Parse parameters
params = json.loads('''${paramsStr}''')

# Execute the protocol
print("[Browser] Executing protocol...")
result = ${functionName}(**params) if params else ${functionName}()
print(f"[Browser] Protocol finished with result: {result}")
`;
  }

  /**
   * Helper to update run state
   */
  private updateRunState(updates: Partial<ExecutionState>): void {
    const current = this._currentRun();
    if (current) {
      this._currentRun.set({ ...current, ...updates });
    }
  }

  /**
   * Helper to add a log message
   */
  private addLog(message: string): void {
    const current = this._currentRun();
    if (current) {
      this._currentRun.set({
        ...current,
        logs: [...current.logs, message]
      });
      // Also emit as message for subscribers
      this.messagesSubject.next({
        type: 'log',
        payload: { message },
        timestamp: new Date().toISOString()
      });
    }
  }

  /**
   * Connect to WebSocket for real-time updates
   */
  private connectWebSocket(runId: string) {
    if (this.socket$) {
      this.socket$.complete();
    }

    this.socket$ = webSocket<ExecutionMessage>({
      url: `${this.WS_URL}/execution/${runId}`,
      openObserver: {
        next: () => {
          console.log('WebSocket connected for run:', runId);
          this._isConnected.set(true);
        }
      },
      closeObserver: {
        next: () => {
          console.log('WebSocket disconnected');
          this._isConnected.set(false);
        }
      }
    });

    this.socket$.pipe(
      retry({ delay: 3000, count: 3 }),
      catchError(error => {
        console.error('WebSocket error:', error);
        this._isConnected.set(false);
        return of();
      })
    ).subscribe({
      next: (message) => this.handleMessage(message),
      error: (err) => console.error('WebSocket subscription error:', err)
    });
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(message: ExecutionMessage) {
    this.messagesSubject.next(message);

    const currentState = this._currentRun();
    if (!currentState) return;

    switch (message.type) {
      case 'status':
        this._currentRun.set({
          ...currentState,
          status: message.payload.status,
          currentStep: message.payload.step
        });
        break;

      case 'log':
        this._currentRun.set({
          ...currentState,
          logs: [...currentState.logs, message.payload.message]
        });
        break;

      case 'progress':
        this._currentRun.set({
          ...currentState,
          progress: message.payload.progress
        });
        break;

      case 'complete':
        this._currentRun.set({
          ...currentState,
          status: ExecutionStatus.COMPLETED,
          progress: 100,
          endTime: message.timestamp
        });
        this.disconnect();
        break;

      case 'error':
        this._currentRun.set({
          ...currentState,
          status: ExecutionStatus.FAILED,
          logs: [...currentState.logs, `ERROR: ${message.payload.error}`]
        });
        this.disconnect();
        break;

      case 'telemetry':
        this._currentRun.set({
          ...currentState,
          telemetry: {
            temperature: message.payload.temperature,
            absorbance: message.payload.absorbance
          }
        });
        break;

      case 'well_state_update':
        // Compressed bitmask format for efficient well/tip state sync
        this._currentRun.set({
          ...currentState,
          wellState: message.payload
        });
        break;
    }
  }

  /**
   * Stop the current run
   */
  stopRun(): Observable<void> {
    const runId = this._currentRun()?.runId;
    if (!runId) return of(void 0);

    return this.http.post<void>(`${this.API_URL}/protocols/runs/${runId}/cancel`, {}).pipe(
      tap(() => {
        const current = this._currentRun();
        if (current) {
          this._currentRun.set({
            ...current,
            status: ExecutionStatus.CANCELLED
          });
        }
        this.disconnect();
      })
    );
  }

  /**
   * Disconnect WebSocket connection
   */
  disconnect() {
    if (this.socket$) {
      this.socket$.complete();
      this.socket$ = null;
    }
    this._isConnected.set(false);
  }

  /**
   * Clear the current run state
   */
  clearRun() {
    this._currentRun.set(null);
    this.disconnect();
  }
}
