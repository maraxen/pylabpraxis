/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ConnectionStateResponse } from '../models/ConnectionStateResponse';
import type { ConnectRequest } from '../models/ConnectRequest';
import type { ConnectResponse } from '../models/ConnectResponse';
import type { DisconnectRequest } from '../models/DisconnectRequest';
import type { DiscoveredDeviceResponse } from '../models/DiscoveredDeviceResponse';
import type { DiscoveryResponse } from '../models/DiscoveryResponse';
import type { HeartbeatRequest } from '../models/HeartbeatRequest';
import type { HeartbeatResponse } from '../models/HeartbeatResponse';
import type { RegisterMachineRequest } from '../models/RegisterMachineRequest';
import type { RegisterMachineResponse } from '../models/RegisterMachineResponse';
import type { ReplCommand } from '../models/ReplCommand';
import type { ReplResponse } from '../models/ReplResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class HardwareService {
    /**
     * Discover available hardware
     * Scan for connected hardware devices including serial ports, USB, network, and simulators.
     * @returns DiscoveryResponse Successful Response
     * @throws ApiError
     */
    public static discoverHardwareApiV1HardwareDiscoverGet(): CancelablePromise<DiscoveryResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/hardware/discover',
        });
    }
    /**
     * Discover serial devices
     * Scan for devices connected via serial/USB ports.
     * @returns DiscoveredDeviceResponse Successful Response
     * @throws ApiError
     */
    public static discoverSerialApiV1HardwareDiscoverSerialGet(): CancelablePromise<Array<DiscoveredDeviceResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/hardware/discover/serial',
        });
    }
    /**
     * List available simulators
     * Get list of available PyLabRobot simulator backends.
     * @returns DiscoveredDeviceResponse Successful Response
     * @throws ApiError
     */
    public static discoverSimulatorsApiV1HardwareDiscoverSimulatorsGet(): CancelablePromise<Array<DiscoveredDeviceResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/hardware/discover/simulators',
        });
    }
    /**
     * Connect to a device
     * Establish connection to a discovered hardware device.
     * @param requestBody
     * @returns ConnectResponse Successful Response
     * @throws ApiError
     */
    public static connectDeviceApiV1HardwareConnectPost(
        requestBody: ConnectRequest,
    ): CancelablePromise<ConnectResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/hardware/connect',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Disconnect from a device
     * Close connection to a hardware device.
     * @param requestBody
     * @returns ConnectResponse Successful Response
     * @throws ApiError
     */
    public static disconnectDeviceApiV1HardwareDisconnectPost(
        requestBody: DisconnectRequest,
    ): CancelablePromise<ConnectResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/hardware/disconnect',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List active connections
     * Get list of currently active hardware connections.
     * @returns ConnectionStateResponse Successful Response
     * @throws ApiError
     */
    public static listConnectionsApiV1HardwareConnectionsGet(): CancelablePromise<Array<ConnectionStateResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/hardware/connections',
        });
    }
    /**
     * Send connection heartbeat
     * Keep a connection alive by sending a heartbeat.
     * @param requestBody
     * @returns HeartbeatResponse Successful Response
     * @throws ApiError
     */
    public static sendHeartbeatApiV1HardwareHeartbeatPost(
        requestBody: HeartbeatRequest,
    ): CancelablePromise<HeartbeatResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/hardware/heartbeat',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get connection state
     * Get the current state of a specific connection.
     * @param deviceId
     * @returns ConnectionStateResponse Successful Response
     * @throws ApiError
     */
    public static getConnectionApiV1HardwareConnectionsDeviceIdGet(
        deviceId: string,
    ): CancelablePromise<ConnectionStateResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/hardware/connections/{device_id}',
            path: {
                'device_id': deviceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Register a device as a machine
     * Register a discovered hardware device as a machine in the system.
     * @param requestBody
     * @returns RegisterMachineResponse Successful Response
     * @throws ApiError
     */
    public static registerMachineApiV1HardwareRegisterPost(
        requestBody: RegisterMachineRequest,
    ): CancelablePromise<RegisterMachineResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/hardware/register',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Execute REPL command
     * Execute a command on a connected hardware device.
     * @param requestBody
     * @returns ReplResponse Successful Response
     * @throws ApiError
     */
    public static executeReplCommandApiV1HardwareReplPost(
        requestBody: ReplCommand,
    ): CancelablePromise<ReplResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/hardware/repl',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
