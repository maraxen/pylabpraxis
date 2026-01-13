/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PositioningConfig } from './PositioningConfig';
/**
 * Schema for reading a DeckDefinition (API response).
 */
export type DeckDefinitionRead = {
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
     * Human readable name for the deck type
     */
    name?: string;
    /**
     * Arbitrary metadata.
     */
    properties_json?: (Record<string, any> | null);
    /**
     * Fully qualified name
     */
    fqn: string;
    /**
     * Version string for the deck type
     */
    version?: (string | null);
    /**
     * Positioning configuration for the deck type
     */
    positioning_config?: (PositioningConfig | null);
    /**
     * Description of the deck type
     */
    description?: (string | null);
    /**
     * PyLabRobot category
     */
    plr_category?: (string | null);
    /**
     * Default size in X dimension (mm)
     */
    default_size_x_mm?: (number | null);
    /**
     * Default size in Y dimension (mm)
     */
    default_size_y_mm?: (number | null);
    /**
     * Default size in Z dimension (mm)
     */
    default_size_z_mm?: (number | null);
};

