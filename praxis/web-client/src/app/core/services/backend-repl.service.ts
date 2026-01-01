import { Injectable, inject } from '@angular/core';
import { Observable, Subject, map, tap } from 'rxjs';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { environment } from '@env/environment';
import { ReplOutput, ReplRuntime, CompletionItem, SignatureInfo } from './repl-runtime.interface';

@Injectable({
    providedIn: 'root'
})
export class BackendReplService implements ReplRuntime {
    private readonly WS_URL = `${environment.wsUrl}/repl/session`;
    private socket$: WebSocketSubject<any> | null = null;
    private connectionSubject = new Subject<void>();

    connect(): Observable<void> {
        if (this.socket$) {
            return this.connectionSubject.asObservable();
        }

        this.socket$ = webSocket({
            url: this.WS_URL,
            openObserver: {
                next: () => {
                    console.log('REPL WebSocket connected');
                    this.connectionSubject.next();
                }
            }
        });

        return this.connectionSubject.asObservable();
    }

    disconnect(): void {
        if (this.socket$) {
            this.socket$.complete();
            this.socket$ = null;
        }
    }

    execute(code: string): Observable<ReplOutput> {
        if (!this.socket$) {
            throw new Error('REPL not connected');
        }

        const commandId = crypto.randomUUID();
        this.socket$.next({
            type: 'EXEC',
            id: commandId,
            payload: { code }
        });

        return this.socket$.asObservable().pipe(
            // Filter by ID if we want multiplexing, but standard REPL is serial
            // We check if the message corresponds to our execution
            map(msg => {
                if (msg.id === commandId) {
                    if (msg.type === 'RESULT') {
                        return {
                            type: 'result' as const,
                            content: msg.payload.output,
                            more: msg.payload.more // backend push() returns more
                        };
                    } else if (msg.type === 'ERROR') {
                        return {
                            type: 'error' as const,
                            content: msg.payload.error
                        };
                    }
                }
                return null;
            }),
            // Filter out nulls (messages for other requests if any)
            map(val => val as any as ReplOutput)
        );
    }

    interrupt(): void {
        // Backend console.push is synchronous for now, interrupt is hard without signals
        // but we can send a message if we had an async kernel
        this.socket$?.next({ type: 'INTERRUPT' });
    }

    async getCompletions(code: string, _cursor: number): Promise<CompletionItem[]> {
        if (!this.socket$) return [];

        const id = crypto.randomUUID();
        return new Promise((resolve) => {
            const subscription = this.socket$?.asObservable().subscribe(msg => {
                if (msg.id === id && msg.type === 'COMPLETION_RESULT') {
                    subscription?.unsubscribe();
                    // Backend may return either string[] or CompletionItem[]
                    const matches = msg.payload.matches || [];
                    const items = matches.map((m: string | CompletionItem) =>
                        typeof m === 'string' ? { name: m, type: 'unknown' } : m
                    );
                    resolve(items);
                }
            });

            this.socket$?.next({
                type: 'COMPLETION',
                id,
                payload: { code }
            });

            // Timeout after 2 seconds
            setTimeout(() => {
                subscription?.unsubscribe();
                resolve([]);
            }, 2000);
        });
    }

    async getSignatures(code: string, _cursor: number): Promise<SignatureInfo[]> {
        if (!this.socket$) return [];

        const id = crypto.randomUUID();
        return new Promise((resolve) => {
            const subscription = this.socket$?.asObservable().subscribe(msg => {
                if (msg.id === id && msg.type === 'SIGNATURE_RESULT') {
                    subscription?.unsubscribe();
                    resolve(msg.payload.signatures || []);
                }
            });

            this.socket$?.next({
                type: 'SIGNATURES',
                id,
                payload: { code }
            });

            // Timeout after 2 seconds
            setTimeout(() => {
                subscription?.unsubscribe();
                resolve([]);
            }, 2000);
        });
    }
}
