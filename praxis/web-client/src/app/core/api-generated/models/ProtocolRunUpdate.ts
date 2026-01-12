/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProtocolRunStatusEnum } from './ProtocolRunStatusEnum';
/**
 * Schema for updating a ProtocolRun (partial update).
 */
export type ProtocolRunUpdate = {
    status?: (ProtocolRunStatusEnum | null);
    start_time?: (string | null);
    end_time?: (string | null);
    output_data_json?: (Record<string, any> | null);
    data_directory_path?: (string | null);
};

