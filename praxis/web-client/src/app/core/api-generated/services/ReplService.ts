/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SaveSessionRequest } from '../models/SaveSessionRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ReplService {
    /**
     * Save Session
     * Save the current session history as a protocol.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static saveSessionApiV1ReplSaveSessionPost(
        requestBody: SaveSessionRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/repl/save_session',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
