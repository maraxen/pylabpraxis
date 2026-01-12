/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Schema for creating a ResourceDefinition.
 */
export type ResourceDefinitionCreate = {
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
    name: string;
    /**
     * Fully qualified name
     */
    fqn: string;
    /**
     * Description of the resource type
     */
    description?: (string | null);
    /**
     * PyLabRobot category
     */
    plr_category?: (string | null);
    /**
     * Human-readable type of the resource
     */
    resource_type?: (string | null);
    is_consumable?: boolean;
    /**
     * Nominal volume in microliters
     */
    nominal_volume_ul?: (number | null);
    /**
     * Material (polypropylene, glass, etc.)
     */
    material?: (string | null);
    manufacturer?: (string | null);
    model?: (string | null);
    /**
     * Ordering information
     */
    ordering?: (string | null);
    /**
     * Size in X dimension (mm)
     */
    size_x_mm?: (number | null);
    /**
     * Size in Y dimension (mm)
     */
    size_y_mm?: (number | null);
    /**
     * Size in Z dimension (mm)
     */
    size_z_mm?: (number | null);
    /**
     * Number of items (wells, tips)
     */
    num_items?: (number | null);
    /**
     * Plate skirt type
     */
    plate_type?: (string | null);
    /**
     * Well volume for plates
     */
    well_volume_ul?: (number | null);
    /**
     * Tip volume for tip racks
     */
    tip_volume_ul?: (number | null);
    /**
     * Vendor from FQN
     */
    vendor?: (string | null);
    /**
     * Additional PyLabRobot definition details
     */
    plr_definition_details_json?: (Record<string, any> | null);
    /**
     * PLR rotation object
     */
    rotation_json?: (Record<string, any> | null);
};

