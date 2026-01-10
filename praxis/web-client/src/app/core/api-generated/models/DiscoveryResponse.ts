/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DiscoveredDeviceResponse } from './DiscoveredDeviceResponse';
/**
 * Response model for discovery results.
 */
export type DiscoveryResponse = {
    devices: Array<DiscoveredDeviceResponse>;
    total: number;
    serial_count: number;
    simulator_count: number;
    network_count: number;
};

