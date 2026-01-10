/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ProtocolCapabilityMatchingService {
    /**
     * Get Protocol Compatibility
     * Check protocol compatibility against all machines.
     *
     * Returns a list of compatibility results for each available machine.
     * @param accessionId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getProtocolCompatibilityApiV1ProtocolsAccessionIdCompatibilityGet(
        accessionId: string,
    ): CancelablePromise<Array<Record<string, any>>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/protocols/{accession_id}/compatibility',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
