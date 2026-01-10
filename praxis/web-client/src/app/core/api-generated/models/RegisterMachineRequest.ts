/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request to register a discovered device as a machine.
 */
export type RegisterMachineRequest = {
    device_id: string;
    name: string;
    plr_backend: string;
    connection_type: string;
    port?: (string | null);
    ip_address?: (string | null);
    configuration?: (Record<string, any> | null);
};

