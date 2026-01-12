/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * A requirement inferred from protocol simulation.
 */
export type InferredRequirementModel = {
    /**
     * Type: tips_required, resource_on_deck, liquid_present
     */
    requirement_type: string;
    /**
     * Resource involved
     */
    resource?: (string | null);
    details?: Record<string, any>;
    /**
     * Level at which this was inferred
     */
    inferred_at_level?: string;
};

