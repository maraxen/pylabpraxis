
import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { Observable, Subject, BehaviorSubject, of } from 'rxjs';
import { catchError, tap, retry, delay } from 'rxjs/operators';
import { ExecutionState, ExecutionMessage, ExecutionStatus } from '../models/execution.models';
import { environment } from '@env/environment';

@Injectable({
  providedIn: 'root'
})
export class ExecutionService {
  private http = inject(HttpClient);
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
   * Start a new protocol run
   */
  startRun(protocolId: string, runName: string, parameters?: Record<string, any>): Observable<{ run_id: string }> {
    return this.http.post<{ run_id: string }>(`${this.API_URL}/runs`, {
      protocol_definition_accession_id: protocolId,
      name: runName,
      parameters
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
   * Connect to WebSocket for real-time updates
   */
  private connectWebSocket(runId: string) {
    if (this.socket$) {
      this.socket$.complete();
    }

    this.socket$ = webSocket<ExecutionMessage>({
      url: `${this.WS_URL}/${runId}`,
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
    }
  }

  /**
   * Stop the current run
   */
  stopRun(): Observable<void> {
    const runId = this._currentRun()?.runId;
    if (!runId) return of(void 0);

    return this.http.post<void>(`${this.API_URL}/runs/${runId}/stop`, {}).pipe(
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
