/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Schema for reading a WellDataOutput (API response).
 */
export type WellDataOutputRead = {
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
     * Well position (e.g., 'A1')
     */
    well_position?: (string | null);
    /**
     * Type of measurement
     */
    measurement_type?: (string | null);
    /**
     * Measured value
     */
    value?: (number | null);
    /**
     * Unit of measurement
     */
    unit?: (string | null);
    /**
     * Well name (e.g. A1)
     */
    well_name?: (string | null);
    data_value?: (number | null);
    metadata_json?: (Record<string, any> | null);
};

