/**
 * Service for fetching simulation results and state history.
 * Supports both backend API mode and browser mode via SqliteService.
 */

import { Injectable, inject } from '@angular/core';
import { Observable, of } from 'rxjs';
import { map, catchError, switchMap } from 'rxjs/operators';

import { ModeService } from '@core/services/mode.service';
import { SqliteService } from '@core/services/sqlite.service';
import {
    InferredRequirement,
    FailureMode,
    SimulationResult,
    StateHistory,
    OperationStateSnapshot,
    StateSnapshot,
} from '@core/models/simulation.models';

import { ProtocolDefinitionsService } from '../api-generated/services/ProtocolDefinitionsService';
import { ApiWrapperService } from './api-wrapper.service';

@Injectable({ providedIn: 'root' })
export class SimulationResultsService {
    private readonly apiWrapper = inject(ApiWrapperService);
    private readonly modeService = inject(ModeService);
    private readonly sqliteService = inject(SqliteService);

    /**
     * Get inferred requirements for a protocol.
     * @param protocolId Protocol accession ID
     */
    getInferredRequirements(protocolId: string): Observable<InferredRequirement[]> {
        if (this.modeService.isBrowserMode()) {
            return this.getRequirementsFromBrowserMode(protocolId);
        }

        return this.apiWrapper.wrap(ProtocolDefinitionsService.getApiV1ProtocolsDefinitionsAccessionIdGet(protocolId)).pipe(
            map(response => ((response as any).inferred_requirements_json as InferredRequirement[]) || []),
            catchError(err => {
                console.error('[SimulationResults] Error fetching requirements:', err);
                return of([]);
            })
        );
    }

    /**
     * Get failure modes for a protocol.
     * @param protocolId Protocol accession ID
     */
    getFailureModes(protocolId: string): Observable<FailureMode[]> {
        if (this.modeService.isBrowserMode()) {
            return this.getFailureModesFromBrowserMode(protocolId);
        }

        return this.apiWrapper.wrap(ProtocolDefinitionsService.getApiV1ProtocolsDefinitionsAccessionIdGet(protocolId)).pipe(
            map(response => ((response as any).failure_modes_json as FailureMode[]) || []),
            catchError(err => {
                console.error('[SimulationResults] Error fetching failure modes:', err);
                return of([]);
            })
        );
    }

    /**
     * Get the full simulation result for a protocol.
     * @param protocolId Protocol accession ID
     */
    getSimulationResult(protocolId: string): Observable<SimulationResult | null> {
        if (this.modeService.isBrowserMode()) {
            return this.getSimulationResultFromBrowserMode(protocolId);
        }

        return this.apiWrapper.wrap(ProtocolDefinitionsService.getApiV1ProtocolsDefinitionsAccessionIdGet(protocolId)).pipe(
            map(response => ((response as any).simulation_result_json as unknown as SimulationResult) || null),
            catchError(err => {
                console.error('[SimulationResults] Error fetching simulation result:', err);
                return of(null);
            })
        );
    }

    /**
     * Get state history for a run (for time travel debugging).
     * @param runId Run accession ID
     */
    getStateHistory(runId: string): Observable<StateHistory | null> {
        if (this.modeService.isBrowserMode()) {
            return this.getStateHistoryFromBrowserMode(runId);
        }

        // TODO: Implement state-history endpoint in backend/OpenAPI
        console.warn('[SimulationResults] getStateHistory not yet implemented in API mode');
        return of(null);
    }

    /**
     * Check if a protocol has simulation data available.
     * @param protocolId Protocol accession ID
     */
    hasSimulationData(protocolId: string): Observable<boolean> {
        return this.getSimulationResult(protocolId).pipe(
            map(result => result !== null)
        );
    }

    // =========================================================================
    // Browser Mode Implementations
    // =========================================================================

