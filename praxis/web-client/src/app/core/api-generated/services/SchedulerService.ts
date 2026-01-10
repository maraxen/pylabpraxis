/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetReservationListResponse } from '../models/AssetReservationListResponse';
import type { Body_get_multi_api_v1_scheduler_entries_get } from '../models/Body_get_multi_api_v1_scheduler_entries_get';
import type { ReleaseReservationResponse } from '../models/ReleaseReservationResponse';
import type { ScheduleEntryResponse } from '../models/ScheduleEntryResponse';
import type { ScheduleEntryUpdate } from '../models/ScheduleEntryUpdate';
import type { SchedulePriorityUpdateRequest } from '../models/SchedulePriorityUpdateRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SchedulerService {
    /**
     * Create
     * @returns ScheduleEntryResponse Successful Response
     * @throws ApiError
     */
    public static createApiV1SchedulerEntriesPost(): CancelablePromise<ScheduleEntryResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/scheduler/entries',
        });
    }
    /**
     * Get Multi
     * @param limit
     * @param offset
     * @param sortBy
     * @param dateRangeStart
     * @param dateRangeEnd
     * @param protocolRunAccessionId
     * @param machineAccessionId
     * @param resourceAccessionId
     * @param parentAccessionId
     * @param requestBody
     * @returns ScheduleEntryResponse Successful Response
     * @throws ApiError
     */
    public static getMultiApiV1SchedulerEntriesGet(
        limit: number = 100,
        offset?: number,
        sortBy?: (string | null),
        dateRangeStart?: (string | null),
        dateRangeEnd?: (string | null),
        protocolRunAccessionId?: (string | null),
        machineAccessionId?: (string | null),
        resourceAccessionId?: (string | null),
        parentAccessionId?: (string | null),
        requestBody?: Body_get_multi_api_v1_scheduler_entries_get,
    ): CancelablePromise<Array<ScheduleEntryResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/scheduler/entries',
            query: {
                'limit': limit,
                'offset': offset,
                'sort_by': sortBy,
                'date_range_start': dateRangeStart,
                'date_range_end': dateRangeEnd,
                'protocol_run_accession_id': protocolRunAccessionId,
                'machine_accession_id': machineAccessionId,
                'resource_accession_id': resourceAccessionId,
                'parent_accession_id': parentAccessionId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get
     * @param accessionId
     * @returns ScheduleEntryResponse Successful Response
     * @throws ApiError
     */
    public static getApiV1SchedulerEntriesAccessionIdGet(
        accessionId: string,
    ): CancelablePromise<ScheduleEntryResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/scheduler/entries/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update
     * @param accessionId
     * @returns ScheduleEntryResponse Successful Response
     * @throws ApiError
     */
    public static updateApiV1SchedulerEntriesAccessionIdPut(
        accessionId: string,
    ): CancelablePromise<ScheduleEntryResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/scheduler/entries/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete
     * @param accessionId
     * @returns void
     * @throws ApiError
     */
    public static deleteApiV1SchedulerEntriesAccessionIdDelete(
        accessionId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/scheduler/entries/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Status
     * Update the status of a schedule entry.
     * @param scheduleEntryAccessionId
     * @param requestBody
     * @returns ScheduleEntryResponse Successful Response
     * @throws ApiError
     */
    public static updateStatusApiV1SchedulerScheduleEntryAccessionIdStatusPut(
        scheduleEntryAccessionId: string,
        requestBody: ScheduleEntryUpdate,
    ): CancelablePromise<ScheduleEntryResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/scheduler/{schedule_entry_accession_id}/status',
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
     * Update Priority
     * Update the priority of a schedule entry.
     * @param scheduleEntryAccessionId
     * @param requestBody
     * @returns ScheduleEntryResponse Successful Response
     * @throws ApiError
     */
    public static updatePriorityApiV1SchedulerScheduleEntryAccessionIdPriorityPut(
        scheduleEntryAccessionId: string,
        requestBody: SchedulePriorityUpdateRequest,
    ): CancelablePromise<ScheduleEntryResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/scheduler/{schedule_entry_accession_id}/priority',
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
     * List Reservations
     * List all asset reservations.
     *
     * Admin endpoint for inspecting current reservation state. By default, only
     * shows active reservations (PENDING, RESERVED, ACTIVE). Set include_released=true
     * to see all reservations including released ones.
     * @param includeReleased Include released reservations in results
     * @param assetKey Filter by specific asset key (e.g., 'asset:my_plate')
     * @returns AssetReservationListResponse Successful Response
     * @throws ApiError
     */
    public static listReservationsApiV1SchedulerReservationsGet(
        includeReleased: boolean = false,
        assetKey?: (string | null),
    ): CancelablePromise<AssetReservationListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/scheduler/reservations',
            query: {
                'include_released': includeReleased,
                'asset_key': assetKey,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Release Reservation
     * Release asset reservations by asset key.
     *
     * Admin endpoint for manually clearing stuck reservations. This releases
     * all active reservations for the specified asset key.
     *
     * The asset_key format is typically "type:name", e.g., "asset:my_plate".
     *
     * Use force=true to also release ACTIVE reservations (use with caution as
     * this may interrupt running protocols).
     * @param assetKey
     * @param force Force release even for reservations in ACTIVE state
     * @returns ReleaseReservationResponse Successful Response
     * @throws ApiError
     */
    public static releaseReservationApiV1SchedulerReservationsAssetKeyDelete(
        assetKey: string,
        force: boolean = false,
    ): CancelablePromise<ReleaseReservationResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/scheduler/reservations/{asset_key}',
            path: {
                'asset_key': assetKey,
            },
            query: {
                'force': force,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
