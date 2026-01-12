/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Schema for reading a FunctionDataOutput (API response).
 */
export type FunctionDataOutputRead = {
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
     * Type of data output
     */
    data_type?: (string | null);
    /**
     * File path for output data
     */
    file_path?: (string | null);
    /**
     * MIME type of the output
     */
    mime_type?: (string | null);
    data_json?: (Record<string, any> | null);
    data_quality_score?: (number | null);
    data_key?: (string | null);
};

