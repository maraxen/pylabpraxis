/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
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
     * An optional name for the record.
     */
    name: string;
    /**
     * Fully qualified name
     */
    fqn: string;
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

