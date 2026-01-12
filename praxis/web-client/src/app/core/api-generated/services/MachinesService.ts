/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_get_multi_api_v1_machines__get } from '../models/Body_get_multi_api_v1_machines__get';
import type { Body_get_multi_api_v1_machines_definitions_get } from '../models/Body_get_multi_api_v1_machines_definitions_get';
import type { MachineDefinitionRead } from '../models/MachineDefinitionRead';
import type { MachineRead } from '../models/MachineRead';
import type { MachineStatusEnum } from '../models/MachineStatusEnum';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class MachinesService {
    /**
     * Get facet values with counts for machine filtering
     * Return unique values and counts for filterable machine definition fields.
     *
     * Returns facets for: machine_category, manufacturer.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getMachineDefinitionFacetsApiV1MachinesDefinitionsFacetsGet(): CancelablePromise<Record<string, Array<Record<string, any>>>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/machines/definitions/facets',
        });
    }
    /**
     * Create
     * @returns MachineDefinitionRead Successful Response
     * @throws ApiError
     */
    public static createApiV1MachinesDefinitionsPost(): CancelablePromise<MachineDefinitionRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/machines/definitions',
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
     * @returns MachineDefinitionRead Successful Response
     * @throws ApiError
     */
    public static getMultiApiV1MachinesDefinitionsGet(
        limit: number = 100,
        offset?: number,
        sortBy?: (string | null),
        dateRangeStart?: (string | null),
        dateRangeEnd?: (string | null),
        protocolRunAccessionId?: (string | null),
        machineAccessionId?: (string | null),
        resourceAccessionId?: (string | null),
        parentAccessionId?: (string | null),
        requestBody?: Body_get_multi_api_v1_machines_definitions_get,
    ): CancelablePromise<Array<MachineDefinitionRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/machines/definitions',
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
     * @returns MachineDefinitionRead Successful Response
     * @throws ApiError
     */
    public static getApiV1MachinesDefinitionsAccessionIdGet(
        accessionId: string,
    ): CancelablePromise<MachineDefinitionRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/machines/definitions/{accession_id}',
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
     * @returns MachineDefinitionRead Successful Response
     * @throws ApiError
     */
    public static updateApiV1MachinesDefinitionsAccessionIdPut(
        accessionId: string,
    ): CancelablePromise<MachineDefinitionRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/machines/definitions/{accession_id}',
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
    public static deleteApiV1MachinesDefinitionsAccessionIdDelete(
        accessionId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/machines/definitions/{accession_id}',
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
     * @returns MachineRead Successful Response
     * @throws ApiError
     */
    public static createApiV1MachinesPost(): CancelablePromise<MachineRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/machines/',
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
     * @returns MachineRead Successful Response
     * @throws ApiError
     */
    public static getMultiApiV1MachinesGet(
        limit: number = 100,
        offset?: number,
        sortBy?: (string | null),
        dateRangeStart?: (string | null),
        dateRangeEnd?: (string | null),
        protocolRunAccessionId?: (string | null),
        machineAccessionId?: (string | null),
        resourceAccessionId?: (string | null),
        parentAccessionId?: (string | null),
        requestBody?: Body_get_multi_api_v1_machines__get,
    ): CancelablePromise<Array<MachineRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/machines/',
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
     * @returns MachineRead Successful Response
     * @throws ApiError
     */
    public static getApiV1MachinesAccessionIdGet(
        accessionId: string,
    ): CancelablePromise<MachineRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/machines/{accession_id}',
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
     * @returns MachineRead Successful Response
     * @throws ApiError
     */
    public static updateApiV1MachinesAccessionIdPut(
        accessionId: string,
    ): CancelablePromise<MachineRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/machines/{accession_id}',
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
    public static deleteApiV1MachinesAccessionIdDelete(
        accessionId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/machines/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Machine Status
     * Update the status of a machine.
     * @param accession
     * @param newStatus
     * @param statusDetails
     * @param currentProtocolRunAccessionId
     * @returns MachineRead Successful Response
     * @throws ApiError
     */
    public static updateMachineStatusApiV1MachinesAccessionStatusPatch(
        accession: string,
        newStatus: MachineStatusEnum,
        statusDetails?: (string | null),
        currentProtocolRunAccessionId?: (string | null),
    ): CancelablePromise<MachineRead> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/machines/{accession}/status',
            path: {
                'accession': accession,
            },
            query: {
                'new_status': newStatus,
                'status_details': statusDetails,
                'current_protocol_run_accession_id': currentProtocolRunAccessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
