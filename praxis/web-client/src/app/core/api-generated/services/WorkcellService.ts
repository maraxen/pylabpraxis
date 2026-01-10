/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_get_multi_api_v1_workcell__get } from '../models/Body_get_multi_api_v1_workcell__get';
import type { WorkcellResponse } from '../models/WorkcellResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class WorkcellService {
    /**
     * Create
     * @returns WorkcellResponse Successful Response
     * @throws ApiError
     */
    public static createApiV1WorkcellPost(): CancelablePromise<WorkcellResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/workcell/',
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
     * @returns WorkcellResponse Successful Response
     * @throws ApiError
     */
    public static getMultiApiV1WorkcellGet(
        limit: number = 100,
        offset?: number,
        sortBy?: (string | null),
        dateRangeStart?: (string | null),
        dateRangeEnd?: (string | null),
        protocolRunAccessionId?: (string | null),
        machineAccessionId?: (string | null),
        resourceAccessionId?: (string | null),
        parentAccessionId?: (string | null),
        requestBody?: Body_get_multi_api_v1_workcell__get,
    ): CancelablePromise<Array<WorkcellResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/workcell/',
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
     * @returns WorkcellResponse Successful Response
     * @throws ApiError
     */
    public static getApiV1WorkcellAccessionIdGet(
        accessionId: string,
    ): CancelablePromise<WorkcellResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/workcell/{accession_id}',
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
     * @returns WorkcellResponse Successful Response
     * @throws ApiError
     */
    public static updateApiV1WorkcellAccessionIdPut(
        accessionId: string,
    ): CancelablePromise<WorkcellResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/workcell/{accession_id}',
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
    public static deleteApiV1WorkcellAccessionIdDelete(
        accessionId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/workcell/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
