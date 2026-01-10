/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_get_multi_api_v1_resources__get } from '../models/Body_get_multi_api_v1_resources__get';
import type { Body_get_multi_api_v1_resources_definitions_get } from '../models/Body_get_multi_api_v1_resources_definitions_get';
import type { ResourceDefinitionResponse } from '../models/ResourceDefinitionResponse';
import type { ResourceResponse } from '../models/ResourceResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AssetsService {
    /**
     * Get facet values with counts for filtering
     * Return unique values and counts for filterable resource definition fields.
     *
     * Used for dynamically generating filter chips in the frontend.
     * Returns facets for: plr_category, vendor, num_items, plate_type, well_volume_ul, tip_volume_ul.
     *
     * Supports dynamic filtering: passing a filter (e.g. plr_category='plate') will update
     * the counts for other facets (e.g. only showing vendors that make plates).
     * @param plrCategory
     * @param vendor
     * @param numItems
     * @param plateType
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getResourceDefinitionFacetsApiV1ResourcesDefinitionsFacetsGet(
        plrCategory?: (string | null),
        vendor?: (string | null),
        numItems?: (number | null),
        plateType?: (string | null),
    ): CancelablePromise<Record<string, Array<Record<string, any>>>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/resources/definitions/facets',
            query: {
                'plr_category': plrCategory,
                'vendor': vendor,
                'num_items': numItems,
                'plate_type': plateType,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create
     * @returns ResourceDefinitionResponse Successful Response
     * @throws ApiError
     */
    public static createApiV1ResourcesDefinitionsPost(): CancelablePromise<ResourceDefinitionResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/resources/definitions',
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
     * @returns ResourceDefinitionResponse Successful Response
     * @throws ApiError
     */
    public static getMultiApiV1ResourcesDefinitionsGet(
        limit: number = 100,
        offset?: number,
        sortBy?: (string | null),
        dateRangeStart?: (string | null),
        dateRangeEnd?: (string | null),
        protocolRunAccessionId?: (string | null),
        machineAccessionId?: (string | null),
        resourceAccessionId?: (string | null),
        parentAccessionId?: (string | null),
        requestBody?: Body_get_multi_api_v1_resources_definitions_get,
    ): CancelablePromise<Array<ResourceDefinitionResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/resources/definitions',
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
     * @returns ResourceDefinitionResponse Successful Response
     * @throws ApiError
     */
    public static getApiV1ResourcesDefinitionsAccessionIdGet(
        accessionId: string,
    ): CancelablePromise<ResourceDefinitionResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/resources/definitions/{accession_id}',
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
     * @returns ResourceDefinitionResponse Successful Response
     * @throws ApiError
     */
    public static updateApiV1ResourcesDefinitionsAccessionIdPut(
        accessionId: string,
    ): CancelablePromise<ResourceDefinitionResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/resources/definitions/{accession_id}',
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
    public static deleteApiV1ResourcesDefinitionsAccessionIdDelete(
        accessionId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/resources/definitions/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create
     * @returns ResourceResponse Successful Response
     * @throws ApiError
     */
    public static createApiV1ResourcesPost(): CancelablePromise<ResourceResponse> {
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
     * @returns ResourceResponse Successful Response
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
    ): CancelablePromise<Array<ResourceResponse>> {
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
     * @returns ResourceResponse Successful Response
     * @throws ApiError
     */
    public static getApiV1ResourcesAccessionIdGet(
        accessionId: string,
    ): CancelablePromise<ResourceResponse> {
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
     * @returns ResourceResponse Successful Response
     * @throws ApiError
     */
    public static updateApiV1ResourcesAccessionIdPut(
        accessionId: string,
    ): CancelablePromise<ResourceResponse> {
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
