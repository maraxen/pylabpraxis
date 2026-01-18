/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StateSnapshot } from './StateSnapshot';
/**
 * State snapshot at a specific operation during execution.
 */
export type OperationStateSnapshot_Input = {
    operation_index: number;
    operation_id: string;
    method_name: string;
    resource?: (string | null);
    args?: (Record<string, any> | null);
    state_before?: (StateSnapshot | null);
    state_after?: (StateSnapshot | null);
    timestamp?: (string | null);
    duration_ms?: (number | null);
    status?: string;
    error_message?: (string | null);
    state_delta?: (Record<string, any> | null);
};

