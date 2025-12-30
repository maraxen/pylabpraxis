import { Observable } from 'rxjs';

export interface ReplOutput {
    type: 'stdout' | 'stderr' | 'result' | 'error';
    content: string;
}

export interface ReplRuntime {
    /**
     * Connect to the runtime environment (WebSocket or Web Worker).
     */
    connect(): Observable<void>;

    /**
     * Disconnect from the runtime.
     */
    disconnect(): void;

    /**
     * Execute code in the REPL.
     * Returns an observable that emits stdout, stderr, and the final result.
     */
    execute(code: string): Observable<ReplOutput>;

    /**
     * Interrupt the current execution.
     */
    interrupt(): void;

    /**
     * Get tab completions for the code at the cursor position.
     */
    getCompletions(code: string, cursor: number): Promise<string[]>;
}
