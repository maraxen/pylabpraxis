/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SimulationRequest } from '../models/SimulationRequest';
import type { SimulationResponse } from '../models/SimulationResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ProtocolSimulationService {
    /**
     * Simulate Protocol
     * Simulate a protocol using graph replay.
     *
     * This endpoint provides backend simulation for browser-mode fallback.
     * It replays the computation graph with state tracking to detect violations
     * like missing tips, incorrect deck placement, or liquid handling errors.
     *
     * The simulation uses boolean-level state tracking which catches:
     * - Tips not loaded before aspiration
     * - Resources not on deck
     * - Liquid operations on empty wells
     *
     * This is useful when the browser can't run Pyodide-based simulation
     * directly, or when you want to use the backend's full simulation
     * capabilities.
     *
     * Returns clear error messages to help fix protocol issues.
     * @param accessionId
     * @param requestBody
     * @returns SimulationResponse Successful Response
     * @throws ApiError
     */
    public static simulateProtocolApiV1ProtocolsDefinitionsAccessionIdSimulatePost(
        accessionId: string,
        requestBody?: (SimulationRequest | null),
    ): CancelablePromise<SimulationResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/protocols/definitions/{accession_id}/simulate',
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
     * Get Simulation Status
     * Get simulation status and cached results for a protocol.
     *
     * Returns information about:
     * - Whether simulation results are cached
     * - Cache validity (version, timestamp)
     * - Summary of cached results if available
     * @param accessionId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getSimulationStatusApiV1ProtocolsDefinitionsAccessionIdSimulationStatusGet(
        accessionId: string,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/protocols/definitions/{accession_id}/simulation-status',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
