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
    name: string;
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
    data_directory_path?: (string | null);
    function_args_json?: (Record<string, any> | null);
    function_kwargs_json?: (Record<string, any> | null);
    result_json?: (Record<string, any> | null);
    output_data_json?: (Record<string, any> | null);
};

