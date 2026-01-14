import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { CancelablePromise } from '../api-generated/core/CancelablePromise';
import { ApiError } from '../api-generated/core/ApiError';

@Injectable({
    providedIn: 'root'
})
export class ApiWrapperService {
    /**
     * Wraps a CancelablePromise from the generated API client into an RxJS Observable.
     * Handles cancellation when the Observable is unsubscribed.
     * 
     * NOTE: Browser-mode interception happens in the custom request handler
     * (see api-generated/core/browser-request.ts), not here.
     */
    wrap<T>(promise: CancelablePromise<T>): Observable<T> {
        return new Observable<T>(observer => {
            promise
                .then(result => {
                    observer.next(result);
                    observer.complete();
                })
                .catch(error => {
                    observer.error(this.normalizeError(error));
                });

            // Cleanup: cancel the promise if the observable is unsubscribed
            return () => {
                if (promise.cancel) {
                    promise.cancel();
                }
            };
        });
    }

    /**
     * Normalizes errors from the API client.
     */
    private normalizeError(error: unknown): unknown {
        if (error instanceof ApiError) {
            console.error(`[API-ERROR] ${error.status} ${error.statusText}:`, error.body);
            return {
                status: error.status,
                message: (error.body as Record<string, unknown>)?.['detail'] || error.message || 'API Error',
                originalError: error
            };
        }
        return error;
    }
}
