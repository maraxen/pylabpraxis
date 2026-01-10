/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DiscoveryService {
    /**
     * Sync All Definitions
     * Synchronize all PyLabRobot type definitions and protocol definitions with the database.
     *
     * This endpoint triggers a full discovery and synchronization process for all
     * known PyLabRobot resources, machines, decks, and protocol definitions.
     * It should be used to ensure the database reflects the latest available
     * definitions from the connected PyLabRobot environment and protocol sources.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static syncAllDefinitionsApiV1DiscoverySyncAllPost(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/discovery/sync-all',
        });
    }
}
