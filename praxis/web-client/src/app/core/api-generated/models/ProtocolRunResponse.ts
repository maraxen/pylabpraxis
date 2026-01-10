/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProtocolRunStatusEnum } from './ProtocolRunStatusEnum';
/**
 * Model for API responses for a protocol run.
 */
export type ProtocolRunResponse = {
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
    name?: (string | null);
    /**
     * Arbitrary metadata associated with the record.
     */
    properties_json?: (Record<string, any> | null);
    status?: (ProtocolRunStatusEnum | null);
    start_time?: (string | null);
    end_time?: (string | null);
    input_parameters_json?: (Record<string, any> | null);
    resolved_assets_json?: (Record<string, any> | null);
    output_data_json?: (Record<string, any> | null);
    initial_state_json?: (Record<string, any> | null);
    final_state_json?: (Record<string, any> | null);
    data_directory_path?: (string | null);
    created_by_user?: (Record<string, any> | null);
    previous_accession_id?: (string | null);
};

