import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, catchError, switchMap } from 'rxjs/operators';
import { environment } from '@env/environment';
import { ModeService } from '@core/services/mode.service';
import { SqliteService } from '@core/services/sqlite.service';
import {
    RunSummary,
    RunDetail,
    RunHistoryParams,
    RunStatus,
} from '../models/monitor.models';

/**
 * Service for fetching protocol run history and details.
 */
@Injectable({
    providedIn: 'root',
})
export class RunHistoryService {
    private readonly http = inject(HttpClient);
    private readonly modeService = inject(ModeService);
    private readonly sqliteService = inject(SqliteService);
    private readonly API_URL = environment.apiUrl;

    /**
     * Get paginated run history.
     */
    getRunHistory(params?: RunHistoryParams): Observable<RunSummary[]> {
        // Browser mode: use SqliteService with client-side filtering
        if (this.modeService.isBrowserMode()) {
            return this.sqliteService.getProtocolRuns().pipe(
                map(runs => {
                    let filtered = runs as RunSummary[];

                    // Apply status filter
                    if (params?.status && params.status.length > 0) {
                        const statusList = Array.isArray(params.status) ? params.status : [params.status];
                        filtered = filtered.filter(r => statusList.includes(r.status as RunStatus));
                    }

                    // Apply protocol filter
                    if (params?.protocol_id) {
                        const protocolIds = Array.isArray(params.protocol_id) ? params.protocol_id : [params.protocol_id];
                        filtered = filtered.filter(r => protocolIds.includes(r.protocol_accession_id || ''));
                    }

                    // Apply sorting
                    const sortBy = params?.sort_by || 'created_at';
                    const sortOrder = params?.sort_order || 'desc';
                    filtered.sort((a, b) => {
                        const aVal = (a as any)[sortBy] || '';
                        const bVal = (b as any)[sortBy] || '';
                        const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
                        return sortOrder === 'desc' ? -comparison : comparison;
                    });

                    // Apply pagination
                    const offset = params?.offset || 0;
                    const limit = params?.limit || 50;
                    return filtered.slice(offset, offset + limit);
                }),
                catchError(err => {
                    console.error('[RunHistoryService] Browser mode error:', err);
                    return of([]);
                })
            );
        }

        // Backend mode: use HTTP API
        let httpParams = new HttpParams();

        if (params?.limit) {
            httpParams = httpParams.set('limit', params.limit.toString());
        }
        if (params?.offset) {
            httpParams = httpParams.set('offset', params.offset.toString());
        }
        if (params?.status) {
            const statusStr = Array.isArray(params.status)
                ? params.status.join(',')
                : params.status;
            httpParams = httpParams.set('status', statusStr);
        }
        if (params?.protocol_id) {
            const protocolStr = Array.isArray(params.protocol_id)
                ? params.protocol_id.join(',')
                : params.protocol_id;
            httpParams = httpParams.set('protocol_id', protocolStr);
        }
        if (params?.sort_by) {
            httpParams = httpParams.set('sort_by', params.sort_by);
        }
        if (params?.sort_order) {
            httpParams = httpParams.set('sort_order', params.sort_order);
        }

        return this.http
            .get<RunSummary[]>(`${this.API_URL}/protocols/runs/records`, {
                params: httpParams,
            })
            .pipe(
                catchError((err) => {
                    console.error('[RunHistoryService] Failed to fetch run history:', err);
                    return of([]);
                })
            );
    }

    /**
     * Get active (in-progress) runs.
     * Uses the /runs/queue endpoint which returns PENDING, PREPARING, QUEUED, RUNNING statuses.
     */
    getActiveRuns(): Observable<RunSummary[]> {
        // Browser mode: filter for active statuses
        if (this.modeService.isBrowserMode()) {
            const activeStatuses: RunStatus[] = ['PENDING', 'PREPARING', 'QUEUED', 'RUNNING', 'PAUSED'];
            return this.sqliteService.getProtocolRuns().pipe(
                map(runs => (runs as RunSummary[]).filter(r => activeStatuses.includes(r.status as RunStatus))),
                catchError(err => {
                    console.error('[RunHistoryService] Browser mode getActiveRuns error:', err);
                    return of([]);
                })
            );
        }

        return this.http.get<RunSummary[]>(`${this.API_URL}/protocols/runs/queue`).pipe(
            catchError((err) => {
                console.error('[RunHistoryService] Failed to fetch active runs:', err);
                return of([]);
            })
        );
    }

    /**
     * Get detailed information for a specific run.
     */
    getRunDetail(runId: string): Observable<RunDetail | null> {
        // Browser mode: use SqliteService
        if (this.modeService.isBrowserMode()) {
            return this.sqliteService.getProtocolRun(runId).pipe(
                map(run => run as RunDetail | null),
                catchError(err => {
                    console.error('[RunHistoryService] Browser mode getRunDetail error:', err);
                    return of(null);
                })
            );
        }

        return this.http
            .get<RunDetail>(`${this.API_URL}/protocols/runs/records/${runId}`)
            .pipe(
                catchError((err) => {
                    console.error('[RunHistoryService] Failed to fetch run detail:', err);
                    return of(null);
                })
            );
    }

    /**
     * Returns color class based on run status.
     */
    getStatusColor(status: RunStatus): string {
        switch (status) {
            case 'RUNNING':
                return 'text-green-500';
            case 'QUEUED':
            case 'PREPARING':
                return 'text-amber-500';
            case 'PENDING':
                return 'text-blue-500';
            case 'COMPLETED':
                return 'text-gray-500';
            case 'FAILED':
                return 'text-red-500';
            case 'CANCELLED':
                return 'text-gray-400';
            case 'PAUSED':
                return 'text-yellow-500';
            default:
                return 'text-gray-500';
        }
    }

    /**
     * Returns icon name based on run status.
     */
    getStatusIcon(status: RunStatus): string {
        switch (status) {
            case 'RUNNING':
                return 'play_circle';
            case 'QUEUED':
                return 'schedule';
            case 'PREPARING':
                return 'hourglass_empty';
            case 'PENDING':
                return 'pending';
            case 'COMPLETED':
                return 'check_circle';
            case 'FAILED':
                return 'error';
            case 'CANCELLED':
                return 'cancel';
            case 'PAUSED':
                return 'pause_circle';
            default:
                return 'help';
        }
    }

    /**
     * Format duration in milliseconds to human-readable string.
     */
    formatDuration(durationMs?: number): string {
        if (!durationMs) return '-';
        const seconds = Math.floor(durationMs / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);

        if (hours > 0) {
            return `${hours}h ${minutes % 60}m`;
        } else if (minutes > 0) {
            return `${minutes}m ${seconds % 60}s`;
        } else {
            return `${seconds}s`;
        }
    }
}
