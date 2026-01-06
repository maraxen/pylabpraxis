/**
 * Models for State Resolution feature.
 *
 * When a protocol operation fails, there is uncertainty about what state actually
 * changed. These models represent uncertain states and user resolutions.
 */

/**
 * Types of state properties that can be uncertain.
 */
export type StatePropertyType =
    | 'volume'
    | 'has_liquid'
    | 'has_tip'
    | 'tip_loaded'
    | 'temperature'
    | 'position'
    | 'arbitrary';

/**
 * Types of user resolution.
 */
export type ResolutionType =
    | 'confirmed_success' // Effect actually happened as expected
    | 'confirmed_failure' // Effect did not happen at all
    | 'partial'           // Effect partially happened
    | 'arbitrary'         // User specifies custom value
    | 'unknown';          // User cannot determine

/**
 * Actions to take after resolution.
 */
export type ResolutionAction = 'resume' | 'abort' | 'retry';

/**
 * Represents state that may or may not have changed due to a failed operation.
 */
export interface UncertainStateChange {
    state_key: string;
    current_value: unknown;
    expected_value?: unknown;
    description: string;
    resolution_type: string;
    resource_name?: string;
    property_name?: string;
    property_type: StatePropertyType;
    suggested_resolutions: string[];
}

/**
 * User's resolution of uncertain state changes.
 */
export interface StateResolution {
    operation_id: string;
    resolution_type: ResolutionType;
    resolved_values: Record<string, unknown>;
    resolved_by?: string;
    resolved_at?: string;
    notes?: string;
}

/**
 * Request model for submitting a state resolution.
 */
export interface StateResolutionRequest {
    operation_id: string;
    resolution_type: ResolutionType;
    resolved_values: Record<string, unknown>;
    notes?: string;
    action: ResolutionAction;
}

/**
 * Response from the state resolution API.
 */
export interface StateResolutionLogResponse {
    id: string;
    run_id: string;
    operation_id: string;
    operation_description: string;
    resolution_type: string;
    action_taken: string;
    resolved_at: string;
    resolved_by: string;
}

/**
 * Failed operation context shown in the resolution dialog.
 */
export interface FailedOperationContext {
    operation_id: string;
    method_name: string;
    description: string;
    error_message: string;
    error_type?: string;
    timestamp?: string;
}

/**
 * Data passed to the StateResolutionDialog.
 */
export interface StateResolutionDialogData {
    runId: string;
    operation: FailedOperationContext;
    uncertainStates: UncertainStateChange[];
}

/**
 * Result returned from the StateResolutionDialog.
 */
export interface StateResolutionDialogResult {
    action: ResolutionAction;
    resolution?: StateResolution;
}
