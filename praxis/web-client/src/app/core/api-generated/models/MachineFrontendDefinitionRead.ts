/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MachineCategoryEnum } from './MachineCategoryEnum';
/**
 * Schema for reading a MachineFrontendDefinition (API response).
 */
export type MachineFrontendDefinitionRead = {
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
     * An optional name for the record.
     */
    name?: (string | null);
    /**
     * Arbitrary metadata.
     */
    properties_json?: (Record<string, any> | null);
    /**
     * Fully qualified name of the frontend class
     */
    fqn: string;
    /**
     * Description of the machine interface
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
    /**
     * Hardware capabilities (channels, modules)
     */
    capabilities?: (Record<string, any> | null);
    /**
     * User-configurable capabilities schema
     */
    capabilities_config?: (Record<string, any> | null);
    /**
     * Whether this machine has a deck
     */
    has_deck?: boolean;
    manufacturer?: (string | null);
    model?: (string | null);
};

