/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetType } from './AssetType';
import type { ResourceStatusEnum } from './ResourceStatusEnum';
/**
 * Schema for updating a Resource (partial update).
 */
export type ResourceUpdate = {
    asset_type?: (AssetType | null);
    name?: (string | null);
    fqn?: (string | null);
    location?: (string | null);
    plr_state?: (Record<string, any> | null);
    plr_definition?: (Record<string, any> | null);
    properties_json?: (Record<string, any> | null);
    status?: (ResourceStatusEnum | null);
    status_details?: (string | null);
    location_label?: (string | null);
    current_deck_position_name?: (string | null);
    resource_definition_accession_id?: (string | null);
};

