/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataOutputTypeEnum } from './DataOutputTypeEnum';
import type { SpatialContextEnum } from './SpatialContextEnum';
/**
 * Model for function data output responses.
 */
export type FunctionDataOutputResponse = {
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
    spatial_context: SpatialContextEnum;
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
     * ID of the function call
     */
    function_call_log_accession_id: string;
    /**
     * ID of the protocol run
     */
    protocol_run_accession_id: string;
    /**
     * ID of associated resource
     */
    resource_accession_id?: (string | null);
    /**
     * ID of associated machine
     */
    machine_accession_id?: (string | null);
    /**
     * ID of associated deck position
     */
    deck_accession_id?: (string | null);
    /**
     * Numeric data value
     */
    data_value_numeric?: (number | null);
    /**
     * Structured data
     */
    data_value_json?: (Record<string, any> | null);
    /**
     * Text data
     */
    data_value_text?: (string | null);
    /**
     * Path to external file
     */
    file_path?: (string | null);
    /**
     * File size in bytes
     */
    file_size_bytes?: (number | null);
    /**
     * When the measurement was captured
     */
    measurement_timestamp: string;
    /**
     * ID of source data if derived
     */
    derived_from_data_output_accession_id?: (string | null);
};

