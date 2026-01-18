/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MachineBackendDefinitionCreate } from '../models/MachineBackendDefinitionCreate';
import type { MachineBackendDefinitionRead } from '../models/MachineBackendDefinitionRead';
import type { MachineBackendDefinitionUpdate } from '../models/MachineBackendDefinitionUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class MachineBackendsService {
    /**
     * List machine backend definitions
     * Retrieve a list of machine backend definitions.
     * @param skip
     * @param limit
     * @returns MachineBackendDefinitionRead Successful Response
     * @throws ApiError
     */
    public static listBackendDefinitionsApiV1MachineBackendsGet(
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<Array<MachineBackendDefinitionRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/machine-backends/',
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create machine backend definition
     * Create a new machine backend definition.
     * @param requestBody
     * @returns MachineBackendDefinitionRead Successful Response
     * @throws ApiError
     */
    public static createBackendDefinitionApiV1MachineBackendsPost(
        requestBody: MachineBackendDefinitionCreate,
    ): CancelablePromise<MachineBackendDefinitionRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/machine-backends/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get machine backend definition by ID
     * Retrieve a specific machine backend definition by its accession ID.
     * @param accessionId
     * @returns MachineBackendDefinitionRead Successful Response
     * @throws ApiError
     */
    public static getBackendDefinitionApiV1MachineBackendsAccessionIdGet(
        accessionId: string,
    ): CancelablePromise<MachineBackendDefinitionRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/machine-backends/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update machine backend definition
     * Update an existing machine backend definition.
     * @param accessionId
     * @param requestBody
     * @returns MachineBackendDefinitionRead Successful Response
     * @throws ApiError
     */
    public static updateBackendDefinitionApiV1MachineBackendsAccessionIdPut(
        accessionId: string,
        requestBody: MachineBackendDefinitionUpdate,
    ): CancelablePromise<MachineBackendDefinitionRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/machine-backends/{accession_id}',
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
     * Delete machine backend definition
     * Delete a machine backend definition.
     * @param accessionId
     * @returns void
     * @throws ApiError
     */
    public static deleteBackendDefinitionApiV1MachineBackendsAccessionIdDelete(
        accessionId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/machine-backends/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
