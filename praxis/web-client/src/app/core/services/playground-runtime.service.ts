import { Injectable, inject } from '@angular/core';
import { Observable, Subject, map } from 'rxjs';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { environment } from '@env/environment';
import { ReplOutput, ReplRuntime, CompletionItem, SignatureInfo, ReplacementVariable } from './repl-runtime.interface';
import { BehaviorSubject, filter } from 'rxjs';
import { ReplService } from './api-generated/services/ReplService';
import { ApiWrapperService } from './api-wrapper.service';

@Injectable({
    providedIn: 'root'
})
export class PlaygroundRuntimeService implements ReplRuntime {
    private readonly WS_URL = `${environment.wsUrl}/repl/session`;
    private readonly apiWrapper = inject(ApiWrapperService);
    private socket$: WebSocketSubject<unknown> | null = null;
    private connectionSubject = new Subject<void>();
    private variablesSubject = new BehaviorSubject<ReplacementVariable[]>([]);

    variables$ = this.variablesSubject.asObservable();


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

        // Listen for global updates (like variables) on the main socket observable
        // Note: Creating a subscription here might consume messages intended for execute()
        // if execute() uses multiplexing. However, webSocket subject multicasts.
        this.socket$.subscribe(msg => {
            const m = msg as any;
            if (m.type === 'VARS_UPDATE') {
                this.variablesSubject.next(m.payload.variables);
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
            filter(msg => (msg as any).id === commandId),
            map(msg => {
                const m = msg as any;
                if (m.type === 'RESULT') {
                    return {
                        type: 'result' as const,
                        content: m.payload.output,
                        more: m.payload.more // backend push() returns more
                    };
                } else if (m.type === 'ERROR') {
                    return {
                        type: 'error' as const,
                        content: m.payload.error
                    };
                }
                return { type: 'error' as const, content: 'Unknown response' };
            })
        );
    }

    restart(): Observable<void> {
        if (!this.socket$) return new Observable();

        const id = crypto.randomUUID();
        this.socket$.next({ type: 'RESTART', id });

        return this.socket$.asObservable().pipe(
            filter(msg => msg.id === id),
            map(() => void 0)
        );
    }

    saveSession(history: string[]) {
        return this.apiWrapper.wrap(ReplService.saveSessionApiV1ReplSaveSessionPost({ history }));
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
