import { Observable } from 'rxjs';

export interface ReplOutput {
    type: 'stdout' | 'stderr' | 'result' | 'error' | 'well_state_update' | 'function_call_log';
    content: string;
}

/**
 * Structured completion item with metadata from Jedi.
 */
export interface CompletionItem {
    name: string;
    type: 'function' | 'class' | 'module' | 'instance' | 'statement' | 'param' | 'keyword' | string;
    description?: string;
}

/**
 * Function signature information for parameter hints.
 */
export interface SignatureInfo {
    name: string;
    params: string[];
    index: number; // Current parameter index
    docstring?: string;
}

export interface ReplacementVariable {
    name: string;
    type: string;
    value: string;
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
     * Restart the runtime (reload kernel/worker).
     */
    restart?(): Observable<void>;

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
     * Returns structured completion items with type metadata.
     */
    getCompletions(code: string, cursor: number): Promise<CompletionItem[]>;

    /**
     * Get function signature help for the code at the cursor position.
     */
    getSignatures?(code: string, cursor: number): Promise<SignatureInfo[]>;

    /**
     * Observable of currently defined variables in the REPL session.
     */
    variables$?: Observable<ReplacementVariable[]>;
}
