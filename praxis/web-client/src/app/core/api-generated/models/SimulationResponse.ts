/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SimulationViolationResponse } from './SimulationViolationResponse';
/**
 * Response body for protocol simulation.
 */
export type SimulationResponse = {
    /**
     * Whether simulation passed without violations
     */
    passed: boolean;
    /**
     * All violations found during simulation
     */
    violations?: Array<SimulationViolationResponse>;
    /**
     * Number of operations replayed
     */
    operations_executed?: number;
    /**
     * Replay mode used
     */
    replay_mode?: string;
    /**
     * Non-violation errors (parse errors, etc.)
     */
    errors?: Array<string>;
    /**
     * Summary of final state
     */
    final_state_summary?: Record<string, any>;
};

