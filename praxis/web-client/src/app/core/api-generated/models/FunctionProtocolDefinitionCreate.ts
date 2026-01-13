/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetRequirementCreate } from './AssetRequirementCreate';
import type { DataViewMetadataModel } from './DataViewMetadataModel';
import type { ParameterMetadataModel } from './ParameterMetadataModel';
/**
 * Schema for creating a FunctionProtocolDefinition.
 */
export type FunctionProtocolDefinitionCreate = {
    accession_id?: (string | null);
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
     * Fully qualified name
     */
    fqn: string;
    /**
     * Semantic version
     */
    version?: string;
    description?: (string | null);
    source_file_path?: string;
    module_name?: string;
    function_name?: string;
    is_top_level?: boolean;
    solo_execution?: boolean;
    preconfigure_deck?: boolean;
    requires_deck?: boolean;
    deck_param_name?: (string | null);
    deck_construction_function_fqn?: (string | null);
    deck_layout_path?: (string | null);
    state_param_name?: (string | null);
    category?: (string | null);
    deprecated?: boolean;
    source_hash?: (string | null);
    graph_cached_at?: (string | null);
    simulation_version?: (string | null);
    simulation_cached_at?: (string | null);
    bytecode_python_version?: (string | null);
    bytecode_cache_version?: (string | null);
    bytecode_cached_at?: (string | null);
    commit_hash?: (string | null);
    tags?: (Array<string> | Record<string, any> | null);
    parameters?: (Array<ParameterMetadataModel> | null);
    assets?: (Array<AssetRequirementCreate> | null);
    data_views?: (Array<DataViewMetadataModel> | null);
    setup_instructions_json?: null;
    source_repository_name?: (string | null);
    file_system_source_name?: (string | null);
};

