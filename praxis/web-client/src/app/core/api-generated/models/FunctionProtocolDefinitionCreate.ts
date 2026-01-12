/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetRequirementModel_Input } from './AssetRequirementModel_Input';
import type { DataViewMetadataModel } from './DataViewMetadataModel';
import type { ParameterMetadataModel_Input } from './ParameterMetadataModel_Input';
/**
 * Represents a detailed definition of a function-based protocol.
 *
 * This model encapsulates core definition details, source information,
 * execution behavior, categorization, and inferred parameters and assets.
 */
export type FunctionProtocolDefinitionCreate = {
    name: string;
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
    requires_deck?: boolean;
    deck_param_name?: (string | null);
    deck_construction_function_fqn?: (string | null);
    deck_layout_path?: (string | null);
    state_param_name?: (string | null);
    category?: (string | null);
    tags?: Array<string>;
    deprecated?: boolean;
    source_hash?: (string | null);
    computation_graph?: (Record<string, any> | null);
    parameters?: Array<ParameterMetadataModel_Input>;
    assets?: Array<AssetRequirementModel_Input>;
    data_views?: (Array<DataViewMetadataModel> | null);
    hardware_requirements?: (Record<string, any> | null);
    /**
     * Pre-run setup instructions to display in Deck Setup wizard
     */
    setup_instructions_json?: null;
    /**
     * Optional accession ID.
     */
    accession_id?: (string | null);
};

