/**
 * Frontend models for simulation data from the backend.
 * These mirror the backend Pydantic models for protocol simulation results.
 */

/**
 * Inferred requirement from protocol simulation.
 * Represents conditions that must be met for successful execution.
 */
export interface InferredRequirement {
    /** Type of requirement: tips_required, resource_on_deck, liquid_present */
    requirement_type: 'tips_required' | 'resource_on_deck' | 'liquid_present' | string;
    /** Resource involved in the requirement (if applicable) */
    resource?: string;
    /** Additional details about the requirement */
    details: Record<string, unknown>;
    /** Simulation level where this was inferred (boolean, symbolic, exact) */
    inferred_at_level: string;
}

/**
 * Detected failure mode for a protocol.
 * Describes a specific way the protocol can fail.
 */
export interface FailureMode {
    /** State configuration that causes failure */
    initial_state: Record<string, unknown>;
    /** Operation ID where failure occurs */
    failure_point: string;
    /** Type of failure (tips_not_loaded, no_liquid, etc.) */
    failure_type: string;
    /** Human-readable failure description */
    message: string;
    /** Suggested fix to prevent this failure */
    suggested_fix?: string;
    /** Severity: error, warning, info */
    severity: 'error' | 'warning' | 'info';
}

/**
 * Cached simulation result for a protocol definition.
 */
export interface SimulationResult {
    /** Whether protocol passed all validation */
    passed: boolean;
    /** Highest simulation level completed (structural, boolean, symbolic, exact) */
    level_completed: string;
    /** Level where failure occurred (if any) */
    level_failed?: string;
    /** Structural error message if any */
    structural_error?: string;
    /** All violations from simulation */
    violations: SimulationViolation[];
    /** Requirements inferred from simulation */
    inferred_requirements: InferredRequirement[];
    /** Enumerated failure modes */
    failure_modes: FailureMode[];
    /** Failure detection statistics */
    failure_mode_stats: Record<string, unknown>;
    /** Simulator version */
    simulation_version: string;
    /** When simulation was run */
    simulated_at?: string;
    /** Simulation execution time in milliseconds */
    execution_time_ms: number;
}

/**
 * A violation detected during simulation.
 */
export interface SimulationViolation {
    /** Type of violation */
    type: string;
    /** Operation ID where violation occurred */
    operation_id: string;
    /** Method name involved */
    method_name: string;
    /** Resource involved */
    resource?: string;
    /** Human-readable message */
    message: string;
    /** Suggested fix */
    suggested_fix?: string;
    /** Simulation level where detected */
    level: string;
    /** Additional details */
    details: Record<string, unknown>;
}

/**
 * State snapshot at a specific operation during execution.
 * Used for time travel debugging.
 */
export interface OperationStateSnapshot {
    /** Index of the operation in the sequence */
    operation_index: number;
    /** Unique operation identifier */
    operation_id: string;
    /** Method name called */
    method_name: string;
    /** Resource involved (if any) */
    resource?: string;
    /** Arguments passed to the method */
    args?: Record<string, unknown>;
    /** State before the operation */
    state_before: StateSnapshot;
    /** State after the operation */
    state_after: StateSnapshot;
    /** Timestamp of the operation */
    timestamp?: string;
    /** Duration of the operation in ms */
    duration_ms?: number;
    /** Status of the operation */
    status: 'completed' | 'failed' | 'skipped';
    /** Error message if failed */
    error_message?: string;
}

/**
 * Complete state snapshot at a point in time.
 */
export interface StateSnapshot {
    /** Tip state - which tips are loaded */
    tips: TipStateSnapshot;
    /** Liquid volumes by resource and well */
    liquids: Record<string, WellVolumeMap>;
    /** Resources currently on deck */
    on_deck: string[];
}

/**
 * Snapshot of tip state.
 */
export interface TipStateSnapshot {
    /** Whether tips are currently loaded */
    tips_loaded: boolean;
    /** Number of tips loaded (for multi-channel) */
    tips_count: number;
    /** Tip rack usage by rack name */
    tip_usage?: Record<string, number>;
}

/**
 * Map of well identifiers to volumes.
 */
export type WellVolumeMap = Record<string, number>;

/**
 * Complete state history for a protocol run.
 * Used for time travel debugging in the execution monitor.
 */
export interface StateHistory {
    /** Run identifier */
    run_id: string;
    /** Protocol name for context */
    protocol_name?: string;
    /** All operations with state snapshots */
    operations: OperationStateSnapshot[];
    /** Final state after all operations */
    final_state: StateSnapshot;
    /** Total execution time in ms */
    total_duration_ms?: number;
}

/**
 * Status of a requirement validation check.
 */
export interface RequirementStatus {
    /** The requirement being checked */
    requirement: InferredRequirement;
    /** Whether the requirement is met */
    isMet: boolean;
    /** Whether the requirement is in a warning state (partial/unverifiable) */
    isWarning: boolean;
    /** Message explaining the status */
    message?: string;
}

/**
 * Metrics tracked over time for the state history timeline.
 */
export interface TimelineMetric {
    /** Metric identifier */
    id: string;
    /** Display label */
    label: string;
    /** Values at each operation index */
    values: number[];
    /** Unit for display (e.g., 'µL', 'tips') */
    unit?: string;
    /** Color for visualization */
    color?: string;
}
