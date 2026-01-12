/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FailureModeModel } from './FailureModeModel';
import type { InferredRequirementModel } from './InferredRequirementModel';
/**
 * Cached simulation result for a protocol definition.
 */
export type SimulationResultModel = {
    /**
     * Whether protocol passed all validation
     */
    passed?: boolean;
    /**
     * Highest level completed
     */
    level_completed?: string;
    /**
     * Level where failure occurred
     */
    level_failed?: (string | null);
    /**
     * Structural error if any
     */
    structural_error?: (string | null);
    /**
     * All violations from simulation
     */
    violations?: Array<Record<string, any>>;
    /**
     * Requirements inferred from simulation
     */
    inferred_requirements?: Array<InferredRequirementModel>;
    /**
     * Enumerated failure modes
     */
    failure_modes?: Array<FailureModeModel>;
    /**
     * Failure detection statistics
     */
    failure_mode_stats?: Record<string, any>;
    /**
     * Simulator version
     */
    simulation_version?: string;
    /**
     * When simulation was run
     */
    simulated_at?: (string | null);
    /**
     * Simulation execution time
     */
    execution_time_ms?: number;
};

