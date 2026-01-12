/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_get_multi_api_v1_resources__get } from '../models/Body_get_multi_api_v1_resources__get';
import type { ResourceRead } from '../models/ResourceRead';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ResourcesService {
    /**
     * Create
     * @returns ResourceRead Successful Response
     * @throws ApiError
     */
    public static createApiV1ResourcesPost(): CancelablePromise<ResourceRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/resources/',
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
     * @returns ResourceRead Successful Response
     * @throws ApiError
     */
    public static getMultiApiV1ResourcesGet(
        limit: number = 100,
        offset?: number,
        sortBy?: (string | null),
        dateRangeStart?: (string | null),
        dateRangeEnd?: (string | null),
        protocolRunAccessionId?: (string | null),
        machineAccessionId?: (string | null),
        resourceAccessionId?: (string | null),
        parentAccessionId?: (string | null),
        requestBody?: Body_get_multi_api_v1_resources__get,
    ): CancelablePromise<Array<ResourceRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/resources/',
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
     * @returns ResourceRead Successful Response
     * @throws ApiError
     */
    public static getApiV1ResourcesAccessionIdGet(
        accessionId: string,
    ): CancelablePromise<ResourceRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/resources/{accession_id}',
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
     * @returns ResourceRead Successful Response
     * @throws ApiError
     */
    public static updateApiV1ResourcesAccessionIdPut(
        accessionId: string,
    ): CancelablePromise<ResourceRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/resources/{accession_id}',
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
    public static deleteApiV1ResourcesAccessionIdDelete(
        accessionId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/resources/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
