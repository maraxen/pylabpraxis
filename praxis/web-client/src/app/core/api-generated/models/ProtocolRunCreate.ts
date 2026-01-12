/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProtocolRunStatusEnum } from './ProtocolRunStatusEnum';
/**
 * Schema for creating a ProtocolRun.
 */
export type ProtocolRunCreate = {
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
    updated_at?: (string | null);
    name?: (string | null);
    /**
     * Name of the protocol function
     */
    function_name?: (string | null);
    /**
     * File containing the protocol function
     */
    function_file?: (string | null);
    status?: ProtocolRunStatusEnum;
    /**
     * When the protocol run started
     */
    started_at?: (string | null);
    /**
     * When the protocol run completed
     */
    completed_at?: (string | null);
    /**
     * Error message if the run failed
     */
    error_message?: (string | null);
    /**
     * Path to data directory
     */
    data_directory_path?: (string | null);
    top_level_protocol_definition_accession_id: string;
    run_accession_id?: (string | null);
};

