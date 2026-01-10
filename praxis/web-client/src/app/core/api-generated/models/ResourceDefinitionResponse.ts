/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Represents a resource definition for API responses.
 */
export type ResourceDefinitionResponse = {
    /**
     * The unique accession ID of the record.
     */
    accession_id?: string;
    /**
     * The time the record was created.
     */
    created_at?: string;
    /**
     * The time the record was last updated.
     */
    last_updated?: (string | null);
    /**
     * An optional name for the record.
     */
    name?: string;
    /**
     * Arbitrary metadata associated with the record.
     */
    properties_json?: (Record<string, any> | null);
    fqn: string;
    description?: (string | null);
    plr_category?: (string | null);
    resource_type?: (string | null);
    is_consumable?: boolean;
    nominal_volume_ul?: (number | null);
    material?: (string | null);
    manufacturer?: (string | null);
    plr_definition_details_json?: (Record<string, any> | null);
    size_x_mm?: (number | null);
    size_y_mm?: (number | null);
    size_z_mm?: (number | null);
    model?: (string | null);
    rotation_json?: (Record<string, any> | null);
    ordering?: (string | null);
    num_items?: (number | null);
    plate_type?: (string | null);
    well_volume_ul?: (number | null);
    tip_volume_ul?: (number | null);
    vendor?: (string | null);
};

