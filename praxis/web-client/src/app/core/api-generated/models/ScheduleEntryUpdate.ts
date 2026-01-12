/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ScheduleStatusEnum } from './ScheduleStatusEnum';
/**
 * Schema for updating a ScheduleEntry (partial update).
 */
export type ScheduleEntryUpdate = {
    name?: (string | null);
    status?: (ScheduleStatusEnum | null);
    scheduled_at?: (string | null);
    execution_started_at?: (string | null);
    execution_completed_at?: (string | null);
    priority?: (number | null);
    last_error_message?: (string | null);
};

