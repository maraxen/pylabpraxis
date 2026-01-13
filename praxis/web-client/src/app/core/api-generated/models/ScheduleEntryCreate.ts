/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ScheduleStatusEnum } from './ScheduleStatusEnum';
/**
 * Schema for creating a ScheduleEntry.
 */
export type ScheduleEntryCreate = {
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
    name?: (string | null);
    /**
     * Arbitrary metadata.
     */
    properties_json?: (Record<string, any> | null);
    status?: ScheduleStatusEnum;
    /**
     * Scheduled start time
     */
    scheduled_at?: (string | null);
    /**
     * Actual start time
     */
    execution_started_at?: (string | null);
    /**
     * Actual end time
     */
    execution_completed_at?: (string | null);
    /**
     * Priority for scheduling
     */
    priority?: number;
    /**
     * Estimated duration
     */
    estimated_duration_ms?: (number | null);
    /**
     * Required asset count
     */
    required_asset_count?: number;
    /**
     * User parameters
     */
    user_params_json?: (Record<string, any> | null);
    /**
     * Asset requirements
     */
    asset_requirements_json?: (Record<string, any> | null);
    asset_analysis_completed_at?: (string | null);
    assets_reserved_at?: (string | null);
    celery_task_id?: (string | null);
    celery_queue_name?: (string | null);
    retry_count?: number;
    max_retries?: number;
    last_error_message?: (string | null);
    initial_state_json?: (Record<string, any> | null);
    protocol_run_accession_id: string;
};

