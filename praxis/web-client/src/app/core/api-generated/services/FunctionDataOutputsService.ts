/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_get_multi_api_v1_data_outputs_outputs_get } from '../models/Body_get_multi_api_v1_data_outputs_outputs_get';
import type { FunctionDataOutputRead } from '../models/FunctionDataOutputRead';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class FunctionDataOutputsService {
    /**
     * Create
     * @returns FunctionDataOutputRead Successful Response
     * @throws ApiError
     */
    public static createApiV1DataOutputsOutputsPost(): CancelablePromise<FunctionDataOutputRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/data-outputs/outputs',
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
     * @returns FunctionDataOutputRead Successful Response
     * @throws ApiError
     */
    public static getMultiApiV1DataOutputsOutputsGet(
        limit: number = 100,
        offset?: number,
        sortBy?: (string | null),
        dateRangeStart?: (string | null),
        dateRangeEnd?: (string | null),
        protocolRunAccessionId?: (string | null),
        machineAccessionId?: (string | null),
        resourceAccessionId?: (string | null),
        parentAccessionId?: (string | null),
        requestBody?: Body_get_multi_api_v1_data_outputs_outputs_get,
    ): CancelablePromise<Array<FunctionDataOutputRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/data-outputs/outputs',
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
     * @returns FunctionDataOutputRead Successful Response
     * @throws ApiError
     */
    public static getApiV1DataOutputsOutputsAccessionIdGet(
        accessionId: string,
    ): CancelablePromise<FunctionDataOutputRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/data-outputs/outputs/{accession_id}',
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
     * @returns FunctionDataOutputRead Successful Response
     * @throws ApiError
     */
    public static updateApiV1DataOutputsOutputsAccessionIdPut(
        accessionId: string,
    ): CancelablePromise<FunctionDataOutputRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/data-outputs/outputs/{accession_id}',
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
    public static deleteApiV1DataOutputsOutputsAccessionIdDelete(
        accessionId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/data-outputs/outputs/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
