/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Model for well data output responses.
 */
export type WellDataOutputResponse = {
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
     * Well name (e.g., 'A1')
     */
    well_name: string;
    /**
     * 0-based row index
     */
    well_row: number;
    /**
     * 0-based column index
     */
    well_column: number;
    /**
     * Linear well index
     */
    well_index?: (number | null);
    /**
     * Primary numeric value for this well
     */
    data_value?: (number | null);
    /**
     * ID of the parent function data output
     */
    function_data_output_accession_id: string;
    /**
     * ID of the plate resource
     */
    plate_resource_accession_id: string;
};

