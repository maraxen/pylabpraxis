/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ScheduleStatusEnum } from './ScheduleStatusEnum';
/**
 * Request model for updating a schedule entry.
 */
export type ScheduleEntryUpdate = {
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
    status?: (ScheduleStatusEnum | null);
    priority?: (number | null);
    last_error_message?: (string | null);
    execution_started_at?: (string | null);
    execution_completed_at?: (string | null);
};

