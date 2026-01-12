/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * A detected failure mode for a protocol.
 */
export type FailureModeModel = {
    /**
     * State configuration that causes failure
     */
    initial_state?: Record<string, any>;
    /**
     * Operation ID where failure occurs
     */
    failure_point?: string;
    /**
     * Type of failure
     */
    failure_type?: string;
    /**
     * Human-readable failure description
     */
    message?: string;
    /**
     * How to prevent this failure
     */
    suggested_fix?: (string | null);
    /**
     * Severity: error, warning, info
     */
    severity?: string;
};

