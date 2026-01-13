/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MachineCategoryEnum } from './MachineCategoryEnum';
/**
 * Schema for creating a MachineDefinition.
 */
export type MachineDefinitionCreate = {
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
     * Fully qualified name
     */
    fqn: string;
    /**
     * Description of the machine type
     */
    description?: (string | null);
    /**
     * PyLabRobot category
     */
    plr_category?: (string | null);
    /**
     * Category of the machine
     */
    machine_category?: (MachineCategoryEnum | null);
    material?: (string | null);
    manufacturer?: (string | null);
    model?: (string | null);
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
     * Whether this machine has a deck
     */
    has_deck?: (boolean | null);
    /**
     * PLR frontend class FQN
     */
    frontend_fqn?: (string | null);
    /**
     * Nominal volume in microliters
     */
    nominal_volume_ul?: (number | null);
    /**
     * Additional PyLabRobot definition details
     */
    plr_definition_details_json?: (Record<string, any> | null);
    /**
     * PLR rotation object
     */
    rotation_json?: (Record<string, any> | null);
    /**
     * Setup method configuration
     */
    setup_method_json?: (Record<string, any> | null);
    /**
     * Hardware capabilities (channels, modules)
     */
    capabilities?: (Record<string, any> | null);
    /**
     * Compatible backend class FQNs
     */
    compatible_backends?: (Record<string, any> | null);
    /**
     * User-configurable capabilities schema
     */
    capabilities_config?: (Record<string, any> | null);
    /**
     * Connection parameters schema
     */
    connection_config?: (Record<string, any> | null);
};

