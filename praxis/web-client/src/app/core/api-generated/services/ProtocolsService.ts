/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_get_multi_api_v1_protocols_definitions_get } from '../models/Body_get_multi_api_v1_protocols_definitions_get';
import type { Body_get_multi_api_v1_protocols_runs_get } from '../models/Body_get_multi_api_v1_protocols_runs_get';
import type { CancelRunResponse } from '../models/CancelRunResponse';
import type { FunctionProtocolDefinitionCreate } from '../models/FunctionProtocolDefinitionCreate';
import type { FunctionProtocolDefinitionRead } from '../models/FunctionProtocolDefinitionRead';
import type { FunctionProtocolDefinitionUpdate } from '../models/FunctionProtocolDefinitionUpdate';
import type { ProtocolRunCreate } from '../models/ProtocolRunCreate';
import type { ProtocolRunRead } from '../models/ProtocolRunRead';
import type { ProtocolRunUpdate } from '../models/ProtocolRunUpdate';
import type { QueuedRunResponse } from '../models/QueuedRunResponse';
import type { SimulationRequest } from '../models/SimulationRequest';
import type { SimulationResponse } from '../models/SimulationResponse';
import type { StartRunRequest } from '../models/StartRunRequest';
import type { StartRunResponse } from '../models/StartRunResponse';
import type { StateHistory } from '../models/StateHistory';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ProtocolsService {
    /**
     * Start Protocol Run
     * Start a new protocol run.
     *
     * Creates a protocol run record and begins execution. If simulation_mode is True,
     * the protocol will run without triggering actual hardware actions.
     * @param requestBody
     * @returns StartRunResponse Successful Response
     * @throws ApiError
     */
    public static startProtocolRunApiV1ProtocolsRunsActionsStartPost(
        requestBody: StartRunRequest,
    ): CancelablePromise<StartRunResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/protocols/runs/actions/start',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create
     * @param requestBody
     * @returns FunctionProtocolDefinitionRead Successful Response
     * @throws ApiError
     */
    public static createApiV1ProtocolsDefinitionsPost(
        requestBody: FunctionProtocolDefinitionCreate,
    ): CancelablePromise<FunctionProtocolDefinitionRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/protocols/definitions',
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
     * @returns FunctionProtocolDefinitionRead Successful Response
     * @throws ApiError
     */
    public static getMultiApiV1ProtocolsDefinitionsGet(
        limit: number = 100,
        offset?: number,
        sortBy?: (string | null),
        dateRangeStart?: (string | null),
        dateRangeEnd?: (string | null),
        protocolRunAccessionId?: (string | null),
        machineAccessionId?: (string | null),
        resourceAccessionId?: (string | null),
        parentAccessionId?: (string | null),
        requestBody?: Body_get_multi_api_v1_protocols_definitions_get,
    ): CancelablePromise<Array<FunctionProtocolDefinitionRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/protocols/definitions',
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
     * @returns FunctionProtocolDefinitionRead Successful Response
     * @throws ApiError
     */
    public static getApiV1ProtocolsDefinitionsAccessionIdGet(
        accessionId: string,
    ): CancelablePromise<FunctionProtocolDefinitionRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/protocols/definitions/{accession_id}',
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
     * @returns FunctionProtocolDefinitionRead Successful Response
     * @throws ApiError
     */
    public static updateApiV1ProtocolsDefinitionsAccessionIdPut(
        accessionId: string,
        requestBody: FunctionProtocolDefinitionUpdate,
    ): CancelablePromise<FunctionProtocolDefinitionRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/protocols/definitions/{accession_id}',
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
    public static deleteApiV1ProtocolsDefinitionsAccessionIdDelete(
        accessionId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/protocols/definitions/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Cancel Protocol Run
     * Cancel a running or queued protocol run.
     *
     * Releases reserved assets and updates the run status to CANCELLED.
     *
     * TODO: Add permission check - only admin or run owner can cancel.
     * @param runId
     * @returns CancelRunResponse Successful Response
     * @throws ApiError
     */
    public static cancelProtocolRunApiV1ProtocolsRunsRunIdCancelPost(
        runId: string,
    ): CancelablePromise<CancelRunResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/protocols/runs/{run_id}/cancel',
            path: {
                'run_id': runId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Protocol Queue
     * Get list of active/queued protocol runs.
     *
     * Returns runs with status: PENDING, PREPARING, QUEUED, RUNNING.
     * @returns QueuedRunResponse Successful Response
     * @throws ApiError
     */
    public static getProtocolQueueApiV1ProtocolsRunsQueueGet(): CancelablePromise<Array<QueuedRunResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/protocols/runs/queue',
        });
    }
    /**
     * Get Run State History
     * Get granular state history for a protocol run.
     * @param runId
     * @returns StateHistory Successful Response
     * @throws ApiError
     */
    public static getRunStateHistoryApiV1ProtocolsRunsRunIdStateHistoryGet(
        runId: string,
    ): CancelablePromise<StateHistory> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/protocols/runs/{run_id}/state-history',
            path: {
                'run_id': runId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create
     * @param requestBody
     * @returns ProtocolRunRead Successful Response
     * @throws ApiError
     */
    public static createApiV1ProtocolsRunsPost(
        requestBody: ProtocolRunCreate,
    ): CancelablePromise<ProtocolRunRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/protocols/runs',
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
     * @returns ProtocolRunRead Successful Response
     * @throws ApiError
     */
    public static getMultiApiV1ProtocolsRunsGet(
        limit: number = 100,
        offset?: number,
        sortBy?: (string | null),
        dateRangeStart?: (string | null),
        dateRangeEnd?: (string | null),
        protocolRunAccessionId?: (string | null),
        machineAccessionId?: (string | null),
        resourceAccessionId?: (string | null),
        parentAccessionId?: (string | null),
        requestBody?: Body_get_multi_api_v1_protocols_runs_get,
    ): CancelablePromise<Array<ProtocolRunRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/protocols/runs',
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
     * @returns ProtocolRunRead Successful Response
     * @throws ApiError
     */
    public static getApiV1ProtocolsRunsAccessionIdGet(
        accessionId: string,
    ): CancelablePromise<ProtocolRunRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/protocols/runs/{accession_id}',
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
     * @returns ProtocolRunRead Successful Response
     * @throws ApiError
     */
    public static updateApiV1ProtocolsRunsAccessionIdPut(
        accessionId: string,
        requestBody: ProtocolRunUpdate,
    ): CancelablePromise<ProtocolRunRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/protocols/runs/{accession_id}',
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
    public static deleteApiV1ProtocolsRunsAccessionIdDelete(
        accessionId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/protocols/runs/{accession_id}',
            path: {
                'accession_id': accessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
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
