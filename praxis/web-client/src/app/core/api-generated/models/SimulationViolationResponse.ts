/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * A violation detected during simulation.
 */
export type SimulationViolationResponse = {
    /**
     * ID of the operation that caused violation
     */
    operation_id: string;
    /**
     * Index in execution order
     */
    operation_index: number;
    /**
     * Method that failed
     */
    method_name: string;
    /**
     * Variable receiving the call
     */
    receiver: string;
    /**
     * Type of violation
     */
    violation_type: string;
    /**
     * Human-readable error message
     */
    message: string;
    /**
     * How to fix this
     */
    suggested_fix?: (string | null);
    /**
     * Source line if available
     */
    line_number?: (number | null);
};

