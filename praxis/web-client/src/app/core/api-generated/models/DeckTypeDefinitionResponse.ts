/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DeckPositionDefinitionResponse } from './DeckPositionDefinitionResponse';
import type { PositioningConfig } from './PositioningConfig';
/**
 * Model for API responses for a deck type definition.
 */
export type DeckTypeDefinitionResponse = {
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
    positioning_config?: (PositioningConfig | null);
    positions: Array<DeckPositionDefinitionResponse>;
};

