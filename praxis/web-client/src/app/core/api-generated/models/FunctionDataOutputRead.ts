/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataOutputTypeEnum } from './DataOutputTypeEnum';
import type { SpatialContextEnum } from './SpatialContextEnum';
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
    data_type: DataOutputTypeEnum;
    /**
     * Unique key within the function call
     */
    data_key: string;
    /**
     * Spatial context of the data
     */
    spatial_context?: SpatialContextEnum;
    /**
     * Spatial coordinates within resource
     */
    spatial_coordinates_json?: (Record<string, any> | null);
    /**
     * Units of measurement
     */
    data_units?: (string | null);
    /**
     * Quality score (0.0-1.0)
     */
    data_quality_score?: (number | null);
    /**
     * Measurement conditions
     */
    measurement_conditions_json?: (Record<string, any> | null);
    /**
     * Sequence number within the function call
     */
    sequence_in_function?: (number | null);
    /**
     * Path to external file
     */
    file_path?: (string | null);
    /**
     * File size in bytes
     */
    file_size_bytes?: (number | null);
    /**
     * MIME type of the output
     */
    mime_type?: (string | null);
    /**
     * When the measurement was captured
     */
    measurement_timestamp?: (string | null);
    data_json?: (Record<string, any> | null);
    data_value_numeric?: (number | null);
    data_value_text?: (string | null);
    function_call_log_accession_id: string;
    protocol_run_accession_id: string;
    resource_accession_id?: (string | null);
    machine_accession_id?: (string | null);
    deck_accession_id?: (string | null);
    derived_from_data_output_accession_id?: (string | null);
};

