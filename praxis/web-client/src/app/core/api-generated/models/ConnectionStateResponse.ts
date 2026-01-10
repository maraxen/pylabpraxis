/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Response model for connection state.
 */
export type ConnectionStateResponse = {
    device_id: string;
    status: string;
    connected_at?: (string | null);
    last_heartbeat: string;
    backend_class?: (string | null);
    config?: Record<string, any>;
    error_message?: (string | null);
};

