/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Model for data view metadata.
 */
export type DataViewMetadataModel = {
    name: string;
    description?: (string | null);
    source_type?: string;
    source_filter_json?: (Record<string, any> | null);
    data_schema_json?: (Record<string, any> | null);
    required?: boolean;
    default_value_json?: any;
};

