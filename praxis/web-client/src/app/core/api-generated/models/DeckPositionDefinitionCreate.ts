/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Schema for creating a DeckPositionDefinition.
 */
export type DeckPositionDefinitionCreate = {
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
    updated_at?: (string | null);
    /**
     * An optional name for the record.
     */
    name?: (string | null);
    /**
     * Arbitrary metadata.
     */
    properties_json?: (Record<string, any> | null);
    /**
     * Human-readable identifier for the position (e.g., 'A1', 'trash_bin')
     */
    position_accession_id?: (string | null);
    /**
     * X-coordinate of the position's center
     */
    nominal_x_mm?: number;
    /**
     * Y-coordinate of the position's center
     */
    nominal_y_mm?: number;
    /**
     * Z-coordinate of the position's center
     */
    nominal_z_mm?: number;
    /**
     * PyLabRobot position type
     */
    pylabrobot_position_type_name?: (string | null);
    /**
     * Whether position accepts tips
     */
    accepts_tips?: (boolean | null);
    /**
     * Whether position accepts plates
     */
    accepts_plates?: (boolean | null);
    /**
     * Whether position accepts tubes
     */
    accepts_tubes?: (boolean | null);
    /**
     * Additional notes for the position
     */
    notes?: (string | null);
    deck_type_id?: (string | null);
    deck_type_accession_id?: (string | null);
    compatible_resource_fqns?: (Record<string, any> | null);
};

