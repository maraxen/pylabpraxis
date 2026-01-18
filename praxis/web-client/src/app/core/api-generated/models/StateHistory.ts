/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OperationStateSnapshot_Output } from './OperationStateSnapshot_Output';
import type { StateSnapshot } from './StateSnapshot';
/**
 * Complete state history for a protocol run.
 */
export type StateHistory = {
    run_id: string;
    protocol_name?: (string | null);
    operations?: Array<OperationStateSnapshot_Output>;
    final_state?: (StateSnapshot | null);
    total_duration_ms?: (number | null);
};

