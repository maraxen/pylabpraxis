/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetConstraintsModel } from './AssetConstraintsModel';
import type { LocationConstraintsModel } from './LocationConstraintsModel';
/**
 * Schema for reading an AssetRequirement.
 */
export type AssetRequirementRead = {
    accession_id: string;
    /**
     * The time the record was created.
     */
    created_at?: string;
    /**
     * The time the record was last updated.
     */
    updated_at?: (string | null);
    /**
     * The name of the asset requirement
     */
    name?: string;
    /**
     * Arbitrary metadata.
     */
    properties_json?: (Record<string, any> | null);
    /**
     * Type hint
     */
    type_hint_str?: string;
    /**
     * Fully qualified name
     */
    fqn?: (string | null);
    /**
     * Actual type
     */
    actual_type_str?: (string | null);
    optional?: boolean;
    default_value_repr?: (string | null);
    description?: (string | null);
    required_plr_category?: (string | null);
    constraints?: (AssetConstraintsModel | null);
    location_constraints?: (LocationConstraintsModel | null);
};