    private getRequirementsFromBrowserMode(protocolId: string): Observable<InferredRequirement[]> {
        return this.sqliteService.isReady$.pipe(
            switchMap(isReady => {
                if (!isReady) return of([]);
                return this.sqliteService.getProtocolSimulationData(protocolId).pipe(
                    map(data => (data as any)?.inferred_requirements_json || [])
                );
            }),
            catchError(() => of([]))
        );
    }

    private getFailureModesFromBrowserMode(protocolId: string): Observable<FailureMode[]> {
        return this.sqliteService.isReady$.pipe(
            switchMap(isReady => {
                if (!isReady) return of([]);
                return this.sqliteService.getProtocolSimulationData(protocolId).pipe(
                    map(data => (data as any)?.failure_modes_json || [])
                );
            }),
            catchError(() => of([]))
        );
    }

    private getSimulationResultFromBrowserMode(protocolId: string): Observable<SimulationResult | null> {
        return this.sqliteService.isReady$.pipe(
            switchMap(isReady => {
                if (!isReady) return of(null);
                return this.sqliteService.getProtocolSimulationData(protocolId).pipe(
                    map(data => (data as any)?.simulation_result_json || null)
                );
            }),
            catchError(() => of(null))
        );
    }

    private getStateHistoryFromBrowserMode(runId: string): Observable<StateHistory | null> {
        return this.sqliteService.isReady$.pipe(
            switchMap(isReady => {
                if (!isReady) return of(null);
                return this.sqliteService.getRunStateHistory(runId);
            }),
            catchError(() => of(null))
        );
    }

    // =========================================================================
    // Utility Methods
    // =========================================================================

    /**
     * Create a mock state history for browser mode/testing purposes.
     */
    createMockStateHistory(runId: string, operationCount: number = 10): StateHistory {
        const operations: OperationStateSnapshot[] = [];
        let tipsLoaded = false;
        let tipsCount = 0;
        const wellVolumes: Record<string, number> = { A1: 500, A2: 500, A3: 500 };

        const methodSequence = [
            { method: 'pick_up_tips', resource: 'tip_rack' },
            { method: 'aspirate', resource: 'source_plate' },
            { method: 'dispense', resource: 'dest_plate' },
            { method: 'aspirate', resource: 'source_plate' },
            { method: 'dispense', resource: 'dest_plate' },
            { method: 'drop_tips', resource: 'tip_rack' },
        ];

        for (let i = 0; i < operationCount && i < methodSequence.length; i++) {
            const { method, resource } = methodSequence[i];

            const stateBefore: StateSnapshot = {
                tips: { tips_loaded: tipsLoaded, tips_count: tipsCount },
                liquids: { source_plate: { ...wellVolumes } },
                on_deck: ['tip_rack', 'source_plate', 'dest_plate'],
            };

            // Update state based on operation
            if (method === 'pick_up_tips') {
                tipsLoaded = true;
                tipsCount = 8;
            } else if (method === 'drop_tips') {
                tipsLoaded = false;
                tipsCount = 0;
            } else if (method === 'aspirate') {
                wellVolumes['A1'] -= 50;
            } else if (method === 'dispense') {
                // Volume added to dest (not tracked in this simple mock)
            }

            const stateAfter: StateSnapshot = {
                tips: { tips_loaded: tipsLoaded, tips_count: tipsCount },
                liquids: { source_plate: { ...wellVolumes } },
                on_deck: ['tip_rack', 'source_plate', 'dest_plate'],
            };

            operations.push({
                operation_index: i,
                operation_id: `op_${i}`,
                method_name: method,
                resource,
                state_before: stateBefore,
                state_after: stateAfter,
                timestamp: new Date(Date.now() + i * 1000).toISOString(),
                duration_ms: 500 + Math.random() * 1000,
                status: 'completed',
            });
        }

        return {
            run_id: runId,
            protocol_name: 'Mock Protocol',
            operations,
            final_state: operations.length > 0
                ? operations[operations.length - 1].state_after
                : { tips: { tips_loaded: false, tips_count: 0 }, liquids: {}, on_deck: [] },
            total_duration_ms: operations.reduce((sum, op) => sum + (op.duration_ms || 0), 0),
        };
    }
}
