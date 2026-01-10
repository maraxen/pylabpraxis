/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MachineCategoryEnum } from './MachineCategoryEnum';
/**
 * Represents a machine definition for API responses.
 */
export type MachineDefinitionResponse = {
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
    name: string;
    /**
     * Arbitrary metadata associated with the record.
     */
    properties_json?: (Record<string, any> | null);
    fqn: string;
    description?: (string | null);
    plr_category?: (string | null);
    /**
     * The category of the machine.
     */
    machine_category?: (MachineCategoryEnum | null);
    /**
     * The nominal volume in microliters.
     */
    nominal_volume_ul?: (number | null);
    /**
     * The material of the machine.
     */
    material?: (string | null);
    /**
     * The manufacturer of the machine.
     */
    manufacturer?: (string | null);
    /**
     * PyLabRobot specific definition details.
     */
    plr_definition_details_json?: (Record<string, any> | null);
    /**
     * The size in the x-dimension in millimeters.
     */
    size_x_mm?: (number | null);
    /**
     * The size in the y-dimension in millimeters.
     */
    size_y_mm?: (number | null);
    /**
     * The size in the z-dimension in millimeters.
     */
    size_z_mm?: (number | null);
    /**
     * The model of the machine.
     */
    model?: (string | null);
    /**
     * The rotation of the machine.
     */
    rotation_json?: (Record<string, any> | null);
    /**
     * The accession ID of the resource definition.
     */
    resource_definition_accession_id?: (string | null);
    /**
     * Whether the machine has a deck.
     */
    has_deck?: (boolean | null);
    /**
     * The accession ID of the deck definition.
     */
    deck_definition_accession_id?: (string | null);
    /**
     * The setup method for the machine.
     */
    setup_method_json?: (Record<string, any> | null);
    /**
     * Hardware capabilities (channels, modules, etc).
     */
    capabilities?: (Record<string, any> | null);
    /**
     * List of compatible backend FQNs.
     */
    compatible_backends?: (Array<string> | null);
    /**
     * Schema for user-configurable capabilities.
     */
    capabilities_config?: (Record<string, any> | null);
};

