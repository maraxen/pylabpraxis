/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MachineBackendDefinitionRead } from '../models/MachineBackendDefinitionRead';
import type { MachineFrontendDefinitionCreate } from '../models/MachineFrontendDefinitionCreate';
import type { MachineFrontendDefinitionRead } from '../models/MachineFrontendDefinitionRead';
import type { MachineFrontendDefinitionUpdate } from '../models/MachineFrontendDefinitionUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class MachineFrontendsService {
    /**
     * List Frontend Definitions
     * List all machine frontend definitions.
     * @param skip
     * @param limit
     * @returns MachineFrontendDefinitionRead Successful Response
     * @throws ApiError
     */
    public static listFrontendDefinitionsApiV1MachineFrontendsGet(
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<Array<MachineFrontendDefinitionRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/machine-frontends/',
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
     * Create Frontend Definition
     * Create a new machine frontend definition.
     * @param requestBody
     * @returns MachineFrontendDefinitionRead Successful Response
     * @throws ApiError
     */
    public static createFrontendDefinitionApiV1MachineFrontendsPost(
        requestBody: MachineFrontendDefinitionCreate,
    ): CancelablePromise<MachineFrontendDefinitionRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/machine-frontends/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Frontend Definition
     * Get a machine frontend definition by accession ID.
     * @param accessionId
     * @returns MachineFrontendDefinitionRead Successful Response
     * @throws ApiError
     */
    public static getFrontendDefinitionApiV1MachineFrontendsAccessionIdGet(
        accessionId: string,
    ): CancelablePromise<MachineFrontendDefinitionRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/machine-frontends/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Frontend Definition
     * Update a machine frontend definition.
     * @param accessionId
     * @param requestBody
     * @returns MachineFrontendDefinitionRead Successful Response
     * @throws ApiError
     */
    public static updateFrontendDefinitionApiV1MachineFrontendsAccessionIdPut(
        accessionId: string,
        requestBody: MachineFrontendDefinitionUpdate,
    ): CancelablePromise<MachineFrontendDefinitionRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/machine-frontends/{accession_id}',
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
     * Delete Frontend Definition
     * Delete a machine frontend definition.
     * @param accessionId
     * @returns void
     * @throws ApiError
     */
    public static deleteFrontendDefinitionApiV1MachineFrontendsAccessionIdDelete(
        accessionId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/machine-frontends/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Compatible Backends
     * Get compatible backend definitions for a frontend definition.
     * @param accessionId
     * @returns MachineBackendDefinitionRead Successful Response
     * @throws ApiError
     */
    public static getCompatibleBackendsApiV1MachineFrontendsAccessionIdBackendsGet(
        accessionId: string,
    ): CancelablePromise<Array<MachineBackendDefinitionRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/machine-frontends/{accession_id}/backends',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
