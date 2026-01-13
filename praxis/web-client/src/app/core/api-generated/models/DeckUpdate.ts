/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetType } from './AssetType';
/**
 * Schema for updating a Deck (partial update).
 */
export type DeckUpdate = {
    asset_type?: (AssetType | null);
    name?: (string | null);
    fqn?: (string | null);
    location?: (string | null);
    plr_state?: (Record<string, any> | null);
    plr_definition?: (Record<string, any> | null);
    properties_json?: (Record<string, any> | null);
    status?: null;
    parent_machine_accession_id?: (string | null);
    machine_id?: (string | null);
};

