/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResourceReservationResponse } from './ResourceReservationResponse';
import type { ScheduleStatusEnum } from './ScheduleStatusEnum';
/**
 * Response model for schedule entries.
 */
export type ScheduleEntryResponse = {
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
    protocol_run_accession_id: string;
    status: ScheduleStatusEnum;
    priority: number;
    scheduled_at: (string | null);
    started_at?: (string | null);
    completed_at?: (string | null);
    estimated_duration_ms?: (number | null);
    estimated_resource_count?: (number | null);
    analysis_details?: (Record<string, any> | null);
    scheduling_metadata?: (Record<string, any> | null);
    error_details?: (string | null);
    status_details?: (string | null);
    resource_reservations?: (Array<ResourceReservationResponse> | null);
};

