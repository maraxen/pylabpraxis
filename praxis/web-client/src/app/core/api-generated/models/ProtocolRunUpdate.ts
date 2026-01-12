/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProtocolRunStatusEnum } from './ProtocolRunStatusEnum';
/**
 * Schema for updating a ProtocolRun (partial update).
 */
export type ProtocolRunUpdate = {
    name?: (string | null);
    status?: (ProtocolRunStatusEnum | null);
    started_at?: (string | null);
    completed_at?: (string | null);
    error_message?: (string | null);
    result_json?: (Record<string, any> | null);
    output_data_json?: (Record<string, any> | null);
    data_directory_path?: (string | null);
};

