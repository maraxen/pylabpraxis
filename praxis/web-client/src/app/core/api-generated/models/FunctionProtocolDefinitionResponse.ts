/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetRequirementModel_Output } from './AssetRequirementModel_Output';
import type { DataViewMetadataModel } from './DataViewMetadataModel';
import type { ParameterMetadataModel } from './ParameterMetadataModel';
/**
 * Model for API responses for a function protocol definition.
 */
export type FunctionProtocolDefinitionResponse = {
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
    version?: string;
    description?: (string | null);
    source_file_path: string;
    module_name: string;
    function_name: string;
    source_repository_name?: (string | null);
    commit_hash?: (string | null);
    file_system_source_name?: (string | null);
    is_top_level?: boolean;
    solo_execution?: boolean;
    preconfigure_deck?: boolean;
    deck_param_name?: (string | null);
    deck_construction_function_fqn?: (string | null);
    deck_layout_path?: (string | null);
    state_param_name?: (string | null);
    category?: (string | null);
    tags?: any;
    deprecated?: boolean;
    parameters?: Array<ParameterMetadataModel>;
    assets?: Array<AssetRequirementModel_Output>;
    data_views?: Array<DataViewMetadataModel>;
    hardware_requirements?: (Record<string, any> | null);
};

