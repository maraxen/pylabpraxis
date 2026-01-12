/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class StateResolutionService {
    /**
     * Get Uncertain States
     * Get uncertain states for a failed/paused run.
     *
     * Returns the list of state changes that are uncertain due to a failed
     * operation. This is used to build a state resolution UI.
     * @param scheduleEntryAccessionId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getUncertainStatesApiV1SchedulerScheduleEntryAccessionIdUncertainStateGet(
        scheduleEntryAccessionId: string,
    ): CancelablePromise<Array<any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/scheduler/{schedule_entry_accession_id}/uncertain-state',
            path: {
                'schedule_entry_accession_id': scheduleEntryAccessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Resolve State
     * Submit a state resolution for a failed operation.
     *
     * The user provides their determination of what actually happened during the
     * failed operation. This is logged for audit purposes and the simulation
     * state is updated accordingly.
     * @param scheduleEntryAccessionId
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static resolveStateApiV1SchedulerScheduleEntryAccessionIdResolveStatePost(
        scheduleEntryAccessionId: string,
        requestBody: Record<string, any>,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/scheduler/{schedule_entry_accession_id}/resolve-state',
            path: {
                'schedule_entry_accession_id': scheduleEntryAccessionId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Resume Run
     * Resume a paused/failed run after state resolution.
     *
     * This transitions the run back to EXECUTING status so that it can continue.
     * Must be called after resolve_state to ensure state is correct.
     * @param scheduleEntryAccessionId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static resumeRunApiV1SchedulerScheduleEntryAccessionIdResumePost(
        scheduleEntryAccessionId: string,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/scheduler/{schedule_entry_accession_id}/resume',
            path: {
                'schedule_entry_accession_id': scheduleEntryAccessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Abort Run
     * Abort a run after state resolution.
     *
     * This cancels the run entirely. Use when the user determines the run
     * cannot be safely continued.
     * @param scheduleEntryAccessionId
     * @param reason Reason for aborting the run
     * @returns any Successful Response
     * @throws ApiError
     */
    public static abortRunApiV1SchedulerScheduleEntryAccessionIdAbortPost(
        scheduleEntryAccessionId: string,
        reason?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/scheduler/{schedule_entry_accession_id}/abort',
            path: {
                'schedule_entry_accession_id': scheduleEntryAccessionId,
            },
            query: {
                'reason': reason,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
