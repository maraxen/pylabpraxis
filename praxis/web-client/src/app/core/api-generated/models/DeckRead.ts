/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetType } from './AssetType';
import type { ResourceStatusEnum } from './ResourceStatusEnum';
/**
 * Schema for reading a Deck (API response).
 */
export type DeckRead = {
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
     * Type of asset, e.g., machine, resource, etc.
     */
    asset_type?: AssetType;
    /**
     * Fully qualified name of the asset's class, if applicable.
     */
    fqn?: (string | null);
    /**
     * Location of the asset in the lab.
     */
    location?: (string | null);
    status?: ResourceStatusEnum;
    /**
     * Additional status details
     */
    status_details?: (string | null);
    /**
     * Physical location label
     */
    location_label?: (string | null);
    /**
     * Current deck position
     */
    current_deck_position_name?: (string | null);
};

