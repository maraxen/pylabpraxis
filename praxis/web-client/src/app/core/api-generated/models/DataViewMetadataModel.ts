/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Defines a data view required by a protocol for input data.
 *
 * Data views allow protocols to declare what input data they need in a structured way.
 * They can reference:
 * - PLR state data (e.g., liquid volume tracking, resource positions)
 * - Function data outputs from previous protocol runs (e.g., plate reader reads)
 *
 * Schema validation errors during protocol setup generate warnings but do not
 * block protocol execution.
 */
export type DataViewMetadataModel = {
    name: string;
    description?: (string | null);
    source_type?: string;
    /**
     * Filter criteria to select specific data. For 'plr_state': {'state_key': 'tracker.volumes', 'resource_pattern': '*plate*'}. For 'function_output': {'function_fqn': '...', 'output_type': 'absorbance'}.
     */
    source_filter_json?: (Record<string, any> | null);
    /**
     * Expected data schema for validation (column names, types).
     */
    data_schema_json?: (Record<string, any> | null);
    required?: boolean;
    default_value_json?: any;
};

