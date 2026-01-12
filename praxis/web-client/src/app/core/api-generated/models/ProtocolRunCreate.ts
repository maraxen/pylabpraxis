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
    /**
     * An optional name for the record.
     */
    name: string;
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
};

