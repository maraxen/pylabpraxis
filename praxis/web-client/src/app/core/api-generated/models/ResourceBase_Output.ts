/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetType } from './AssetType';
import type { ResourceStatusEnum } from './ResourceStatusEnum';
/**
 * Base model for a resource instance.
 */
export type ResourceBase_Output = {
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
    /**
     * An optional name for the record.
     */
    name?: string;
    /**
     * Arbitrary metadata associated with the record.
     */
    properties_json?: (Record<string, any> | null);
    /**
     * The type of the asset.
     */
    asset_type: (AssetType | null);
    /**
     * Fully qualified name of the asset's class, if applicable.
     */
    fqn?: (string | null);
    /**
     * The location of the asset.
     */
    location?: (string | null);
    status?: (ResourceStatusEnum | null);
    status_details?: (string | null);
    workcell_accession_id?: (string | null);
    parent_accession_id?: (string | null);
    plr_state?: (Record<string, any> | null);
    plr_definition?: (Record<string, any> | null);
    /**
     * List of child resources associated with this resource.
     */
    children?: Array<ResourceBase_Output>;
    parent?: (ResourceBase_Output | null);
    /**
     * List of accession IDs for child resources to be associated with this resource.
     */
    child_accession_ids?: Array<string>;
    resource_definition_accession_id?: (string | null);
};

