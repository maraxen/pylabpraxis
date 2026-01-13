/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProtocolRunStatusEnum } from './ProtocolRunStatusEnum';
/**
 * Schema for reading a ProtocolRun (API response).
 */
export type ProtocolRunRead = {
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
    name?: (string | null);
    /**
     * Arbitrary metadata.
     */
    properties_json?: (Record<string, any> | null);
    /**
     * Current status of the protocol run
     */
    status?: ProtocolRunStatusEnum;
    /**
     * When the protocol run started
     */
    start_time?: (string | null);
    /**
     * When the protocol run completed
     */
    end_time?: (string | null);
    /**
     * Path to data directory
     */
    data_directory_path?: (string | null);
    /**
     * Duration in milliseconds
     */
    duration_ms?: (number | null);
    top_level_protocol_definition_accession_id: string;
    protocol_name?: (string | null);
    started_at?: (string | null);
    completed_at?: (string | null);
    input_parameters_json?: (Record<string, any> | null);
    resolved_assets_json?: (Record<string, any> | null);
    output_data_json?: (Record<string, any> | null);
};

