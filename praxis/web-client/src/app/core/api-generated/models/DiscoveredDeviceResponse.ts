/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ConnectionType } from './ConnectionType';
import type { DeviceStatus } from './DeviceStatus';
/**
 * Response model for a discovered device.
 */
export type DiscoveredDeviceResponse = {
    id: string;
    name: string;
    connection_type: ConnectionType;
    status: DeviceStatus;
    port?: (string | null);
    ip_address?: (string | null);
    manufacturer?: (string | null);
    model?: (string | null);
    serial_number?: (string | null);
    plr_backend?: (string | null);
    properties?: (Record<string, any> | null);
};

