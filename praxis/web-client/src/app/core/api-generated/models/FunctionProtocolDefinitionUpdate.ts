/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetRequirementModel_Input } from './AssetRequirementModel_Input';
import type { DataViewMetadataModel } from './DataViewMetadataModel';
import type { ParameterMetadataModel_Input } from './ParameterMetadataModel_Input';
/**
 * Model for updating a function protocol definition.
 */
export type FunctionProtocolDefinitionUpdate = {
    name?: (string | null);
    version?: (string | null);
    description?: (string | null);
    source_file_path?: (string | null);
    module_name?: (string | null);
    function_name?: (string | null);
    source_repository_name?: (string | null);
    commit_hash?: (string | null);
    file_system_source_name?: (string | null);
    is_top_level?: (boolean | null);
    solo_execution?: (boolean | null);
    preconfigure_deck?: (boolean | null);
    requires_deck?: (boolean | null);
    deck_param_name?: (string | null);
    deck_construction_function_fqn?: (string | null);
    deck_layout_path?: (string | null);
    state_param_name?: (string | null);
    category?: (string | null);
    tags?: (Array<string> | null);
    deprecated?: (boolean | null);
    parameters?: (Array<ParameterMetadataModel_Input> | null);
    assets?: (Array<AssetRequirementModel_Input> | null);
    data_views?: (Array<DataViewMetadataModel> | null);
    hardware_requirements?: (Record<string, any> | null);
    setup_instructions_json?: null;
    source_hash?: (string | null);
    computation_graph?: (Record<string, any> | null);
};

