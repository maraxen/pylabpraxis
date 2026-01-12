/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_get_multi_api_v1_resources_definitions_get } from '../models/Body_get_multi_api_v1_resources_definitions_get';
import type { ResourceDefinitionCreate } from '../models/ResourceDefinitionCreate';
import type { ResourceDefinitionRead } from '../models/ResourceDefinitionRead';
import type { ResourceDefinitionUpdate } from '../models/ResourceDefinitionUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ResourceDefinitionsService {
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
     * @param requestBody
     * @returns ResourceDefinitionRead Successful Response
     * @throws ApiError
     */
    public static createApiV1ResourcesDefinitionsPost(
        requestBody: ResourceDefinitionCreate,
    ): CancelablePromise<ResourceDefinitionRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/resources/definitions',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
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
     * @returns ResourceDefinitionRead Successful Response
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
    ): CancelablePromise<Array<ResourceDefinitionRead>> {
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
     * @returns ResourceDefinitionRead Successful Response
     * @throws ApiError
     */
    public static getApiV1ResourcesDefinitionsAccessionIdGet(
        accessionId: string,
    ): CancelablePromise<ResourceDefinitionRead> {
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
     * @param requestBody
     * @returns ResourceDefinitionRead Successful Response
     * @throws ApiError
     */
    public static updateApiV1ResourcesDefinitionsAccessionIdPut(
        accessionId: string,
        requestBody: ResourceDefinitionUpdate,
    ): CancelablePromise<ResourceDefinitionRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/resources/definitions/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            body: requestBody,
            mediaType: 'application/json',
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
}
